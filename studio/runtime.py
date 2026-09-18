from __future__ import annotations

import json
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeCheck:
    name: str
    status: str
    detail: str
    path: str | None = None


def _repo_candidate(name: str) -> Path:
    return Path.home() / name


def check_runtime() -> list[RuntimeCheck]:
    checks: list[RuntimeCheck] = []

    for binary in ("ffmpeg", "ffprobe", "blender", "ollama"):
        path = shutil.which(binary)
        checks.append(
            RuntimeCheck(
                name=binary,
                status="ready" if path else "missing",
                detail="binary found on PATH" if path else "binary not found on PATH",
                path=path,
            )
        )

    for repo_name in ("ltx-video", "digital-human", "voicebox", "video-creator"):
        path = _repo_candidate(repo_name)
        checks.append(
            RuntimeCheck(
                name=repo_name,
                status="present-unverified" if path.exists() else "missing",
                detail=(
                    "repository exists; entrypoint/license/runtime still require verification"
                    if path.exists()
                    else "repository not found at expected home-directory path"
                ),
                path=str(path) if path.exists() else None,
            )
        )

    return checks


def save_runtime_report(path: Path) -> Path:
    payload = {"checks": [asdict(item) for item in check_runtime()]}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
