from __future__ import annotations

import json
from dataclasses import asdict, dataclass

import requests

from .scorecard import ViralityScorecard, score_idea


class ViralityBrainError(RuntimeError):
    pass


@dataclass(frozen=True)
class Idea:
    idea_id: str
    concept: str
    hook: str
    stakes: str
    target_viewer: str
    funnel_stage: str
    recommended_format: str


@dataclass(frozen=True)
class RankedIdea:
    idea: Idea
    score: float
    decision: str
    scorecard: dict
    reason: str


class OllamaViralityBrain:
    def __init__(self, model: str = "qwen2.5:7b", base_url: str = "http://127.0.0.1:11434", timeout: float = 300):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def verify(self) -> dict:
        try:
            r = requests.get(self.base_url + "/api/tags", timeout=3)
            if not r.ok:
                return {"ready": False, "status": r.status_code}
            models = [(x.get("name") or x.get("model")) for x in r.json().get("models", [])]
            return {"ready": True, "model": self.model, "models": models}
        except requests.RequestException as exc:
            return {"ready": False, "reason": f"{type(exc).__name__}: {exc}"}

    def _json_chat(self, prompt: str, temperature: float) -> dict:
        r = requests.post(
            self.base_url + "/api/chat",
            json={
                "model": self.model,
                "stream": False,
                "format": "json",
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": temperature},
            },
            timeout=self.timeout,
        )
        if not r.ok:
            raise ViralityBrainError(f"Ollama HTTP {r.status_code}: {r.text[:500]}")
        try:
            return json.loads(r.json()["message"]["content"])
        except Exception as exc:
            raise ViralityBrainError(f"Invalid JSON from Ollama: {exc}") from exc

    def generate_ideas(self, topic_space: str, audience: str, channel_promise: str, count: int = 100, batch_size: int = 20, research_context: str | None = None) -> list[Idea]:
        ideas: list[Idea] = []
        seen: set[str] = set()
        attempts = 0
        while len(ideas) < count:
            needed = min(batch_size, count - len(ideas))
            prompt = f"""
Create exactly {needed} distinct YouTube concepts for this media channel.

Channel promise: {channel_promise}
Topic space: {topic_space}
Audience: {audience}

Prefer specific, concrete stories with understandable stakes. Avoid vague motivational ideas.
Each concept should make sense to core viewers, casual viewers, and someone new.

Return only JSON:
{{"ideas":[{{"concept":"...","hook":"...","stakes":"...","target_viewer":"...","funnel_stage":"discovery|trust|conversion","recommended_format":"short|longform|podcast|news|commercial"}}]}}

Do not repeat: {json.dumps([x.concept for x in ideas[-30:]], ensure_ascii=False)}
""".strip()
            data = self._json_chat(prompt, 0.75)
            raw = data.get("ideas")
            if not isinstance(raw, list):
                raise ViralityBrainError("Missing ideas list")
            for item in raw:
                concept = str(item.get("concept", "")).strip()
                key = " ".join(concept.lower().split())
                if not concept or key in seen:
                    continue
                seen.add(key)
                ideas.append(Idea(
                    idea_id=f"I{len(ideas)+1:03d}",
                    concept=concept,
                    hook=str(item.get("hook", "")).strip(),
                    stakes=str(item.get("stakes", "")).strip(),
                    target_viewer=str(item.get("target_viewer", "")).strip(),
                    funnel_stage=str(item.get("funnel_stage", "discovery")).strip(),
                    recommended_format=str(item.get("recommended_format", "longform")).strip(),
                ))
                if len(ideas) >= count:
                    break
            attempts += 1
            if attempts > max(10, count):
                raise ViralityBrainError("Could not produce enough unique ideas")
        return ideas[:count]

    def critic_score(self, ideas: list[Idea], batch_size: int = 10) -> list[RankedIdea]:
        ranked: list[RankedIdea] = []
        fields = list(ViralityScorecard.__dataclass_fields__)
        for offset in range(0, len(ideas), batch_size):
            batch = ideas[offset:offset + batch_size]
            prompt = f"""
Act as a skeptical editorial critic. Score every idea independently from 0-10 on:
{", ".join(fields)}

Use real audience clarity, stakes, promise/proof, packaging potential, novelty, timeliness,
production feasibility, funnel fit, and shareability. Do not claim access to platform algorithms.

Return only JSON:
{{"scores":[{{"idea_id":"I001","scores":{{{",".join(f'"{x}":7' for x in fields)}}},"critic_note":"..."}}]}}

Ideas:
{json.dumps([asdict(x) for x in batch], ensure_ascii=False)}
""".strip()
            data = self._json_chat(prompt, 0.1)
            responses = data.get("scores")
            if not isinstance(responses, list):
                raise ViralityBrainError("Missing critic scores")
            response_map = {str(x.get("idea_id")): x for x in responses}
            for idea in batch:
                item = response_map.get(idea.idea_id)
                if not item:
                    raise ViralityBrainError(f"Missing score for {idea.idea_id}")
                raw = item.get("scores", {})
                card = ViralityScorecard(**{field: float(raw[field]) for field in fields})
                result = score_idea(card)
                ranked.append(RankedIdea(
                    idea=idea,
                    score=result.total,
                    decision=result.decision,
                    scorecard=asdict(card),
                    reason=str(item.get("critic_note", "")).strip() or result.reason,
                ))
        return sorted(ranked, key=lambda x: (-x.score, x.idea.idea_id))

    def package_idea(self, ranked: RankedIdea) -> dict:
        prompt = f"""
Package this video concept:
Concept: {ranked.idea.concept}
Hook: {ranked.idea.hook}
Stakes: {ranked.idea.stakes}
Viewer: {ranked.idea.target_viewer}

Generate exactly 10 distinct titles and 5 thumbnail concepts.
Titles and thumbnails should complement rather than repeat each other.
Keep thumbnail text to 0-4 words and make the visual readable on a phone.

Return only JSON:
{{"titles":["..."],"thumbnail_concepts":[{{"id":"T01","visual":"...","text":"...","reason":"..."}}]}}
""".strip()
        data = self._json_chat(prompt, 0.65)
        titles = data.get("titles")
        thumbs = data.get("thumbnail_concepts")
        if not isinstance(titles, list) or len(titles) != 10:
            raise ViralityBrainError("Expected exactly 10 titles")
        if not isinstance(thumbs, list) or len(thumbs) != 5:
            raise ViralityBrainError("Expected exactly 5 thumbnails")
        return {"idea_id": ranked.idea.idea_id, "concept": ranked.idea.concept, "idea_score": ranked.score, "titles": titles, "thumbnail_concepts": thumbs}
