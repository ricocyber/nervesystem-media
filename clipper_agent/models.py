from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class Word(BaseModel):
    text: str
    start: float = Field(ge=0)
    end: float = Field(ge=0)


class Transcript(BaseModel):
    source: str
    language: str | None = None
    duration: float = 0
    words: list[Word] = Field(default_factory=list)
    text: str = ""


class Candidate(BaseModel):
    candidate_id: int
    start: float
    end: float
    text: str
    score: float = 0
    title: str = ""
    reason: str = ""
    scorer: Literal["heuristic", "ollama"] = "heuristic"

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


class CropRect(BaseModel):
    x: int
    y: int
    width: int
    height: int
    strategy: str = "center"


class RenderedClip(BaseModel):
    candidate: Candidate
    output_path: str
    caption_path: str
    crop: CropRect


class ReviewManifest(BaseModel):
    source: str
    generated_at: str
    model: str
    scorer: str
    candidates: list[Candidate]
    rendered: list[RenderedClip] = Field(default_factory=list)

    def save(self, path: Path) -> None:
        path.write_text(self.model_dump_json(indent=2), encoding="utf-8")
