from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .podcast import build_camera_timeline


class PodcastEditError(RuntimeError):
    pass


def _single_camera_filter(input_index: int, start: float, end: float, label: str) -> str:
    return (
        f"[{input_index}:v]trim=start={start}:end={end},"
        "setpts=PTS-STARTPTS,"
        "scale=1920:1080:force_original_aspect_ratio=increase,"
        f"crop=1920:1080[v{label}]"
    )


def _wide_filter(start: float, end: float, label: str) -> list[str]:
    left = f"wl{label}"
    right = f"wr{label}"
    return [
        (
            f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
            f"scale=960:1080:force_original_aspect_ratio=increase,"
            f"crop=960:1080[{left}]"
        ),
        (
            f"[1:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
            f"scale=960:1080:force_original_aspect_ratio=increase,"
            f"crop=960:1080[{right}]"
        ),
        f"[{left}][{right}]hstack=inputs=2[v{label}]",
    ]


def build_podcast_filter(project_dir: Path) -> tuple[str, list[str]]:
    timeline = build_camera_timeline(project_dir)
    filters: list[str] = []
    video_labels: list[str] = []

    for idx, cut in enumerate(timeline["cuts"]):
        label = str(idx)
        start = float(cut["start"])
        end = float(cut["end"])
        camera = cut["camera"]

        if camera == "CAM_A":
            filters.extend(_wide_filter(start, end, label))
        elif camera == "CAM_B":
            filters.append(_single_camera_filter(0, start, end, label))
        elif camera == "CAM_C":
            filters.append(_single_camera_filter(1, start, end, label))
        else:
            raise PodcastEditError(f"Unknown camera: {camera}")

        video_labels.append(f"[v{label}]")

    filters.append(
        "".join(video_labels)
        + f"concat=n={len(video_labels)}:v=1:a=0[vout]"
    )
    filters.append(
        "[2:a][3:a]amix=inputs=2:duration=longest:normalize=0,"
        "loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
    )
    return ";".join(filters), video_labels


def edit_podcast_master(
    project_dir: Path,
    host_a_video: Path,
    host_b_video: Path,
    host_a_audio: Path,
    host_b_audio: Path,
    output_path: Path | None = None,
) -> Path:
    for path in (host_a_video, host_b_video, host_a_audio, host_b_audio):
        if not path.exists():
            raise PodcastEditError(f"Missing input: {path}")

    output_path = output_path or (project_dir / "work" / "podcast_master.mp4")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    filter_complex, _ = build_podcast_filter(project_dir)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(host_a_video),
        "-i", str(host_b_video),
        "-i", str(host_a_audio),
        "-i", str(host_b_audio),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-t", "60",
        "-r", "24",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise PodcastEditError(proc.stderr.strip())
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise PodcastEditError("Podcast editor produced no master video")
    return output_path
