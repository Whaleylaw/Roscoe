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


async def verify_landmark(case_name: str, landmark_id: str) -> bool:
    """
    Run verification query for a landmark.

    Args:
        case_name: Case identifier
        landmark_id: Landmark identifier

    Returns:
        True if landmark conditions are met
    """
    from roscoe.core.graphiti_client import run_cypher_query

    # Get landmark verification query
    result = await run_cypher_query('''
        MATCH (l:Entity {entity_type: 'Landmark', landmark_id: $landmark_id})
        WHERE l.verification_method IN ['graph_query', 'hybrid']
          AND l.verification_query IS NOT NULL
        RETURN l.verification_query as query
    ''', {"landmark_id": landmark_id})

    if not result or not result[0].get("query"):
        return False

    verification_query = result[0]["query"]

    # Run the verification query with error handling
    try:
        verification_result = await run_cypher_query(
            verification_query,
            {"case_name": case_name}
        )
    except Exception:
        # Malformed query - skip gracefully
        return False

    # Check if verified (query should return 'verified' field) - consistent null check
    if not verification_result or len(verification_result) == 0:
        return False

    return verification_result[0].get("verified", False)


async def initialize_phase_landmarks(case_name: str, phase_name: str) -> int:
    """
    Create initial LANDMARK_STATUS relationships for all landmarks in a phase.

    Sets status to 'not_started' for each landmark.

    Args:
        case_name: Case identifier
        phase_name: Phase name

    Returns:
        Number of landmarks initialized
    """
    from roscoe.core.graphiti_client import run_cypher_query

    result = await run_cypher_query('''
        MATCH (case:Entity {name: $case_name})
        MATCH (phase:Entity {entity_type: 'Phase', name: $phase_name})-[:HAS_LANDMARK]->(lm:Entity {entity_type: 'Landmark'})
        MERGE (case)-[r:LANDMARK_STATUS]->(lm)
        ON CREATE SET
          r.status = 'not_started',
          r.created_at = $now,
          r.updated_at = $now
        RETURN count(lm) as landmark_count
    ''', {
        "case_name": case_name,
        "phase_name": phase_name,
        "now": datetime.now().isoformat()
    })

    return result[0]["landmark_count"] if result else 0


async def auto_verify_all_landmarks(case_name: str) -> List[str]:
    """
    Check all auto-verifiable landmarks for a case and update statuses.

    Call this after major graph updates (adding claims, providers, documents).

    Args:
        case_name: Case identifier

    Returns:
        List of landmark IDs that were auto-verified
    """
    from roscoe.core.graphiti_client import run_cypher_query, get_case_phase

    # Get current phase
    phase_info = await get_case_phase(case_name)
    if not phase_info:
        return []

    # Get auto-verifiable landmarks for current phase
    landmarks_to_check = await run_cypher_query('''
        MATCH (phase:Entity {entity_type: 'Phase', name: $phase_name})-[:HAS_LANDMARK]->(l:Entity {entity_type: 'Landmark'})
        WHERE l.auto_verify = true
          AND l.verification_query IS NOT NULL
        MATCH (case:Entity {name: $case_name})
        OPTIONAL MATCH (case)-[ls:LANDMARK_STATUS]->(l)
        WHERE ls.status IS NULL OR ls.status <> 'complete'
        RETURN l.landmark_id, l.verification_query
    ''', {
        "phase_name": phase_info["name"],
        "case_name": case_name
    })

    verified_landmarks = []

    # Verify each and update if passed
    for lm in landmarks_to_check:
        is_verified = await verify_landmark(case_name, lm["landmark_id"])

        if is_verified:
            await update_landmark_status(
                case_name=case_name,
                landmark_id=lm["landmark_id"],
                status="complete",
                notes="Auto-verified from graph data"
            )
            verified_landmarks.append(lm["landmark_id"])

    return verified_landmarks


# =============================================================================
# Calendar Event Management
# =============================================================================

