"""
Direct Cypher Graph Management

Provides deterministic graph operations for structured data.
Use this for: Cases, Clients, Claims, Providers, Workflow State
DO NOT use for: Notes, unstructured updates (use graphiti_client.py)
"""

from typing import Optional, Dict, List
from datetime import datetime, date


async def create_case(
    client_name: str,
    accident_date: str,
    case_type: str = "MVA",
    sol_date: Optional[str] = None
) -> str:
    """
    Create new case with Case and Client entities.

    Uses Direct Cypher for deterministic entity creation.

    Args:
        client_name: Client full name
        accident_date: Date of accident (YYYY-MM-DD)
        case_type: MVA, Premise, WC, Med-Mal, Dog-Bite, Slip-Fall
        sol_date: Optional SOL deadline (computed if not provided)

    Returns:
        case_name: Generated case folder name
    """
    from roscoe.core.graphiti_client import run_cypher_query, CASE_DATA_GROUP_ID

    # Generate case name
    case_name = f"{client_name.replace(' ', '-')}-{case_type}-{accident_date}"

    # Create Case entity
    await run_cypher_query('''
        CREATE (c:Entity {
            name: $case_name,
            entity_type: 'Case',
            case_type: $case_type,
            accident_date: $accident_date,
            sol_date: $sol_date,
            group_id: $group_id,
            created_at: $now
        })
    ''', {
        "case_name": case_name,
        "case_type": case_type,
        "accident_date": accident_date,
        "sol_date": sol_date,
        "group_id": CASE_DATA_GROUP_ID,
        "now": datetime.now().isoformat()
    })

    # Create or find Client entity
    await run_cypher_query('''
        MERGE (client:Entity {
            name: $client_name,
            entity_type: 'Client',
            group_id: $group_id
        })
    ''', {
        "client_name": client_name,
        "group_id": CASE_DATA_GROUP_ID
    })

    # Create HAS_CLIENT relationship
    await run_cypher_query('''
        MATCH (case:Entity {entity_type: 'Case', name: $case_name})
        MATCH (client:Entity {entity_type: 'Client', name: $client_name})
        CREATE (case)-[:HAS_CLIENT]->(client)
        CREATE (client)-[:PLAINTIFF_IN]->(case)
    ''', {"case_name": case_name, "client_name": client_name})

    return case_name


