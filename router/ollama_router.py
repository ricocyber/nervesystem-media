from __future__ import annotations

from dataclasses import dataclass

import requests


class RouterError(RuntimeError):
    pass


@dataclass(frozen=True)
class RouteDecision:
    task_type: str
    model: str
    reason: str
    installed_models: list[str]


DEFAULT_PREFERENCES = {
    "coding": [
        "qwen2.5-coder",
        "qwen3-coder",
        "codellama",
        "deepseek-coder",
    ],
    "reasoning": [
        "qwen3",
        "deepseek-r1",
        "qwen2.5",
        "llama3.3",
        "gemma3",
    ],
    "creative": [
        "qwen3",
        "qwen2.5",
        "llama3.3",
        "gemma3",
    ],
    "fast": [
        "qwen2.5:7b",
        "qwen2.5",
        "llama3.2",
        "gemma3",
    ],
    "research": [
        "qwen3",
        "qwen2.5",
        "deepseek-r1",
        "llama3.3",
    ],
    "packaging": [
        "qwen3",
        "qwen2.5",
        "gemma3",
        "llama3.3",
    ],
}


AGENT_TASKS = {
    "coder": "coding",
    "developer": "coding",
    "researcher": "research",
    "virality_generator": "creative",
    "virality_critic": "reasoning",
    "writer": "creative",
    "packaging_director": "packaging",
    "director": "reasoning",
    "producer": "reasoning",
    "summarizer": "fast",
}


class OllamaModelRouter:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        preferences: dict[str, list[str]] | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.preferences = preferences or DEFAULT_PREFERENCES

    def installed_models(self) -> list[str]:
        try:
            r = requests.get(self.base_url + "/api/tags", timeout=3)
        except requests.RequestException as exc:
            raise RouterError(f"Ollama unavailable: {exc}") from exc
        if not r.ok:
            raise RouterError(f"Ollama returned HTTP {r.status_code}")
        return [
            str(item.get("name") or item.get("model"))
            for item in r.json().get("models", [])
            if item.get("name") or item.get("model")
        ]

    @staticmethod
    def _base_name(model: str) -> str:
        return model.lower().split(":", 1)[0]

    def _match(self, installed: list[str], preference: str) -> str | None:
        pref = preference.lower()
        # Exact tag first.
        for model in installed:
            if model.lower() == pref:
                return model

        # Then family/prefix match.
        for model in installed:
            name = model.lower()
            base = self._base_name(model)
            if name.startswith(pref + ":") or base == pref or base.startswith(pref):
                return model
        return None

    def route(self, task_type: str) -> RouteDecision:
        installed = self.installed_models()
        if not installed:
            raise RouterError("Ollama has no installed models")

        task = task_type.lower().strip()
        preferences = self.preferences.get(task) or self.preferences.get("reasoning", [])

        for preference in preferences:
            model = self._match(installed, preference)
            if model:
                return RouteDecision(
                    task_type=task,
                    model=model,
                    reason=f"first installed match for {task}: {preference}",
                    installed_models=installed,
                )

        # Honest fallback: use an installed model rather than inventing a tag.
        return RouteDecision(
            task_type=task,
            model=installed[0],
            reason=f"no preferred {task} family installed; using first available local model",
            installed_models=installed,
        )

    def route_agent(self, agent_role: str) -> RouteDecision:
        role = agent_role.lower().strip()
        task = AGENT_TASKS.get(role, "reasoning")
        decision = self.route(task)
        return RouteDecision(
            task_type=f"{role}->{decision.task_type}",
            model=decision.model,
            reason=decision.reason,
            installed_models=decision.installed_models,
        )
