from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from .models import ReviewManifest


class GoldInterval(BaseModel):
    start: float
    end: float
    label: str = ""


class BenchmarkResult(BaseModel):
    predictions: int
    gold: int
    matched: int
    precision_at_k: float
    recall: float
    mean_score: float
    details: list[dict] = Field(default_factory=list)


def _iou(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    intersection = max(0.0, min(a_end, b_end) - max(a_start, b_start))
    union = max(a_end, b_end) - min(a_start, b_start)
    return intersection / union if union > 0 else 0.0


def evaluate(review_path: Path, gold_path: Path, iou_threshold: float = 0.25) -> BenchmarkResult:
    review = ReviewManifest.model_validate_json(review_path.read_text(encoding="utf-8"))
    gold_raw = json.loads(gold_path.read_text(encoding="utf-8"))
    gold = [GoldInterval.model_validate(item) for item in gold_raw["gold"]]

    matched_gold: set[int] = set()
    details: list[dict] = []
    matched = 0
    for candidate in review.candidates:
        best_idx = -1
        best_iou = 0.0
        for idx, item in enumerate(gold):
            score = _iou(candidate.start, candidate.end, item.start, item.end)
            if score > best_iou:
                best_idx = idx
                best_iou = score
        hit = best_iou >= iou_threshold
        if hit:
            matched += 1
            matched_gold.add(best_idx)
        details.append(
            {
                "candidate_id": candidate.candidate_id,
                "score": candidate.score,
                "hit": hit,
                "best_iou": round(best_iou, 3),
                "gold_label": gold[best_idx].label if best_idx >= 0 else "",
            }
        )

    n = max(1, len(review.candidates))
    mean_score = sum(c.score for c in review.candidates) / n
    return BenchmarkResult(
        predictions=len(review.candidates),
        gold=len(gold),
        matched=matched,
        precision_at_k=round(matched / n, 3),
        recall=round(len(matched_gold) / max(1, len(gold)), 3),
        mean_score=round(mean_score, 3),
        details=details,
    )
