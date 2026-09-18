from pathlib import Path

from studio.preflight import build_preflight_report


def test_preflight_contains_gate_and_schedule():
    report = build_preflight_report(Path("projects/nervesystem_authority_30s"))
    assert "production_gate" in report
    assert "render_waves" in report
    assert report["production_gate"]["passed"] is True
