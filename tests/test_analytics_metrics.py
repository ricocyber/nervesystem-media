from analytics.metrics import PerformanceRecord, derive


def test_derived_metrics_and_margin():
    record = PerformanceRecord(
        publication_id="p1",
        channel_id="c1",
        language="en",
        content_format="short",
        topic="ai",
        duration_seconds=30,
        publication_week="2026-W38",
        engaged_views=1000,
        likes=50,
        comments=10,
        shares=20,
        subscribers_gained=5,
        estimated_revenue_usd=25,
        attributable_external_income_usd=100,
        production_cost_usd=30,
        compute_cost_usd=5,
    )
    metrics = derive(record)
    assert metrics.engagement_per_1000_engaged_views == 80
    assert metrics.shares_per_1000_engaged_views == 20
    assert metrics.subscriber_conversion_per_1000 == 5
    assert metrics.contribution_margin_30d == 90
