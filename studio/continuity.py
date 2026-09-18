from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


class ContinuityError(RuntimeError):
    pass


@dataclass(frozen=True)
class ContinuityDependency:
    continuity_id: str
    source_shot_id: str
    dependent_shot_id: str


def build_continuity_plan(project_dir: Path) -> list[ContinuityDependency]:
    manifest = json.loads(
        (project_dir / "generation_manifest.json").read_text(encoding="utf-8")
    )
    first_seen: dict[str, str] = {}
    dependencies: list[ContinuityDependency] = []

    for shot in manifest["shots"]:
        shot_id = shot["id"]
        for continuity_id in shot.get("continuity_ids", []):
            source = first_seen.get(continuity_id)
            if source is None:
                first_seen[continuity_id] = shot_id
                continue
            if source != shot_id:
                dependencies.append(
                    ContinuityDependency(
                        continuity_id=continuity_id,
                        source_shot_id=source,
                        dependent_shot_id=shot_id,
                    )
                )
    return dependencies


def extract_reference_frame(
    source_video: Path,
    output_image: Path,
    at_seconds: float | None = None,
) -> Path:
    if not source_video.exists():
        raise ContinuityError(f"Source shot does not exist: {source_video}")

    output_image.parent.mkdir(parents=True, exist_ok=True)

    if at_seconds is None:
        probe = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(source_video),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if probe.returncode != 0:
            raise ContinuityError(probe.stderr.strip())
        duration = float(probe.stdout.strip())
        at_seconds = max(0.0, duration * 0.55)

    proc = subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", f"{at_seconds:.3f}",
            "-i", str(source_video),
            "-frames:v", "1",
            "-q:v", "2",
            str(output_image),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise ContinuityError(proc.stderr.strip())
    if not output_image.exists() or output_image.stat().st_size == 0:
        raise ContinuityError("Reference frame was not produced")
    return output_image


def prepare_continuity_assets(
    project_dir: Path,
    work_dir: Path | None = None,
) -> dict:
    work_dir = work_dir or (project_dir / "work")
    shots_dir = work_dir / "shots"
    conditioning_dir = work_dir / "conditioning"
    conditioning_dir.mkdir(parents=True, exist_ok=True)

    dependencies = build_continuity_plan(project_dir)
    output: dict[str, list[dict]] = {}

    # Multiple continuity IDs can point back to the same source shot. Reuse one
    # extracted frame for that source/dependent pair rather than duplicating work.
    cached: dict[tuple[str, str], Path] = {}

    for dep in dependencies:
        key = (dep.source_shot_id, dep.dependent_shot_id)
        if key not in cached:
            source_video = shots_dir / f"{dep.source_shot_id}.mp4"
            ref = conditioning_dir / (
                f"{dep.dependent_shot_id}_from_{dep.source_shot_id}.jpg"
            )
            cached[key] = extract_reference_frame(source_video, ref)

        output.setdefault(dep.dependent_shot_id, []).append(
            {
                "continuity_id": dep.continuity_id,
                "source_shot_id": dep.source_shot_id,
                "conditioning_media": str(cached[key].resolve()),
            }
        )

    plan_path = work_dir / "continuity_plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "dependencies": [asdict(x) for x in dependencies],
                "conditioning": output,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return {"dependencies": [asdict(x) for x in dependencies], "conditioning": output}
