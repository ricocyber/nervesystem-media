# Continuity System

Photoreal production fails quickly when the same person, room, robot, or prop changes between shots.

NerveStudio assigns stable continuity IDs in the generation manifest.

For the first commercial:

- `OPERATOR_01`: S01 establishes, S10 must match
- `CONTROL_ROOM_01`: S01 establishes, S10 must match
- `FACTORY_01`: S03 establishes, S08 must match
- `ROBOT_01`: S03 establishes, S08 must match

After the establishing shot is rendered, the continuity system extracts a clean reference frame and makes it available as conditioning media to later image-to-video generation.

This is preferable to regenerating every shot from text alone.

The continuity system does not claim identity consistency is guaranteed. It creates the conditioning path required to measure and improve it.
