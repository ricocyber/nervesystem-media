from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class QCCheck:
    name: str
    passed: bool
    detail: str


@dataclass
class QCReport:
    passed: bool
    checks: list[QCCheck]


def probe(path: Path) -> dict:
    proc = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate",
            "-of", "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout)


def qc_master(path: Path, expected_duration: float = 30.0, duration_tolerance: float = 0.75) -> QCReport:
    data = probe(path)
    duration = float(data["format"]["duration"])
    video_streams = [x for x in data.get("streams", []) if x.get("codec_type") == "video"]

    checks = [
        QCCheck(
            "file_exists",
            path.exists() and path.stat().st_size > 0,
            f"{path.stat().st_size if path.exists() else 0} bytes",
        ),
        QCCheck(
            "video_stream",
            len(video_streams) == 1,
            f"{len(video_streams)} video stream(s)",
        ),
        QCCheck(
            "duration",
            abs(duration - expected_duration) <= duration_tolerance,
            f"{duration:.3f}s (target {expected_duration:.3f}s)",
        ),
    ]

    if video_streams:
        stream = video_streams[0]
        width = int(stream.get("width", 0))
        height = int(stream.get("height", 0))
        checks.append(
            QCCheck(
                "minimum_resolution",
                width >= 1920 and height >= 1080,
                f"{width}x{height}",
            )
        )

    return QCReport(passed=all(x.passed for x in checks), checks=checks)


def write_qc_report(report: QCReport, path: Path) -> Path:
    path.write_text(
        json.dumps(
            {
                "passed": report.passed,
                "checks": [asdict(x) for x in report.checks],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return path
