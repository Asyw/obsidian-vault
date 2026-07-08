#!/usr/bin/env python3
"""Create WeChat Official Account drafts from local Markdown articles.

Default behavior is intentionally conservative: create a draft only. Use
--publish when you explicitly want to submit the created draft for publishing.
"""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import re
import sys
import warnings
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

try:
    warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL.*")
    import requests
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("缺少 requests：请先运行 python3 -m pip install requests") from exc


API_BASE = "https://api.weixin.qq.com/cgi-bin"
ARTICLE_STYLE = (
    "max-width:100%;"
    "box-sizing:border-box;"
    "font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','PingFang SC','Microsoft YaHei',Arial,sans-serif;"
    "color:#2b2f33;"
    "font-size:16px;"
    "line-height:1.95;"
    "letter-spacing:0;"
)
P_STYLE = "margin:18px 0;color:#3f464d;font-size:16px;line-height:1.95;"
H1_STYLE = (
    "margin:8px 0 28px;padding:24px 20px;"
    "border-radius:12px;background:#f7f4ed;color:#1f252b;"
    "font-size:24px;line-height:1.45;font-weight:700;text-align:center;"
)
H2_STYLE = (
    "margin:44px 0 18px;padding:8px 0 8px 14px;"
    "border-left:4px solid #b08a45;color:#1f252b;"
    "font-size:20px;line-height:1.55;font-weight:700;"
)
H3_STYLE = "margin:34px 0 14px;color:#1f252b;font-size:18px;line-height:1.55;font-weight:700;"
UL_STYLE = "margin:18px 0;padding:0;list-style:none;"
LI_STYLE = (
    "margin:10px 0;padding:12px 14px;"
    "border-radius:10px;background:#f8f8f5;color:#3f464d;"
    "font-size:16px;line-height:1.8;"
)
QUOTE_STYLE = (
    "margin:24px 0;padding:18px 18px;"
    "border-left:4px solid #b08a45;background:#f7f4ed;"
    "border-radius:0 10px 10px 0;color:#2b2f33;"
)
QUOTE_P_STYLE = "margin:0;color:#2b2f33;font-size:17px;line-height:1.9;font-weight:600;"
IMG_WRAP_STYLE = "margin:28px 0;text-align:center;"
IMG_STYLE = "max-width:100%;height:auto;border-radius:10px;display:block;margin:0 auto;"
MISSING_IMAGE_STYLE = "margin:18px 0;color:#7a6b50;font-size:15px;line-height:1.8;"
PRE_STYLE = (
    "margin:18px 0;padding:14px;border-radius:10px;"
    "background:#f6f6f3;color:#555;font-size:14px;line-height:1.7;white-space:pre-wrap;"
)


class WeChatError(RuntimeError):
    pass


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def api_json(method: str, path: str, *, token: str | None = None, **kwargs: Any) -> dict[str, Any]:
    params = kwargs.pop("params", {})
    if token:
        params["access_token"] = token
    json_payload = kwargs.pop("json", None)
    if json_payload is not None:
        kwargs["data"] = json.dumps(json_payload, ensure_ascii=False).encode("utf-8")
        headers = kwargs.pop("headers", {})
        kwargs["headers"] = {"Content-Type": "application/json; charset=utf-8", **headers}
    url = f"{API_BASE}/{path}"
    response = requests.request(method, url, params=params, timeout=30, **kwargs)
    response.encoding = "utf-8"
    response.raise_for_status()
    data = response.json()
    if data.get("errcode") not in (None, 0):
        raise WeChatError(f"WeChat API error {data.get('errcode')}: {data.get('errmsg')}")
    return data


def get_access_token(app_id: str, app_secret: str) -> str:
    query = urlencode({"grant_type": "client_credential", "appid": app_id, "secret": app_secret})
    data = api_json("GET", f"token?{query}")
    token = data.get("access_token")
    if not token:
        raise WeChatError(f"未拿到 access_token：{data}")
    return str(token)


def upload_material(token: str, file_path: Path, media_type: str = "image") -> str:
    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    suffix = file_path.suffix.lower() or ".bin"
    with file_path.open("rb") as fh:
        files = {"media": (f"cover{suffix}", fh, mime)}
        data = api_json(
            "POST",
            "material/add_material",
            token=token,
            params={"type": media_type},
            files=files,
        )
    media_id = data.get("media_id")
    if not media_id:
        raise WeChatError(f"上传永久素材失败：{data}")
    return str(media_id)


