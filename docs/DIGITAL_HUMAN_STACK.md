# Digital Human Stack

## Local-first decision

The existing NVIDIA `digital-human` clone is valuable as an architecture/reference blueprint, but it should not be treated as the first local Mac production engine merely because the repository is present.

For the current local studio, NerveStudio separates:

1. **Voice generation** — Voicebox local TTS
2. **Reference/idle actor video** — owned, licensed, Blender/LTX-generated, or otherwise authorized media
3. **Face/lip animation** — a local MuseTalk-Mac compatible service
4. **Environment/full-body/cutaways** — LTX Video and Blender
5. **Final edit** — FFmpeg/NerveStudio

## Why separate voice from lip sync

Some third-party digital-human projects bundle external voice providers. NerveStudio deliberately does not rely on those bundled paid speech paths. Voicebox generates the audio; the lip-sync engine receives finished audio.

## Expected MuseTalk-Mac API

Default local service:

`http://127.0.0.1:8000`

The adapter expects:
- `GET /health`
- `POST /warmup` with `video_b64` + `avatar_key`
- `POST /` with `video_b64` + `audio_b64` + `avatar_key`
- response containing `video_b64`

The adapter fails if the service is unavailable or no real video artifact is returned.

## Identity rule

Do not claim character consistency from text prompts alone.

Each recurring host/character should receive:
- stable character ID
- reference assets
- stable voice profile
- wardrobe/set continuity
- avatar cache key
- approved source rights/provenance

## Podcast target

For a two-host virtual podcast:
- Voicebox profile A -> Host A dialogue
- Voicebox profile B -> Host B dialogue
- MuseTalk avatar A -> Host A close-up
- MuseTalk avatar B -> Host B close-up
- LTX/Blender -> wide/establishing/cutaway shots
- editor -> speaker-aware camera switching
- Clipper -> Shorts after master approval
