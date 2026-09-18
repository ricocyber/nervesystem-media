from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict


@dataclass(frozen=True)
class ViralityScorecard:
    """
    Human/agent-entered 0-10 judgments made BEFORE production.

    The scorecard intentionally separates idea strength from production quality.
    A beautiful edit cannot rescue an idea that has no audience, hook, stakes,
    or packaging potential.
    """

    core_audience_fit: float
    casual_audience_fit: float
    new_audience_fit: float
    stakes: float
    curiosity_gap: float
    hook_promise: float
    proof_specificity: float
    title_potential: float
    thumbnail_potential: float
    novelty: float
    timeliness: float
    production_feasibility: float
    funnel_fit: float
    shareability: float

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if not 0 <= value <= 10:
                raise ValueError(f"{name} must be between 0 and 10, got {value}")


@dataclass(frozen=True)
class IdeaScore:
    total: float
    decision: str
    breakdown: Dict[str, float]
    reason: str


WEIGHTS = {
    # Audience breadth: Paddy-style Core / Casual / New test.
    "audience": 20,
    "stakes": 12,
    "curiosity_gap": 10,
    # Daniel playbook: hook = promise + proof.
    "hook": 14,
    # Packaging before production.
    "packaging": 16,
    "novelty": 6,
    "timeliness": 5,
    "production_feasibility": 5,
    # The content must match its funnel job instead of optimizing views blindly.
    "funnel_fit": 5,
    # Content people send to other people compounds distribution.
    "shareability": 7,
}


def _avg(*values: float) -> float:
    return sum(values) / len(values)


def score_idea(card: ViralityScorecard) -> IdeaScore:
    card.validate()

    audience = _avg(
        card.core_audience_fit,
        card.casual_audience_fit,
        card.new_audience_fit,
    )
    hook = _avg(card.hook_promise, card.proof_specificity)
    packaging = _avg(card.title_potential, card.thumbnail_potential)

    normalized = {
        "audience": audience,
        "stakes": card.stakes,
        "curiosity_gap": card.curiosity_gap,
        "hook": hook,
        "packaging": packaging,
        "novelty": card.novelty,
        "timeliness": card.timeliness,
        "production_feasibility": card.production_feasibility,
        "funnel_fit": card.funnel_fit,
        "shareability": card.shareability,
    }

    weighted = {
        name: round((score / 10) * WEIGHTS[name], 2)
        for name, score in normalized.items()
    }
    total = round(sum(weighted.values()), 2)

    # Hard gates stop expensive production when the premise/package is weak.
    if audience < 5:
        decision = "KILL"
        reason = "Audience breadth failed: the concept is too narrow or unclear."
    elif hook < 5:
        decision = "KILL"
        reason = "Hook failed: the promise/proof is not strong enough."
    elif packaging < 5:
        decision = "REPACKAGE"
        reason = "Idea may work, but title/thumbnail potential is too weak."
    elif total >= 85:
        decision = "PRODUCE"
        reason = "Strong idea and packaging candidate. Move into production."
    elif total >= 70:
        decision = "ITERATE"
        reason = "Promising, but improve the weakest scoring dimensions first."
    else:
        decision = "KILL"
        reason = "Below the production threshold."

    return IdeaScore(
        total=total,
        decision=decision,
        breakdown=weighted,
        reason=reason,
    )
