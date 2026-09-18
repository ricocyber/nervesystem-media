# Executable Adapters

## LTX-Video

The LTX adapter targets a local clone with:
- `inference.py`
- `configs/*.yaml`
- CLI flags for prompt, height, width, frame count, pipeline config and output.

Before every generation it runs the local inference help command and verifies the expected flags. It uses 8n+1 frame counts and 32-divisible output dimensions.

The adapter can optionally use a conditioning image/video path, which is the preferred route for character continuity once reference assets are created.

## Voicebox

The Voicebox adapter uses a local REST server.

Default:
`http://127.0.0.1:17493`

It probes the service first, then:
1. POSTs dialogue to `/generate`
2. copies the returned local `audio_path` when available, or
3. fetches `/audio/{generation_id}`

A profile ID is required so the same narrator/character voice remains stable between generations.

## Design rule

Adapters must fail loudly when:
- the local service/repository is unavailable,
- CLI/API shape does not match what we expect,
- the subprocess/API reports failure,
- no actual media artifact is produced.

A text response is never accepted as proof of completed rendering.
