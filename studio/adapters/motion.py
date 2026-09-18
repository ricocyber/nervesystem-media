from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np


class MotionGraphicsError(RuntimeError):
    pass


W, H, FPS = 1920, 1080
BG = (15, 18, 23)
PANEL = (28, 34, 43)
WHITE = (240, 244, 248)
MUTED = (145, 155, 168)
AMBER = (62, 167, 255)
RED = (90, 90, 240)
GREEN = (140, 220, 120)


def _center(frame, text: str, y: int, scale: float, color=WHITE, thickness: int = 2):
    font = cv2.FONT_HERSHEY_SIMPLEX
    size, _ = cv2.getTextSize(text, font, scale, thickness)
    x = max(20, (W - size[0]) // 2)
    cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)


def _base(frame, t: float):
    frame[:] = BG
    for x in range(0, W, 96):
        cv2.line(frame, (x, 0), (x, H), (26, 31, 39), 1)
    for y in range(0, H, 96):
        cv2.line(frame, (0, y), (W, y), (26, 31, 39), 1)
    cv2.line(frame, (120, 110), (W - 120, 110), (71, 78, 89), 2)
    pulse = int(140 + 80 * (0.5 + 0.5 * math.sin(t * 4)))
    cv2.circle(frame, (95, 110), 7, (40, pulse, 240), -1)


def render_motion_shot(
    shot_id: str,
    duration_seconds: float,
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        FPS,
        (W, H),
    )
    if not writer.isOpened():
        raise MotionGraphicsError("Could not open OpenCV video writer")

    total = max(1, round(duration_seconds * FPS))
    for i in range(total):
        t = i / FPS
        p = i / max(1, total - 1)
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        _base(frame, t)

        if shot_id == "S02":
            _center(frame, "AUTONOMOUS AGENT / PAYMENT RAIL", 320, 1.0, MUTED)
            cv2.rectangle(frame, (290, 390), (1630, 690), PANEL, -1)
            _center(frame, "TRANSFER APPROVED", 520, 2.0, WHITE, 4)
            dots = "." * (1 + int(t * 2) % 3)
            _center(frame, "EXECUTING" + dots, 620, 1.2, AMBER, 3)

        elif shot_id == "S04":
            _center(frame, "HIGH-VALUE TRANSFER", 290, 1.5, WHITE, 3)
            cv2.rectangle(frame, (340, 465), (1580, 555), (55, 62, 72), -1)
            progress = int((1580 - 340) * min(0.96, 0.1 + p * 0.86))
            cv2.rectangle(frame, (340, 465), (340 + progress, 555), AMBER, -1)
            _center(frame, f"PROCESSING  {int(min(96, 10 + p * 86)):02d}%", 690, 1.1, MUTED)

        elif shot_id == "S05":
            gate = int((W // 2 - 80) * min(1.0, p * 2.2))
            cv2.rectangle(frame, (0, 0), (gate, H), (20, 22, 27), -1)
            cv2.rectangle(frame, (W - gate, 0), (W, H), (20, 22, 27), -1)
            _center(frame, "WHO AUTHORIZED IT?", 560, 2.4, WHITE, 5)

        elif shot_id == "S06":
            labels = ["REQUESTER IDENTITY", "ACTION INTENT", "GOVERNING POLICY", "TARGET SYSTEM", "OPERATING LIMITS"]
            _center(frame, "NERVESYSTEM / AUTHORITY CHECK", 240, 1.3, WHITE, 3)
            for idx, label in enumerate(labels):
                y = 365 + idx * 115
                cv2.rectangle(frame, (360, y - 48), (1560, y + 38), PANEL, -1)
                color = GREEN if p > (idx + 1) / (len(labels) + 1) else MUTED
                cv2.putText(frame, label, (410, y + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.85, WHITE, 2, cv2.LINE_AA)
                cv2.circle(frame, (1490, y - 5), 15, color, -1)

        elif shot_id == "S07":
            states = [("DENIED", RED), ("QUARANTINED", AMBER), ("AUTHORIZED", GREEN)]
            segment = min(2, int(p * 3))
            text, color = states[segment]
            _center(frame, "ACTION DECISION", 320, 1.2, MUTED)
            cv2.rectangle(frame, (420, 420), (1500, 710), PANEL, -1)
            _center(frame, text, 590, 2.5, color, 5)

        elif shot_id == "S09":
            _center(frame, "CRYPTOGRAPHIC ACTION RECEIPT", 240, 1.35, WHITE, 3)
            rows = [
                ("REQUESTED BY", "agent_07"),
                ("AUTHORIZED POLICY", "policy_4.2"),
                ("TARGET", "relay_zone_3"),
                ("EXECUTED ACTION", "close_relay"),
                ("TIME", "18:42:16.442"),
                ("PROOF", "7C9F...A21D"),
            ]
            for idx, (k, v) in enumerate(rows):
                y = 360 + idx * 95
                cv2.putText(frame, k, (330, y), cv2.FONT_HERSHEY_SIMPLEX, 0.62, MUTED, 2, cv2.LINE_AA)
                cv2.putText(frame, v, (850, y), cv2.FONT_HERSHEY_SIMPLEX, 0.72, WHITE, 2, cv2.LINE_AA)
                cv2.line(frame, (330, y + 24), (1580, y + 24), (55, 62, 72), 1)

        else:
            _center(frame, "NERVESYSTEM", 500, 2.1, WHITE, 4)
            _center(frame, "AUTHORITY LAYER", 610, 1.1, AMBER, 3)

        writer.write(frame)

    writer.release()
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise MotionGraphicsError("Motion graphics render produced no output")
    return output_path
