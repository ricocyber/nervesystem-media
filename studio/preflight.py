from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from virality.project_gate import evaluate_project_gate

from .discovery import inspect_media_repos
from .runtime import check_runtime
from .scheduler import build_render_waves


def build_preflight_report(project_dir: Path) -> dict:
    gate = evaluate_project_gate(project_dir)
    runtime = check_runtime()
    repos = inspect_media_repos()

    report = {
        "project": str(project_dir),
        "production_gate": asdict(gate),
        "runtime": [asdict(x) for x in runtime],
        "media_repos": [asdict(x) for x in repos],
        "render_waves": build_render_waves(project_dir),
    }

    blockers: list[str] = []
    if not gate.passed:
        blockers.append("virality_or_packaging_gate")

    runtime_map = {x.name: x.status for x in runtime}
    if runtime_map.get("ffmpeg") != "ready":
        blockers.append("ffmpeg_missing")
    if runtime_map.get("ltx-video") == "missing":
        blockers.append("ltx_video_repo_missing")
    if runtime_map.get("voicebox") == "missing":
        blockers.append("voicebox_repo_missing")

    report["blockers"] = blockers
    report["ready_for_local_execution"] = not blockers
    return report


def save_preflight_report(project_dir: Path, output: Path) -> Path:
    report = build_preflight_report(project_dir)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return output
