"""
Agent tools for Direct Cypher graph operations.

These tools wrap graph_manager functions for agent use.
"""

from langchain.tools import tool
from typing import Optional


@tool
async def create_new_case_tool(
    client_name: str,
    accident_date: str,
    case_type: str = "MVA"
) -> dict:
    """
    Create a new case in the knowledge graph.

    This initializes:
    - Case entity
    - Client entity
    - HAS_CLIENT relationship
    - IN_PHASE relationship (set to file_setup)
    - LANDMARK_STATUS relationships for all file_setup landmarks

    Args:
        client_name: Client full name (e.g., "Elizabeth Lindsey")
        accident_date: Date of accident in YYYY-MM-DD format
        case_type: Type of case (MVA, Premise, WC, Med-Mal, Dog-Bite, Slip-Fall)

    Returns:
        Dictionary with case_name and success status
    """
    from roscoe.core.graph_manager import create_case, set_case_phase, initialize_phase_landmarks

    # Create case and client
    case_name = await create_case(client_name, accident_date, case_type)

    # Set to file_setup phase
    await set_case_phase(case_name, "file_setup")

    # Initialize landmarks
    await initialize_phase_landmarks(case_name, "file_setup")

    return {
        "success": True,
        "case_name": case_name,
        "phase": "file_setup",
        "message": f"Case created for {client_name}. Initialized in File Setup phase."
    }
