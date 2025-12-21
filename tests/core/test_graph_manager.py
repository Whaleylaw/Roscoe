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
from roscoe.core.graph_manager import create_case, create_biclaim, create_pipclaim


async def cleanup_test_data():
    """Helper function to clean up test entities and close connections."""
    from roscoe.core.graphiti_client import run_cypher_query, close_graphiti
    await run_cypher_query('''
        MATCH (n:Entity)
        WHERE n.name STARTS WITH 'Test-Client' OR
              n.name STARTS WITH 'BIClaim-TEST' OR
              n.name STARTS WITH 'PIPClaim-TEST' OR
              n.name = 'State Farm Insurance Company' OR
              n.name = 'Allstate Insurance' OR
              n.name = 'Test Adjuster'
        DETACH DELETE n
    ''')
    # Close the Graphiti connection to prevent event loop issues
    await close_graphiti()


@pytest.mark.asyncio
async def test_create_case_creates_entities_and_relationships():
    """Test that create_case creates Case, Client entities and relationships."""
    try:
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
    finally:
        await cleanup_test_data()


@pytest.mark.asyncio
async def test_create_biclaim():
    """Test creating BI claim with insurer and adjuster relationships."""
    try:
        # Setup: Create case first
        case_name = await create_case("Test Client 2", "2024-12-01", "MVA")

        # Create BI claim
        claim_name = await create_biclaim(
            case_name=case_name,
            claim_number="TEST-BI-12345",
            insurer_name="State Farm Insurance Company",
            adjuster_name="Test Adjuster",
            policy_limit=100000.0,
            coverage_confirmation="Coverage Confirmed"
        )

        assert "BIClaim" in claim_name

        # Verify claim entity
        from roscoe.core.graphiti_client import run_cypher_query
        result = await run_cypher_query('''
            MATCH (claim:Entity {entity_type: 'BIClaim', claim_number: $claim_number})
            RETURN claim.insurer_name, claim.policy_limit
        ''', {"claim_number": "TEST-BI-12345"})

        assert len(result) == 1
        assert result[0]["claim.insurer_name"] == "State Farm Insurance Company"
        assert result[0]["claim.policy_limit"] == 100000.0

        # Verify HAS_CLAIM relationship
        result = await run_cypher_query('''
            MATCH (case:Entity {name: $case_name})-[:HAS_CLAIM]->(claim:Entity {entity_type: 'BIClaim'})
            RETURN claim.claim_number
        ''', {"case_name": case_name})

        assert len(result) == 1
        assert result[0]["claim.claim_number"] == "TEST-BI-12345"

        # Verify INSURED_BY relationship
        result = await run_cypher_query('''
            MATCH (claim)-[:INSURED_BY]->(insurer:Entity {entity_type: 'Insurer'})
            WHERE claim.claim_number = $claim_number
            RETURN insurer.name
        ''', {"claim_number": "TEST-BI-12345"})

        assert len(result) == 1
        assert result[0]["insurer.name"] == "State Farm Insurance Company"
    finally:
        await cleanup_test_data()


@pytest.mark.asyncio
async def test_create_pipclaim():
    """Test creating PIP claim."""
    try:
        case_name = await create_case("Test Client 3", "2024-12-01", "MVA")

        claim_name = await create_pipclaim(
            case_name=case_name,
            claim_number="TEST-PIP-67890",
            insurer_name="Allstate Insurance",
            policy_limit=10000.0,
            exhausted=False
        )

        # Verify PIP claim entity
        from roscoe.core.graphiti_client import run_cypher_query
        result = await run_cypher_query('''
            MATCH (claim:Entity {entity_type: 'PIPClaim', claim_number: $claim_number})
            RETURN claim.exhausted, claim.policy_limit
        ''', {"claim_number": "TEST-PIP-67890"})

        assert len(result) == 1
        assert result[0]["claim.exhausted"] == False
        assert result[0]["claim.policy_limit"] == 10000.0
    finally:
        await cleanup_test_data()
