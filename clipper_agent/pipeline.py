from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from .captions import write_word_synced_ass
from .highlights import build_candidates, score_heuristic, score_with_ollama, select_top
from .ingest import ingest
from .models import RenderedClip, ReviewManifest
from .reframe import choose_crop
from .render import render_clip
from .review import write_review_html
from .transcribe import transcribe


def _slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return value[:80] or "video"


def run_pipeline(
    source: str,
    output_root: Path,
    whisper_model: str = "small",
    language: str | None = None,
    top_k: int = 5,
    min_score: float = 6.0,
    ollama_model: str = "qwen2.5:7b",
    use_ollama: bool = True,
    render: bool = True,
    confirm_rights: bool = False,
) -> ReviewManifest:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    source_slug = _slug(Path(source).stem if "://" not in source else "remote")
    job_dir = output_root / f"{source_slug}-{timestamp}"
    work_dir = job_dir / "work"
    clips_dir = job_dir / "clips"
    work_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)

    local_source = ingest(source, work_dir, confirm_rights=confirm_rights)
    transcript = transcribe(
        local_source,
        work_dir / "transcript.json",
        model_size=whisper_model,
        language=language,
    )

    candidates = build_candidates(transcript)
    if not candidates:
        raise RuntimeError("No clip candidates could be built from the transcript")

    if use_ollama:
        scored = score_with_ollama(candidates, model=ollama_model)
        scorer = "ollama-or-fallback"
    else:
        scored = score_heuristic(candidates)
        scorer = "heuristic"

    selected = select_top(scored, top_k=top_k, min_score=min_score)
    if not selected:
        selected = sorted(scored, key=lambda c: (-c.score, c.start))[:top_k]

    manifest = ReviewManifest(
        source=str(local_source),
        generated_at=datetime.now(timezone.utc).isoformat(),
        model=whisper_model,
        scorer=scorer,
        candidates=selected,
    )
    manifest.save(job_dir / "review.json")
    write_review_html(manifest, job_dir / "review.html")

    if render:
        for index, candidate in enumerate(selected, start=1):
            crop = choose_crop(local_source, candidate.start, candidate.end)
            caption_path = clips_dir / f"clip_{index:02d}.ass"
            write_word_synced_ass(
                transcript.words,
                candidate.start,
                candidate.end,
                caption_path,
            )
            output_path = clips_dir / f"clip_{index:02d}.mp4"
            render_clip(local_source, candidate, crop, caption_path, output_path)
            manifest.rendered.append(
                RenderedClip(
                    candidate=candidate,
                    output_path=str(output_path),
                    caption_path=str(caption_path),
                    crop=crop,
                )
            )
            manifest.save(job_dir / "review.json")
            write_review_html(manifest, job_dir / "review.html")

    return manifest
