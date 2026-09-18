from __future__ import annotations

import json
import subprocess
from pathlib import Path


class AssemblyError(RuntimeError):
    pass


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise AssemblyError(proc.stderr.strip() or "FFmpeg command failed")
    return proc


def normalize_shot(
    source: Path,
    output: Path,
    duration_seconds: float,
    width: int = 1920,
    height: int = 1080,
    fps: int = 24,
) -> Path:
    if not source.exists():
        raise AssemblyError(f"Missing shot: {source}")

    output.parent.mkdir(parents=True, exist_ok=True)
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
        f"setsar=1,fps={fps},"
        "tpad=stop_mode=clone:stop_duration=3"
    )
    _run([
        "ffmpeg", "-y",
        "-i", str(source),
        "-vf", vf,
        "-t", f"{duration_seconds:.3f}",
        "-an",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output),
    ])
    return output


def assemble_master(
    project_dir: Path,
    work_dir: Path | None = None,
    output: Path | None = None,
) -> Path:
    """
    Normalize every generated shot to the editorial contract, then concatenate
    in shot-list order.
    """
    work_dir = work_dir or (project_dir / "work")
    output = output or (work_dir / "master_picture.mp4")
    shots_dir = work_dir / "shots"
    normalized_dir = work_dir / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    shot_list = json.loads(
        (project_dir / "shot_list.json").read_text(encoding="utf-8")
    )["shots"]

    normalized: list[Path] = []
    for shot in shot_list:
        source = shots_dir / f"{shot['id']}.mp4"
        if not source.exists():
            raise AssemblyError(f"Missing shot render: {source}")
        target = normalized_dir / f"{shot['id']}.mp4"
        normalize_shot(
            source,
            target,
            duration_seconds=float(shot["end"]) - float(shot["start"]),
        )
        normalized.append(target)

    concat_file = work_dir / "picture_concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in normalized) + "\n",
        encoding="utf-8",
    )

    _run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-an",
        "-movflags", "+faststart",
        str(output),
    ])
    return output
