# Build Decision Record

Date: 2026-09-17

## Evaluated references

The build decision considered several public open-source OpusClip-style projects, including:

- artbyjazi/autoclip — MIT
- mehbul/chopify — MIT
- PriyeshPandey2000/ai-video-clipper — MIT
- nzeronfourme/MovieShort-AI — MIT
- FujiwaraChoki/supoclip — AGPL-3.0
- ColinGPT9/clips-studio (Clips Kitty) — AGPL-3.0
- Anil-matcha/AI-Youtube-Shorts-Generator — MIT

## Decision

V1 is a clean implementation in this repository rather than a wholesale fork.

Reasons:
1. zero-paid-credit operation is a hard requirement;
2. Mac compatibility matters;
3. AGPL projects contain useful architecture ideas but are not copied into this MIT codebase;
4. several popular projects still require a remote LLM for highlight ranking;
5. clip quality needs to be benchmarked independently from repository popularity.

The architecture borrows common, non-proprietary pipeline ideas (transcribe -> rank -> reframe -> caption -> render), while the code in this repository is written independently.

## Benchmark gate

Before adding autonomous publishing, test the pipeline on the same owned/authorized source set and measure:
- top-k useful clip precision
- overlap with human gold moments
- caption timing
- face framing stability
- crash/retry rate
- processing time

Do not use GitHub stars as the deciding metric.
