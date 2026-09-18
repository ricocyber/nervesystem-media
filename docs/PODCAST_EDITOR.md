# Podcast Multi-Camera Editor

The V1 editor consumes:
- Maya full-length lip-synced video,
- Axel full-length lip-synced video,
- Maya aligned voice stem,
- Axel aligned voice stem.

Camera mapping:
- CAM_A: two-host wide, built from both host video tracks
- CAM_B: Maya close-up
- CAM_C: Axel close-up

The speaker-aware timeline controls cuts. Both audio stems are mixed separately from the host video files so camera cuts never alter dialogue timing.

V1 uses a side-by-side synthetic wide as a reliable fallback. A future Blender/LTX studio-wide render can replace CAM_A without changing the dialogue or close-up tracks.
