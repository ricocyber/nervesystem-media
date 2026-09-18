from __future__ import annotations

import statistics
from dataclasses import asdict
from typing import Iterable

from .metrics import PerformanceRecord, derive


COHORT_KEYS = (
    "channel_id",
    "language",
    "content_format",
    "topic",
    "publication_week",
)


def duration_band(seconds: float) -> str:
    if seconds < 30:
        return "<30s"
    if seconds < 60:
        return "30-59s"
    if seconds < 180:
        return "1-3m"
    if seconds < 600:
        return "3-10m"
    if seconds < 1800:
        return "10-30m"
    return "30m+"


def cohort_key(record: PerformanceRecord) -> tuple:
    return (
        record.channel_id,
        record.language,
        record.content_format,
        record.topic,
        duration_band(record.duration_seconds),
        record.publication_week,
    )


def median_metrics(records: Iterable[PerformanceRecord]) -> dict[str, float | None]:
    records = list(records)
    values: dict[str, list[float]] = {
        "average_view_percentage": [],
        "finish_watch_ratio": [],
        "engagement_per_1000_engaged_views": [],
        "shares_per_1000_engaged_views": [],
        "subscriber_conversion_per_1000": [],
        "contribution_margin_30d": [],
    }

    for record in records:
        derived = derive(record)
        raw = {
            "average_view_percentage": record.average_view_percentage,
            "finish_watch_ratio": record.finish_watch_ratio,
            **asdict(derived),
        }
        for key in values:
            value = raw.get(key)
            if value is not None:
                values[key].append(float(value))

    return {
        key: statistics.median(series) if series else None
        for key, series in values.items()
    }
