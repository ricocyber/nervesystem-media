from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class ExternalToolError(RuntimeError):
    pass


def require_binary(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise ExternalToolError(f"{name} was not found on PATH")
    return found


def _ffmpeg_listing(flag: str) -> str:
    require_binary("ffmpeg")
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", flag],
        capture_output=True,
        text=True,
        check=False,
    )
    return (proc.stdout or "") + "\n" + (proc.stderr or "")


def ffmpeg_capabilities() -> dict[str, bool]:
    filters = _ffmpeg_listing("-filters")
    encoders = _ffmpeg_listing("-encoders")
    return {
        "ass_filter": " ass " in filters or " ass             " in filters,
        "libx264": "libx264" in encoders,
        "aac": " aac " in encoders or "aac" in encoders,
    }


def require_ffmpeg_capabilities() -> None:
    caps = ffmpeg_capabilities()
    missing = [name for name, ok in caps.items() if not ok]
    if missing:
        raise ExternalToolError(
            "FFmpeg is installed but missing required capabilities: "
            + ", ".join(missing)
            + ". Install a full FFmpeg build with libass, libx264, and AAC."
        )


def ffprobe_video(path: str | Path) -> tuple[int, int, float]:
    require_binary("ffprobe")
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    values = [v.strip() for v in proc.stdout.splitlines() if v.strip()]
    if len(values) < 3:
        raise ExternalToolError(f"Could not probe video: {path}")
    return int(values[0]), int(values[1]), float(values[2])


def run_checked(cmd: list[str]) -> None:
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise ExternalToolError(f"Command failed with exit code {proc.returncode}: {' '.join(cmd)}")
