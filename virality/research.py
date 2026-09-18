from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


class ResearchPacketError(ValueError):
    pass


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    title: str
    source_uri: str
    source_type: str
    observed_at: str
    claim: str
    confidence: str = "unknown"


@dataclass
class ResearchPacket:
    topic: str
    evidence: list[EvidenceItem] = field(default_factory=list)
    audience_questions: list[str] = field(default_factory=list)
    trend_signals: list[str] = field(default_factory=list)
    forbidden_claims: list[str] = field(default_factory=list)

    def validate(self) -> None:
        seen: set[str] = set()
        for item in self.evidence:
            if not item.evidence_id:
                raise ResearchPacketError("evidence_id is required")
            if item.evidence_id in seen:
                raise ResearchPacketError(f"duplicate evidence_id: {item.evidence_id}")
            seen.add(item.evidence_id)
            if not item.source_uri:
                raise ResearchPacketError(f"{item.evidence_id} missing source_uri")
            if not item.claim:
                raise ResearchPacketError(f"{item.evidence_id} missing claim")

    @classmethod
    def load(cls, path: Path) -> "ResearchPacket":
        raw = json.loads(path.read_text(encoding="utf-8"))
        packet = cls(
            topic=str(raw.get("topic", "")).strip(),
            evidence=[EvidenceItem(**item) for item in raw.get("evidence", [])],
            audience_questions=[str(x) for x in raw.get("audience_questions", [])],
            trend_signals=[str(x) for x in raw.get("trend_signals", [])],
            forbidden_claims=[str(x) for x in raw.get("forbidden_claims", [])],
        )
        packet.validate()
        return packet

    def prompt_context(self, max_evidence: int = 50) -> str:
        payload = {
            "topic": self.topic,
            "evidence": [asdict(x) for x in self.evidence[:max_evidence]],
            "audience_questions": self.audience_questions,
            "trend_signals": self.trend_signals,
            "forbidden_claims": self.forbidden_claims,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)
