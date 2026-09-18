# Local Model Router

The model dropdown should eventually become an **override**, not the normal operating mode.

NerveStudio asks Ollama which models are actually installed and routes work by task:

- coding -> coder-family models first
- research/reasoning -> reasoning-capable local family
- virality generation/writing -> creative local family
- packaging -> creative/visual-description family
- summarization -> fast local model

The router never claims an uninstalled model exists. If no preferred family is installed, it falls back to one model Ollama actually reports.

## Agent mapping

- coder / developer -> coding
- researcher -> research
- virality_generator -> creative
- virality_critic -> reasoning
- writer -> creative
- packaging_director -> packaging
- director / producer -> reasoning
- summarizer -> fast

Manual model selection remains useful for debugging and explicit overrides.
