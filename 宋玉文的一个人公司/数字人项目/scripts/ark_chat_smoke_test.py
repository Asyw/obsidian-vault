#!/usr/bin/env python3
"""Small Volcengine Ark chat-completions smoke test.

Usage:
  python3 scripts/ark_chat_smoke_test.py --check
  python3 scripts/ark_chat_smoke_test.py "Say hello in Chinese."
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "ark_config.json"


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


def load_settings() -> dict[str, str]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    env_names = config["env"]
    env_values = load_dotenv(ROOT / config["env_file"])

    def get_value(name: str, default: str = "") -> str:
        return os.environ.get(name) or env_values.get(name) or default

    selected_profile = config.get("selected_profile", "agent_plan")
    profile = config["profiles"][selected_profile]
    base_url = get_value(env_names["base_url"], profile["base_url"])

    return {
        "api_key": get_value(env_names["api_key"]),
        "model": get_value(env_names["model"]),
        "base_url": base_url.rstrip("/"),
        "timeout_seconds": get_value(env_names["timeout_seconds"], "60"),
        "chat_path": config["endpoints"]["chat_completions"],
    }


def require_settings(settings: dict[str, str]) -> None:
    missing = [
        name
        for name in ("api_key", "model", "base_url")
        if not settings.get(name)
    ]
    if missing:
        names = ", ".join(missing)
        raise SystemExit(f"Missing required Ark config values: {names}")


def print_check(settings: dict[str, str]) -> None:
    print("Ark config check:")
    print(f"  api_key: {'set' if settings['api_key'] else 'missing'}")
    print(f"  model: {'set' if settings['model'] else 'missing'}")
    print(f"  base_url: {settings['base_url'] or 'missing'}")
    print(f"  timeout_seconds: {settings['timeout_seconds']}")


def call_chat(settings: dict[str, str], prompt: str) -> str:
    require_settings(settings)

    payload = {
        "model": settings["model"],
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }
    request = urllib.request.Request(
        settings["base_url"] + settings["chat_path"],
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings['api_key']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=float(settings["timeout_seconds"]),
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Ark HTTP {exc.code}: {body}") from exc

    choices = data.get("choices") or []
    if not choices:
        return json.dumps(data, ensure_ascii=False, indent=2)

    message = choices[0].get("message") or {}
    content = message.get("content")
    return content if isinstance(content, str) else json.dumps(data, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="?", default="你好，请用一句话介绍你自己。")
    parser.add_argument("--check", action="store_true", help="Only check local config.")
    args = parser.parse_args()

    settings = load_settings()
    if args.check:
        print_check(settings)
        return 0

    print(call_chat(settings, args.prompt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
