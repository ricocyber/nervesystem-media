from pathlib import Path

from studio.podcast import build_camera_timeline, build_host_scripts


PROJECT = Path("projects/novo_ai_podcast_pilot")


def test_dialogue_splits_between_two_hosts():
    scripts = build_host_scripts(PROJECT)
    assert set(scripts) == {"MAYA_01", "AXEL_01"}
    assert len(scripts["MAYA_01"]) == 3
    assert len(scripts["AXEL_01"]) == 3


def test_camera_timeline_covers_episode():
    timeline = build_camera_timeline(PROJECT)
    cuts = timeline["cuts"]
    assert cuts[0]["start"] == 0.0
    assert cuts[-1]["end"] == 60.0
    assert {cut["camera"] for cut in cuts} >= {"CAM_A", "CAM_B", "CAM_C"}
