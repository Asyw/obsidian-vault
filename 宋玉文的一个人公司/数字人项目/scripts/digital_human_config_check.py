#!/usr/bin/env python3
"""Check local digital-human talking-video configuration without exposing secrets."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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


def main() -> int:
    config = json.loads((ROOT / "digital_human_config.json").read_text(encoding="utf-8"))
    env = load_dotenv(ROOT / config["env_file"])

    required = {
        "volcengine_access_key_id": config["auth"]["access_key_id_env"],
        "volcengine_secret_access_key": config["auth"]["secret_access_key_env"],
        "digital_human_avatar_id": config["inputs"]["avatar_id_env"],
        "digital_human_req_key": config["inputs"]["req_key_env"],
        "tts_voice_id": config["inputs"]["voice_id_env"],
        "tts_resource_id": config["inputs"]["tts_resource_id_env"],
        "aspect_ratio": config["output"]["aspect_ratio_env"],
        "resolution": config["output"]["resolution_env"],
    }

    optional = {
        "digital_human_audio_url": config["inputs"]["audio_url_env"],
        "doubao_speech_api_key": "DOUBAO_SPEECH_API_KEY",
        "doubao_speech_app_id": "DOUBAO_SPEECH_APP_ID",
        "doubao_speech_access_token": "DOUBAO_SPEECH_ACCESS_TOKEN",
        "doubao_speech_secret_key": "DOUBAO_SPEECH_SECRET_KEY",
    }

    missing: list[str] = []
    print("Digital-human config check:")
    for label, env_name in required.items():
        value = env.get(env_name, "")
        if value:
            display = "set"
            if "key" in label or "secret" in label or "id" in label:
                display = "set, hidden"
        else:
            display = "missing"
            missing.append(env_name)
        print(f"  {label}: {display}")

    print("\nOptional speech-service credentials:")
    for label, env_name in optional.items():
        value = env.get(env_name, "")
        if value:
            display = "set, hidden" if "token" in label or "secret" in label else "set"
        else:
            display = "missing"
        print(f"  {label}: {display}")

    if missing:
        print("\nMissing env values:")
        for env_name in missing:
            print(f"  - {env_name}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
