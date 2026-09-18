from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import CommandAdapterConfig, StudioLocalConfig


class ShotRunnerError(RuntimeError):
    pass


@dataclass
class ShotRunResult:
    shot_id: str
    adapter: str
    returncode: int
    output_video: str
    stdout: str
    stderr: str


def _format_argv(template: list[str], task: dict) -> list[str]:
    fields = {
        "shot_id": task["shot_id"],
        "prompt": task["prompt"],
        "duration": str(task["duration_seconds"]),
        "output": task["output_video"],
        "metadata": task["output_metadata"],
    }
    return [part.format(**fields) for part in template]


def run_shot_task(task_path: Path, config_path: Path) -> ShotRunResult:
    task = json.loads(task_path.read_text(encoding="utf-8"))
    config = StudioLocalConfig.load(config_path)

    candidates = []
    for name in task["preferred_adapters"]:
        adapter = config.adapters.get(name)
        if adapter and adapter.enabled and adapter.argv:
            candidates.append(adapter)

    if not candidates:
        raise ShotRunnerError(
            f"No enabled adapter for {task['shot_id']}; preferred={task['preferred_adapters']}"
        )

    adapter = candidates[0]
    output = Path(task["output_video"])
    output.parent.mkdir(parents=True, exist_ok=True)

    argv = _format_argv(adapter.argv, task)
    proc = subprocess.run(
        argv,
        cwd=adapter.cwd,
        capture_output=True,
        text=True,
        check=False,
    )

    result = ShotRunResult(
        shot_id=task["shot_id"],
        adapter=adapter.name,
        returncode=proc.returncode,
        output_video=str(output),
        stdout=proc.stdout,
        stderr=proc.stderr,
    )

    metadata_path = Path(task["output_metadata"])
    metadata_path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

    if proc.returncode != 0:
        raise ShotRunnerError(
            f"{task['shot_id']} failed with {adapter.name}: {proc.stderr.strip()}"
        )
    if not output.exists() or output.stat().st_size == 0:
        raise ShotRunnerError(
            f"{task['shot_id']} adapter exited successfully but produced no video: {output}"
        )

    return result
