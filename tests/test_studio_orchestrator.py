from studio.models import ProductionBrief
from studio.orchestrator import StudioOrchestrator


def test_photoreal_plan_contains_character_and_voice_stages():
    brief = ProductionBrief(
        title="Test",
        objective="Make a cinematic test commercial",
        format="commercial",
        target_audience="AI infrastructure buyers",
        duration_seconds=30,
        topic="AI authority",
        realism="photoreal",
    )
    plan = StudioOrchestrator().plan(brief)
    stages = [x.stage for x in plan.work_orders]
    assert "casting" in stages
    assert "voice" in stages
    assert "visuals" in stages
    assert "qc" in stages
    assert plan.status == "ready_for_production"


def test_longform_adds_clipper_stage():
    brief = ProductionBrief(
        title="Podcast",
        objective="Create an AI podcast",
        format="podcast",
        target_audience="business owners",
        duration_seconds=1200,
        topic="AI revolution",
        realism="hybrid",
    )
    plan = StudioOrchestrator().plan(brief)
    assert any(x.stage == "clip" for x in plan.work_orders)


def test_graphic_short_skips_casting():
    brief = ProductionBrief(
        title="Short",
        objective="Create a graphic short",
        format="short",
        target_audience="general",
        duration_seconds=30,
        topic="AI safety",
        realism="graphic",
    )
    plan = StudioOrchestrator().plan(brief)
    assert all(x.stage != "casting" for x in plan.work_orders)
