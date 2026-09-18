from __future__ import annotations

import json
from pathlib import Path

from .continuity import build_continuity_plan


def build_render_waves(project_dir: Path) -> list[list[str]]:
    manifest = json.loads(
        (project_dir / "generation_manifest.json").read_text(encoding="utf-8")
    )
    shot_ids = [shot["id"] for shot in manifest["shots"]]
    dependencies = build_continuity_plan(project_dir)

    prereqs: dict[str, set[str]] = {shot_id: set() for shot_id in shot_ids}
    for dep in dependencies:
        prereqs.setdefault(dep.dependent_shot_id, set()).add(dep.source_shot_id)

    remaining = set(shot_ids)
    completed: set[str] = set()
    waves: list[list[str]] = []

    while remaining:
        ready = sorted(
            shot for shot in remaining
            if prereqs.get(shot, set()).issubset(completed)
        )
        if not ready:
            raise RuntimeError("Cycle detected in shot continuity dependencies")
        waves.append(ready)
        completed.update(ready)
        remaining.difference_update(ready)

    return waves
