"""
Tests for agent tools that wrap graph_manager functions.

Tests verify:
- LangChain tool decorator integration
- Async tool invocation
- Proper wrapping of graph_manager functions
- Case creation with phase initialization
"""

import pytest
from roscoe.agents.paralegal.graph_tools import create_new_case_tool


async def cleanup_test_data():
    """Helper function to clean up test entities and close connections."""
    from roscoe.core.graphiti_client import run_cypher_query, close_graphiti
    await run_cypher_query('''
        MATCH (n:Entity)
        WHERE n.name STARTS WITH 'John-Doe' OR
              n.name = 'John Doe' OR
              (n.entity_type = 'Phase' AND n.name = 'file_setup')
        DETACH DELETE n
    ''')
    # Close the Graphiti connection to prevent event loop issues
    await close_graphiti()


@pytest.mark.asyncio
async def test_create_new_case_tool():
    """Test agent tool for creating new case."""
    from roscoe.core.graphiti_client import run_cypher_query, CASE_DATA_GROUP_ID

    try:
        # Create file_setup phase entity (in production, this will be pre-loaded)
        await run_cypher_query('''
            MERGE (phase:Entity {
                name: 'file_setup',
                entity_type: 'Phase',
                group_id: $group_id
            })
        ''', {"group_id": CASE_DATA_GROUP_ID})

        result = await create_new_case_tool.ainvoke({
            "client_name": "John Doe",
            "accident_date": "2024-12-15",
            "case_type": "MVA"
        })

        assert "case_name" in result
        assert result["case_name"] == "John-Doe-MVA-2024-12-15"
        assert result["success"] == True
        assert result["phase"] == "file_setup"
        assert "message" in result

        # Verify case was actually created in graph
        case_result = await run_cypher_query('''
            MATCH (c:Entity {entity_type: 'Case', name: $case_name})
            RETURN c.case_type
        ''', {"case_name": "John-Doe-MVA-2024-12-15"})

        assert len(case_result) == 1
        assert case_result[0]["c.case_type"] == "MVA"

        # Verify IN_PHASE relationship was created
        phase_result = await run_cypher_query('''
            MATCH (case:Entity {name: $case_name})-[:IN_PHASE]->(phase:Entity {entity_type: 'Phase'})
            RETURN phase.name
        ''', {"case_name": "John-Doe-MVA-2024-12-15"})

        assert len(phase_result) == 1
        assert phase_result[0]["phase.name"] == "file_setup"

    finally:
        await cleanup_test_data()
