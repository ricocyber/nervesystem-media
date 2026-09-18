from pathlib import Path

from studio.podcast_edit import build_podcast_filter


PROJECT = Path("projects/novo_ai_podcast_pilot")


def test_podcast_filter_has_all_three_camera_behaviors():
    expression, labels = build_podcast_filter(PROJECT)
    assert "hstack=inputs=2" in expression
    assert "[0:v]trim=" in expression
    assert "[1:v]trim=" in expression
    assert "concat=n=" in expression
    assert "amix=inputs=2" in expression
    assert len(labels) >= 6
