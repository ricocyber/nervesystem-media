from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .adapters.voicebox import VoiceboxAdapter


class NarrationError(RuntimeError):
    pass


def render_narration(
    project_dir: Path,
    profile_id: str,
    base_url: str = "http://127.0.0.1:17493",
    output_path: Path | None = None,
) -> Path:
    manifest = json.loads(
        (project_dir / "dialogue_manifest.json").read_text(encoding="utf-8")
    )
    work = project_dir / "work" / "audio"
    work.mkdir(parents=True, exist_ok=True)
    output_path = output_path or (work / "narration.wav")

    adapter = VoiceboxAdapter(base_url=base_url)
    line_paths: list[tuple[Path, int]] = []

    for index, line in enumerate(manifest["lines"], start=1):
        path = work / f"line_{index:02d}.wav"
        adapter.generate(
            text=line["text"],
            profile_id=profile_id,
            output_path=path,
            language=manifest.get("language", "en"),
            instruct=line.get("delivery"),
        )
        delay_ms = max(0, round(float(line["start"]) * 1000))
        line_paths.append((path, delay_ms))

    if not line_paths:
        raise NarrationError("Dialogue manifest has no lines")

    cmd = ["ffmpeg", "-y"]
    for path, _ in line_paths:
        cmd.extend(["-i", str(path)])

    filters = []
    labels = []
    for i, (_, delay_ms) in enumerate(line_paths):
        label = f"a{i}"
        filters.append(
            f"[{i}:a]aresample=48000,adelay={delay_ms}|{delay_ms}[{label}]"
        )
        labels.append(f"[{label}]")

    filters.append(
        "".join(labels)
        + f"amix=inputs={len(labels)}:duration=longest:normalize=0,"
          "apad=pad_dur=30[aout]"
    )

    cmd.extend([
        "-filter_complex", ";".join(filters),
        "-map", "[aout]",
        "-t", "30",
        "-ar", "48000",
        "-ac", "2",
        "-c:a", "pcm_s24le",
        str(output_path),
    ])

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise NarrationError(proc.stderr.strip())
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise NarrationError("Narration mix was not produced")

    return output_path
