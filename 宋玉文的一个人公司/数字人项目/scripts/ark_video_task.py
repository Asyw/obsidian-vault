#!/usr/bin/env python3
"""Submit, poll, and download Ark/Seedance video generation tasks."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARK_CONFIG_PATH = ROOT / "ark_config.json"


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
    config = json.loads(ARK_CONFIG_PATH.read_text(encoding="utf-8"))
    env = load_dotenv(ROOT / config["env_file"])
    env_names = config["env"]

    def value(env_name: str, default: str = "") -> str:
        return os.environ.get(env_name) or env.get(env_name) or default

    base_url = value(env_names["base_url"], config["profiles"]["agent_plan"]["base_url"]).rstrip("/")
    return {
        "api_key": value(env_names["api_key"]),
        "base_url": base_url,
        "video_model": value("ARK_VIDEO_MODEL", "doubao-seedance-1.5-pro"),
        "timeout_seconds": value(env_names["timeout_seconds"], "60"),
        "create_path": config["endpoints"]["video_generation_tasks"],
        "query_path": config["endpoints"]["video_generation_task"],
        "output_dir": value("SHORT_VIDEO_OUTPUT_DIR", "outputs/videos"),
    }


def require_settings(settings: dict[str, str]) -> None:
    missing = [key for key in ("api_key", "base_url", "video_model") if not settings.get(key)]
    if missing:
        raise SystemExit("Missing settings: " + ", ".join(missing))


def request_json(settings: dict[str, str], method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
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
        raise SystemExit(f"HTTP {exc.code}: {raw}") from exc
    return json.loads(raw)


def build_content(prompt: str, image_urls: list[str] | None = None) -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for image_url in image_urls or []:
        content.append({"type": "image_url", "image_url": {"url": image_url}})
    return content


def submit(
    settings: dict[str, str],
    prompt: str,
    model: str | None = None,
    image_urls: list[str] | None = None,
    ratio: str | None = None,
    duration: int | None = None,
    resolution: str | None = None,
) -> dict[str, Any]:
    require_settings(settings)
    payload: dict[str, Any] = {
        "model": model or settings["video_model"],
        "content": build_content(prompt, image_urls),
    }
    if ratio:
        payload["ratio"] = ratio
    if duration:
        payload["duration"] = duration
    if resolution:
        payload["resolution"] = resolution
    return request_json(settings, "POST", settings["base_url"] + settings["create_path"], payload)


def query(settings: dict[str, str], task_id: str) -> dict[str, Any]:
    require_settings(settings)
    path = settings["query_path"].replace("{id}", urllib.parse.quote(task_id, safe=""))
    return request_json(settings, "GET", settings["base_url"] + path)


def find_task_id(response: dict[str, Any]) -> str:
    for key in ("id", "task_id"):
        value = response.get(key)
        if isinstance(value, str) and value:
            return value
    data = response.get("data")
    if isinstance(data, dict):
        for key in ("id", "task_id"):
            value = data.get(key)
            if isinstance(value, str) and value:
                return value
    raise SystemExit("Could not find task id in response: " + json.dumps(response, ensure_ascii=False))


def find_status(response: dict[str, Any]) -> str:
    candidates: list[Any] = [
        response.get("status"),
        response.get("task_status"),
        response.get("state"),
    ]
    data = response.get("data")
    if isinstance(data, dict):
        candidates.extend([data.get("status"), data.get("task_status"), data.get("state")])
    for candidate in candidates:
        if candidate is not None:
            return str(candidate).lower()
    return "unknown"


def find_video_url(response: dict[str, Any]) -> str | None:
    def walk(value: Any) -> str | None:
        if isinstance(value, dict):
            for key in ("url", "video_url", "result_url", "content_url"):
                item = value.get(key)
                if isinstance(item, str) and item.startswith(("http://", "https://")):
                    return item
            for item in value.values():
                found = walk(item)
                if found:
                    return found
        elif isinstance(value, list):
            for item in value:
                found = walk(item)
                if found:
                    return found
        return None

    return walk(response)


def download(url: str, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=300) as response:
        output.write_bytes(response.read())
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    submit_parser = sub.add_parser("submit")
    submit_parser.add_argument("--prompt", required=True)
    submit_parser.add_argument("--model")
    submit_parser.add_argument("--image-url", action="append", default=[])
    submit_parser.add_argument("--ratio")
    submit_parser.add_argument("--duration", type=int)
    submit_parser.add_argument("--resolution")
    submit_parser.add_argument("--metadata-output")
    submit_parser.add_argument("--dry-run", action="store_true")

    query_parser = sub.add_parser("query")
    query_parser.add_argument("task_id")

    poll_parser = sub.add_parser("poll")
    poll_parser.add_argument("task_id")
    poll_parser.add_argument("--interval", type=float, default=10)
    poll_parser.add_argument("--max-wait", type=float, default=900)
    poll_parser.add_argument("--download-output")
    poll_parser.add_argument("--metadata-output")

    args = parser.parse_args()
    settings = load_settings()

    if args.command == "submit":
        payload_preview = {
            "model": args.model or settings["video_model"],
            "content": build_content(args.prompt, args.image_url),
        }
        if args.ratio:
            payload_preview["ratio"] = args.ratio
        if args.duration:
            payload_preview["duration"] = args.duration
        if args.resolution:
            payload_preview["resolution"] = args.resolution
        if args.dry_run:
            print(json.dumps(payload_preview, ensure_ascii=False, indent=2))
            return 0
        result = submit(settings, args.prompt, args.model, args.image_url, args.ratio, args.duration, args.resolution)
        if args.metadata_output:
            Path(args.metadata_output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.metadata_output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "query":
        result = query(settings, args.task_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    deadline = time.monotonic() + args.max_wait
    result: dict[str, Any] = {}
    while True:
        result = query(settings, args.task_id)
        status = find_status(result)
        video_url = find_video_url(result)
        print(json.dumps({"task_id": args.task_id, "status": status, "has_video_url": bool(video_url)}, ensure_ascii=False))
        if video_url:
            if args.download_output:
                path = download(video_url, Path(args.download_output))
                result["_downloaded_to"] = str(path)
            break
        if status in {"failed", "failure", "cancelled", "canceled", "error"}:
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(args.interval)

    if args.metadata_output:
        Path(args.metadata_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.metadata_output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
