from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class RepoDiscovery:
    name: str
    path: str
    exists: bool
    license_files: list[str]
    entrypoint_candidates: list[str]
    config_files: list[str]


ENTRYPOINT_NAMES = (
    "inference.py",
    "app.py",
    "main.py",
    "run.py",
    "generate.py",
    "server.py",
    "cli.py",
)
CONFIG_NAMES = (
    "pyproject.toml",
    "requirements.txt",
    "environment.yml",
    "package.json",
    "docker-compose.yml",
    "README.md",
)
LICENSE_NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")


def inspect_repo(name: str, base: Path | None = None) -> RepoDiscovery:
    root = (base or Path.home()) / name
    if not root.exists():
        return RepoDiscovery(name, str(root), False, [], [], [])

    licenses = [str(root / x) for x in LICENSE_NAMES if (root / x).exists()]
    configs = [str(root / x) for x in CONFIG_NAMES if (root / x).exists()]

    candidates: list[str] = []
    for filename in ENTRYPOINT_NAMES:
        for match in list(root.glob(filename)) + list(root.glob(f"**/{filename}"))[:20]:
            value = str(match)
            if value not in candidates:
                candidates.append(value)
            if len(candidates) >= 20:
                break

    return RepoDiscovery(
        name=name,
        path=str(root),
        exists=True,
        license_files=licenses,
        entrypoint_candidates=candidates,
        config_files=configs,
    )


def inspect_media_repos() -> list[RepoDiscovery]:
    return [
        inspect_repo(name)
        for name in ("ltx-video", "digital-human", "voicebox", "video-creator")
    ]


def write_discovery_report(path: Path) -> Path:
    path.write_text(
        json.dumps({"repos": [asdict(x) for x in inspect_media_repos()]}, indent=2),
        encoding="utf-8",
    )
    return path