async def create_biclaim(
    case_name: str,
    claim_number: str,
    insurer_name: str,
    adjuster_name: Optional[str] = None,
    policy_limit: Optional[float] = None,
    coverage_confirmation: Optional[str] = None,
    adjuster_email: Optional[str] = None,
    adjuster_phone: Optional[str] = None
) -> str:
    """
    Create new BI claim with insurer and optional adjuster relationships.

    Uses Direct Cypher for deterministic entity creation.

    Args:
        case_name: Case entity name
        claim_number: Insurance claim number
        insurer_name: Insurance company name
        adjuster_name: Optional adjuster name
        policy_limit: Optional policy limit amount
        coverage_confirmation: Optional coverage status
        adjuster_email: Optional adjuster email
        adjuster_phone: Optional adjuster phone

    Returns:
        claim_name: Generated claim identifier
    """
    from roscoe.core.graphiti_client import run_cypher_query, CASE_DATA_GROUP_ID

    # Generate claim name
    claim_name = f"BIClaim-{claim_number}"

    # Create BIClaim entity
    await run_cypher_query('''
        CREATE (claim:Entity {
            name: $claim_name,
            entity_type: 'BIClaim',
            claim_number: $claim_number,
            insurer_name: $insurer_name,
            policy_limit: $policy_limit,
            coverage_confirmation: $coverage_confirmation,
            group_id: $group_id,
            created_at: $now
        })
    ''', {
        "claim_name": claim_name,
        "claim_number": claim_number,
        "insurer_name": insurer_name,
        "policy_limit": policy_limit,
        "coverage_confirmation": coverage_confirmation,
        "group_id": CASE_DATA_GROUP_ID,
        "now": datetime.now().isoformat()
    })

    # MERGE insurer entity
    await run_cypher_query('''
        MERGE (insurer:Entity {
            name: $insurer_name,
            entity_type: 'Insurer',
            group_id: $group_id
        })
    ''', {
        "insurer_name": insurer_name,
        "group_id": CASE_DATA_GROUP_ID
    })

    # Create HAS_CLAIM relationship (Case -> Claim)
    await run_cypher_query('''
        MATCH (case:Entity {entity_type: 'Case', name: $case_name})
        MATCH (claim:Entity {entity_type: 'BIClaim', claim_number: $claim_number})
        CREATE (case)-[:HAS_CLAIM]->(claim)
    ''', {"case_name": case_name, "claim_number": claim_number})

    # Create INSURED_BY relationship (Claim -> Insurer)
    await run_cypher_query('''
        MATCH (claim:Entity {entity_type: 'BIClaim', claim_number: $claim_number})
        MATCH (insurer:Entity {entity_type: 'Insurer', name: $insurer_name})
        CREATE (claim)-[:INSURED_BY]->(insurer)
    ''', {"claim_number": claim_number, "insurer_name": insurer_name})

    # If adjuster provided, create adjuster entity and relationships
    if adjuster_name:
        await run_cypher_query('''
            MERGE (adjuster:Entity {
                name: $adjuster_name,
                entity_type: 'Adjuster',
                group_id: $group_id
            })
            ON CREATE SET
                adjuster.email = $adjuster_email,
                adjuster.phone = $adjuster_phone
        ''', {
            "adjuster_name": adjuster_name,
            "adjuster_email": adjuster_email,
            "adjuster_phone": adjuster_phone,
            "group_id": CASE_DATA_GROUP_ID
        })

        # Create ASSIGNED_ADJUSTER relationship (Claim -> Adjuster)
        await run_cypher_query('''
            MATCH (claim:Entity {entity_type: 'BIClaim', claim_number: $claim_number})
            MATCH (adjuster:Entity {entity_type: 'Adjuster', name: $adjuster_name})
            CREATE (claim)-[:ASSIGNED_ADJUSTER]->(adjuster)
        ''', {"claim_number": claim_number, "adjuster_name": adjuster_name})

        # Create HANDLES_INSURANCE_CLAIM relationship (Adjuster -> Claim)
        await run_cypher_query('''
            MATCH (adjuster:Entity {entity_type: 'Adjuster', name: $adjuster_name})
            MATCH (claim:Entity {entity_type: 'BIClaim', claim_number: $claim_number})
            CREATE (adjuster)-[:HANDLES_INSURANCE_CLAIM]->(claim)
        ''', {"adjuster_name": adjuster_name, "claim_number": claim_number})

    return claim_name


async def create_pipclaim(
    case_name: str,
    claim_number: str,
    insurer_name: str,
    policy_limit: Optional[float] = None,
    exhausted: bool = False,
    amount_paid: Optional[float] = None
) -> str:
    """
    Create new PIP claim with insurer relationship.

    Uses Direct Cypher for deterministic entity creation.

    Args:
        case_name: Case entity name
        claim_number: PIP claim number
        insurer_name: Insurance company name
        policy_limit: Optional policy limit
        exhausted: Whether PIP benefits exhausted
        amount_paid: Optional amount paid so far

    Returns:
        claim_name: Generated claim identifier
    """
    from roscoe.core.graphiti_client import run_cypher_query, CASE_DATA_GROUP_ID

    # Generate claim name
    claim_name = f"PIPClaim-{claim_number}"

    # Create PIPClaim entity
    await run_cypher_query('''
        CREATE (claim:Entity {
            name: $claim_name,
            entity_type: 'PIPClaim',
            claim_number: $claim_number,
            insurer_name: $insurer_name,
            policy_limit: $policy_limit,
            exhausted: $exhausted,
            amount_paid: $amount_paid,
            group_id: $group_id,
            created_at: $now
        })
    ''', {
        "claim_name": claim_name,
        "claim_number": claim_number,
        "insurer_name": insurer_name,
        "policy_limit": policy_limit,
        "exhausted": exhausted,
        "amount_paid": amount_paid,
        "group_id": CASE_DATA_GROUP_ID,
        "now": datetime.now().isoformat()
    })

    # MERGE insurer entity
    await run_cypher_query('''
        MERGE (insurer:Entity {
            name: $insurer_name,
            entity_type: 'Insurer',
            group_id: $group_id
        })
    ''', {
        "insurer_name": insurer_name,
        "group_id": CASE_DATA_GROUP_ID
    })

    # Create HAS_CLAIM relationship (Case -> Claim)
    await run_cypher_query('''
        MATCH (case:Entity {entity_type: 'Case', name: $case_name})
        MATCH (claim:Entity {entity_type: 'PIPClaim', claim_number: $claim_number})
        CREATE (case)-[:HAS_CLAIM]->(claim)
    ''', {"case_name": case_name, "claim_number": claim_number})

    # Create INSURED_BY relationship (Claim -> Insurer)
    await run_cypher_query('''
        MATCH (claim:Entity {entity_type: 'PIPClaim', claim_number: $claim_number})
        MATCH (insurer:Entity {entity_type: 'Insurer', name: $insurer_name})
        CREATE (claim)-[:INSURED_BY]->(insurer)
    ''', {"claim_number": claim_number, "insurer_name": insurer_name})

    return claim_name


