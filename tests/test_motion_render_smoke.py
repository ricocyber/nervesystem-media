from pathlib import Path

from studio.adapters.motion import render_motion_shot


def test_motion_graphics_produces_real_mp4(tmp_path: Path):
    output = tmp_path / "S02.mp4"
    render_motion_shot("S02", 0.12, output)
    assert output.exists()
    assert output.stat().st_size > 1000
