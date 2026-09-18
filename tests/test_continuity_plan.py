from pathlib import Path

from studio.continuity import build_continuity_plan


def test_first_project_continuity_dependencies():
    deps = build_continuity_plan(Path("projects/nervesystem_authority_30s"))
    triples = {(d.continuity_id, d.source_shot_id, d.dependent_shot_id) for d in deps}
    assert ("OPERATOR_01", "S01", "S10") in triples
    assert ("CONTROL_ROOM_01", "S01", "S10") in triples
    assert ("FACTORY_01", "S03", "S08") in triples
    assert ("ROBOT_01", "S03", "S08") in triples
