from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass

import requests

from .models import Candidate, Transcript, Word


HOOK_WORDS = {
    "secret", "mistake", "never", "nobody", "crazy", "truth", "problem", "money",
    "million", "billion", "why", "how", "warning", "danger", "future", "changed",
    "wrong", "best", "worst", "first", "last", "actually", "imagine", "listen",
}
EMOTION_WORDS = {
    "love", "hate", "angry", "scared", "afraid", "excited", "shocked", "insane",
    "amazing", "terrible", "wild", "unbelievable", "risk", "fail", "failed",
}


@dataclass
class Sentence:
    start_index: int
    end_index: int
    start: float
    end: float
    text: str


def _sentences(words: list[Word]) -> list[Sentence]:
    if not words:
        return []
    out: list[Sentence] = []
    start = 0
    for i, word in enumerate(words):
        terminal = bool(re.search(r"[.!?…][\"')\]]*$", word.text))
        too_long = word.end - words[start].start >= 14
        if terminal or too_long or i == len(words) - 1:
            chunk = words[start : i + 1]
            out.append(
                Sentence(
                    start_index=start,
                    end_index=i,
                    start=chunk[0].start,
                    end=chunk[-1].end,
                    text=" ".join(w.text for w in chunk),
                )
            )
            start = i + 1
    return out


def build_candidates(
    transcript: Transcript,
    min_seconds: float = 20,
    max_seconds: float = 60,
    stride_sentences: int = 1,
) -> list[Candidate]:
    sents = _sentences(transcript.words)
    candidates: list[Candidate] = []
    cid = 1
    for i in range(0, len(sents), max(1, stride_sentences)):
        for j in range(i, len(sents)):
            duration = sents[j].end - sents[i].start
            if duration < min_seconds:
                continue
            if duration > max_seconds:
                break
            text = " ".join(s.text for s in sents[i : j + 1]).strip()
            if len(text.split()) < 25:
                continue
            candidates.append(
                Candidate(
                    candidate_id=cid,
                    start=sents[i].start,
                    end=sents[j].end,
                    text=text,
                )
            )
            cid += 1
            break
    return candidates


def heuristic_score(candidate: Candidate) -> float:
    text = candidate.text.lower()
    tokens = re.findall(r"[a-z0-9']+", text)
    if not tokens:
        return 0.0
    token_set = set(tokens)
    hook = len(token_set & HOOK_WORDS)
    emotion = len(token_set & EMOTION_WORDS)
    question = 1 if "?" in candidate.text else 0
    numeric = min(2, sum(any(ch.isdigit() for ch in t) for t in tokens))
    length_fit = max(0.0, 1.0 - abs(candidate.duration - 38.0) / 38.0)
    opening = " ".join(tokens[:18])
    opening_bonus = 1.5 if any(w in opening for w in HOOK_WORDS) else 0.0
    raw = 4.2 + 0.45 * hook + 0.4 * emotion + 0.5 * question + 0.25 * numeric + 1.1 * length_fit + opening_bonus
    return round(min(10.0, raw), 2)


def score_heuristic(candidates: list[Candidate]) -> list[Candidate]:
    out = []
    for c in candidates:
        copy = c.model_copy(deep=True)
        copy.score = heuristic_score(copy)
        copy.title = " ".join(copy.text.split()[:8]).rstrip(".,!?")
        copy.reason = "Local deterministic hook/emotion/structure score"
        copy.scorer = "heuristic"
        out.append(copy)
    return out


def ollama_available(base_url: str = "http://127.0.0.1:11434") -> bool:
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=1.5)
        return r.ok
    except requests.RequestException:
        return False


def score_with_ollama(
    candidates: list[Candidate],
    model: str = "qwen2.5:7b",
    base_url: str = "http://127.0.0.1:11434",
    batch_size: int = 8,
) -> list[Candidate]:
    if not ollama_available(base_url):
        return score_heuristic(candidates)

    by_id = {c.candidate_id: c.model_copy(deep=True) for c in candidates}
    for offset in range(0, len(candidates), batch_size):
        batch = candidates[offset : offset + batch_size]
        payload_items = [
            {
                "id": c.candidate_id,
                "duration_seconds": round(c.duration, 1),
                "transcript": c.text[:3500],
            }
            for c in batch
        ]
        prompt = f"""
You are selecting short-form clips from a longer video.
Score each candidate from 0 to 10 for: immediate hook, standalone context,
insight/surprise, emotion/energy, clear payoff, and likelihood a viewer keeps watching.
Do not reward ragebait by itself. Penalize clips that begin mid-thought, depend on missing
context, or have no payoff.

Return ONLY JSON in this exact shape:
{{"clips":[{{"id":1,"score":8.4,"title":"short accurate title","reason":"one sentence"}}]}}

Candidates:
{json.dumps(payload_items, ensure_ascii=False)}
""".strip()
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={
                    "model": model,
                    "stream": False,
                    "format": "json",
                    "messages": [{"role": "user", "content": prompt}],
                    "options": {"temperature": 0.15},
                },
                timeout=180,
            )
            response.raise_for_status()
            content = response.json()["message"]["content"]
            data = json.loads(content)
            for item in data.get("clips", []):
                cid = int(item["id"])
                if cid not in by_id:
                    continue
                c = by_id[cid]
                c.score = float(item.get("score", 0))
                c.title = str(item.get("title", "")).strip()[:100]
                c.reason = str(item.get("reason", "")).strip()[:240]
                c.scorer = "ollama"
        except (requests.RequestException, KeyError, ValueError, TypeError, json.JSONDecodeError):
            for c in batch:
                fallback = score_heuristic([c])[0]
                by_id[c.candidate_id] = fallback

    return list(by_id.values())


def _overlap_ratio(a: Candidate, b: Candidate) -> float:
    overlap = max(0.0, min(a.end, b.end) - max(a.start, b.start))
    shorter = max(0.001, min(a.duration, b.duration))
    return overlap / shorter


def select_top(candidates: list[Candidate], top_k: int = 5, min_score: float = 6.0) -> list[Candidate]:
    ranked = sorted(candidates, key=lambda c: (-c.score, c.start))
    selected: list[Candidate] = []
    for candidate in ranked:
        if candidate.score < min_score:
            continue
        if any(_overlap_ratio(candidate, chosen) > 0.5 for chosen in selected):
            continue
        selected.append(candidate)
        if len(selected) >= top_k:
            break
    return selected
