from __future__ import annotations

import json
from pathlib import Path

import typer

from .discovery import write_discovery_report
from .executor import execute_project
from .models import ProductionBrief
from .orchestrator import StudioOrchestrator
from .queue import build_shot_queue
from .runtime import check_runtime, save_runtime_report
from .shot_runner import run_shot_task
from .adapters.ltx import LTXAdapter
from .adapters.voicebox import VoiceboxAdapter
from .narration import render_narration
from .continuity import prepare_continuity_assets
from .scheduler import build_render_waves
from virality.project_gate import evaluate_project_gate
from .preflight import build_preflight_report
from .autonomous import run_autonomous_project
from .adapters.musetalk_mac import MuseTalkMacAdapter
from .digital_human import render_talking_human
from .podcast import build_camera_timeline, render_host_video

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


@app.command("inspect-media")
def inspect_media(
    output: Path = typer.Option(Path("media_repo_report.json"), "--output"),
) -> None:
    """Inspect local media repos for license/config/entrypoint candidates."""
    write_discovery_report(output)
    typer.echo(f"Wrote media repo discovery report to {output}")


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


@app.command("prep-project")
def prep_project(
    project: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    output_dir: Path | None = typer.Option(None, "--output-dir"),
) -> None:
    """Create one queued work order per cinematic shot."""
    queue = build_shot_queue(project, output_dir)
    typer.echo(f"Queued {queue['shot_count']} shots for {queue['project']}.")


@app.command("run-shot")
def run_shot(
    task: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
    config: Path = typer.Option(Path("studio.local.json"), "--config"),
) -> None:
    """Execute exactly one queued shot with the first enabled compatible local adapter."""
    if not config.exists():
        raise typer.BadParameter(
            "Local adapter config not found. Copy studio.local.example.json to studio.local.json "
            "and fill only verified entrypoints."
        )
    result = run_shot_task(task, config)
    typer.echo(
        f"{result.shot_id} rendered with {result.adapter} -> {result.output_video}"
    )


@app.command("run-project")
def run_project(
    project: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    ltx_repo: Path = typer.Option(Path.home() / "ltx-video", "--ltx-repo"),
    voice_profile_id: str | None = typer.Option(None, "--voice-profile-id"),
    voicebox_url: str = typer.Option("http://127.0.0.1:17493", "--voicebox-url"),
    seed: int = typer.Option(42, "--seed"),
) -> None:
    """Run every locally supported production department for one project."""
    state = run_autonomous_project(
        project_dir=project,
        ltx_repo=ltx_repo,
        voice_profile_id=voice_profile_id,
        voicebox_url=voicebox_url,
        seed=seed,
    )
    typer.echo(json.dumps(state, indent=2))


@app.command("preflight")
def preflight(
    project: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    output: Path | None = typer.Option(None, "--output"),
) -> None:
    """Run the full production preflight: idea gate, machine, repos, and render schedule."""
    report = build_preflight_report(project)
    payload = json.dumps(report, indent=2)
    typer.echo(payload)
    if output:
        output.write_text(payload, encoding="utf-8")
    if not report["ready_for_local_execution"]:
        raise typer.Exit(code=2)


