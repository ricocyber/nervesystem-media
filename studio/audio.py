from __future__ import annotations

import subprocess
from pathlib import Path


class AudioMixError(RuntimeError):
    pass


def mux_narration(
    picture: Path,
    narration: Path,
    output: Path,
) -> Path:
    if not picture.exists():
        raise AudioMixError(f"Missing picture master: {picture}")
    if not narration.exists():
        raise AudioMixError(f"Missing narration: {narration}")

    output.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(picture),
            "-i", str(narration),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AudioMixError(proc.stderr.strip())
    if not output.exists() or output.stat().st_size == 0:
        raise AudioMixError("Muxed master was not produced")
    return output
