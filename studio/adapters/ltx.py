from __future__ import annotations

import math
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


class LTXAdapterError(RuntimeError):
    pass


@dataclass(frozen=True)
class LTXResult:
    output_path: str
    prompt: str
    duration_seconds: float
    num_frames: int
    width: int
    height: int
    seed: int
    pipeline_config: str


class LTXAdapter:
    """
    Adapter for a local clone of the official LTX-Video repository.

    V1 deliberately verifies the repository shape and CLI help before running.
    It does not assume that a directory named ltx-video is compatible.
    """

    def __init__(self, repo_path: Path | None = None):
        self.repo = (repo_path or (Path.home() / "ltx-video")).expanduser().resolve()

    def _python(self) -> str:
        candidates = [
            self.repo / ".venv" / "bin" / "python",
            self.repo / "env" / "bin" / "python",
            self.repo / "venv" / "bin" / "python",
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        return sys.executable

    def _inference(self) -> Path:
        path = self.repo / "inference.py"
        if not path.exists():
            raise LTXAdapterError(f"Missing inference.py in {self.repo}")
        return path

    def _pipeline_config(self) -> Path:
        config_dir = self.repo / "configs"
        if not config_dir.exists():
            raise LTXAdapterError(f"Missing configs directory in {self.repo}")

        preferred = sorted(config_dir.glob("*distilled*.yaml"), reverse=True)
        if preferred:
            return preferred[0]

        any_yaml = sorted(config_dir.glob("*.yaml"), reverse=True)
        if not any_yaml:
            raise LTXAdapterError("No pipeline YAML found in LTX configs")
        return any_yaml[0]

    @staticmethod
    def _frames_for_duration(duration_seconds: float, fps: int = 24) -> int:
        # LTX expects 8n+1 frame counts. Keep shots comfortably below 257 frames.
        desired = max(9, round(duration_seconds * fps))
        n = max(1, round((desired - 1) / 8))
        frames = 8 * n + 1
        return min(frames, 249)

    def verify(self) -> dict:
        if not self.repo.exists():
            return {"ready": False, "reason": f"repo not found: {self.repo}"}

        inference = self._inference()
        proc = subprocess.run(
            [self._python(), str(inference), "--help"],
            cwd=str(self.repo),
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        text = (proc.stdout or "") + "\n" + (proc.stderr or "")
        required = ["--prompt", "--height", "--width", "--num_frames", "--pipeline_config"]
        missing = [flag for flag in required if flag not in text]
        if proc.returncode != 0 or missing:
            return {
                "ready": False,
                "reason": f"inference CLI verification failed; missing={missing}; returncode={proc.returncode}",
            }

        return {
            "ready": True,
            "repo": str(self.repo),
            "python": self._python(),
            "inference": str(inference),
            "pipeline_config": str(self._pipeline_config()),
        }

    def generate(
        self,
        prompt: str,
        output_path: Path,
        duration_seconds: float,
        width: int = 1216,
        height: int = 704,
        seed: int = 42,
        conditioning_media_path: Path | None = None,
    ) -> LTXResult:
        status = self.verify()
        if not status.get("ready"):
            raise LTXAdapterError(status.get("reason", "LTX adapter not ready"))

        if width % 32 or height % 32:
            raise LTXAdapterError("LTX width and height must be divisible by 32")

        frames = self._frames_for_duration(duration_seconds)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self._python(),
            str(self._inference()),
            "--prompt", prompt,
            "--height", str(height),
            "--width", str(width),
            "--num_frames", str(frames),
            "--seed", str(seed),
            "--pipeline_config", str(self._pipeline_config()),
            "--output_path", str(output_path),
        ]

        if conditioning_media_path:
            cmd.extend([
                "--conditioning_media_paths", str(conditioning_media_path),
                "--conditioning_start_frames", "0",
            ])

        proc = subprocess.run(
            cmd,
            cwd=str(self.repo),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise LTXAdapterError(proc.stderr.strip() or "LTX inference failed")
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise LTXAdapterError(
                f"LTX exited successfully but produced no output at {output_path}"
            )

        return LTXResult(
            output_path=str(output_path),
            prompt=prompt,
            duration_seconds=duration_seconds,
            num_frames=frames,
            width=width,
            height=height,
            seed=seed,
            pipeline_config=str(self._pipeline_config()),
        )