async def create_calendar_event(
    title: str,
    event_date: str,
    event_type: str = "task",
    case_name: Optional[str] = None,
    priority: str = "medium",
    event_time: Optional[str] = None,
    description: Optional[str] = None,
    notes: Optional[str] = None,
    source: str = "user"
) -> Dict:
    """
    Create a calendar event in the knowledge graph.

    Args:
        title: Event title (required)
        event_date: Date in YYYY-MM-DD format (required)
        event_type: deadline|task|hearing|deposition|mediation|reminder|meeting|other
        case_name: Associated case name, or None for firm-wide events
        priority: high|medium|low
        event_time: Optional time (e.g., "9:00 AM")
        description: Optional detailed description
        notes: Optional additional notes
        source: user|agent|system|migration

    Returns:
        Dict with event_id and details
    """
    from roscoe.core.graphiti_client import run_cypher_query, CASE_DATA_GROUP_ID
    import uuid

    event_id = f"cal_{uuid.uuid4().hex[:12]}"
    now = datetime.now().isoformat()

    # Create the CalendarEvent entity
    await run_cypher_query('''
        CREATE (e:Entity {
            name: $event_id,
            entity_type: 'CalendarEvent',
            title: $title,
            event_date: $event_date,
            event_type: $event_type,
            event_time: $event_time,
            status: 'pending',
            priority: $priority,
            description: $description,
            notes: $notes,
            case_name: $case_name,
            source: $source,
            created_at: $now,
            group_id: $group_id
        })
    ''', {
        "event_id": event_id,
        "title": title,
        "event_date": event_date,
        "event_type": event_type,
        "event_time": event_time,
        "priority": priority,
        "description": description,
        "notes": notes,
        "case_name": case_name,
        "source": source,
        "now": now,
        "group_id": CASE_DATA_GROUP_ID
    })

    # If case_name provided, create relationship to case
    if case_name:
        await run_cypher_query('''
            MATCH (case:Entity {entity_type: 'Case', name: $case_name})
            MATCH (event:Entity {entity_type: 'CalendarEvent', name: $event_id})
            CREATE (case)-[:HasEvent]->(event)
        ''', {"case_name": case_name, "event_id": event_id})

    return {
        "event_id": event_id,
        "title": title,
        "event_date": event_date,
        "event_type": event_type,
        "priority": priority,
        "case_name": case_name
    }


async def get_calendar_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    case_name: Optional[str] = None,
    status: str = "pending",
    event_type: Optional[str] = None,
    include_firm_wide: bool = True
) -> List[Dict]:
    """
    Query calendar events from graph.

    Args:
        start_date: Filter events on/after this date (YYYY-MM-DD)
        end_date: Filter events on/before this date (YYYY-MM-DD)
        case_name: Filter to specific case, or None for all
        status: pending|completed|cancelled|all
        event_type: Filter by type, or None for all
        include_firm_wide: Include events not tied to a case

    Returns:
        List of event dicts
    """
    from roscoe.core.graphiti_client import run_cypher_query

    # Build dynamic WHERE clauses
    where_clauses = ["e.entity_type = 'CalendarEvent'"]
    params = {}

    if status != "all":
        where_clauses.append("e.status = $status")
        params["status"] = status

    if start_date:
        where_clauses.append("e.event_date >= $start_date")
        params["start_date"] = start_date

    if end_date:
        where_clauses.append("e.event_date <= $end_date")
        params["end_date"] = end_date

    if case_name:
        where_clauses.append("e.case_name = $case_name")
        params["case_name"] = case_name
    elif not include_firm_wide:
        where_clauses.append("e.case_name IS NOT NULL")

    if event_type:
        where_clauses.append("e.event_type = $event_type")
        params["event_type"] = event_type

    where_str = " AND ".join(where_clauses)

    query = f'''
        MATCH (e:Entity)
        WHERE {where_str}
        RETURN e.name as event_id, e.title as title, e.event_date as event_date,
               e.event_time as event_time, e.event_type as event_type,
               e.status as status, e.priority as priority,
               e.case_name as case_name, e.notes as notes,
               e.description as description, e.completed_at as completed_at
        ORDER BY e.event_date ASC,
                 CASE e.priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END
    '''

    results = await run_cypher_query(query, params)
    return results if results else []


