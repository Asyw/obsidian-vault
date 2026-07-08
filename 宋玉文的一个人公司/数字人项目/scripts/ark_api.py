#!/usr/bin/env python3
"""Unified Volcengine Ark API helper for this project."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


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


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_settings() -> dict[str, Any]:
    config = load_config()
    env = load_dotenv(ROOT / config["env_file"])
    env_names = config["env"]

    def value(env_name: str, default: str = "") -> str:
        return os.environ.get(env_name) or env.get(env_name) or default

    selected_profile = config.get("selected_profile", "agent_plan")
    profile = config["profiles"][selected_profile]
    base_url = value(env_names["base_url"], profile["base_url"]).rstrip("/")
    default_model = value(env_names["model"], config["models"]["language"]["routing_model"])

    return {
        "config": config,
        "api_key": value(env_names["api_key"]),
        "base_url": base_url,
        "timeout_seconds": value(env_names["timeout_seconds"], "60"),
        "model": default_model,
        "responses_model": value(env_names["responses_model"], default_model),
        "embedding_model": value(
            env_names["embedding_model"],
            (config["models"].get("embedding", {}).get("model_names") or [""])[0],
        ),
        "image_model": value("ARK_IMAGE_MODEL", "doubao-seedream-5.0-lite"),
        "video_model": value("ARK_VIDEO_MODEL", "doubao-seedance-1.5-pro"),
    }


def require_auth(settings: dict[str, Any]) -> None:
    missing = [key for key in ("api_key", "base_url") if not settings.get(key)]
    if missing:
        raise SystemExit("Missing Ark settings: " + ", ".join(missing))


def endpoint(settings: dict[str, Any], name: str, **params: str) -> str:
    path = settings["config"]["endpoints"][name]
    for key, value in params.items():
        path = path.replace("{" + key + "}", urllib.parse.quote(value, safe=""))
    return settings["base_url"] + path


def request_json(
    settings: dict[str, Any],
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    require_auth(settings)
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {settings['api_key']}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=float(settings["timeout_seconds"])) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Ark HTTP {exc.code}: {raw}") from exc
    return json.loads(raw)


def print_check(settings: dict[str, Any]) -> None:
    config = settings["config"]
    print("Ark API config:")
    print(f"  api_key: {'set, hidden' if settings.get('api_key') else 'missing'}")
    print(f"  base_url: {settings['base_url']}")
    print(f"  chat_model: {settings['model']}")
    print(f"  responses_model: {settings['responses_model']}")
    print(f"  embedding_model: {settings['embedding_model']}")
    print(f"  image_model: {settings['image_model']}")
    print(f"  video_model: {settings['video_model']}")
    print("  endpoints:")
    for name in config["endpoints"]:
        print(f"    {name}: {settings['base_url']}{config['endpoints'][name]}")


def output_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def command_chat(settings: dict[str, Any], prompt: str) -> dict[str, Any]:
    return request_json(
        settings,
        "POST",
        endpoint(settings, "chat_completions"),
        {
            "model": settings["model"],
            "messages": [{"role": "user", "content": prompt}],
        },
    )


def command_responses(settings: dict[str, Any], prompt: str) -> dict[str, Any]:
    return request_json(
        settings,
        "POST",
        endpoint(settings, "responses"),
        {
            "model": settings["responses_model"],
            "input": prompt,
        },
    )


def command_embeddings(settings: dict[str, Any], text: str) -> dict[str, Any]:
    return request_json(
        settings,
        "POST",
        endpoint(settings, "embeddings"),
        {
            "model": settings["embedding_model"],
            "input": text,
        },
    )


def command_image(settings: dict[str, Any], prompt: str, model: str | None) -> dict[str, Any]:
    return request_json(
        settings,
        "POST",
        endpoint(settings, "images_generations"),
        {
            "model": model or settings["image_model"],
            "prompt": prompt,
        },
    )


def command_video_submit(settings: dict[str, Any], prompt: str, model: str | None) -> dict[str, Any]:
    return request_json(
        settings,
        "POST",
        endpoint(settings, "video_generation_tasks"),
        {
            "model": model or settings["video_model"],
            "content": [{"type": "text", "text": prompt}],
        },
    )


def command_video_query(settings: dict[str, Any], task_id: str) -> dict[str, Any]:
    return request_json(
        settings,
        "GET",
        endpoint(settings, "video_generation_task", id=task_id),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check")

    chat = sub.add_parser("chat")
    chat.add_argument("prompt")

    responses = sub.add_parser("responses")
    responses.add_argument("prompt")

    embeddings = sub.add_parser("embeddings")
    embeddings.add_argument("text")

    image = sub.add_parser("image")
    image.add_argument("prompt")
    image.add_argument("--model")

    video_submit = sub.add_parser("video-submit")
    video_submit.add_argument("prompt")
    video_submit.add_argument("--model")

    video_query = sub.add_parser("video-query")
    video_query.add_argument("task_id")

    args = parser.parse_args()
    settings = load_settings()

    if args.command == "check":
        print_check(settings)
    elif args.command == "chat":
        output_json(command_chat(settings, args.prompt))
    elif args.command == "responses":
        output_json(command_responses(settings, args.prompt))
    elif args.command == "embeddings":
        output_json(command_embeddings(settings, args.text))
    elif args.command == "image":
        output_json(command_image(settings, args.prompt, args.model))
    elif args.command == "video-submit":
        output_json(command_video_submit(settings, args.prompt, args.model))
    elif args.command == "video-query":
        output_json(command_video_query(settings, args.task_id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
