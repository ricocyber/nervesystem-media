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
