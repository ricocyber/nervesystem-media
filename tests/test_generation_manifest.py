import json
from pathlib import Path


def test_generation_manifest_covers_all_shots():
    root = Path("projects/nervesystem_authority_30s")
    shots = json.loads((root / "shot_list.json").read_text())["shots"]
    gen = json.loads((root / "generation_manifest.json").read_text())["shots"]
    assert [x["id"] for x in shots] == [x["id"] for x in gen]


def test_dialogue_fits_runtime():
    root = Path("projects/nervesystem_authority_30s")
    dialogue = json.loads((root / "dialogue_manifest.json").read_text())["lines"]
    assert max(x["end"] for x in dialogue) <= 30.0
