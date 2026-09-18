from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceSpan:
    source_id: str
    source_start_ms: int
    source_end_ms: int
    output_start_ms: int
    output_end_ms: int
    playback_rate: float = 1.0


def validate_spans(spans: list[SourceSpan], output_duration_ms: int) -> None:
    if output_duration_ms <= 0:
        raise ValueError("output_duration_ms must be positive")

    ordered = sorted(spans, key=lambda x: x.output_start_ms)
    for span in ordered:
        if span.source_start_ms < 0 or span.output_start_ms < 0:
            raise ValueError("span start times cannot be negative")
        if span.source_end_ms <= span.source_start_ms:
            raise ValueError("source span must have positive duration")
        if span.output_end_ms <= span.output_start_ms:
            raise ValueError("output span must have positive duration")
        if span.output_end_ms > output_duration_ms:
            raise ValueError("output span exceeds output duration")
        if span.playback_rate <= 0:
            raise ValueError("playback_rate must be positive")

    for previous, current in zip(ordered, ordered[1:]):
        if current.output_start_ms < previous.output_end_ms:
            raise ValueError("output spans overlap")
