from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

import requests


class VoiceboxAdapterError(RuntimeError):
    pass


@dataclass(frozen=True)
class VoiceboxResult:
    output_path: str
    generation_id: str | None
    profile_id: str
    duration: float | None
    engine: str | None


class VoiceboxAdapter:
    """
    REST adapter for a local Voicebox server.

    The base URL is configurable because current Voicebox builds may expose
    different loopback ports. The API shape is verified before generation.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:17493", timeout: float = 300):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def verify(self) -> dict:
        errors: list[str] = []
        for path in ("/profiles", "/docs", "/openapi.json"):
            try:
                response = requests.get(self.base_url + path, timeout=3)
                if response.ok:
                    return {"ready": True, "base_url": self.base_url, "probe": path}
                errors.append(f"{path}:{response.status_code}")
            except requests.RequestException as exc:
                errors.append(f"{path}:{type(exc).__name__}")

        return {"ready": False, "base_url": self.base_url, "errors": errors}

    def list_profiles(self) -> object:
        response = requests.get(self.base_url + "/profiles", timeout=10)
        response.raise_for_status()
        return response.json()

    def generate(
        self,
        text: str,
        profile_id: str,
        output_path: Path,
        language: str = "en",
        instruct: str | None = None,
    ) -> VoiceboxResult:
        status = self.verify()
        if not status.get("ready"):
            raise VoiceboxAdapterError(
                f"Voicebox is not reachable at {self.base_url}: {status.get('errors')}"
            )

        payload = {
            "text": text,
            "profile_id": profile_id,
            "language": language,
        }
        if instruct:
            payload["instruct"] = instruct

        response = requests.post(
            self.base_url + "/generate",
            json=payload,
            timeout=self.timeout,
        )
        if not response.ok:
            raise VoiceboxAdapterError(
                f"Voicebox generation failed {response.status_code}: {response.text[:500]}"
            )
        data = response.json()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        audio_path = data.get("audio_path")
        copied = False
        if audio_path:
            local_audio = Path(audio_path).expanduser()
            if local_audio.exists():
                shutil.copyfile(local_audio, output_path)
                copied = True

        generation_id = data.get("id")
        if not copied and generation_id:
            audio = requests.get(
                self.base_url + f"/audio/{generation_id}",
                timeout=self.timeout,
            )
            if audio.ok and audio.content:
                output_path.write_bytes(audio.content)
                copied = True

        if not copied:
            raise VoiceboxAdapterError(
                "Voicebox returned a generation record but no accessible audio artifact"
            )

        return VoiceboxResult(
            output_path=str(output_path),
            generation_id=str(generation_id) if generation_id else None,
            profile_id=profile_id,
            duration=float(data["duration"]) if data.get("duration") is not None else None,
            engine=data.get("engine"),
        )
