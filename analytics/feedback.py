from __future__ import annotations

from dataclasses import asdict

from .cohorts import median_metrics
from .metrics import PerformanceRecord, derive


def _delta(value: float | None, median: float | None) -> dict:
    if value is None or median is None:
        return {"value": value, "cohort_median": median, "status": "insufficient_data"}

    difference = value - median
    if median == 0:
        relative = None
    else:
        relative = difference / abs(median)

    if difference > 0:
        status = "above_cohort"
    elif difference < 0:
        status = "below_cohort"
    else:
        status = "at_cohort"

    return {
        "value": value,
        "cohort_median": median,
        "difference": difference,
        "relative_difference": relative,
        "status": status,
    }


def compare_to_cohort(
    target: PerformanceRecord,
    comparable_records: list[PerformanceRecord],
) -> dict:
    """
    Compare one publication against a declared comparable cohort.

    This intentionally avoids collapsing everything into one magical
    'virality score'. Exposure, retention, response, conversion, and economics
    are kept separate.
    """
    medians = median_metrics(comparable_records)
    derived = derive(target)
    target_metrics = {
        "average_view_percentage": target.average_view_percentage,
        "finish_watch_ratio": target.finish_watch_ratio,
        **asdict(derived),
    }

    return {
        "publication_id": target.publication_id,
        "cohort_size": len(comparable_records),
        "comparisons": {
            key: _delta(target_metrics.get(key), medians.get(key))
            for key in medians
        },
    }
