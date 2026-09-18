from pathlib import Path

from virality.project_gate import evaluate_project_gate


def test_first_project_passes_virality_and_packaging_gate():
    result = evaluate_project_gate(Path("projects/nervesystem_authority_30s"))
    assert result.passed is True
    assert result.idea_decision == "PRODUCE"
    assert result.idea_total >= 85
    assert result.selected_title
    assert result.selected_thumbnail
