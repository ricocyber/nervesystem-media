from __future__ import annotations

import json
from pathlib import Path

import typer

from .executor import execute_project
from .models import ProductionBrief
from .orchestrator import StudioOrchestrator
from .runtime import check_runtime, save_runtime_report

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
    production_plan = StudioOrchestrator().plan(brief)
    output.write_text(json.dumps(production_plan.to_dict(), indent=2), encoding="utf-8")
    typer.echo(f"Wrote {output} with {len(production_plan.work_orders)} work orders.")


@app.command()
def doctor(
    output: Path | None = typer.Option(None, "--output"),
) -> None:
    """Audit the local production workstation without pretending missing tools exist."""
    checks = check_runtime()
    for item in checks:
        typer.echo(f"{item.name:16} {item.status:20} {item.path or ''}")
    if output:
        save_runtime_report(output)
        typer.echo(f"Wrote runtime report to {output}")


@app.command("check-project")
def check_project(
    project: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    output: Path | None = typer.Option(None, "--output"),
) -> None:
    """Validate a production project and report runnable vs blocked stages."""
    result = execute_project(project)
    payload = json.dumps(result, indent=2)
    typer.echo(payload)
    if output:
        output.write_text(payload, encoding="utf-8")
        typer.echo(f"Wrote project execution report to {output}")


if __name__ == "__main__":
    app()
