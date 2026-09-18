from __future__ import annotations

CREW = {
    "producer": {
        "role": "Owns the production plan, budget, gates, and handoffs.",
        "tools": ["Virality Director", "workflow router", "project manifest"],
    },
    "researcher": {
        "role": "Collects source-grounded facts, trends, and audience evidence.",
        "tools": ["web/research", "RAG", "YouTube intel"],
    },
    "virality_director": {
        "role": "Kills weak ideas before production and forces packaging discipline.",
        "tools": ["virality.scorecard"],
    },
    "packaging_director": {
        "role": "Creates title and thumbnail variants before production starts.",
        "tools": ["image generation", "thumbnail templates"],
    },
    "writer": {
        "role": "Writes spoken-language scripts with hooks, stakes, and open loops.",
        "tools": ["local LLM/router"],
    },
    "director": {
        "role": "Breaks scripts into shots, scenes, performances, and camera intent.",
        "tools": ["shot planner", "storyboard"],
    },
    "casting": {
        "role": "Maintains character identity, wardrobe, look, and continuity.",
        "tools": ["digital-human", "character references"],
    },
    "voice": {
        "role": "Generates/assigns voices and dialogue timing.",
        "tools": ["voicebox", "local TTS", "nemotron-voice-agent"],
    },
    "visuals": {
        "role": "Creates 3D/AI footage, sets, characters, and camera renders.",
        "tools": ["Blender", "LTX Video", "digital-human", "ComfyUI-compatible adapters"],
    },
    "vfx": {
        "role": "Handles compositing, overlays, particles, screens, and cleanup.",
        "tools": ["Blender compositor", "FFmpeg", "motion graphics"],
    },
    "sound": {
        "role": "Builds dialogue mix, music, Foley, and loudness master.",
        "tools": ["voicebox", "audio tools", "FFmpeg"],
    },
    "editor": {
        "role": "Builds the master timeline and pacing.",
        "tools": ["FFmpeg", "video-creator", "hyperframes/remotion"],
    },
    "qc": {
        "role": "Checks continuity, lip sync, hands/faces, captions, rights, and output specs.",
        "tools": ["visual QA", "audio QA", "manifest validation"],
    },
    "clipper": {
        "role": "Repurposes long-form output into ranked short-form clips.",
        "tools": ["clipper_agent"],
    },
    "analytics": {
        "role": "Measures packaging, retention, conversion, economics, and feeds learning back.",
        "tools": ["YouTube Analytics", "performance lineage database"],
    },
}
