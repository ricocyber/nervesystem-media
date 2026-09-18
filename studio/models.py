from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Literal

Format = Literal["short", "longform", "podcast", "commercial", "news", "film"]
Stage = Literal[
    "research", "virality", "packaging", "writing", "direction", "casting",
    "voice", "visuals", "vfx", "sound", "edit", "qc", "clip", "publish", "analytics"
]


@dataclass
class ProductionBrief:
    title: str
    objective: str
    format: Format
    target_audience: str
    duration_seconds: int
    topic: str
    funnel_stage: Literal["discovery", "trust", "conversion"] = "discovery"
    language: str = "en"
    realism: Literal["graphic", "hybrid", "photoreal"] = "hybrid"
    platforms: list[str] = field(default_factory=lambda: ["youtube"])
    constraints: list[str] = field(default_factory=list)


@dataclass
class WorkOrder:
    stage: Stage
    agent: str
    task: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    gate: str | None = None


@dataclass
class ProductionPlan:
    brief: ProductionBrief
    work_orders: list[WorkOrder]
    status: Literal["planned", "blocked", "ready_for_production"] = "planned"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
