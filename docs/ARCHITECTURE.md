# Clipper Agent V1 Architecture

## Goal

Turn long-form video into reviewable short-form clips with **no paid AI API required**.

```
source
  -> ingest
  -> faster-whisper word timestamps
  -> sentence-aware candidate builder
  -> local ranker (Ollama) OR deterministic fallback
  -> overlap dedupe / top-k
  -> per-clip face-aware fixed crop
  -> word-synced ASS captions
  -> FFmpeg render
  -> review.json + MP4s
```

## Why fixed crop in V1

A stable crop is intentionally preferred over constant camera panning. Jitter and panning across scene cuts are common failure modes in automatic vertical reframing. V1 samples each selected clip, finds the median dominant face position, and uses one stable crop.

A later active-speaker module can split a clip into shots and choose a separate fixed crop per shot.

## Provider boundaries

The pipeline is intentionally modular:

- **Ingest:** local path or authorized URL via yt-dlp
- **Transcription:** faster-whisper
- **Selection:** Ollama-compatible local LLM, with deterministic fallback
- **Framing:** OpenCV
- **Captions:** native ASS generation
- **Render:** FFmpeg

None of those interfaces require OpenAI, Anthropic, Gemini, HeyGen, or another paid inference service.

## Publishing

V1 deliberately stops at review/export. Direct YouTube publishing will be a separate module after clip quality is benchmarked.

## Rights

The tool is intended for footage the operator owns or has authorization to process. It does not include DRM circumvention or Content-ID evasion features.
