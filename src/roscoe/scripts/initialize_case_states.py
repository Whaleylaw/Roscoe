#!/usr/bin/env python3
"""
Initialize Case States in Graph

This script creates IN_PHASE and LANDMARK_STATUS relationships for all existing
cases based on their current data (insurance claims, providers, liens, etc.).

The initial state is derived from what entities are already connected to each case.

Usage:
    python -m roscoe.scripts.initialize_case_states
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


async def run_query(query: str, params: dict = None):
    """Execute a Cypher query."""
    from roscoe.core.graphiti_client import run_cypher_query
    try:
        return await run_cypher_query(query, params or {})
    except Exception as e:
        print(f"  Error: {e}")
        return []


async def get_all_cases() -> List[Dict]:
    """Get all cases from the graph with their connected entities."""
    query = """
    MATCH (c:Entity {entity_type: 'Case'})
    OPTIONAL MATCH (c)-[:HAS_CLIENT]->(client:Entity {entity_type: 'Client'})
    OPTIONAL MATCH (c)-[:HAS_CLAIM]->(claim:Entity {entity_type: 'InsuranceClaim'})
    OPTIONAL MATCH (c)-[:TREATING_AT]->(provider:Entity {entity_type: 'MedicalProvider'})
    OPTIONAL MATCH (c)-[:HAS_LIEN]->(lien:Entity {entity_type: 'Lien'})
    WITH c, client,
         count(DISTINCT claim) as claim_count,
         count(DISTINCT provider) as provider_count,
         count(DISTINCT lien) as lien_count
    RETURN c.name as case_name,
           c.phase as current_phase_from_json,
           c.status as status,
           c.accident_date as accident_date,
           client.name as client_name,
           claim_count,
           provider_count,
           lien_count
    ORDER BY c.name
    """
    return await run_query(query)


async def get_case_claims(case_name: str) -> List[Dict]:
    """Get insurance claims for a case with their details."""
    query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[:HAS_CLAIM]->(claim:Entity {entity_type: 'InsuranceClaim'})
    OPTIONAL MATCH (claim)-[:INSURED_BY]->(insurer:Entity {entity_type: 'Insurer'})
    OPTIONAL MATCH (claim)-[:ASSIGNED_ADJUSTER]->(adjuster:Entity {entity_type: 'Adjuster'})
    RETURN claim.name as claim_name,
           claim.claim_type as claim_type,
           insurer.name as insurer_name,
           adjuster.name as adjuster_name
    """
    return await run_query(query, {"case_name": case_name})


async def set_case_phase(case_name: str, phase_name: str):
    """Create Case -[IN_PHASE]-> Phase relationship."""
    query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})
    MATCH (p:Entity {entity_type: 'Phase', name: $phase_name})
    MERGE (c)-[r:IN_PHASE]->(p)
    ON CREATE SET r.entered_at = $entered_at
    RETURN c.name, p.name
    """
    params = {
        "case_name": case_name,
        "phase_name": phase_name,
        "entered_at": datetime.now().isoformat()
    }
    return await run_query(query, params)


async def set_landmark_status(
    case_name: str, 
    landmark_id: str, 
    status: str,
    sub_steps: dict = None,
    notes: str = None
):
    """Create Case -[LANDMARK_STATUS]-> Landmark relationship."""
    sub_steps_json = json.dumps(sub_steps) if sub_steps else "{}"
    
    query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})
    MATCH (l:Entity {entity_type: 'Landmark', name: $landmark_id})
    MERGE (c)-[r:LANDMARK_STATUS]->(l)
    ON CREATE SET 
        r.status = $status,
        r.sub_steps = $sub_steps,
        r.notes = $notes,
        r.created_at = $created_at
    ON MATCH SET
        r.status = $status,
        r.sub_steps = $sub_steps,
        r.notes = $notes,
        r.updated_at = $updated_at
    RETURN c.name, l.name, r.status
    """
    
    now = datetime.now().isoformat()
    params = {
        "case_name": case_name,
        "landmark_id": landmark_id,
        "status": status,
        "sub_steps": sub_steps_json,
        "notes": notes,
        "created_at": now,
        "updated_at": now
    }
    
    return await run_query(query, params)


