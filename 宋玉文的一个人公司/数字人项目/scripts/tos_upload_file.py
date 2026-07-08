#!/usr/bin/env python3
"""Upload a local file to Volcengine TOS and optionally save a presigned URL."""

from __future__ import annotations

import argparse
import datetime as dt
import mimetypes
import os
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
    missing = [key for key in ("access_key_id", "secret_access_key", "endpoint", "region", "bucket") if not settings.get(key)]
    if missing:
        raise SystemExit("Missing TOS settings: " + ", ".join(missing))


def upload_file(settings: dict[str, str], file_path: Path, prefix: str, expires: int) -> str:
    if not file_path.exists():
        raise SystemExit(f"File not found: {file_path}")
    require_settings(settings)
    client = tos.TosClientV2(
        settings["access_key_id"],
        settings["secret_access_key"],
        settings["endpoint"],
        settings["region"],
    )
    suffix = file_path.suffix.lower()
    key = f"{prefix.strip('/')}/{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}{suffix}"
    content_type = mimetypes.guess_type(file_path.name)[0]
    client.put_object_from_file(settings["bucket"], key, str(file_path), content_type=content_type)
    signed = client.pre_signed_url(tos.HttpMethodType.Http_Method_Get, settings["bucket"], key, expires=expires)
    return signed.signed_url


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--prefix", default="digital-human/reference")
    parser.add_argument("--expires", type=int, default=86400)
    parser.add_argument("--url-output", default="")
    args = parser.parse_args()

    url = upload_file(load_settings(), Path(args.file), args.prefix, args.expires)
    if args.url_output:
        output_path = Path(args.url_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(url + "\n", encoding="utf-8")
        output_path.chmod(0o600)
    else:
        print(url)
    print(f"Uploaded file to TOS; url=set, expires={args.expires}s, length={len(url)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
