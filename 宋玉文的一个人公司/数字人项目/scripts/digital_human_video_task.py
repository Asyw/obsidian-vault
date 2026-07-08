#!/usr/bin/env python3
"""Submit/query Volcengine cloned digital-human video tasks.

The digital-human video API accepts a public audio_url, not raw text.
Use this after narration audio has been uploaded somewhere the API can fetch.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import hmac
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "digital_human_config.json"


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
    env = load_dotenv(ROOT / config["env_file"])

    def value(env_name: str, default: str = "") -> str:
        return os.environ.get(env_name) or env.get(env_name) or default

    auth = config["auth"]
    api = config["api"]
    inputs = config["inputs"]
    return {
        "access_key_id": value(auth["access_key_id_env"]),
        "secret_access_key": value(auth["secret_access_key_env"]),
        "endpoint": value(api["endpoint_env"], api["default_endpoint"]).rstrip("/"),
        "region": value(api["region_env"], api["default_region"]),
        "service": value(api["service_env"], api["default_service"]),
        "version": value(api["version_env"], api["default_version"]),
        "submit_action": api["submit_action"],
        "query_action": api["query_action"],
        "req_key": value(inputs["req_key_env"], inputs["default_req_key"]),
        "resource_id": value(inputs["avatar_id_env"]),
        "audio_url": value(inputs["audio_url_env"]),
    }


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hmac_sha256(key: bytes, message: str) -> bytes:
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()


def sign_key(secret: str, date: str, region: str, service: str) -> bytes:
    k_date = hmac_sha256(secret.encode("utf-8"), date)
    k_region = hmac_sha256(k_date, region)
    k_service = hmac_sha256(k_region, service)
    return hmac_sha256(k_service, "request")


def signed_request(settings: dict[str, str], action: str, body: dict[str, Any]) -> dict[str, Any]:
    missing = [
        key
        for key in ("access_key_id", "secret_access_key", "endpoint", "region", "service")
        if not settings.get(key)
    ]
    if missing:
        raise SystemExit("Missing required settings: " + ", ".join(missing))

    parsed = urllib.parse.urlparse(settings["endpoint"])
    host = parsed.netloc
    canonical_uri = parsed.path or "/"
    query = urllib.parse.urlencode({"Action": action, "Version": settings["version"]})
    payload = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    payload_hash = sha256_hex(payload)
    now = dt.datetime.now(dt.timezone.utc)
    x_date = now.strftime("%Y%m%dT%H%M%SZ")
    short_date = now.strftime("%Y%m%d")

    headers = {
        "content-type": "application/json",
        "host": host,
        "x-content-sha256": payload_hash,
        "x-date": x_date,
    }
    signed_headers = ";".join(sorted(headers))
    canonical_headers = "".join(f"{key}:{headers[key]}\n" for key in sorted(headers))
    canonical_request = "\n".join(
        ["POST", canonical_uri, query, canonical_headers, signed_headers, payload_hash]
    )
    credential_scope = f"{short_date}/{settings['region']}/{settings['service']}/request"
    string_to_sign = "\n".join(
        [
            "HMAC-SHA256",
            x_date,
            credential_scope,
            sha256_hex(canonical_request.encode("utf-8")),
        ]
    )
    signature = hmac.new(
        sign_key(settings["secret_access_key"], short_date, settings["region"], settings["service"]),
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    headers["authorization"] = (
        "HMAC-SHA256 "
        f"Credential={settings['access_key_id']}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    request_headers = {key.title(): value for key, value in headers.items()}
    url = f"{settings['endpoint']}{canonical_uri}?{query}"
    request = urllib.request.Request(url, data=payload, headers=request_headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {raw}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def submit(settings: dict[str, str], audio_url: str | None, templ_start_seconds: float | None) -> dict[str, Any]:
    audio_url = audio_url or settings.get("audio_url")
    if not audio_url:
        raise SystemExit("Missing audio URL. Pass --audio-url or set DIGITAL_HUMAN_AUDIO_URL.")
    if not settings.get("resource_id"):
        raise SystemExit("Missing DIGITAL_HUMAN_AVATAR_ID.")

    body: dict[str, Any] = {
        "req_key": settings["req_key"],
        "resource_id": settings["resource_id"],
        "audio_url": audio_url,
    }
    if templ_start_seconds is not None:
        body["templ_start_strategy"] = "start_from_given_seconds"
        body["templ_start_seconds"] = templ_start_seconds
    return signed_request(settings, settings["submit_action"], body)


def query(settings: dict[str, str], task_id: str) -> dict[str, Any]:
    body = {
        "req_key": settings["req_key"],
        "task_id": task_id,
    }
    return signed_request(settings, settings["query_action"], body)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    submit_parser = sub.add_parser("submit")
    submit_parser.add_argument("--audio-url", help="Public wav/mp3 URL for the narration audio.")
    submit_parser.add_argument("--templ-start-seconds", type=float)
    submit_parser.add_argument("--dry-run", action="store_true")

    query_parser = sub.add_parser("query")
    query_parser.add_argument("task_id")

    args = parser.parse_args()
    settings = load_settings()

    if args.command == "submit":
        audio_url = args.audio_url or settings.get("audio_url")
        body = {
            "req_key": settings.get("req_key"),
            "resource_id": "<set, hidden>" if settings.get("resource_id") else "",
            "audio_url": audio_url or "",
        }
        if args.templ_start_seconds is not None:
            body["templ_start_strategy"] = "start_from_given_seconds"
            body["templ_start_seconds"] = args.templ_start_seconds
        if args.dry_run:
            print(json.dumps(body, ensure_ascii=False, indent=2))
            return 0
        result = submit(settings, args.audio_url, args.templ_start_seconds)
    else:
        result = query(settings, args.task_id)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
