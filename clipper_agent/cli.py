from __future__ import annotations

import json
import platform
import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .benchmark import evaluate
from .highlights import ollama_available
from .pipeline import run_pipeline

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


@app.command()
def doctor() -> None:
    """Check the local machine before running the pipeline."""
    table = Table(title="Clipper Agent doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detail")

    for binary in ("ffmpeg", "ffprobe"):
        found = shutil.which(binary)
        table.add_row(binary, "OK" if found else "MISSING", found or "install a full ffmpeg build")

    table.add_row("Ollama", "OK" if ollama_available() else "OPTIONAL", "local ranking model" if ollama_available() else "heuristic fallback will be used")
    table.add_row("OS", "INFO", f"{platform.system()} {platform.machine()}")
    table.add_row("Python", "INFO", platform.python_version())
    console.print(table)


@app.command()
def clip(
    source: str = typer.Argument(..., help="Local video path or authorized URL"),
    output: Path = typer.Option(Path("output"), "--output", "-o"),
    whisper_model: str = typer.Option("small", "--whisper-model"),
    language: str | None = typer.Option(None, "--language"),
    top: int = typer.Option(5, "--top", min=1, max=20),
    min_score: float = typer.Option(6.0, "--min-score", min=0, max=10),
    ollama_model: str = typer.Option("qwen2.5:7b", "--ollama-model"),
    no_ollama: bool = typer.Option(False, "--no-ollama"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Score/select only; do not render MP4s"),
    confirm_rights: bool = typer.Option(False, "--confirm-rights", help="Required for URL ingest"),
) -> None:
    """Turn one long video into ranked vertical clips."""
    manifest = run_pipeline(
        source=source,
        output_root=output,
        whisper_model=whisper_model,
        language=language,
        top_k=top,
        min_score=min_score,
        ollama_model=ollama_model,
        use_ollama=not no_ollama,
        render=not dry_run,
        confirm_rights=confirm_rights,
    )
    console.print(f"[bold green]Done.[/bold green] Selected {len(manifest.candidates)} clip(s).")
    for clip_item in manifest.candidates:
        console.print(
            f"#{clip_item.candidate_id} {clip_item.start:.1f}s-{clip_item.end:.1f}s "
            f"score={clip_item.score:.1f} {clip_item.title}"
        )


@app.command()
def benchmark(
    review: Path = typer.Argument(..., exists=True),
    gold: Path = typer.Argument(..., exists=True),
    iou: float = typer.Option(0.25, "--iou", min=0.01, max=1.0),
) -> None:
    """Compare selected clips against a human-made gold set."""
    result = evaluate(review, gold, iou_threshold=iou)
    console.print_json(json.dumps(result.model_dump()))


if __name__ == "__main__":
    app()