async def get_overdue_and_today_events() -> Dict[str, List[Dict]]:
    """
    Get overdue events and today's events for context injection.

    Returns:
        Dict with "overdue" and "today" lists
    """
    import pytz
    from roscoe.core.graphiti_client import run_cypher_query

    eastern = pytz.timezone('America/New_York')
    today = datetime.now(eastern).strftime('%Y-%m-%d')

    query = '''
        MATCH (e:Entity)
        WHERE e.entity_type = 'CalendarEvent'
          AND e.status = 'pending'
          AND e.event_date <= $today
        RETURN e.title as title, e.event_date as date, e.priority as priority,
               e.case_name as project_name, e.notes as notes, e.event_time as time,
               e.event_type as event_type
        ORDER BY e.event_date ASC,
                 CASE e.priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END
    '''

    results = await run_cypher_query(query, {"today": today})

    if not results:
        return {"overdue": [], "today": []}

    overdue = []
    today_events = []

    for event in results:
        event_date = event.get("date", "")
        if event_date < today:
            overdue.append(event)
        else:
            today_events.append(event)

    return {"overdue": overdue, "today": today_events}


def get_overdue_and_today_events_sync() -> Dict[str, List[Dict]]:
    """
    Synchronous wrapper for get_overdue_and_today_events.
    For use in middleware that runs synchronously.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in an async context, run in thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, get_overdue_and_today_events())
                return future.result(timeout=10)
        else:
            return loop.run_until_complete(get_overdue_and_today_events())
    except RuntimeError:
        return asyncio.run(get_overdue_and_today_events())


async def complete_calendar_event(
    event_id: Optional[str] = None,
    title: Optional[str] = None,
    event_date: Optional[str] = None,
    case_name: Optional[str] = None
) -> bool:
    """
    Mark a calendar event as completed.

    Args:
        event_id: Direct event ID if known
        title: Event title to match (if event_id not provided)
        event_date: Date to help disambiguate (if title provided)
        case_name: Case to help disambiguate (if title provided)

    Returns:
        True if event was completed, False if not found
    """
    from roscoe.core.graphiti_client import run_cypher_query

    now = datetime.now().isoformat()

    if event_id:
        # Direct lookup by ID
        result = await run_cypher_query('''
            MATCH (e:Entity {entity_type: 'CalendarEvent', name: $event_id})
            SET e.status = 'completed', e.completed_at = $now
            RETURN e.name as event_id
        ''', {"event_id": event_id, "now": now})
    else:
        # Lookup by title (and optionally date/case)
        where_clauses = ["e.entity_type = 'CalendarEvent'", "e.title = $title", "e.status = 'pending'"]
        params = {"title": title, "now": now}

        if event_date:
            where_clauses.append("e.event_date = $event_date")
            params["event_date"] = event_date

        if case_name:
            where_clauses.append("e.case_name = $case_name")
            params["case_name"] = case_name

        where_str = " AND ".join(where_clauses)

        result = await run_cypher_query(f'''
            MATCH (e:Entity)
            WHERE {where_str}
            SET e.status = 'completed', e.completed_at = $now
            RETURN e.name as event_id
        ''', params)

    return bool(result)


async def update_calendar_event(
    event_id: Optional[str] = None,
    title: Optional[str] = None,
    event_date: Optional[str] = None,
    new_title: Optional[str] = None,
    new_date: Optional[str] = None,
    new_time: Optional[str] = None,
    new_priority: Optional[str] = None,
    new_notes: Optional[str] = None,
    new_status: Optional[str] = None
) -> bool:
    """
    Update a calendar event.

    Args:
        event_id: Direct event ID if known
        title: Event title to match (if event_id not provided)
        event_date: Date to help disambiguate (if title provided)
        new_*: Fields to update

    Returns:
        True if event was updated, False if not found
    """
    from roscoe.core.graphiti_client import run_cypher_query

    # Build SET clauses dynamically
    set_clauses = []
    params = {}

    if new_title:
        set_clauses.append("e.title = $new_title")
        params["new_title"] = new_title

    if new_date:
        set_clauses.append("e.event_date = $new_date")
        params["new_date"] = new_date

    if new_time:
        set_clauses.append("e.event_time = $new_time")
        params["new_time"] = new_time

    if new_priority:
        set_clauses.append("e.priority = $new_priority")
        params["new_priority"] = new_priority

    if new_notes:
        set_clauses.append("e.notes = $new_notes")
        params["new_notes"] = new_notes

    if new_status:
        set_clauses.append("e.status = $new_status")
        params["new_status"] = new_status
        if new_status == "completed":
            set_clauses.append("e.completed_at = $now")
            params["now"] = datetime.now().isoformat()

    if not set_clauses:
        return False

    set_str = ", ".join(set_clauses)

    if event_id:
        params["event_id"] = event_id
        result = await run_cypher_query(f'''
            MATCH (e:Entity {{entity_type: 'CalendarEvent', name: $event_id}})
            SET {set_str}
            RETURN e.name as event_id
        ''', params)
    else:
        params["title"] = title
        where_clauses = ["e.entity_type = 'CalendarEvent'", "e.title = $title"]

        if event_date:
            where_clauses.append("e.event_date = $event_date")
            params["event_date"] = event_date

        where_str = " AND ".join(where_clauses)

        result = await run_cypher_query(f'''
            MATCH (e:Entity)
            WHERE {where_str}
            SET {set_str}
            RETURN e.name as event_id
        ''', params)

    return bool(result)


async def search_calendar_events(
    query: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    case_name: Optional[str] = None,
    status: str = "all",
    event_type: Optional[str] = None,
    limit: int = 50
) -> List[Dict]:
    """
    Search calendar events with text matching.

    Args:
        query: Text to search in title and notes
        start_date: Events on/after this date
        end_date: Events on/before this date
        case_name: Filter to specific case
        status: pending|completed|cancelled|all
        event_type: Filter by type
        limit: Max results

    Returns:
        List of matching events
    """
    from roscoe.core.graphiti_client import run_cypher_query

    where_clauses = ["e.entity_type = 'CalendarEvent'"]
    params = {"limit": limit}

    if query:
        # Case-insensitive search in title and notes
        where_clauses.append("(toLower(e.title) CONTAINS toLower($query) OR toLower(e.notes) CONTAINS toLower($query))")
        params["query"] = query

    if status != "all":
        where_clauses.append("e.status = $status")
        params["status"] = status

    if start_date:
        where_clauses.append("e.event_date >= $start_date")
        params["start_date"] = start_date

    if end_date:
        where_clauses.append("e.event_date <= $end_date")
        params["end_date"] = end_date

    if case_name:
        where_clauses.append("e.case_name = $case_name")
        params["case_name"] = case_name

    if event_type:
        where_clauses.append("e.event_type = $event_type")
        params["event_type"] = event_type

    where_str = " AND ".join(where_clauses)

    results = await run_cypher_query(f'''
        MATCH (e:Entity)
        WHERE {where_str}
        RETURN e.name as event_id, e.title as title, e.event_date as event_date,
               e.event_time as event_time, e.event_type as event_type,
               e.status as status, e.priority as priority,
               e.case_name as case_name, e.notes as notes
        ORDER BY e.event_date ASC
        LIMIT $limit
    ''', params)

    return results if results else []


async def update_case_sol_status(
    case_name: str,
    sol_status: str,
    complaint_filed_date: Optional[str] = None,
    sol_notes: Optional[str] = None
) -> Dict:
    """
    Update statute of limitations status on a Case node.

    Use this when:
    - A complaint has been filed (status='filed', include filed_date)
    - SOL is tolled for some reason (status='tolled', include notes explaining why)
    - SOL doesn't apply (status='n/a', e.g., workers comp cases in some jurisdictions)

    Args:
        case_name: Case folder name (e.g., "John-Doe-MVA-01-15-2024")
        sol_status: pending | filed | tolled | n/a
        complaint_filed_date: Date complaint was filed (YYYY-MM-DD), required if status='filed'
        sol_notes: Optional notes explaining the status

    Returns:
        Dict with updated status or error
    """
    from roscoe.core.graphiti_client import run_cypher_query

    # Validate status
    valid_statuses = {"pending", "filed", "tolled", "n/a"}
    if sol_status not in valid_statuses:
        return {"error": f"Invalid status '{sol_status}'. Must be one of: {valid_statuses}"}

    # If status is 'filed', complaint_filed_date is required
    if sol_status == "filed" and not complaint_filed_date:
        return {"error": "complaint_filed_date is required when sol_status='filed'"}

    # Build SET clauses
    set_clauses = ["c.sol_status = $sol_status", "c.sol_updated_at = $now"]
    params = {
        "case_name": case_name,
        "sol_status": sol_status,
        "now": datetime.now().isoformat()
    }

    if complaint_filed_date:
        set_clauses.append("c.complaint_filed_date = $complaint_filed_date")
        params["complaint_filed_date"] = complaint_filed_date

    if sol_notes:
        set_clauses.append("c.sol_notes = $sol_notes")
        params["sol_notes"] = sol_notes

    set_str = ", ".join(set_clauses)

    # Try updating Case node (primary label)
    result = await run_cypher_query(f'''
        MATCH (c:Case {{name: $case_name}})
        SET {set_str}
        RETURN c.name as case_name, c.sol_status as sol_status,
               c.complaint_filed_date as complaint_filed_date, c.sol_notes as sol_notes
    ''', params)

    # If not found, try Entity with entity_type='Case'
    if not result:
        result = await run_cypher_query(f'''
            MATCH (c:Entity {{entity_type: 'Case', name: $case_name}})
            SET {set_str}
            RETURN c.name as case_name, c.sol_status as sol_status,
                   c.complaint_filed_date as complaint_filed_date, c.sol_notes as sol_notes
        ''', params)

    if result:
        return {
            "success": True,
            "case_name": result[0].get("case_name"),
            "sol_status": result[0].get("sol_status"),
            "complaint_filed_date": result[0].get("complaint_filed_date"),
            "sol_notes": result[0].get("sol_notes")
        }
    else:
        return {"error": f"Case '{case_name}' not found in graph"}


async def get_case_sol_status(case_name: str) -> Dict:
    """
    Get current SOL status for a case.

    Returns:
        Dict with sol_status, complaint_filed_date, sol_notes, accident_date, case_type
    """
    from roscoe.core.graphiti_client import run_cypher_query

    # Try Case node first
    result = await run_cypher_query('''
        MATCH (c:Case {name: $case_name})
        RETURN c.name as case_name, c.sol_status as sol_status,
               c.complaint_filed_date as complaint_filed_date, c.sol_notes as sol_notes,
               c.accident_date as accident_date, c.case_type as case_type
    ''', {"case_name": case_name})

    # Fallback to Entity
    if not result:
        result = await run_cypher_query('''
            MATCH (c:Entity {entity_type: 'Case', name: $case_name})
            RETURN c.name as case_name, c.sol_status as sol_status,
                   c.complaint_filed_date as complaint_filed_date, c.sol_notes as sol_notes,
                   c.accident_date as accident_date, c.case_type as case_type
        ''', {"case_name": case_name})

    if result:
        return result[0]
    else:
        return {"error": f"Case '{case_name}' not found"}
