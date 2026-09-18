from studio.autonomous import MOTION_SHOTS


def test_first_project_native_graphics_shots_are_declared():
    assert {"S02", "S04", "S05", "S06", "S07", "S09"} <= MOTION_SHOTS
