#!/usr/bin/env python3
"""
Initialize Workflow State for All Cases (Phase 0 Start)

USER DECISION: All 110 cases start at Phase 0 (onboarding).
User will manually advance cases through conversation with the agent.

Creates:
- IN_PHASE relationships (all cases → Phase:onboarding)
- LandmarkStatus nodes for every case × landmark combination
- All statuses start as 'not_started', version=1

Usage:
    python -m roscoe.scripts.initialize_case_states_NEW
    python -m roscoe.scripts.initialize_case_states_NEW --dry-run
"""

import asyncio
import hashlib
import uuid as uuid_lib
from datetime import datetime
import argparse


async def initialize_case_state(case_name: str, dry_run: bool = False) -> int:
    """
    Initialize workflow state for a single case.

    Sets case to Phase 0 (onboarding) and creates LandmarkStatus nodes
    for all landmarks (status='not_started').

    Args:
        case_name: Case name
        dry_run: If True, show what would be done without making changes

    Returns:
        Number of LandmarkStatus nodes created
    """
    from roscoe.core.graphiti_client import run_cypher_query

    now = datetime.now().isoformat()

    if dry_run:
        # Just count landmarks
        landmarks_query = """
        MATCH (l:Entity {entity_type: 'Landmark'})
        WHERE l.group_id = '__workflow_definitions__'
        RETURN count(l) as count
        """
        result = await run_cypher_query(landmarks_query, {})
        count = result[0]['count'] if result else 68
        print(f"  [DRY RUN] {case_name}: Would set to Phase 0, create {count} LandmarkStatus nodes")
        return count

    # Step 1: Set IN_PHASE to onboarding (Phase 0)
    phase_query = """
    MATCH (case:Case {name: $case_name})
    MATCH (phase:Phase {name: 'onboarding'})
    MERGE (case)-[r:IN_PHASE]->(phase)
    SET r.entered_at = $now
    RETURN case.name
    """
    await run_cypher_query(phase_query, {
        "case_name": case_name,
        "now": now
    })

    # Step 2: Get all landmarks (use label, not entity_type)
    landmarks_query = """
    MATCH (l:Landmark)
    WHERE l.group_id = '__workflow_definitions__'
    RETURN l.landmark_id as landmark_id, l.name as name, l.phase as phase, l.subphase as subphase
    ORDER BY l.phase, l.order
    """
    landmarks = await run_cypher_query(landmarks_query, {})

    # Step 3: Create LandmarkStatus node for each landmark
    created_count = 0

    for landmark in landmarks:
        landmark_id = landmark['landmark_id']

        # Generate deterministic UUID
        status_key = f"{case_name}_{landmark_id}"
        status_hash = hashlib.md5(status_key.encode()).hexdigest()
        status_uuid = str(uuid_lib.UUID(status_hash))

        status_query = """
        MATCH (case:Case {name: $case_name})
        MATCH (l:Landmark {landmark_id: $landmark_id})

        // Merge LandmarkStatus node (idempotent - safe to run multiple times)
        MERGE (ls:LandmarkStatus {uuid: $uuid})
        ON CREATE SET
          ls.group_id = 'roscoe_graph',
          ls.case_name = $case_name,
          ls.landmark_id = $landmark_id,
          ls.status = 'not_started',
          ls.sub_steps = null,
          ls.notes = null,
          ls.completed_at = null,
          ls.created_at = $now,
          ls.updated_at = $now,
          ls.updated_by = 'system',
          ls.version = 1,
          ls.archived_at = null

        // Link Case → LandmarkStatus → Landmark
        MERGE (case)-[:HAS_STATUS]->(ls)
        MERGE (ls)-[:FOR_LANDMARK]->(l)

        RETURN ls.uuid
        """

        await run_cypher_query(status_query, {
            "case_name": case_name,
            "landmark_id": landmark_id,
            "uuid": status_uuid,
            "now": now
        })

        created_count += 1

    return created_count


async def initialize_all_cases(dry_run: bool = False):
    """Initialize workflow state for all cases."""
    from roscoe.core.graphiti_client import run_cypher_query

    print("=" * 70)
    print("INITIALIZING CASE WORKFLOW STATES")
    print("=" * 70)
    print("Strategy: ALL cases start at Phase 0 (onboarding)")
    print("User will manually advance cases via conversation with agent")
    print()

    # Get all cases (use label, not entity_type)
    cases_query = """
    MATCH (c:Case)
    RETURN c.name as name
    ORDER BY c.name
    """
    cases = await run_cypher_query(cases_query, {})

    if dry_run:
        print(f"[DRY RUN] Would initialize {len(cases)} cases")
        print()
    else:
        print(f"Initializing {len(cases)} cases...")
        print()

    total_status_nodes = 0

    for i, case in enumerate(cases, 1):
        case_name = case['name']
        status_count = await initialize_case_state(case_name, dry_run)
        total_status_nodes += status_count

        if i % 10 == 0:
            print(f"  Progress: {i}/{len(cases)} cases initialized...")

    print()
    print("=" * 70)
    print("✅ INITIALIZATION COMPLETE")
    print("=" * 70)
    print(f"Total cases: {len(cases)}")
    print(f"All cases set to Phase: onboarding")
    print(f"LandmarkStatus nodes created: {total_status_nodes}")
    print(f"Average landmarks per case: {total_status_nodes / len(cases):.0f}" if len(cases) > 0 else "")
    print()
    print("Verification:")
    print("  1. Check: MATCH (c)-[:IN_PHASE]->(p) RETURN p.name, count(c)")
    print("  2. Check: MATCH (ls:Entity {entity_type: 'LandmarkStatus'}) RETURN count(ls)")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Initialize workflow state for all cases')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    args = parser.parse_args()

    asyncio.run(initialize_all_cases(args.dry_run))


if __name__ == "__main__":
    main()