def determine_phase(case_data: dict) -> str:
    """
    Determine the current phase based on case data.
    
    This uses heuristics based on what entities exist:
    - No claims/providers → file_setup
    - Has claims and providers but no liens → treatment
    - Has liens → demand_in_progress or later
    """
    claim_count = case_data.get("claim_count", 0)
    provider_count = case_data.get("provider_count", 0)
    lien_count = case_data.get("lien_count", 0)
    status = (case_data.get("status") or "").lower()
    
    # Check if case is closed
    if status in ["closed", "archived", "settled"]:
        return "closed"
    
    # Use CURRENT phase names from regenerated phase_definitions.json
    existing_phase = case_data.get("current_phase_from_json")

    # Map OLD phase names to NEW names (for legacy data)
    phase_migration_map = {
        "demand_in_progress": "demand",
        "lien_phase": "lien"
    }

    # Current valid phase names (from workflows folder)
    valid_phases = [
        "onboarding", "file_setup", "treatment", "demand", "negotiation",
        "settlement", "lien", "litigation", "closed"
    ]

    # Migrate old phase name to new if needed
    if existing_phase and existing_phase in phase_migration_map:
        existing_phase = phase_migration_map[existing_phase]

    # Use existing phase if valid
    if existing_phase and existing_phase in valid_phases:
        return existing_phase

    # Heuristic-based determination (use CURRENT phase names from workflows folder)
    if claim_count == 0 and provider_count == 0:
        return "file_setup"
    elif claim_count > 0 and provider_count == 0:
        return "file_setup"  # Still setting up
    elif provider_count > 0 and lien_count == 0:
        return "treatment"  # Has providers, still treating
    elif lien_count > 0:
        return "demand"  # Has liens → demand phase (NEW NAME)
    else:
        return "treatment"  # Default to treatment if has providers


def determine_landmark_statuses(case_data: dict, claims: List[Dict]) -> Dict[str, Dict]:
    """
    Determine landmark statuses based on case data.
    
    Returns dict of {landmark_id: {status, sub_steps, notes}}
    """
    statuses = {}
    
    claim_count = case_data.get("claim_count", 0)
    provider_count = case_data.get("provider_count", 0)
    lien_count = case_data.get("lien_count", 0)
    client_name = case_data.get("client_name")
    
    # File Setup landmarks
    if client_name:
        statuses["full_intake_complete"] = {
            "status": "complete",
            "sub_steps": {
                "demographics_complete": True,
                "incident_details_complete": True,
                "injuries_documented": True
            },
            "notes": f"Client: {client_name}"
        }
    else:
        statuses["full_intake_complete"] = {
            "status": "incomplete",
            "sub_steps": {},
            "notes": "No client linked"
        }
    
    # Insurance claims setup
    if claim_count > 0:
        # Check claim types
        bi_claims = [c for c in claims if c.get("claim_type") in ["BI", "Bodily Injury"]]
        pip_claims = [c for c in claims if c.get("claim_type") in ["PIP", "Personal Injury Protection"]]
        
        sub_steps = {
            "bi_insurance_identified": len(bi_claims) > 0,
            "bi_lor_sent": len(bi_claims) > 0,  # Assume sent if claim exists
            "bi_claim_acknowledged": any(c.get("adjuster_name") for c in bi_claims),
            "pip_carrier_determined": len(pip_claims) > 0,
            "pip_claim_acknowledged": any(c.get("adjuster_name") for c in pip_claims),
        }
        
        # Determine overall status
        if all(sub_steps.values()):
            status = "complete"
        elif any(sub_steps.values()):
            status = "in_progress"
        else:
            status = "incomplete"
        
        statuses["insurance_claims_setup"] = {
            "status": status,
            "sub_steps": sub_steps,
            "notes": f"{len(bi_claims)} BI claims, {len(pip_claims)} PIP claims"
        }
    else:
        statuses["insurance_claims_setup"] = {
            "status": "not_started",
            "sub_steps": {},
            "notes": "No claims found"
        }
    
    # Providers setup
    if provider_count > 0:
        statuses["providers_setup"] = {
            "status": "complete",
            "sub_steps": {
                "providers_identified": True,
                "contact_verified": True
            },
            "notes": f"{provider_count} providers linked"
        }
    else:
        statuses["providers_setup"] = {
            "status": "not_started",
            "sub_steps": {},
            "notes": "No providers found"
        }
    
    # Treatment landmarks
    if provider_count > 0:
        statuses["providers_monitored"] = {
            "status": "in_progress",
            "sub_steps": {"active_providers_tracked": True},
            "notes": f"Monitoring {provider_count} providers"
        }
    
    # Demand landmarks
    if lien_count > 0:
        statuses["liens_identified"] = {
            "status": "complete",
            "sub_steps": {},
            "notes": f"{lien_count} liens identified"
        }
    
    return statuses


