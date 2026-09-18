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


def assemble_master(
    project_dir: Path,
    work_dir: Path | None = None,
    output: Path | None = None,
) -> Path:
    """
    Concatenate approved shot renders in shot-list order.

    Audio mastering is a separate pass because narration/SFX may be generated
    independently. This function proves the visual editorial path.
    """
    work_dir = work_dir or (project_dir / "work")
    output = output or (work_dir / "master_picture.mp4")
    shots_dir = work_dir / "shots"

    shot_list = json.loads((project_dir / "shot_list.json").read_text(encoding="utf-8"))["shots"]
    expected = [shots_dir / f"{shot['id']}.mp4" for shot in shot_list]
    missing = [str(p) for p in expected if not p.exists()]
    if missing:
        raise AssemblyError("Missing shot renders: " + ", ".join(missing))

    concat_file = work_dir / "picture_concat.txt"
    concat_file.parent.mkdir(parents=True, exist_ok=True)
    concat_file.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in expected) + "\n",
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
