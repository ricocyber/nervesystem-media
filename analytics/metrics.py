from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceRecord:
    publication_id: str
    channel_id: str
    language: str
    content_format: str
    topic: str
    duration_seconds: float
    publication_week: str

    views: int | None = None
    engaged_views: int | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    subscribers_gained: int | None = None
    average_view_percentage: float | None = None
    finish_watch_ratio: float | None = None
    estimated_revenue_usd: float | None = None
    attributable_external_income_usd: float | None = None
    production_cost_usd: float | None = None
    license_cost_usd: float | None = None
    compute_cost_usd: float | None = None
    promotion_cost_usd: float | None = None


@dataclass(frozen=True)
class DerivedMetrics:
    engagement_per_1000_engaged_views: float | None
    shares_per_1000_engaged_views: float | None
    subscriber_conversion_per_1000: float | None
    contribution_margin_30d: float | None


def _per_1000(numerator: int | None, denominator: int | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return 1000.0 * numerator / denominator


def derive(record: PerformanceRecord) -> DerivedMetrics:
    interactions = None
    if (
        record.likes is not None
        and record.comments is not None
        and record.shares is not None
    ):
        interactions = record.likes + record.comments + record.shares

    income_values = [
        record.estimated_revenue_usd,
        record.attributable_external_income_usd,
    ]
    cost_values = [
        record.production_cost_usd,
        record.license_cost_usd,
        record.compute_cost_usd,
        record.promotion_cost_usd,
    ]

    contribution_margin = None
    if any(v is not None for v in income_values + cost_values):
        income = sum(v or 0.0 for v in income_values)
        cost = sum(v or 0.0 for v in cost_values)
        contribution_margin = income - cost

    return DerivedMetrics(
        engagement_per_1000_engaged_views=_per_1000(
            interactions, record.engaged_views
        ),
        shares_per_1000_engaged_views=_per_1000(
            record.shares, record.engaged_views
        ),
        subscriber_conversion_per_1000=_per_1000(
            record.subscribers_gained, record.engaged_views
        ),
        contribution_margin_30d=contribution_margin,
    )
