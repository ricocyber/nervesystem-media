# Autonomous Podcast Pipeline

## Inputs

- researched episode topic
- Virality Director-approved package
- dialogue script
- stable character bible
- Voicebox profile for each host
- authorized/synthetic idle/reference video for each host
- local MuseTalk-Mac service

## Production

```
Dialogue
  -> split by speaker
  -> Voicebox local TTS per line
  -> place each line at its exact episode time
  -> 60-second host audio stem
  -> MuseTalk lip sync against host reference/idle video
  -> host A camera track
  -> host B camera track
  -> optional LTX/Blender wide track
  -> speaker-aware camera timeline
  -> editor
  -> QC
  -> master
  -> Clipper Agent
```

## Why full-length host tracks

Each host receives a full episode-length audio timeline, including silence while the other host speaks. This allows the lip-sync/video track to remain time-aligned with the master edit.

## Camera logic

Close-up defaults to the active speaker. A periodic wide shot resets visual context. Later versions can use:
- listener reaction cuts,
- semantic emphasis,
- hand-gesture/activity detection,
- retention-informed camera timing.

## Identity / rights

Hosts should be synthetic characters or based on media the operator is authorized to use. The system does not clone an unconsenting person's likeness or voice.
