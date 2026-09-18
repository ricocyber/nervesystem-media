from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandAdapterConfig:
    name: str
    enabled: bool
    cwd: str | None
    argv: list[str]


@dataclass(frozen=True)
class StudioLocalConfig:
    adapters: dict[str, CommandAdapterConfig]

    @classmethod
    def load(cls, path: Path) -> "StudioLocalConfig":
        raw = json.loads(path.read_text(encoding="utf-8"))
        adapters = {
            name: CommandAdapterConfig(
                name=name,
                enabled=bool(value.get("enabled", False)),
                cwd=value.get("cwd"),
                argv=list(value.get("argv", [])),
            )
            for name, value in raw.get("adapters", {}).items()
        }
        return cls(adapters=adapters)
