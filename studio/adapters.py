from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Adapter:
    name: str
    capability: str
    local_first: bool
    command_hint: str
    ready: bool = False


DEFAULT_ADAPTERS = {
    "blender": Adapter(
        name="blender",
        capability="3d_scene_render",
        local_first=True,
        command_hint="blender --background <scene.blend> --python <render.py>",
    ),
    "ltx_video": Adapter(
        name="ltx-video",
        capability="ai_video_generation",
        local_first=True,
        command_hint="repo-specific; verify installed entrypoint before execution",
    ),
    "digital_human": Adapter(
        name="digital-human",
        capability="character_animation",
        local_first=True,
        command_hint="repo-specific; verify installed entrypoint before execution",
    ),
    "voicebox": Adapter(
        name="voicebox",
        capability="speech_generation",
        local_first=True,
        command_hint="repo-specific; verify installed entrypoint before execution",
    ),
    "ffmpeg": Adapter(
        name="ffmpeg",
        capability="edit_render_encode",
        local_first=True,
        command_hint="ffmpeg",
        ready=True,
    ),
    "clipper": Adapter(
        name="clipper-agent",
        capability="longform_to_shorts",
        local_first=True,
        command_hint="clipper-agent clip <video>",
        ready=True,
    ),
}


def adapter_readiness() -> dict[str, bool]:
    return {name: adapter.ready for name, adapter in DEFAULT_ADAPTERS.items()}
