from studio.executor import execute_project
from pathlib import Path


def test_first_project_has_required_artifacts():
    root = Path("projects/nervesystem_authority_30s")
    result = execute_project(root)
    assert "edit_render" in result["stages"]
    assert "3d_render" in result["stages"]
    assert "ai_video" in result["stages"]
