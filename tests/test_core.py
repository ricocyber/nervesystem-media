from pathlib import Path

from clipper_agent.benchmark import _iou
from clipper_agent.captions import _ts
from clipper_agent.highlights import build_candidates, heuristic_score
from clipper_agent.models import Candidate, Transcript, Word


def test_ass_timestamp():
    assert _ts(65.25) == "0:01:05.25"


def test_iou():
    assert _iou(0, 10, 5, 15) == 5 / 15


def test_candidate_builder_and_score():
    words = []
    t = 0.0
    for sentence in [
        "Here is the first thing you need to know.",
        "Nobody tells you why this mistake costs so much money.",
        "The truth is that the system changes when incentives change.",
        "That is the payoff and the reason this matters.",
    ]:
        tokens = sentence.split()
        for idx, token in enumerate(tokens):
            end = t + 0.8
            words.append(Word(text=token, start=t, end=end))
            t = end
        t += 0.5
    transcript = Transcript(source="x.mp4", duration=t, words=words, text=" ".join(w.text for w in words))
    candidates = build_candidates(transcript, min_seconds=10, max_seconds=60)
    assert candidates
    scored = heuristic_score(candidates[0])
    assert scored > 0


def test_candidate_duration():
    c = Candidate(candidate_id=1, start=3.0, end=8.5, text="hello world")
    assert c.duration == 5.5
