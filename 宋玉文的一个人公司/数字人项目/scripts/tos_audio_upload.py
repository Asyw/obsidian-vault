#!/usr/bin/env python3
"""Upload narration audio to Volcengine TOS and store a presigned URL."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
import uuid
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

try:
    import tos
except ImportError as exc:  # pragma: no cover - environment check
    raise SystemExit("Missing Python package: tos. Install with `python3 -m pip install --user tos`.") from exc


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env.local"
DEFAULT_ENDPOINT = "https://tos-cn-beijing.volces.com"
DEFAULT_REGION = "cn-beijing"


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


def update_dotenv(path: Path, updates: dict[str, str]) -> None:
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    seen: set[str] = set()
    output: list[str] = []
    for line in existing:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            output.append(line)
            continue
        key = line.split("=", 1)[0].strip()
        if key in updates:
            output.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            output.append(line)
    missing = [key for key in updates if key not in seen]
    if missing and output and output[-1].strip():
        output.append("")
    for key in missing:
        output.append(f"{key}={updates[key]}")
    path.write_text("\n".join(output) + "\n", encoding="utf-8")


def parse_access_key_file(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace").replace("\ufeff", "")
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(
            r"^\s*(AccessKeyID|AccessKeyId|AccessKey|SecretAccessKey|SecretKey|Secret Access Key)\s*[:：=]\s*(.+?)\s*$",
            line,
            re.I,
        )
        if not match:
            continue
        key = match.group(1).lower().replace(" ", "")
        value = match.group(2).strip().strip('"').strip("'")
        fields[key] = value
    access_key_id = fields.get("accesskeyid") or fields.get("accesskey")
    secret_access_key = fields.get("secretaccesskey") or fields.get("secretkey")
    if not access_key_id or not secret_access_key:
        raise SystemExit("Access key file did not contain AccessKeyID and SecretAccessKey.")
    return {
        "TOS_ACCESS_KEY_ID": access_key_id,
        "TOS_SECRET_ACCESS_KEY": secret_access_key,
    }


def load_settings() -> dict[str, str]:
    env = load_dotenv(ENV_PATH)
    return {
        "access_key_id": os.environ.get("TOS_ACCESS_KEY_ID") or env.get("TOS_ACCESS_KEY_ID", ""),
        "secret_access_key": os.environ.get("TOS_SECRET_ACCESS_KEY") or env.get("TOS_SECRET_ACCESS_KEY", ""),
        "endpoint": os.environ.get("TOS_ENDPOINT") or env.get("TOS_ENDPOINT", DEFAULT_ENDPOINT),
        "region": os.environ.get("TOS_REGION") or env.get("TOS_REGION", DEFAULT_REGION),
        "bucket": os.environ.get("TOS_BUCKET") or env.get("TOS_BUCKET", ""),
    }


def require_settings(settings: dict[str, str]) -> None:
    missing = [key for key in ("access_key_id", "secret_access_key", "endpoint", "region") if not settings.get(key)]
    if missing:
        raise SystemExit("Missing TOS settings: " + ", ".join(missing))


def client_from_settings(settings: dict[str, str]):
    require_settings(settings)
    return tos.TosClientV2(
        settings["access_key_id"],
        settings["secret_access_key"],
        settings["endpoint"],
        settings["region"],
    )


def safe_bucket_name(prefix: str) -> str:
    cleaned = re.sub(r"[^a-z0-9-]+", "-", prefix.lower()).strip("-")
    cleaned = re.sub(r"-+", "-", cleaned) or "digital-human-audio"
    suffix = dt.datetime.now().strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:8]
    name = f"{cleaned}-{suffix}"
    return name[:63].rstrip("-")


def ensure_bucket(settings: dict[str, str], preferred_bucket: str) -> str:
    client = client_from_settings(settings)
    bucket = preferred_bucket or settings.get("bucket") or safe_bucket_name("digital-human-audio")
    try:
        client.create_bucket(bucket)
    except Exception as exc:
        message = str(exc)
        if "BucketAlreadyOwnedByYou" not in message and "BucketAlreadyExists" not in message:
            raise
    update_dotenv(ENV_PATH, {"TOS_BUCKET": bucket})
    return bucket


def upload_audio(settings: dict[str, str], file_path: Path, bucket: str, expires: int) -> str:
    if not file_path.exists():
        raise SystemExit(f"Audio file not found: {file_path}")
    client = client_from_settings(settings)
    key = f"digital-human/audio/{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}{file_path.suffix}"
    client.put_object_from_file(
        bucket,
        key,
        str(file_path),
        content_type="audio/mpeg" if file_path.suffix.lower() == ".mp3" else None,
    )
    signed = client.pre_signed_url(tos.HttpMethodType.Http_Method_Get, bucket, key, expires=expires)
    url = signed.signed_url
    update_dotenv(ENV_PATH, {"DIGITAL_HUMAN_AUDIO_URL": url})
    return url


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    import_parser = sub.add_parser("import-key")
    import_parser.add_argument("--file", default=str(Path.home() / "Downloads" / "AccessKey.txt"))

    upload_parser = sub.add_parser("upload")
    upload_parser.add_argument("audio_file")
    upload_parser.add_argument("--bucket", default="")
    upload_parser.add_argument("--expires", type=int, default=86400)

    check_parser = sub.add_parser("check")
    check_parser.add_argument("--show-buckets", action="store_true")

    args = parser.parse_args()

    if args.command == "import-key":
        updates = parse_access_key_file(Path(args.file))
        updates.update(
            {
                "TOS_ENDPOINT": DEFAULT_ENDPOINT,
                "TOS_REGION": DEFAULT_REGION,
            }
        )
        update_dotenv(ENV_PATH, updates)
        print("Imported TOS access key into .env.local (hidden).")
        return 0

    settings = load_settings()
    if args.command == "check":
        print("TOS config check:")
        for key in ("access_key_id", "secret_access_key", "endpoint", "region", "bucket"):
            value = settings.get(key, "")
            hidden = key in {"access_key_id", "secret_access_key"}
            print(f"  {key}: {'set, hidden' if hidden and value else (value or 'missing')}")
        if args.show_buckets:
            client = client_from_settings(settings)
            buckets = getattr(client.list_buckets(), "buckets", []) or []
            print(f"  buckets: {len(buckets)}")
            for bucket in buckets:
                print(f"    - {getattr(bucket, 'name', '<unknown>')}")
        return 0

    bucket = ensure_bucket(settings, args.bucket)
    settings["bucket"] = bucket
    audio_url = upload_audio(settings, Path(args.audio_file), bucket, args.expires)
    print("Uploaded audio and stored DIGITAL_HUMAN_AUDIO_URL in .env.local.")
    print(f"bucket={bucket}")
    print(f"url=set, expires={args.expires}s, length={len(audio_url)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
