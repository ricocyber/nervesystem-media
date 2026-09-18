from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

import requests


class MuseTalkMacError(RuntimeError):
    pass


@dataclass(frozen=True)
class MuseTalkResult:
    output_path: str
    avatar_key: str
    video_size_bytes: int | None
    timing: object | None


def _encode_file(path: Path) -> str:
    if not path.exists():
        raise MuseTalkMacError(f"Missing media file: {path}")
    return base64.b64encode(path.read_bytes()).decode("ascii")


def _decode_video(payload: str, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = base64.b64decode(payload, validate=True)
    except Exception as exc:
        raise MuseTalkMacError(f"Invalid base64 video response: {exc}") from exc
    if not data:
        raise MuseTalkMacError("MuseTalk returned an empty video")
    output.write_bytes(data)
    return output


class MuseTalkMacAdapter:
    """
    Adapter for a local MuseTalk-Mac style FastAPI server.

    Voice generation is intentionally external. NerveStudio uses Voicebox for
    local TTS, then sends the resulting audio plus a reference/source video to
    MuseTalk only for lip synchronization.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 600):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def verify(self) -> dict:
        try:
            response = requests.get(self.base_url + "/health", timeout=3)
            if response.ok:
                return {
                    "ready": True,
                    "base_url": self.base_url,
                    "health": response.json() if response.content else {},
                }
            return {
                "ready": False,
                "base_url": self.base_url,
                "reason": f"health returned HTTP {response.status_code}",
            }
        except requests.RequestException as exc:
            return {
                "ready": False,
                "base_url": self.base_url,
                "reason": f"{type(exc).__name__}: {exc}",
            }

    def warmup(self, source_video: Path, avatar_key: str) -> object:
        payload = {
            "video_b64": _encode_file(source_video),
            "avatar_key": avatar_key,
        }
        response = requests.post(
            self.base_url + "/warmup",
            json=payload,
            timeout=self.timeout,
        )
        if not response.ok:
            raise MuseTalkMacError(
                f"Warmup failed {response.status_code}: {response.text[:500]}"
            )
        if not response.content:
            return {}
        return response.json()

    def lipsync(
        self,
        source_video: Path,
        audio_path: Path,
        avatar_key: str,
        output_path: Path,
    ) -> MuseTalkResult:
        status = self.verify()
        if not status.get("ready"):
            raise MuseTalkMacError(status.get("reason", "MuseTalk service unavailable"))

        payload = {
            "video_b64": _encode_file(source_video),
            "audio_b64": _encode_file(audio_path),
            "avatar_key": avatar_key,
        }
        response = requests.post(
            self.base_url + "/",
            json=payload,
            timeout=self.timeout,
        )
        if not response.ok:
            raise MuseTalkMacError(
                f"Lip sync failed {response.status_code}: {response.text[:500]}"
            )
        data = response.json()
        video_b64 = data.get("video_b64")
        if not video_b64:
            raise MuseTalkMacError("MuseTalk response did not contain video_b64")

        _decode_video(video_b64, output_path)
        return MuseTalkResult(
            output_path=str(output_path),
            avatar_key=avatar_key,
            video_size_bytes=data.get("video_size_bytes"),
            timing=data.get("timing"),
        )
