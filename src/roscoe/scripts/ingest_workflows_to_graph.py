"""
Ingest workflow definitions from GCS into knowledge graph.

Reads from: /mnt/workspace/workflows/
Creates: Phase, Landmark, WorkflowDef, WorkflowStep entities in graph

Uses Direct Cypher (NOT Graphiti) - workflow structure is 100% structured.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime


async def ingest_all_workflows(workflows_dir: str = "/mnt/workspace/workflows"):
    """
    Ingest complete workflow structure into graph.

    Creates all entities with group_id='__workflow_definitions__'
    """
    from roscoe.core.graphiti_client import run_cypher_query

    workflows_path = Path(workflows_dir)

    print("🔧 Starting workflow ingestion...")
    print(f"📁 Source: {workflows_path}")

    # Step 1: Ingest phases
    phases_file = workflows_path / "phases.json"
    if phases_file.exists():
        with open(phases_file) as f:
            phases = json.load(f)

        for phase in phases:
            await run_cypher_query('''
                CREATE (p:Entity {
                    name: $name,
                    entity_type: 'Phase',
                    display_name: $display_name,
                    description: $description,
                    order: $order,
                    track: $track,
                    next_phase: $next_phase,
                    group_id: '__workflow_definitions__',
                    created_at: $now
                })
            ''', {
                "name": phase["name"],
                "display_name": phase.get("display_name", phase["name"]),
                "description": phase.get("description", ""),
                "order": phase.get("order", 0),
                "track": phase.get("track", "pre_litigation"),
                "next_phase": phase.get("next_phase"),
                "now": datetime.now().isoformat()
            })

        # Create NEXT_PHASE relationships
        for phase in phases:
            if phase.get("next_phase"):
                await run_cypher_query('''
                    MATCH (p1:Entity {entity_type: 'Phase', name: $current})
                    MATCH (p2:Entity {entity_type: 'Phase', name: $next})
                    CREATE (p1)-[:NEXT_PHASE {is_default: true}]->(p2)
                ''', {"current": phase["name"], "next": phase["next_phase"]})

        print(f"✅ Loaded {len(phases)} phases")

    # Step 2: Ingest landmarks for each phase
    total_landmarks = 0
    for phase_dir in workflows_path.iterdir():
        if not phase_dir.is_dir():
            continue

        landmarks_file = phase_dir / "landmarks.json"
        if landmarks_file.exists():
            with open(landmarks_file) as f:
                landmarks = json.load(f)

            for lm in landmarks:
                await run_cypher_query('''
                    CREATE (l:Entity {
                        name: $landmark_id,
                        entity_type: 'Landmark',
                        landmark_id: $landmark_id,
                        display_name: $display_name,
                        phase: $phase,
                        description: $description,
                        landmark_type: $landmark_type,
                        is_hard_blocker: $is_hard_blocker,
                        can_override: $can_override,
                        verification_method: $verification_method,
                        verification_entities: $verification_entities,
                        verification_relationships: $verification_relationships,
                        verification_query: $verification_query,
                        auto_verify: $auto_verify,
                        sub_steps: $sub_steps,
                        parent_landmark: $parent_landmark,
                        group_id: '__workflow_definitions__',
                        created_at: $now
                    })
                ''', {
                    "landmark_id": lm["landmark_id"],
                    "display_name": lm.get("display_name", lm["landmark_id"]),
                    "phase": lm["phase"],
                    "description": lm.get("description", ""),
                    "landmark_type": lm.get("landmark_type", "entity"),
                    "is_hard_blocker": lm.get("is_hard_blocker", False),
                    "can_override": lm.get("can_override", False),
                    "verification_method": lm.get("verification_method", "manual"),
                    "verification_entities": json.dumps(lm.get("verification_entities", [])),
                    "verification_relationships": json.dumps(lm.get("verification_relationships", [])),
                    "verification_query": lm.get("verification_query"),
                    "auto_verify": lm.get("auto_verify", False),
                    "sub_steps": json.dumps(lm.get("sub_steps", {})),
                    "parent_landmark": lm.get("parent_landmark"),
                    "now": datetime.now().isoformat()
                })

                # Link to phase
                await run_cypher_query('''
                    MATCH (phase:Entity {entity_type: 'Phase', name: $phase})
                    MATCH (lm:Entity {entity_type: 'Landmark', landmark_id: $landmark_id})
                    CREATE (phase)-[:HAS_LANDMARK]->(lm)
                ''', {"phase": lm["phase"], "landmark_id": lm["landmark_id"]})

                total_landmarks += 1

    print(f"✅ Loaded {total_landmarks} landmarks")

    print("✅ Workflow ingestion complete!")
    return {"phases": len(phases) if phases_file.exists() else 0, "landmarks": total_landmarks}


if __name__ == "__main__":
    asyncio.run(ingest_all_workflows())
