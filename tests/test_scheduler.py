from pathlib import Path

from studio.scheduler import build_render_waves


def test_dependent_shots_render_after_establishing_shots():
    waves = build_render_waves(Path("projects/nervesystem_authority_30s"))
    wave_index = {shot: idx for idx, wave in enumerate(waves) for shot in wave}
    assert wave_index["S01"] < wave_index["S10"]
    assert wave_index["S03"] < wave_index["S08"]