async def set_case_phase(
    case_name: str,
    phase_name: str,
    previous_phase: Optional[str] = None
) -> bool:
    """
    Set case to a specific phase.

    Creates or updates IN_PHASE relationship.

    Args:
        case_name: Case identifier
        phase_name: Target phase (file_setup, treatment, demand, etc.)
        previous_phase: Optional previous phase name

    Returns:
        True if successful
    """
    from roscoe.core.graphiti_client import run_cypher_query

    # Remove existing IN_PHASE relationship
    await run_cypher_query('''
        MATCH (case:Entity {name: $case_name})-[r:IN_PHASE]->()
        DELETE r
    ''', {"case_name": case_name})

    # Create new IN_PHASE relationship
    result = await run_cypher_query('''
        MATCH (case:Entity {name: $case_name})
        MATCH (phase:Entity {entity_type: 'Phase', name: $phase_name})
        CREATE (case)-[r:IN_PHASE]->(phase)
        SET r.entered_at = $now,
            r.previous_phase = $previous_phase
        RETURN case.name, phase.name
    ''', {
        "case_name": case_name,
        "phase_name": phase_name,
        "previous_phase": previous_phase,
        "now": datetime.now().isoformat()
    })

    return len(result) > 0


async def update_landmark_status(
    case_name: str,
    landmark_id: str,
    status: str,
    sub_steps: Optional[Dict] = None,
    notes: Optional[str] = None
) -> bool:
    """
    Update a landmark's status for a case.

    Args:
        case_name: Case identifier
        landmark_id: Landmark identifier
        status: 'complete', 'in_progress', 'not_started', 'not_applicable'
        sub_steps: Optional dict of sub-step completion
        notes: Optional notes about completion

    Returns:
        True if updated successfully
    """
    from roscoe.core.graphiti_client import run_cypher_query
    import json

    now = datetime.now().isoformat()
    sub_steps_json = json.dumps(sub_steps) if sub_steps else None

    if status == "complete":
        query = '''
        MATCH (case:Entity {entity_type: 'Case', name: $case_name})
        MATCH (lm:Entity {entity_type: 'Landmark', landmark_id: $landmark_id})
        MERGE (case)-[r:LANDMARK_STATUS]->(lm)
        SET r.status = $status,
            r.sub_steps = $sub_steps,
            r.notes = $notes,
            r.completed_at = $completed_at,
            r.updated_at = $updated_at
        RETURN case.name, lm.landmark_id
        '''
        params = {
            "case_name": case_name,
            "landmark_id": landmark_id,
            "status": status,
            "sub_steps": sub_steps_json,
            "notes": notes,
            "completed_at": now,
            "updated_at": now
        }
    else:
        query = '''
        MATCH (case:Entity {entity_type: 'Case', name: $case_name})
        MATCH (lm:Entity {entity_type: 'Landmark', landmark_id: $landmark_id})
        MERGE (case)-[r:LANDMARK_STATUS]->(lm)
        SET r.status = $status,
            r.sub_steps = $sub_steps,
            r.notes = $notes,
            r.updated_at = $updated_at
        RETURN case.name, lm.landmark_id
        '''
        params = {
            "case_name": case_name,
            "landmark_id": landmark_id,
            "status": status,
            "sub_steps": sub_steps_json,
            "notes": notes,
            "updated_at": now
        }

    result = await run_cypher_query(query, params)
    return len(result) > 0
