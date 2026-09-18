from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .runtime import check_runtime


class ExecutionBlocked(RuntimeError):
    pass


@dataclass
class ExecutionResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def _ready(name: str) -> bool:
    return any(item.name == name and item.status == "ready" for item in check_runtime())


def run_command(command: list[str], cwd: Path | None = None) -> ExecutionResult:
    proc = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    return ExecutionResult(
        command=command,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def render_blender_scene(scene: Path, output_dir: Path, frame_start: int, frame_end: int) -> ExecutionResult:
    if not _ready("blender"):
        raise ExecutionBlocked("Blender is not ready on this workstation.")
    output_dir.mkdir(parents=True, exist_ok=True)
    return run_command([
        "blender",
        "--background",
        str(scene),
        "--render-output",
        str(output_dir / "frame_#####"),
        "--render-frame",
        f"{frame_start}..{frame_end}",
    ])


def execute_project(project_dir: Path) -> dict:
    """
    V1 execution gate.

    This intentionally does NOT fabricate completed media. It validates project
    artifacts and returns explicit runnable/blocked stages based on the local
    workstation.
    """
    required = [
        "brief.json",
        "script.md",
        "shot_list.json",
        "character_bible.json",
        "sound_plan.json",
    ]
    missing = [name for name in required if not (project_dir / name).exists()]
    if missing:
        raise ExecutionBlocked("Missing production artifacts: " + ", ".join(missing))

    runtime = {item.name: item.status for item in check_runtime()}
    stages = {
        "edit_render": "ready" if runtime.get("ffmpeg") == "ready" else "blocked",
        "3d_render": "ready" if runtime.get("blender") == "ready" else "blocked",
        "local_llm": "ready" if runtime.get("ollama") == "ready" else "blocked",
        "ai_video": "verify-entrypoint" if runtime.get("ltx-video") == "present-unverified" else "blocked",
        "digital_human": "verify-entrypoint" if runtime.get("digital-human") == "present-unverified" else "blocked",
        "voice": "verify-entrypoint" if runtime.get("voicebox") == "present-unverified" else "blocked",
    }
    return {"project": str(project_dir), "stages": stages, "runtime": runtime}
