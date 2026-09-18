from __future__ import annotations

import json
from pathlib import Path

import typer

from .models import ProductionBrief
from .orchestrator import StudioOrchestrator

app = typer.Typer(no_args_is_help=True)


@app.command()
def plan(
    title: str = typer.Option(..., "--title"),
    topic: str = typer.Option(..., "--topic"),
    objective: str = typer.Option(..., "--objective"),
    format: str = typer.Option("commercial", "--format"),
    audience: str = typer.Option("general", "--audience"),
    duration: int = typer.Option(30, "--duration"),
    realism: str = typer.Option("hybrid", "--realism"),
    language: str = typer.Option("en", "--language"),
    output: Path = typer.Option(Path("production_plan.json"), "--output"),
) -> None:
    brief = ProductionBrief(
        title=title,
        objective=objective,
        format=format,  # type: ignore[arg-type]
        target_audience=audience,
        duration_seconds=duration,
        topic=topic,
        realism=realism,  # type: ignore[arg-type]
        language=language,
    )
    plan = StudioOrchestrator().plan(brief)
    output.write_text(json.dumps(plan.to_dict(), indent=2), encoding="utf-8")
    typer.echo(f"Wrote {output} with {len(plan.work_orders)} work orders.")


if __name__ == "__main__":
    app()
