from __future__ import annotations

import json
from pathlib import Path


def build_shot_queue(project_dir: Path, output_dir: Path | None = None) -> dict:
    output_dir = output_dir or (project_dir / "work")
    output_dir.mkdir(parents=True, exist_ok=True)
    shots_dir = output_dir / "shots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    generation = json.loads((project_dir / "generation_manifest.json").read_text(encoding="utf-8"))
    global_bible = generation["global_visual_bible"]

    tasks = []
    for shot in generation["shots"]:
        shot_id = shot["id"]
        task = {
            "shot_id": shot_id,
            "status": "queued",
            "preferred_adapters": shot["preferred_adapter"],
            "duration_seconds": shot["duration_seconds"],
            "prompt": shot["prompt"],
            "continuity_ids": shot.get("continuity_ids", []),
            "overlay_text": shot.get("overlay_text"),
            "global_visual_bible": global_bible,
            "output_video": str((shots_dir / f"{shot_id}.mp4").resolve()),
            "output_metadata": str((shots_dir / f"{shot_id}.json").resolve()),
        }
        task_path = shots_dir / f"{shot_id}.task.json"
        task_path.write_text(json.dumps(task, indent=2), encoding="utf-8")
        tasks.append(task)

    queue = {
        "project": project_dir.name,
        "shot_count": len(tasks),
        "status": "queued",
        "tasks": tasks,
    }
    (output_dir / "shot_queue.json").write_text(json.dumps(queue, indent=2), encoding="utf-8")
    return queue
