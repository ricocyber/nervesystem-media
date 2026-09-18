from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from virality.project_gate import evaluate_project_gate

from .adapters.ltx import LTXAdapter
from .adapters.motion import render_motion_shot
from .assembly import assemble_master
from .audio import mux_narration
from .continuity import prepare_continuity_assets
from .narration import render_narration
from .qc import qc_master, write_qc_report
from .queue import build_shot_queue
from .scheduler import build_render_waves


class AutonomousProductionError(RuntimeError):
    pass


MOTION_SHOTS = {"S02", "S04", "S05", "S06", "S07", "S09"}


def _task_map(project_dir: Path) -> dict[str, dict]:
    queue_path = project_dir / "work" / "shot_queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    return {task["shot_id"]: task for task in queue["tasks"]}


def run_autonomous_project(
    project_dir: Path,
    *,
    ltx_repo: Path | None = None,
    voice_profile_id: str | None = None,
    voicebox_url: str = "http://127.0.0.1:17493",
    seed: int = 42,
) -> dict:
    """
    Execute every locally supported production stage.

    Unsupported/missing departments are reported as blocked rather than
    silently simulated.
    """
    gate = evaluate_project_gate(project_dir)
    if not gate.passed:
        raise AutonomousProductionError(
            f"Production gate failed: {gate.failures}"
        )

    work_dir = project_dir / "work"
    work_dir.mkdir(parents=True, exist_ok=True)
    build_shot_queue(project_dir, work_dir)
    tasks = _task_map(project_dir)
    waves = build_render_waves(project_dir)

    ltx = LTXAdapter(ltx_repo)
    ltx_status = ltx.verify()

    state = {
        "project": project_dir.name,
        "gate": asdict(gate),
        "ltx": ltx_status,
        "waves": waves,
        "shots": {},
        "narration": "not_requested",
        "assembly": "pending",
        "qc": "pending",
    }

    if voice_profile_id:
        try:
            narration = render_narration(
                project_dir,
                profile_id=voice_profile_id,
                base_url=voicebox_url,
            )
            state["narration"] = str(narration)
        except Exception as exc:
            state["narration"] = f"blocked:{type(exc).__name__}:{exc}"

    continuity_conditioning: dict[str, list[dict]] = {}

    for wave_index, wave in enumerate(waves):
        for shot_id in wave:
            task = tasks[shot_id]
            output = Path(task["output_video"])

            try:
                if shot_id in MOTION_SHOTS:
                    render_motion_shot(
                        shot_id,
                        float(task["duration_seconds"]),
                        output,
                    )
                    state["shots"][shot_id] = {
                        "status": "complete",
                        "adapter": "motion-graphics",
                        "output": str(output),
                    }
                    continue

                if "ltx-video" not in task["preferred_adapters"]:
                    state["shots"][shot_id] = {
                        "status": "blocked",
                        "reason": "no built-in compatible adapter",
                    }
                    continue

                if not ltx_status.get("ready"):
                    state["shots"][shot_id] = {
                        "status": "blocked",
                        "reason": ltx_status.get("reason", "LTX not ready"),
                    }
                    continue

                conditioning = None
                entries = continuity_conditioning.get(shot_id, [])
                if entries:
                    conditioning = Path(entries[0]["conditioning_media"])

                result = ltx.generate(
                    prompt=task["prompt"],
                    output_path=output,
                    duration_seconds=float(task["duration_seconds"]),
                    seed=seed + int(shot_id[1:]),
                    conditioning_media_path=conditioning,
                )
                state["shots"][shot_id] = {
                    "status": "complete",
                    "adapter": "ltx-video",
                    "output": result.output_path,
                    "conditioning": str(conditioning) if conditioning else None,
                }
            except Exception as exc:
                state["shots"][shot_id] = {
                    "status": "blocked",
                    "reason": f"{type(exc).__name__}:{exc}",
                }

        # Once establishing shots have rendered, create identity/scene reference
        # frames for the next dependency wave.
        if wave_index < len(waves) - 1:
            try:
                continuity = prepare_continuity_assets(project_dir, work_dir)
                continuity_conditioning = continuity["conditioning"]
            except Exception as exc:
                state["continuity"] = f"blocked:{type(exc).__name__}:{exc}"

    incomplete = [
        shot_id for shot_id, value in state["shots"].items()
        if value.get("status") != "complete"
    ]

    if incomplete:
        state["assembly"] = {
            "status": "blocked",
            "missing_or_blocked_shots": incomplete,
        }
    else:
        try:
            picture = assemble_master(project_dir, work_dir)
            state["assembly"] = {
                "status": "picture_complete",
                "picture": str(picture),
            }

            narration_path = project_dir / "work" / "audio" / "narration.wav"
            final_master = project_dir / "work" / "master.mp4"
            if narration_path.exists():
                mux_narration(picture, narration_path, final_master)
            else:
                final_master = picture

            report = qc_master(final_master, expected_duration=30.0)
            report_path = project_dir / "work" / "qc_report.json"
            write_qc_report(report, report_path)
            state["qc"] = {
                "passed": report.passed,
                "report": str(report_path),
                "master": str(final_master),
            }
        except Exception as exc:
            state["assembly"] = f"blocked:{type(exc).__name__}:{exc}"

    state_path = work_dir / "autonomous_state.json"
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state
