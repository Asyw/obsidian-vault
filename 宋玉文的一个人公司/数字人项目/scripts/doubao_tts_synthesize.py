#!/usr/bin/env python3
"""Synthesize narration audio with the configured Doubao cloned voice."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import uuid
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "doubao_speech_config.json"
LEGACY_CONFIG_PATH = ROOT / "ark_config.json"


def load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_config() -> dict[str, object]:
    path = CONFIG_PATH if CONFIG_PATH.exists() else LEGACY_CONFIG_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def env_name(env_names: dict[str, str], primary: str, legacy: str = "") -> str:
    return env_names.get(primary) or env_names.get(legacy, "")


def load_settings() -> dict[str, str]:
    config = load_config()
    env_names = config["env"]
    tts = config.get("tts")
    if not isinstance(tts, dict):
        tts = config["models"]["speech"]["tts"]
    env = load_dotenv(ROOT / config["env_file"])

    def value(env_name: str, default: str = "") -> str:
        if not env_name:
            return default
        return os.environ.get(env_name) or env.get(env_name) or default

    return {
        "ark_api_key": value(env_name(env_names, "ark_api_key", "api_key")),
        "speech_api_key": value(env_name(env_names, "speech_api_key")),
        "app_id": value(env_name(env_names, "app_id", "doubao_speech_app_id")),
        "access_token": value(env_name(env_names, "access_token", "doubao_speech_access_token")),
        "endpoint": value(env_name(env_names, "endpoint", "doubao_tts_endpoint"), tts["default_endpoint"]),
        "resource_id": value(
            env_name(env_names, "resource_id", "doubao_tts_resource_id"),
            tts["default_resource_id_header"],
        ),
        "uid": value(env_name(env_names, "uid", "doubao_tts_uid"), "digital-human-project"),
        "voice_id": value(env_name(env_names, "voice_id", "tts_voice_id")),
        "audio_format": value(env_name(env_names, "audio_format", "tts_audio_format"), tts["default_audio_format"]),
        "sample_rate": value(env_name(env_names, "sample_rate", "tts_sample_rate"), str(tts["default_sample_rate"])),
        "speed_ratio": value(env_name(env_names, "speed_ratio", "tts_speed_ratio"), str(tts["default_speed_ratio"])),
        "volume_ratio": value(env_name(env_names, "volume_ratio", "tts_volume_ratio"), str(tts["default_volume_ratio"])),
        "pitch_ratio": value(env_name(env_names, "pitch_ratio", "tts_pitch_ratio"), str(tts["default_pitch_ratio"])),
    }


def ratio_to_rate(value: str) -> int:
    return round((float(value) - 1.0) * 100)


def required_missing(settings: dict[str, str]) -> list[str]:
    missing = []
    if not settings.get("endpoint"):
        missing.append("endpoint")
    if not settings.get("resource_id"):
        missing.append("resource_id")
    if not settings.get("voice_id"):
        missing.append("voice_id")
    if not (
        settings.get("speech_api_key")
        or settings.get("ark_api_key")
        or (settings.get("app_id") and settings.get("access_token"))
    ):
        missing.append("speech_api_key or ark_api_key or app_id/access_token")
    return missing


def parse_audio_response(raw: bytes) -> bytes:
    audio = bytearray()
    text = raw.decode("utf-8", errors="ignore")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines and raw:
        return raw

    for line in lines:
        if line.startswith("data:"):
            line = line[5:].strip()
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        code = msg.get("code")
        if code not in (None, 0, "0", 20000000, "20000000"):
            raise SystemExit("TTS error: " + json.dumps(msg, ensure_ascii=False))
        data = msg.get("data")
        if data:
            audio.extend(base64.b64decode(data))

    if not audio:
        raise SystemExit("TTS response did not contain audio data.")
    return bytes(audio)


def synthesize(settings: dict[str, str], text: str) -> bytes:
    missing = required_missing(settings)
    if missing:
        raise SystemExit("Missing required TTS settings: " + ", ".join(missing))
    if not text:
        raise SystemExit("Text is empty.")

    audio_params = {
        "format": settings["audio_format"],
        "sample_rate": int(settings["sample_rate"]),
        "speech_rate": ratio_to_rate(settings["speed_ratio"]),
        "loudness_rate": ratio_to_rate(settings["volume_ratio"]),
    }
    additions: dict[str, object] = {
        "explicit_language": "zh",
        "post_process": {
            "pitch": ratio_to_rate(settings["pitch_ratio"]),
        },
    }
    if settings["voice_id"].startswith("S_"):
        # Voice clone 2.0 needs model_type=4, otherwise the service can fall
        # back to the old default clone resource and reject the request.
        additions["model_type"] = 4

    payload = {
        "user": {"uid": settings["uid"]},
        "req_params": {
            "text": text,
            "speaker": settings["voice_id"],
            "audio_params": audio_params,
            "additions": json.dumps(additions, ensure_ascii=False, separators=(",", ":")),
        },
    }
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Api-Resource-Id": settings["resource_id"],
        "X-Api-Request-Id": str(uuid.uuid4()),
    }

    if settings.get("speech_api_key"):
        headers["X-Api-Key"] = settings["speech_api_key"]
    elif "/plan/" in settings["endpoint"] and settings.get("ark_api_key"):
        headers["X-Api-Key"] = settings["ark_api_key"]
    else:
        headers["X-Api-App-Key"] = settings["app_id"]
        headers["X-Api-Access-Key"] = settings["access_token"]
        headers["Authorization"] = "Bearer;" + settings["access_token"]

    request = urllib.request.Request(settings["endpoint"], data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"TTS HTTP {exc.code}: {raw}") from exc
    return parse_audio_response(raw)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?", default="")
    parser.add_argument("--text-file")
    parser.add_argument("--output", default="")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    settings = load_settings()
    if args.check:
        print("Doubao TTS config check:")
        for key in ("endpoint", "resource_id", "voice_id", "speech_api_key", "ark_api_key", "app_id", "access_token"):
            value = settings.get(key, "")
            hidden = key in {"voice_id", "speech_api_key", "ark_api_key", "access_token"}
            print(f"  {key}: {'set, hidden' if hidden and value else (value or 'missing')}")
        missing = required_missing(settings)
        return 1 if missing else 0

    text = Path(args.text_file).read_text(encoding="utf-8").strip() if args.text_file else args.text.strip()
    if args.dry_run:
        print(json.dumps({"text": text, "speaker": "<set, hidden>", "resource_id": settings.get("resource_id")}, ensure_ascii=False, indent=2))
        return 0

    audio = synthesize(settings, text)
    suffix = "." + settings["audio_format"].lstrip(".")
    output = Path(args.output) if args.output else ROOT / "outputs" / "audio" / f"tts_{uuid.uuid4().hex[:8]}{suffix}"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(audio)
    print(str(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
