#!/usr/bin/env python3
"""Replace video audio and burn simple Chinese ASS subtitles."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import imageio_ffmpeg


def ass_time(seconds: float) -> str:
    centiseconds = round(seconds * 100)
    cs = centiseconds % 100
    total_seconds = centiseconds // 100
    s = total_seconds % 60
    total_minutes = total_seconds // 60
    m = total_minutes % 60
    h = total_minutes // 60
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def write_ass(path: Path, lines: list[str], duration: float, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line_duration = duration / max(1, len(lines))
    events = []
    for index, line in enumerate(lines):
        start = index * line_duration
        end = duration if index == len(lines) - 1 else (index + 1) * line_duration
        events.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{line}")

    content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Hiragino Sans GB,58,&H00FFFFFF,&H000000FF,&H7A000000,&H8A000000,-1,0,0,0,100,100,0,0,1,5,1,2,60,60,155,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{chr(10).join(events)}
"""
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--audio", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--duration", type=float, default=5.05)
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=1280)
    parser.add_argument("--subtitle", action="append", required=True)
    parser.add_argument("--loop-video", action="store_true")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    ass_path = output.with_suffix(".ass")
    write_ass(ass_path, args.subtitle, args.duration, args.width, args.height)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg,
        "-y",
    ]
    if args.loop_video:
        cmd.extend(["-stream_loop", "-1"])
    cmd.extend(
        [
        "-i",
        args.video,
        "-i",
        args.audio,
        "-vf",
        f"ass={ass_path.as_posix()}",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
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
        "-t",
        str(args.duration),
        str(output),
        ]
    )
    subprocess.run(cmd, check=True)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
