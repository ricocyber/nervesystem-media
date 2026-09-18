# NerveStudio Orchestrator V1

This closes the missing middle between the Virality Director and the Clipper.

## One production path

```
Research
→ Virality Director
→ Packaging
→ Writer
→ Director
→ Casting
→ Voice
→ Visuals (Blender / LTX / digital-human adapters)
→ VFX
→ Sound
→ Edit
→ QC
→ Clipper
→ Human publish gate
→ Analytics feedback
```

## Design rule

The orchestrator never claims a shot exists because an agent described it.

A stage is complete only when its expected artifact exists:
- script
- shot list
- character bible
- dialogue/audio
- rendered shots
- master edit
- QC report
- publication manifest
- performance snapshot

## Why this exists

The previous repository had:
- a working local clipper,
- a tested Virality Director,
- research/monetization doctrine,

but no single workflow tying production departments together.

V1 fixes that by creating deterministic work orders and adapter boundaries.

## Current adapter status

- FFmpeg: ready
- Clipper Agent: ready
- Blender: adapter defined; runtime integration still needs verification on the workstation
- LTX Video: adapter defined; exact installed repo entrypoint must be verified
- digital-human: adapter defined; exact installed repo entrypoint must be verified
- voicebox: adapter defined; exact installed repo entrypoint must be verified

This distinction is intentional. Presence on disk is not the same thing as a verified working production dependency.

## First target production

A 30-second photoreal NerveSystem commercial is the recommended integration test because it forces:
- characters,
- voice,
- camera/visual generation,
- VFX,
- sound,
- edit,
- QC,

without the complexity of a 20-minute episode.