@app.command("gate-project")
def gate_project(
    project: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Run the Virality Director + packaging gate before production."""
    result = evaluate_project_gate(project)
    typer.echo(json.dumps(result.__dict__, indent=2))
    if not result.passed:
        raise typer.Exit(code=2)


@app.command("render-schedule")
def render_schedule(
    project: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Show dependency-safe render waves for the project."""
    typer.echo(json.dumps({"waves": build_render_waves(project)}, indent=2))


@app.command("prepare-continuity")
def prepare_continuity(
    project: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Extract reference frames from establishing shots for later identity/scene continuity."""
    result = prepare_continuity_assets(project)
    typer.echo(json.dumps(result, indent=2))


@app.command("verify-ltx")
def verify_ltx(
    repo: Path = typer.Option(Path.home() / "ltx-video", "--repo"),
) -> None:
    """Verify the local LTX-Video clone and its inference CLI."""
    typer.echo(json.dumps(LTXAdapter(repo).verify(), indent=2))


@app.command("render-ltx-shot")
def render_ltx_shot(
    task: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
    repo: Path = typer.Option(Path.home() / "ltx-video", "--repo"),
    conditioning: Path | None = typer.Option(None, "--conditioning"),
    seed: int = typer.Option(42, "--seed"),
) -> None:
    """Render one queued shot through the verified local LTX-Video adapter."""
    payload = json.loads(task.read_text(encoding="utf-8"))
    adapter = LTXAdapter(repo)
    result = adapter.generate(
        prompt=payload["prompt"],
        output_path=Path(payload["output_video"]),
        duration_seconds=float(payload["duration_seconds"]),
        seed=seed,
        conditioning_media_path=conditioning,
    )
    typer.echo(json.dumps(result.__dict__, indent=2))


@app.command("podcast-camera-plan")
def podcast_camera_plan(
    project: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
) -> None:
    """Build the speaker-aware camera timeline for a podcast project."""
    typer.echo(json.dumps(build_camera_timeline(project), indent=2))


@app.command("render-podcast-host")
def render_podcast_host(
    project: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    character_id: str = typer.Option(..., "--character-id"),
    reference_video: Path = typer.Option(..., "--reference-video", exists=True),
    profile_id: str = typer.Option(..., "--profile-id"),
    voicebox_url: str = typer.Option("http://127.0.0.1:17493", "--voicebox-url"),
    musetalk_url: str = typer.Option("http://127.0.0.1:8000", "--musetalk-url"),
) -> None:
    """Render one full time-aligned podcast host track."""
    result = render_host_video(
        project_dir=project,
        character_id=character_id,
        reference_video=reference_video,
        profile_id=profile_id,
        voicebox_url=voicebox_url,
        musetalk_url=musetalk_url,
    )
    typer.echo(json.dumps(result.__dict__, indent=2))


@app.command("verify-musetalk")
def verify_musetalk(
    base_url: str = typer.Option("http://127.0.0.1:8000", "--base-url"),
) -> None:
    """Verify the local MuseTalk-Mac lip-sync service."""
    typer.echo(json.dumps(MuseTalkMacAdapter(base_url=base_url).verify(), indent=2))


@app.command("render-talking-human")
def render_talking_human_cmd(
    reference_video: Path = typer.Option(..., "--reference-video", exists=True),
    audio: Path = typer.Option(..., "--audio", exists=True),
    output: Path = typer.Option(..., "--output"),
    avatar_key: str = typer.Option(..., "--avatar-key"),
    base_url: str = typer.Option("http://127.0.0.1:8000", "--base-url"),
    no_warmup: bool = typer.Option(False, "--no-warmup"),
) -> None:
    """Lip-sync a local/authorized human source video to local speech audio."""
    result = render_talking_human(
        reference_video=reference_video,
        narration_audio=audio,
        output_video=output,
        avatar_key=avatar_key,
        musetalk_url=base_url,
        warmup=not no_warmup,
    )
    typer.echo(json.dumps(result.__dict__, indent=2))


@app.command("voicebox-profiles")
def voicebox_profiles(
    base_url: str = typer.Option("http://127.0.0.1:17493", "--base-url"),
) -> None:
    """List locally available Voicebox profiles."""
    adapter = VoiceboxAdapter(base_url=base_url)
    typer.echo(json.dumps(adapter.list_profiles(), indent=2))


@app.command("render-narration")
def render_narration_cmd(
    project: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    profile_id: str = typer.Option(..., "--profile-id"),
    base_url: str = typer.Option("http://127.0.0.1:17493", "--base-url"),
) -> None:
    """Generate scheduled narration lines and mix them into a 30-second stem."""
    output = render_narration(
        project_dir=project,
        profile_id=profile_id,
        base_url=base_url,
    )
    typer.echo(f"Rendered narration -> {output}")


if __name__ == "__main__":
    app()
