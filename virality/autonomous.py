from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .ollama_brain import OllamaViralityBrain


def run_virality_funnel(
    topic_space: str,
    audience: str,
    channel_promise: str,
    output_dir: Path,
    model: str = "qwen2.5:7b",
    count: int = 100,
    shortlist: int = 10,
    package_top: int = 3,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    brain = OllamaViralityBrain(model=model)
    status = brain.verify()
    if not status.get("ready"):
        raise RuntimeError(f"Ollama unavailable: {status}")

    ideas = brain.generate_ideas(
        topic_space=topic_space,
        audience=audience,
        channel_promise=channel_promise,
        count=count,
    )
    ranked = brain.critic_score(ideas)
    survivors = ranked[:shortlist]

    packages = []
    for item in survivors[:package_top]:
        if item.decision in {"PRODUCE", "ITERATE", "REPACKAGE"}:
            packages.append(brain.package_idea(item))

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "topic_space": topic_space,
        "audience": audience,
        "channel_promise": channel_promise,
        "idea_count": len(ideas),
        "ranked": [
            {
                "idea": asdict(item.idea),
                "score": item.score,
                "decision": item.decision,
                "scorecard": item.scorecard,
                "reason": item.reason,
            }
            for item in ranked
        ],
        "shortlist_ids": [item.idea.idea_id for item in survivors],
        "packages": packages,
    }

    (output_dir / "virality_run.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return payload