def upload_inline_image(token: str, file_path: Path) -> str:
    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    suffix = file_path.suffix.lower() or ".bin"
    with file_path.open("rb") as fh:
        files = {"media": (f"image{suffix}", fh, mime)}
        data = api_json("POST", "media/uploadimg", token=token, files=files)
    url = data.get("url")
    if not url:
        raise WeChatError(f"上传正文图片失败：{data}")
    return str(url)


def extract_title(markdown: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
    return match.group(1).strip() if match else fallback


def normalize_wechat_title(title: str) -> str:
    """Prefer a concise title because WeChat rejects some long CJK titles."""
    if len(title.encode("utf-8")) <= 42:
        return title
    book_title = re.search(r"《([^》]+)》", title)
    if book_title:
        return book_title.group(1).strip()
    return truncate_utf8(title, 42)


def extract_digest(markdown: str) -> str:
    match = re.search(r"##\s*摘要\s*\n+(.+?)(?:\n##|\Z)", markdown, flags=re.S)
    if not match:
        return ""
    digest = re.sub(r"[>#`*_!\[\]\(\)]", "", match.group(1))
    digest = re.sub(r"\s+", " ", digest).strip()
    return digest[:120]


def truncate_utf8(value: str, max_bytes: int) -> str:
    encoded = value.encode("utf-8")
    if len(encoded) <= max_bytes:
        return value
    return encoded[:max_bytes].decode("utf-8", errors="ignore").rstrip()


def strip_non_article_sections(markdown: str) -> str:
    # These sections are production notes, not article body.
    skip_sections = {"标题备选", "海报金句", "朋友圈转发文案", "图片建议"}
    kept: list[str] = []
    skipping = False
    for line in markdown.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            section = heading.group(1).strip()
            skipping = any(section.startswith(name) for name in skip_sections)
            if skipping:
                continue
        if not skipping:
            kept.append(line)
    return "\n".join(kept).strip()


def markdown_to_html(markdown: str, base_dir: Path, token: str | None) -> str:
    lines = strip_non_article_sections(markdown).splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    in_list = False
    in_quote = False
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f'<p style="{P_STYLE}">{format_inline(" ".join(paragraph), base_dir, token)}</p>')
            paragraph = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    def close_quote() -> None:
        nonlocal in_quote
        if in_quote:
            output.append("</section>")
            in_quote = False

    for line in lines:
        raw = line.rstrip()
        if raw.startswith("```"):
            if in_code:
                output.append(f'<pre style="{PRE_STYLE}">{html.escape(chr(10).join(code_lines))}</pre>')
                code_lines = []
                in_code = False
            else:
                flush_paragraph()
                close_list()
                close_quote()
                in_code = True
            continue
        if in_code:
            code_lines.append(raw)
            continue
        if not raw.strip():
            flush_paragraph()
            close_list()
            close_quote()
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", raw)
        item = re.match(r"^\s*(?:[-*]|\d+[.、])\s+(.+)$", raw)
        quote = re.match(r"^\s*>\s?(.+)$", raw)
        image_only = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", raw.strip())
        flush = heading or item or quote or image_only
        if flush:
            flush_paragraph()
        if heading:
            close_list()
            close_quote()
            level = min(len(heading.group(1)), 3)
            heading_text = html.escape(heading.group(2).strip())
            if level == 1:
                output.append(f'<h1 style="{H1_STYLE}">{heading_text}</h1>')
            elif level == 2:
                output.append(f'<h2 style="{H2_STYLE}">{heading_text}</h2>')
            else:
                output.append(f'<h3 style="{H3_STYLE}">{heading_text}</h3>')
        elif item:
            close_quote()
            if not in_list:
                output.append(f'<ul style="{UL_STYLE}">')
                in_list = True
            output.append(f'<li style="{LI_STYLE}">{format_inline(item.group(1).strip(), base_dir, token)}</li>')
        elif quote:
            close_list()
            if not in_quote:
                output.append(f'<section style="{QUOTE_STYLE}">')
                in_quote = True
            output.append(f'<p style="{QUOTE_P_STYLE}">{format_inline(quote.group(1).strip(), base_dir, token)}</p>')
        elif image_only:
            close_list()
            close_quote()
            output.append(render_image(image_only.group(1), image_only.group(2), base_dir, token))
        else:
            paragraph.append(raw.strip())

    flush_paragraph()
    close_list()
    close_quote()
    return f'<section style="{ARTICLE_STYLE}">\n' + "\n".join(output) + "\n</section>"


def format_inline(text: str, base_dir: Path, token: str | None) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    return re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: render_image(m.group(1), html.unescape(m.group(2)), base_dir, token),
        escaped,
    )


