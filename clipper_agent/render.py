from __future__ import annotations

from pathlib import Path

from .models import Candidate, CropRect
from .system import require_binary, require_ffmpeg_capabilities, run_checked


def _escape_filter_path(path: Path) -> str:
    value = str(path.resolve())
    value = value.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    return value


def render_clip(
    source: str | Path,
    candidate: Candidate,
    crop: CropRect,
    caption_path: Path,
    output_path: Path,
    crf: int = 20,
) -> Path:
    require_binary("ffmpeg")
    require_ffmpeg_capabilities()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    duration = max(0.1, candidate.end - candidate.start)

    vf = (
        f"crop={crop.width}:{crop.height}:{crop.x}:{crop.y},"
        "scale=1080:1920:flags=lanczos,"
        f"ass='{_escape_filter_path(caption_path)}'"
    )
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{candidate.start:.3f}",
        "-i", str(source),
        "-t", f"{duration:.3f}",
        "-vf", vf,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_path),
    ]
    run_checked(cmd)
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError(f"Render did not produce a usable file: {output_path}")
    return output_path
