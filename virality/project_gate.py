from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

from .scorecard import ViralityScorecard, score_idea


@dataclass(frozen=True)
class ProjectGateResult:
    passed: bool
    idea_total: float
    idea_decision: str
    selected_title: str | None
    selected_thumbnail: str | None
    failures: list[str]


REQUIRED_PROJECT_FILES = (
    "brief.json",
    "idea_scorecard.json",
    "packaging_manifest.json",
    "script.md",
    "shot_list.json",
)


def evaluate_project_gate(project_dir: Path) -> ProjectGateResult:
    failures: list[str] = []

    for name in REQUIRED_PROJECT_FILES:
        if not (project_dir / name).exists():
            failures.append(f"missing:{name}")

    if failures:
        return ProjectGateResult(
            passed=False,
            idea_total=0.0,
            idea_decision="BLOCKED",
            selected_title=None,
            selected_thumbnail=None,
            failures=failures,
        )

    raw = json.loads((project_dir / "idea_scorecard.json").read_text(encoding="utf-8"))
    fields = {
        key: raw[key]
        for key in ViralityScorecard.__dataclass_fields__
    }
    result = score_idea(ViralityScorecard(**fields))

    packaging = json.loads(
        (project_dir / "packaging_manifest.json").read_text(encoding="utf-8")
    )

    selected_title = packaging.get("selected_title")
    selected_thumbnail = packaging.get("selected_thumbnail")

    if result.decision != "PRODUCE":
        failures.append(f"idea_decision:{result.decision}")
    if not selected_title:
        failures.append("missing:selected_title")
    if not selected_thumbnail:
        failures.append("missing:selected_thumbnail")
    if len(packaging.get("titles", [])) < 10:
        failures.append("packaging:requires_at_least_10_titles")
    if len(packaging.get("thumbnail_concepts", [])) < 3:
        failures.append("packaging:requires_at_least_3_thumbnail_concepts")

    return ProjectGateResult(
        passed=not failures,
        idea_total=result.total,
        idea_decision=result.decision,
        selected_title=selected_title,
        selected_thumbnail=selected_thumbnail,
        failures=failures,
    )


def save_project_gate(project_dir: Path, output: Path) -> Path:
    result = evaluate_project_gate(project_dir)
    output.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    return output
