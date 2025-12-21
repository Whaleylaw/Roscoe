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
