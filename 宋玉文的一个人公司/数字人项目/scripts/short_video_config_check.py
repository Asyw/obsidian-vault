#!/usr/bin/env python3
"""Check short-video generation config without exposing secrets."""

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


def status(label: str, env_name: str, env: dict[str, str], secret: bool = False) -> bool:
    value = env.get(env_name, "")
    if value:
        display = "set, hidden" if secret else value
        if not secret and ("KEY" in env_name or "TOKEN" in env_name or "SECRET" in env_name):
            display = "set, hidden"
    else:
        display = "missing"
    print(f"  {label}: {display}")
    return bool(value)


def main() -> int:
    config = json.loads((ROOT / "short_video_config.json").read_text(encoding="utf-8"))
    env = load_dotenv(ROOT / config["env_file"])
    fields = config["env"]

    print("Short-video config check:")
    required = {
        "ark_api_key": fields["ark_api_key"],
        "ark_base_url": fields["ark_base_url"],
        "video_model": fields["video_model"],
        "image_model": fields["image_model"],
        "tts_voice_id": fields["tts_voice_id"],
        "tts_resource_id": fields["tts_resource_id"],
        "aspect_ratio": fields["aspect_ratio"],
        "resolution": fields["resolution"],
        "duration_seconds": fields["duration_seconds"],
        "output_dir": fields["output_dir"],
    }

    missing: list[str] = []
    for label, env_name in required.items():
        secret = label in {"ark_api_key", "tts_voice_id"}
        if not status(label, env_name, env, secret=secret):
            missing.append(env_name)

    print("\nOptional for talking-head mode:")
    status("digital_human_avatar_id", fields["digital_human_avatar_id"], env, secret=True)

    if missing:
        print("\nMissing env values:")
        for env_name in missing:
            print(f"  - {env_name}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
