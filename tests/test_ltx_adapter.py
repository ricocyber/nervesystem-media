from studio.adapters.ltx import LTXAdapter


def test_ltx_frame_count_obeys_8n_plus_1():
    for duration in (1.0, 2.2, 5.0, 10.0):
        frames = LTXAdapter._frames_for_duration(duration)
        assert (frames - 1) % 8 == 0
        assert frames <= 249
