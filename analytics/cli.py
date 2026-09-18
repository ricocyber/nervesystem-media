from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import typer

from .feedback import compare_to_cohort
from .metrics import PerformanceRecord, derive

app = typer.Typer(no_args_is_help=True)


def _record(path: Path) -> PerformanceRecord:
    return PerformanceRecord(**json.loads(path.read_text(encoding="utf-8")))


@app.command("derive")
def derive_cmd(
    record: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
) -> None:
    """Compute derived response/conversion/economic metrics from one publication record."""
    payload = asdict(derive(_record(record)))
    typer.echo(json.dumps(payload, indent=2))


@app.command("compare")
def compare_cmd(
    target: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
    cohort: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
) -> None:
    """Compare one publication to a declared comparable cohort."""
    target_record = _record(target)
    raw = json.loads(cohort.read_text(encoding="utf-8"))
    cohort_records = [PerformanceRecord(**item) for item in raw]
    typer.echo(json.dumps(compare_to_cohort(target_record, cohort_records), indent=2))


if __name__ == "__main__":
    app()
