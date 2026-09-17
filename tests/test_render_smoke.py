import shutil
import subprocess
from pathlib import Path

import pytest

from clipper_agent.captions import write_word_synced_ass
from clipper_agent.models import Candidate, CropRect, Word
from clipper_agent.render import render_clip


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")
def test_vertical_render_smoke(tmp_path: Path):
    source = tmp_path / "source.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=3:r=30",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
            "-shortest",
            "-c:v", "libx264",
            "-c:a", "aac",
            str(source),
        ],
        check=True,
        capture_output=True,
    )

    candidate = Candidate(
        candidate_id=1,
        start=0.0,
        end=2.0,
        text="This is a local render smoke test.",
        score=8.0,
        title="Smoke test",
        reason="CI validation",
    )
    words = [
        Word(text="This", start=0.1, end=0.4),
        Word(text="is", start=0.4, end=0.6),
        Word(text="a", start=0.6, end=0.7),
        Word(text="local", start=0.7, end=1.0),
        Word(text="test.", start=1.0, end=1.4),
    ]
    ass = write_word_synced_ass(words, 0.0, 2.0, tmp_path / "captions.ass")
    output = tmp_path / "clip.mp4"
    crop = CropRect(x=437, y=0, width=404, height=720, strategy="test")
    render_clip(source, candidate, crop, ass, output, crf=28)

    assert output.exists()
    assert output.stat().st_size > 1000
