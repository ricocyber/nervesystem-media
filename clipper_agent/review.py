from __future__ import annotations

import html
from pathlib import Path

from .models import ReviewManifest


def write_review_html(manifest: ReviewManifest, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    cards: list[str] = []

    rendered_by_id = {item.candidate.candidate_id: item for item in manifest.rendered}
    for rank, candidate in enumerate(manifest.candidates, start=1):
        rendered = rendered_by_id.get(candidate.candidate_id)
        media = ""
        if rendered:
            rel = Path(rendered.output_path).resolve().relative_to(path.parent.resolve())
            media = f'<video controls preload="metadata" src="{html.escape(str(rel))}"></video>'
        cards.append(
            f"""
<section class="card" data-id="{candidate.candidate_id}">
  <div class="row">
    <span class="rank">#{rank}</span>
    <span class="score">{candidate.score:.1f}/10</span>
    <span class="time">{candidate.start:.1f}s → {candidate.end:.1f}s</span>
  </div>
  <h2>{html.escape(candidate.title or "Untitled clip")}</h2>
  <p class="reason">{html.escape(candidate.reason)}</p>
  {media}
  <details><summary>Transcript</summary><p>{html.escape(candidate.text)}</p></details>
  <div class="actions">
    <button onclick="setDecision('{candidate.candidate_id}','approved')">Approve</button>
    <button class="reject" onclick="setDecision('{candidate.candidate_id}','rejected')">Reject</button>
    <span id="status-{candidate.candidate_id}" class="status"></span>
  </div>
</section>
"""
        )

    document = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Clipper Agent Review</title>
<style>
:root {{ color-scheme: dark; font-family: Inter, system-ui, sans-serif; }}
body {{ margin:0; background:#0b0d10; color:#f2f4f8; }}
main {{ max-width:1000px; margin:0 auto; padding:32px 18px 80px; }}
header {{ margin-bottom:28px; }}
.muted,.reason,.time {{ color:#a8b0bb; }}
.grid {{ display:grid; gap:20px; }}
.card {{ background:#141820; border:1px solid #29303a; border-radius:16px; padding:18px; }}
.row {{ display:flex; gap:12px; align-items:center; flex-wrap:wrap; }}
.rank {{ font-weight:800; }}
.score {{ background:#233044; padding:5px 9px; border-radius:999px; }}
video {{ width:100%; max-height:70vh; border-radius:12px; background:#000; margin-top:10px; }}
button {{ border:0; border-radius:10px; padding:10px 16px; font-weight:700; cursor:pointer; }}
.reject {{ margin-left:8px; background:#4a2024; color:white; }}
.actions {{ margin-top:14px; }}
.status {{ margin-left:12px; font-weight:700; }}
details {{ margin-top:12px; }}
</style>
</head>
<body>
<main>
<header>
<h1>Clipper Agent Review</h1>
<p class="muted">{html.escape(manifest.source)}</p>
<p class="muted">Ranker: {html.escape(manifest.scorer)} · Whisper: {html.escape(manifest.model)}</p>
</header>
<div class="grid">{''.join(cards)}</div>
</main>
<script>
function key(id) {{ return 'clipper-decision-' + id; }}
function paint(id) {{
  const value = localStorage.getItem(key(id)) || '';
  const el = document.getElementById('status-' + id);
  if (el) el.textContent = value ? value.toUpperCase() : '';
}}
function setDecision(id, value) {{
  localStorage.setItem(key(id), value);
  paint(id);
}}
document.querySelectorAll('[data-id]').forEach(el => paint(el.dataset.id));
</script>
</body>
</html>"""
    path.write_text(document, encoding="utf-8")
    return path
