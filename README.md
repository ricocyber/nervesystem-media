# NerveSystem Media

Local-first media automation tools.

## Clipper Agent V1

A zero-paid-credit pipeline for turning long owned/licensed videos into reviewable Shorts:

```
source video
  -> faster-whisper
  -> sentence-aware candidate windows
  -> Ollama local ranking (or deterministic fallback)
  -> overlap dedupe
  -> face-aware 9:16 crop
  -> word-synced captions
  -> FFmpeg render
  -> review.json + MP4 clips
```

No OpenAI, Gemini, Anthropic, HeyGen, or other paid inference API is required.

### Current branch

Development: `build/clipper-v1`

### Requirements

- macOS, Linux, or Windows
- Python 3.11 or 3.12
- a full FFmpeg build with `ffmpeg` and `ffprobe` on PATH
- optional: Ollama for better local highlight ranking

On macOS:

```bash
brew install ffmpeg-full
brew install python@3.11
```

Optional local AI ranker:

```bash
brew install ollama
ollama pull qwen2.5:7b
```

### Install

```bash
git clone https://github.com/ricocyber/nervesystem-media.git
cd nervesystem-media
git checkout build/clipper-v1

python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

The first transcription run downloads the selected Whisper model weights once. There are no per-video AI credits.

### Check the machine

```bash
clipper-agent doctor
```

### Run on a local video

```bash
clipper-agent clip /path/to/video.mp4 --top 5
```

Run without Ollama:

```bash
clipper-agent clip /path/to/video.mp4 --top 5 --no-ollama
```

Score/select without rendering:

```bash
clipper-agent clip /path/to/video.mp4 --dry-run
```

### Authorized URL ingest

Only use video you own or are authorized to reuse:

```bash
clipper-agent clip "https://www.youtube.com/watch?v=..." --confirm-rights
```

### Output

Each run creates a job directory containing:

```
output/<job>/
  work/
    transcript.json
  clips/
    clip_01.ass
    clip_01.mp4
    ...
  review.json
```

`review.json` contains the exact timestamps, score, title, reason, crop strategy, and output path for each selected clip.

### Benchmark the selector

Create a human gold file using `benchmark/gold.example.json`, then:

```bash
clipper-agent benchmark output/<job>/review.json benchmark/my_gold.json
```

The benchmark reports top-k hit precision, recall, overlap, and mean model score.

### V1 boundary

V1 deliberately stops at review/export. It does **not** auto-publish yet. YouTube publishing comes after the clip-selection and reframing quality pass the benchmark gate.

### Legal / safety

Use footage you own or have authorization to process. This project does not include DRM circumvention or Content-ID-evasion features.

See:
- `docs/ARCHITECTURE.md`
- `docs/DECISION.md`

## License

MIT. Third-party packages and models retain their own licenses.