def render_image(alt: str, target: str, base_dir: Path, token: str | None) -> str:
    if target.startswith(("http://", "https://")):
        src = target
    else:
        image_path = (base_dir / target).resolve()
        if not image_path.exists():
            text = target if target.startswith("配图") else f"{alt}：{target}"
            return f'<p style="{MISSING_IMAGE_STYLE}">{html.escape(text)}</p>'
        if token is None:
            src = target
        else:
            src = upload_inline_image(token, image_path)
    return (
        f'<section style="{IMG_WRAP_STYLE}">'
        f'<img src="{html.escape(src)}" alt="{html.escape(alt)}" style="{IMG_STYLE}" />'
        "</section>"
    )


def create_draft(
    token: str,
    *,
    title: str,
    author: str,
    digest: str,
    content: str,
    thumb_media_id: str,
    source_url: str,
) -> str:
    payload = {
        "articles": [
            {
                "title": truncate_utf8(normalize_wechat_title(title), 42),
                "author": truncate_utf8(author, 8),
                "digest": truncate_utf8(digest, 54),
                "content": content,
                "thumb_media_id": thumb_media_id,
                "content_source_url": source_url,
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
            }
        ]
    }
    data = api_json("POST", "draft/add", token=token, json=payload)
    media_id = data.get("media_id")
    if not media_id:
        raise WeChatError(f"创建草稿失败：{data}")
    return str(media_id)


def submit_publish(token: str, media_id: str) -> str:
    data = api_json("POST", "freepublish/submit", token=token, json={"media_id": media_id})
    publish_id = data.get("publish_id")
    if not publish_id:
        raise WeChatError(f"提交发布失败：{data}")
    return str(publish_id)


def get_publish_status(token: str, publish_id: str) -> dict[str, Any]:
    return api_json("POST", "freepublish/get", token=token, json={"publish_id": publish_id})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="把本地 Markdown 文章创建为微信公众号草稿")
    parser.add_argument("article", type=Path, help="Markdown 文章路径")
    parser.add_argument("--env", type=Path, default=Path(".env"), help="环境变量文件，默认 .env")
    parser.add_argument("--title", help="覆盖文章标题")
    parser.add_argument("--author", default=os.getenv("WECHAT_AUTHOR", ""))
    parser.add_argument("--cover", type=Path, help="封面图路径；默认取文章里的第一张本地图片")
    parser.add_argument("--digest", help="覆盖摘要")
    parser.add_argument("--source-url", default="", help="原文链接，可留空")
    parser.add_argument("--publish", action="store_true", help="创建草稿后提交发布")
    parser.add_argument("--status", help="查询 publish_id 的发布状态")
    return parser.parse_args()


def first_local_image(markdown: str, base_dir: Path) -> Path | None:
    for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", markdown):
        if not target.startswith(("http://", "https://")):
            candidate = (base_dir / target).resolve()
            if candidate.exists():
                return candidate
    return None


def main() -> int:
    args = parse_args()
    load_dotenv(args.env)

    app_id = os.getenv("WECHAT_APP_ID")
    app_secret = os.getenv("WECHAT_APP_SECRET")
    if not app_id or not app_secret:
        raise SystemExit("请先在 .env 设置 WECHAT_APP_ID 和 WECHAT_APP_SECRET")

    token = get_access_token(app_id, app_secret)
    if args.status:
        print(json.dumps(get_publish_status(token, args.status), ensure_ascii=False, indent=2))
        return 0

    article_path = args.article.resolve()
    markdown = article_path.read_text(encoding="utf-8")
    base_dir = article_path.parent
    cover = args.cover.resolve() if args.cover else first_local_image(markdown, base_dir)
    if not cover or not cover.exists():
        raise SystemExit("没有找到封面图。请用 --cover 指定一张 JPG/PNG 图片。")

    thumb_media_id = upload_material(token, cover, "image")
    title = args.title or extract_title(markdown, article_path.stem)
    digest = args.digest or extract_digest(markdown)
    author = args.author or os.getenv("WECHAT_AUTHOR", "")
    content = markdown_to_html(markdown, base_dir, token)
    media_id = create_draft(
        token,
        title=title,
        author=author,
        digest=digest,
        content=content,
        thumb_media_id=thumb_media_id,
        source_url=args.source_url,
    )
    print(json.dumps({"draft_media_id": media_id, "title": title}, ensure_ascii=False, indent=2))

    if args.publish:
        publish_id = submit_publish(token, media_id)
        print(json.dumps({"publish_id": publish_id}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except WeChatError as exc:
        raise SystemExit(str(exc)) from exc
