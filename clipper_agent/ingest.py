from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.parse import urlparse

from yt_dlp import YoutubeDL


def is_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except ValueError:
        return False


def ingest(source: str, workdir: Path, confirm_rights: bool = False) -> Path:
    workdir.mkdir(parents=True, exist_ok=True)
    if not is_url(source):
        path = Path(source).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(path)
        return path

    if not confirm_rights:
        raise ValueError(
            "URL ingest requires --confirm-rights. Only process video you own or are authorized to reuse."
        )

    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]
    template = str(workdir / f"source_{digest}.%(ext)s")
    opts = {
        "outtmpl": template,
        "format": "bv*[height<=1080]+ba/b[height<=1080]/b",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": False,
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(source, download=True)
        requested = ydl.prepare_filename(info)

    candidates = sorted(workdir.glob(f"source_{digest}.*"))
    video_candidates = [p for p in candidates if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm"}]
    if not video_candidates:
        path = Path(requested)
        if path.exists():
            return path.resolve()
        raise FileNotFoundError("yt-dlp completed but no downloaded video was found")
    return video_candidates[0].resolve()
