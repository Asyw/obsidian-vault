#!/usr/bin/env python3
"""Create a simple local talking-video mockup from a portrait and narration."""

from __future__ import annotations

import argparse
import math
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FONT = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")
FALLBACK_FONT = Path("/System/Library/Fonts/STHeiti Medium.ttc")


def audio_duration(path: Path) -> float:
    output = subprocess.check_output(["afinfo", str(path)], text=True, stderr=subprocess.STDOUT)
    for line in output.splitlines():
        if "estimated duration:" in line:
            value = line.split("estimated duration:", 1)[1].split("sec", 1)[0].strip()
            return float(value)
    raise SystemExit(f"Could not determine audio duration: {path}")


def load_font(size: int) -> ImageFont.FreeTypeFont:
    font_path = DEFAULT_FONT if DEFAULT_FONT.exists() else FALLBACK_FONT
    return ImageFont.truetype(str(font_path), size=size)


def cover_resize(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize((math.ceil(image.width * scale), math.ceil(image.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def contain_resize(image: Image.Image, max_size: tuple[int, int]) -> Image.Image:
    max_w, max_h = max_size
    scale = min(max_w / image.width, max_h / image.height)
    return image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)


def rounded_rect_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    center_x: int,
    y: int,
    fill: tuple[int, int, int],
    stroke_fill: tuple[int, int, int],
    stroke_width: int = 4,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    x = center_x - (bbox[2] - bbox[0]) // 2
    draw.text((x, y), text, font=font, fill=fill, stroke_fill=stroke_fill, stroke_width=stroke_width)


def make_frame(
    portrait: Image.Image,
    subtitle: str,
    title: str,
    frame_index: int,
    total_frames: int,
    size: tuple[int, int],
) -> Image.Image:
    width, height = size
    progress = frame_index / max(1, total_frames - 1)

    bg = cover_resize(portrait, size).filter(ImageFilter.GaussianBlur(28))
    overlay = Image.new("RGB", size, (16, 33, 46))
    bg = Image.blend(bg, overlay, 0.38)

    # Soft bottom band for subtitles.
    shade = Image.new("RGBA", size, (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    shade_draw.rectangle((0, height - 430, width, height), fill=(0, 0, 0, 92))
    bg = Image.alpha_composite(bg.convert("RGBA"), shade)

    zoom = 1.0 + 0.035 * progress
    max_portrait_w = int(width * 0.88 * zoom)
    max_portrait_h = int(height * 0.72 * zoom)
    fg = contain_resize(portrait, (max_portrait_w, max_portrait_h))
    mask = rounded_rect_mask(fg.size, 34)

    x = (width - fg.width) // 2
    y = 210 - round(22 * progress)
    shadow = Image.new("RGBA", fg.size, (0, 0, 0, 105))
    shadow_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    shadow_layer.paste(shadow.filter(ImageFilter.GaussianBlur(18)), (x, y + 18), mask)
    bg = Image.alpha_composite(bg, shadow_layer)
    bg.paste(fg.convert("RGBA"), (x, y), mask)

    draw = ImageDraw.Draw(bg)
    title_font = load_font(52)
    subtitle_font = load_font(58)
    small_font = load_font(30)

    draw_centered_text(draw, title, title_font, width // 2, 88, (255, 255, 255), (17, 35, 55), 3)
    draw_centered_text(draw, subtitle, subtitle_font, width // 2, height - 320, (255, 255, 255), (0, 0, 0), 5)
    draw_centered_text(draw, "少年有志  国家有光", small_font, width // 2, height - 220, (220, 240, 255), (0, 0, 0), 3)
    return bg.convert("RGB")


def render_video(
    portrait_path: Path,
    audio_path: Path,
    output_path: Path,
    subtitle: str,
    title: str,
    fps: int,
    size: tuple[int, int],
) -> None:
    duration = audio_duration(audio_path)
    total_frames = max(1, math.ceil(duration * fps))
    portrait = Image.open(portrait_path).convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    width, height = size
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-s",
        f"{width}x{height}",
        "-pix_fmt",
        "rgb24",
        "-r",
        str(fps),
        "-i",
        "-",
        "-i",
        str(audio_path),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-shortest",
        str(output_path),
    ]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert process.stdin is not None
    try:
        for index in range(total_frames):
            frame = make_frame(portrait, subtitle, title, index, total_frames, size)
            process.stdin.write(np.asarray(frame, dtype=np.uint8).tobytes())
    finally:
        process.stdin.close()
    code = process.wait()
    if code != 0:
        raise SystemExit(f"ffmpeg failed with exit code {code}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--portrait", required=True)
    parser.add_argument("--audio", default=str(ROOT / "outputs/audio/少年强则中国强_复刻声音.mp3"))
    parser.add_argument("--output", default=str(ROOT / "outputs/videos/少年强则中国强_照片口播_9x16.mp4"))
    parser.add_argument("--subtitle", default="少年强，则中国强")
    parser.add_argument("--title", default="少年强则中国强")
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1920)
    args = parser.parse_args()

    render_video(
        Path(args.portrait),
        Path(args.audio),
        Path(args.output),
        args.subtitle,
        args.title,
        args.fps,
        (args.width, args.height),
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
