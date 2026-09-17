from __future__ import annotations

from pathlib import Path

from .models import Word


def _ts(seconds: float) -> str:
    seconds = max(0.0, seconds)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:05.2f}"


def _clean(text: str) -> str:
    return text.replace("\\", "").replace("{", "(").replace("}", ")")


def write_word_synced_ass(
    words: list[Word],
    clip_start: float,
    clip_end: float,
    path: Path,
    words_per_group: int = 5,
) -> Path:
    selected = [w for w in words if w.end >= clip_start and w.start <= clip_end]
    path.parent.mkdir(parents=True, exist_ok=True)

    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Caption,Arial,78,&H00FFFFFF,&H0000D7FF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,5,1,2,80,80,260,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events: list[str] = []
    for group_start in range(0, len(selected), words_per_group):
        group = selected[group_start : group_start + words_per_group]
        for active_index, active in enumerate(group):
            start = max(0.0, active.start - clip_start)
            end = max(start + 0.04, min(clip_end, active.end) - clip_start)
            display: list[str] = []
            for idx, item in enumerate(group):
                token = _clean(item.text)
                if idx == active_index:
                    token = r"{\c&H00D7FF&\fscx112\fscy112}" + token + r"{\c&HFFFFFF&\fscx100\fscy100}"
                display.append(token)
            line = " ".join(display)
            events.append(
                f"Dialogue: 0,{_ts(start)},{_ts(end)},Caption,,0,0,0,,{line}"
            )
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return path
