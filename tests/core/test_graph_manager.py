"""
Tests for graph_manager.py - Direct Cypher graph operations

Tests verify:
- Entity creation (Case, Client, etc.)
- Relationship creation
- Deterministic behavior (no LLM variance)
"""

import pytest
import pytest_asyncio
from datetime import date
from roscoe.core.graph_manager import create_case


@pytest_asyncio.fixture(autouse=True)
async def cleanup_test_entities():
    """Clean up test entities after each test."""
    yield
    from roscoe.core.graphiti_client import run_cypher_query
    await run_cypher_query('''
        MATCH (n:Entity)
        WHERE n.name STARTS WITH 'Test-Client'
        DETACH DELETE n
    ''')


@pytest.mark.asyncio
async def test_create_case_creates_entities_and_relationships():
    """Test that create_case creates Case, Client entities and relationships."""
    case_name = await create_case(
        client_name="Test Client",
        accident_date="2024-12-01",
        case_type="MVA"
    )

    assert case_name == "Test-Client-MVA-2024-12-01"

    # Verify Case entity exists
    from roscoe.core.graphiti_client import run_cypher_query
    result = await run_cypher_query('''
        MATCH (c:Entity {entity_type: 'Case', name: $case_name})
        RETURN c.case_type, c.accident_date
    ''', {"case_name": case_name})

    assert len(result) == 1
    assert result[0]["c.case_type"] == "MVA"
    assert result[0]["c.accident_date"] == "2024-12-01"

    # Verify Client entity exists
    result = await run_cypher_query('''
        MATCH (client:Entity {entity_type: 'Client', name: 'Test Client'})
        RETURN client.name
    ''')

    assert len(result) == 1

    # Verify HAS_CLIENT relationship
    result = await run_cypher_query('''
        MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[:HAS_CLIENT]->(client)
        RETURN client.name
    ''', {"case_name": case_name})

    assert len(result) == 1
    assert result[0]["client.name"] == "Test Client"
