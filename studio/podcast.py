from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .adapters.musetalk_mac import MuseTalkMacAdapter
from .adapters.voicebox import VoiceboxAdapter


class PodcastProductionError(RuntimeError):
    pass


@dataclass(frozen=True)
class HostRender:
    character_id: str
    audio_path: str
    video_path: str
    avatar_key: str


def _character_map(project_dir: Path) -> dict[str, dict]:
    data = json.loads((project_dir / "character_bible.json").read_text(encoding="utf-8"))
    return {item["id"]: item for item in data["characters"]}


def _dialogue(project_dir: Path) -> list[dict]:
    data = json.loads((project_dir / "dialogue.json").read_text(encoding="utf-8"))
    return list(data["lines"])


def build_host_scripts(project_dir: Path) -> dict[str, list[dict]]:
    hosts = _character_map(project_dir)
    scripts: dict[str, list[dict]] = {character_id: [] for character_id in hosts}
    for line in _dialogue(project_dir):
        speaker = line["speaker"]
        if speaker not in scripts:
            raise PodcastProductionError(f"Unknown speaker: {speaker}")
        scripts[speaker].append(line)
    return scripts


def render_host_audio(
    project_dir: Path,
    character_id: str,
    profile_id: str,
    base_url: str = "http://127.0.0.1:17493",
) -> Path:
    scripts = build_host_scripts(project_dir)
    if character_id not in scripts:
        raise PodcastProductionError(f"Unknown host: {character_id}")

    work = project_dir / "work" / "podcast" / character_id
    work.mkdir(parents=True, exist_ok=True)
    adapter = VoiceboxAdapter(base_url=base_url)

    inputs: list[tuple[Path, int]] = []
    for idx, line in enumerate(scripts[character_id], start=1):
        output = work / f"line_{idx:02d}.wav"
        adapter.generate(
            text=line["text"],
            profile_id=profile_id,
            output_path=output,
            language="en",
            instruct=line.get("delivery"),
        )
        inputs.append((output, round(float(line["start"]) * 1000)))

    if not inputs:
        raise PodcastProductionError(f"No dialogue for {character_id}")

    cmd = ["ffmpeg", "-y"]
    for path, _ in inputs:
        cmd.extend(["-i", str(path)])

    labels = []
    filters = []
    for idx, (_, delay) in enumerate(inputs):
        label = f"h{idx}"
        filters.append(
            f"[{idx}:a]aresample=48000,adelay={delay}|{delay}[{label}]"
        )
        labels.append(f"[{label}]")

    filters.append(
        "".join(labels)
        + f"amix=inputs={len(labels)}:duration=longest:normalize=0,"
          "apad=pad_dur=60[aout]"
    )
    output = work / "host_track.wav"
    cmd.extend([
        "-filter_complex", ";".join(filters),
        "-map", "[aout]",
        "-t", "60",
        "-ar", "48000",
        "-ac", "2",
        "-c:a", "pcm_s24le",
        str(output),
    ])

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise PodcastProductionError(proc.stderr.strip())
    return output


def render_host_video(
    project_dir: Path,
    character_id: str,
    reference_video: Path,
    profile_id: str,
    voicebox_url: str = "http://127.0.0.1:17493",
    musetalk_url: str = "http://127.0.0.1:8000",
) -> HostRender:
    characters = _character_map(project_dir)
    if character_id not in characters:
        raise PodcastProductionError(f"Unknown host: {character_id}")

    character = characters[character_id]
    audio = render_host_audio(
        project_dir=project_dir,
        character_id=character_id,
        profile_id=profile_id,
        base_url=voicebox_url,
    )
    output = project_dir / "work" / "podcast" / character_id / "host_video.mp4"
    adapter = MuseTalkMacAdapter(base_url=musetalk_url)
    avatar_key = character["avatar_key"]
    adapter.warmup(reference_video, avatar_key)
    adapter.lipsync(
        source_video=reference_video,
        audio_path=audio,
        avatar_key=avatar_key,
        output_path=output,
    )
    return HostRender(
        character_id=character_id,
        audio_path=str(audio),
        video_path=str(output),
        avatar_key=avatar_key,
    )


def build_camera_timeline(project_dir: Path) -> dict:
    characters = _character_map(project_dir)
    lines = _dialogue(project_dir)
    plan = json.loads((project_dir / "camera_plan.json").read_text(encoding="utf-8"))

    cuts = []
    last_wide = -999.0
    for idx, line in enumerate(lines):
        start = float(line["start"])
        end = float(line["end"])
        speaker = characters[line["speaker"]]
        camera = speaker["camera"]

        if start - last_wide >= float(plan["editing_rules"]["wide_every_seconds"]):
            wide_end = min(end, start + 1.8)
            cuts.append({
                "start": start,
                "end": wide_end,
                "camera": "CAM_A",
                "reason": "periodic wide reset",
            })
            last_wide = start
            if wide_end < end:
                cuts.append({
                    "start": wide_end,
                    "end": end,
                    "camera": camera,
                    "reason": f"speaker:{line['speaker']}",
                })
        else:
            cuts.append({
                "start": start,
                "end": end,
                "camera": camera,
                "reason": f"speaker:{line['speaker']}",
            })

    return {"cuts": cuts, "cameras": plan["cameras"]}
