import json
from pathlib import Path

from virality.research import ResearchPacket


def test_research_packet_preserves_source_provenance(tmp_path: Path):
    path = tmp_path / "research.json"
    path.write_text(json.dumps({
        "topic": "AI authority",
        "evidence": [{
            "evidence_id": "E001",
            "title": "Example source",
            "source_uri": "https://example.com/source",
            "source_type": "article",
            "observed_at": "2026-09-18",
            "claim": "A sourced factual claim.",
            "confidence": "high"
        }],
        "audience_questions": ["Who can authorize an AI action?"],
        "trend_signals": ["agentic systems"],
        "forbidden_claims": ["Do not claim universal adoption."]
    }), encoding="utf-8")

    packet = ResearchPacket.load(path)
    context = packet.prompt_context()
    assert "https://example.com/source" in context
    assert "Do not claim universal adoption." in context
