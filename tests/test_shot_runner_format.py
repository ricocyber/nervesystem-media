from studio.shot_runner import _format_argv


def test_format_argv_does_not_use_shell_string():
    task = {
        "shot_id": "S01",
        "prompt": "realistic operator",
        "duration_seconds": 2.2,
        "output_video": "/tmp/S01.mp4",
        "output_metadata": "/tmp/S01.json",
    }
    argv = _format_argv(
        ["tool", "--prompt", "{prompt}", "--duration", "{duration}", "--output", "{output}"],
        task,
    )
    assert argv[0] == "tool"
    assert "realistic operator" in argv
    assert "/tmp/S01.mp4" in argv
