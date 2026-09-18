from __future__ import annotations

import json
from pathlib import Path

import typer

from .autonomous import run_virality_funnel
from .ollama_brain import OllamaViralityBrain

app = typer.Typer(no_args_is_help=True)


@app.command("doctor")
def doctor(
    model: str = typer.Option("qwen2.5:7b", "--model"),
    base_url: str = typer.Option("http://127.0.0.1:11434", "--base-url"),
) -> None:
    """Check the local Ollama virality model."""
    typer.echo(json.dumps(OllamaViralityBrain(model=model, base_url=base_url).verify(), indent=2))


@app.command("funnel")
def funnel(
    topic_space: str = typer.Option(..., "--topic"),
    audience: str = typer.Option(..., "--audience"),
    channel_promise: str = typer.Option(..., "--channel-promise"),
    output: Path = typer.Option(Path("virality_runs/latest"), "--output"),
    model: str = typer.Option("qwen2.5:7b", "--model"),
    count: int = typer.Option(100, "--count", min=10, max=500),
    shortlist: int = typer.Option(10, "--shortlist", min=1, max=50),
    package_top: int = typer.Option(3, "--package-top", min=1, max=10),
    research_packet: Path | None = typer.Option(None, "--research-packet"),
) -> None:
    """Run the full 100-to-1 idea/critic/packaging funnel locally."""
    payload = run_virality_funnel(
        topic_space=topic_space,
        audience=audience,
        channel_promise=channel_promise,
        output_dir=output,
        model=model,
        count=count,
        shortlist=shortlist,
        package_top=package_top,
        research_packet_path=research_packet,
    )
    typer.echo(
        json.dumps(
            {
                "idea_count": payload["idea_count"],
                "shortlist_ids": payload["shortlist_ids"],
                "package_count": len(payload["packages"]),
                "output": str(output / "virality_run.json"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    app()
