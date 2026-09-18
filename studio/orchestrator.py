from __future__ import annotations

from .crew import CREW
from .models import ProductionBrief, ProductionPlan, WorkOrder


class StudioOrchestrator:
    """
    Deterministic V1 production planner.

    It does not pretend a model rendered a movie when an adapter is unavailable.
    Instead it creates explicit work orders and gates so each real tool can be
    connected/tested independently.
    """

    def plan(self, brief: ProductionBrief) -> ProductionPlan:
        orders: list[WorkOrder] = [
            WorkOrder(
                stage="research",
                agent="researcher",
                task=f"Build source-grounded research packet for: {brief.topic}",
                outputs=["research_packet.json"],
                tools=CREW["researcher"]["tools"],
            ),
            WorkOrder(
                stage="virality",
                agent="virality_director",
                task="Generate/rank idea variants and reject weak concepts before production.",
                inputs=["research_packet.json"],
                outputs=["idea_scorecard.json"],
                tools=CREW["virality_director"]["tools"],
                gate="Only strong/iterated concepts advance.",
            ),
            WorkOrder(
                stage="packaging",
                agent="packaging_director",
                task="Create 10 title variants and at least 3 thumbnail concepts.",
                inputs=["idea_scorecard.json"],
                outputs=["packaging_manifest.json"],
                tools=CREW["packaging_director"]["tools"],
                gate="Title/thumbnail package must be selected before script/render.",
            ),
            WorkOrder(
                stage="writing",
                agent="writer",
                task="Write spoken-language script with hook, stakes, open loops, and payoff.",
                inputs=["research_packet.json", "packaging_manifest.json"],
                outputs=["script.md"],
                tools=CREW["writer"]["tools"],
            ),
            WorkOrder(
                stage="direction",
                agent="director",
                task="Convert script into timed shot list, camera plan, performance notes, and continuity state.",
                inputs=["script.md"],
                outputs=["shot_list.json", "storyboard_manifest.json"],
                tools=CREW["director"]["tools"],
            ),
        ]

        if brief.realism in {"hybrid", "photoreal"}:
            orders.extend([
                WorkOrder(
                    stage="casting",
                    agent="casting",
                    task="Create/lock character bible, wardrobe, reference images, and continuity IDs.",
                    inputs=["shot_list.json"],
                    outputs=["character_bible.json"],
                    tools=CREW["casting"]["tools"],
                ),
                WorkOrder(
                    stage="voice",
                    agent="voice",
                    task="Assign/generate character and narrator dialogue with timing manifests.",
                    inputs=["script.md", "character_bible.json"],
                    outputs=["dialogue_manifest.json", "audio/"],
                    tools=CREW["voice"]["tools"],
                ),
                WorkOrder(
                    stage="visuals",
                    agent="visuals",
                    task="Render/generate each shot using the best available 3D/AI-video adapter.",
                    inputs=["shot_list.json", "character_bible.json", "dialogue_manifest.json"],
                    outputs=["shots/"],
                    tools=CREW["visuals"]["tools"],
                    gate="No shot is marked complete without an actual rendered media artifact.",
                ),
            ])
        else:
            orders.append(
                WorkOrder(
                    stage="visuals",
                    agent="visuals",
                    task="Generate motion-graphics/graphic scenes for each shot.",
                    inputs=["shot_list.json"],
                    outputs=["shots/"],
                    tools=["FFmpeg", "motion graphics"],
                )
            )

        orders.extend([
            WorkOrder(
                stage="vfx",
                agent="vfx",
                task="Composite screens, overlays, transitions, cleanup, and visual effects.",
                inputs=["shots/"],
                outputs=["shots_final/"],
                tools=CREW["vfx"]["tools"],
            ),
            WorkOrder(
                stage="sound",
                agent="sound",
                task="Mix dialogue, ambience, Foley, music, impacts, and loudness master.",
                inputs=["dialogue_manifest.json"],
                outputs=["mix.wav"],
                tools=CREW["sound"]["tools"],
            ),
            WorkOrder(
                stage="edit",
                agent="editor",
                task="Assemble master timeline with pacing matched to the selected package promise.",
                inputs=["shots_final/", "mix.wav"],
                outputs=["master.mp4", "edit_manifest.json"],
                tools=CREW["editor"]["tools"],
            ),
            WorkOrder(
                stage="qc",
                agent="qc",
                task="Validate continuity, visual defects, lip sync, captions, audio, aspect ratio, rights, and manifest completeness.",
                inputs=["master.mp4", "edit_manifest.json"],
                outputs=["qc_report.json"],
                tools=CREW["qc"]["tools"],
                gate="Publishing is blocked on QC failure.",
            ),
        ])

        if brief.format in {"longform", "podcast", "news", "film"}:
            orders.append(
                WorkOrder(
                    stage="clip",
                    agent="clipper",
                    task="Create ranked short-form derivatives from the approved master.",
                    inputs=["master.mp4"],
                    outputs=["shorts/"],
                    tools=CREW["clipper"]["tools"],
                )
            )

        orders.extend([
            WorkOrder(
                stage="publish",
                agent="producer",
                task="Prepare publication package. V1 remains human-approved before any external publish action.",
                inputs=["qc_report.json", "packaging_manifest.json"],
                outputs=["publication_manifest.json"],
                tools=["human approval gate"],
                gate="Human approval required.",
            ),
            WorkOrder(
                stage="analytics",
                agent="analytics",
                task="Collect authorized performance data and feed comparable results back into future idea/packaging decisions.",
                inputs=["publication_manifest.json"],
                outputs=["performance_snapshot.json"],
                tools=CREW["analytics"]["tools"],
            ),
        ])

        return ProductionPlan(
            brief=brief,
            work_orders=orders,
            status="ready_for_production",
            notes=[
                "V1 plans real tool handoffs; unavailable adapters remain explicit rather than simulated.",
                "Publishing stays approval-gated until performance and rights workflows are proven.",
            ],
        )
