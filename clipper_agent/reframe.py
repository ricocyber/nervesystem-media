from __future__ import annotations

import statistics
from pathlib import Path

import cv2

from .models import CropRect
from .system import ffprobe_video


def _base_crop(width: int, height: int, aspect: float) -> tuple[int, int]:
    source_aspect = width / height
    if source_aspect > aspect:
        return max(2, int(height * aspect) // 2 * 2), height
    return width, max(2, int(width / aspect) // 2 * 2)


def choose_crop(
    source: str | Path,
    start: float,
    end: float,
    target_aspect: float = 9 / 16,
    samples: int = 12,
) -> CropRect:
    width, height, _ = ffprobe_video(source)
    crop_w, crop_h = _base_crop(width, height, target_aspect)
    center_x = width / 2
    center_y = height / 2
    strategy = "center"

    if crop_w < width:
        cap = cv2.VideoCapture(str(source))
        detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        centers: list[float] = []
        duration = max(0.1, end - start)
        for i in range(samples):
            t = start + duration * (i + 0.5) / samples
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ok, frame = cap.read()
            if not ok:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(50, 50))
            if len(faces):
                best = max(faces, key=lambda f: f[2] * f[3])
                x, y, w, h = best
                centers.append(x + w / 2)
        cap.release()
        if centers:
            center_x = statistics.median(centers)
            strategy = "median-face"

    x = int(round(center_x - crop_w / 2))
    y = int(round(center_y - crop_h / 2))
    x = max(0, min(width - crop_w, x))
    y = max(0, min(height - crop_h, y))
    x -= x % 2
    y -= y % 2
    return CropRect(x=x, y=y, width=crop_w, height=crop_h, strategy=strategy)
