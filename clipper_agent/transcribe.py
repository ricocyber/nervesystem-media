from __future__ import annotations

import json
from pathlib import Path

from faster_whisper import WhisperModel

from .models import Transcript, Word


def transcribe(
    source: str | Path,
    cache_path: Path,
    model_size: str = "small",
    language: str | None = None,
) -> Transcript:
    source = str(Path(source).expanduser().resolve())
    if cache_path.exists():
        return Transcript.model_validate_json(cache_path.read_text(encoding="utf-8"))

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        source,
        language=language,
        word_timestamps=True,
        vad_filter=True,
        beam_size=5,
    )

    words: list[Word] = []
    pieces: list[str] = []
    duration = 0.0
    for segment in segments:
        pieces.append(segment.text.strip())
        duration = max(duration, float(segment.end or 0))
        for item in segment.words or []:
            token = (item.word or "").strip()
            if not token:
                continue
            start = max(0.0, float(item.start or 0))
            end = max(start, float(item.end or start))
            words.append(Word(text=token, start=start, end=end))

    transcript = Transcript(
        source=source,
        language=getattr(info, "language", None),
        duration=duration,
        words=words,
        text=" ".join(p for p in pieces if p),
    )
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(transcript.model_dump_json(indent=2), encoding="utf-8")
    return transcript
