from __future__ import annotations

import json

import typer

from .ollama_router import OllamaModelRouter

app = typer.Typer(no_args_is_help=True)


@app.command("models")
def models(
    base_url: str = typer.Option("http://127.0.0.1:11434", "--base-url"),
) -> None:
    """List models actually installed in local Ollama."""
    router = OllamaModelRouter(base_url=base_url)
    typer.echo(json.dumps({"models": router.installed_models()}, indent=2))


@app.command("task")
def route_task(
    task_type: str = typer.Argument(...),
    base_url: str = typer.Option("http://127.0.0.1:11434", "--base-url"),
) -> None:
    """Choose the best installed local model for a task type."""
    decision = OllamaModelRouter(base_url=base_url).route(task_type)
    typer.echo(json.dumps(decision.__dict__, indent=2))


@app.command("agent")
def route_agent(
    agent_role: str = typer.Argument(...),
    base_url: str = typer.Option("http://127.0.0.1:11434", "--base-url"),
) -> None:
    """Choose the best installed local model for a studio agent role."""
    decision = OllamaModelRouter(base_url=base_url).route_agent(agent_role)
    typer.echo(json.dumps(decision.__dict__, indent=2))


if __name__ == "__main__":
    app()
