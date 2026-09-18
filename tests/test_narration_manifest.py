import json
from pathlib import Path


def test_narration_lines_are_ordered_and_non_overlapping_enough():
    data = json.loads(
        Path("projects/nervesystem_authority_30s/dialogue_manifest.json").read_text()
    )
    starts = [float(x["start"]) for x in data["lines"]]
    assert starts == sorted(starts)
    assert all(float(x["end"]) > float(x["start"]) for x in data["lines"])
