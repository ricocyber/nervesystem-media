from router.ollama_router import OllamaModelRouter


def test_family_match_prefers_coder():
    router = OllamaModelRouter()
    installed = ["qwen2.5:7b", "qwen2.5-coder:7b"]
    assert router._match(installed, "qwen2.5-coder") == "qwen2.5-coder:7b"


def test_exact_tag_wins():
    router = OllamaModelRouter()
    installed = ["qwen2.5:14b", "qwen2.5:7b"]
    assert router._match(installed, "qwen2.5:7b") == "qwen2.5:7b"


def test_unknown_agent_defaults_to_reasoning_mapping():
    assert "reasoning" in router_task_for_unknown()


def router_task_for_unknown():
    from router.ollama_router import AGENT_TASKS
    return AGENT_TASKS.get("unknown", "reasoning")
