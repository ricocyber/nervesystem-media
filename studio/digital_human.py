from __future__ import annotations

from pathlib import Path

from .adapters.musetalk_mac import MuseTalkMacAdapter, MuseTalkResult


def render_talking_human(
    reference_video: Path,
    narration_audio: Path,
    output_video: Path,
    avatar_key: str,
    musetalk_url: str = "http://127.0.0.1:8000",
    warmup: bool = True,
) -> MuseTalkResult:
    """
    Render a talking human from an existing/authorized source or generated idle
    video plus local speech audio.

    Identity creation is not performed here. This stage only animates/lip-syncs
    the supplied source video.
    """
    adapter = MuseTalkMacAdapter(base_url=musetalk_url)
    if warmup:
        adapter.warmup(reference_video, avatar_key)
    return adapter.lipsync(
        source_video=reference_video,
        audio_path=narration_audio,
        avatar_key=avatar_key,
        output_path=output_video,
    )