async def initialize_case_state(case_data: dict):
    """Initialize state for a single case."""
    case_name = case_data.get("case_name")
    
    # Get claim details
    claims = await get_case_claims(case_name)
    
    # Determine phase
    phase = determine_phase(case_data)
    
    # Set the phase relationship
    await set_case_phase(case_name, phase)
    
    # Determine and set landmark statuses
    landmark_statuses = determine_landmark_statuses(case_data, claims)
    
    for landmark_id, status_data in landmark_statuses.items():
        await set_landmark_status(
            case_name,
            landmark_id,
            status_data["status"],
            status_data.get("sub_steps"),
            status_data.get("notes")
        )
    
    return {
        "case_name": case_name,
        "phase": phase,
        "landmarks_set": len(landmark_statuses)
    }


async def initialize_all_case_states():
    """Main function to initialize state for all cases."""
    print("=" * 60)
    print("INITIALIZING CASE STATES IN GRAPH")
    print("=" * 60)
    
    # Get all cases
    print("\n=== Getting all cases ===")
    cases = await get_all_cases()
    print(f"  Found {len(cases)} cases")
    
    stats = {
        "cases_processed": 0,
        "phases_set": 0,
        "landmarks_set": 0,
        "by_phase": {}
    }
    
    # Process each case
    print("\n=== Processing cases ===")
    for case_data in cases:
        case_name = case_data.get("case_name")
        result = await initialize_case_state(case_data)
        
        phase = result["phase"]
        stats["cases_processed"] += 1
        stats["phases_set"] += 1
        stats["landmarks_set"] += result["landmarks_set"]
        stats["by_phase"][phase] = stats["by_phase"].get(phase, 0) + 1
        
        print(f"  [{stats['cases_processed']:3}] {case_name[:40]:<40} → {phase}")
    
    # Summary
    print("\n" + "=" * 60)
    print("INITIALIZATION COMPLETE")
    print("=" * 60)
    print(f"  Cases processed:    {stats['cases_processed']}")
    print(f"  Phases set:         {stats['phases_set']}")
    print(f"  Landmarks set:      {stats['landmarks_set']}")
    print("\nCases by phase:")
    for phase, count in sorted(stats["by_phase"].items()):
        print(f"  {phase}: {count}")
    print("=" * 60)
    
    # Verification
    print("\n=== Verification ===")
    verify_query = """
    MATCH (c:Entity {entity_type: 'Case'})-[:IN_PHASE]->(p:Entity {entity_type: 'Phase'})
    WITH p.name as phase, count(c) as case_count
    RETURN phase, case_count
    ORDER BY case_count DESC
    """
    results = await run_query(verify_query)
    print("\nCases with IN_PHASE relationship:")
    for r in results:
        print(f"  {r.get('phase')}: {r.get('case_count')} cases")
    
    # Sample case with landmarks
    sample_query = """
    MATCH (c:Entity {entity_type: 'Case'})-[:IN_PHASE]->(p:Entity {entity_type: 'Phase'})
    MATCH (c)-[ls:LANDMARK_STATUS]->(l:Entity {entity_type: 'Landmark'})
    WITH c.name as case_name, p.name as phase, 
         collect({landmark: l.name, status: ls.status}) as landmarks
    RETURN case_name, phase, landmarks
    LIMIT 3
    """
    sample_results = await run_query(sample_query)
    print("\nSample cases with landmarks:")
    for r in sample_results:
        print(f"  {r.get('case_name')}: phase={r.get('phase')}")
        for lm in r.get('landmarks', [])[:3]:
            print(f"    - {lm.get('landmark')}: {lm.get('status')}")
    
    return stats


def main():
    asyncio.run(initialize_all_case_states())


if __name__ == "__main__":
    main()
