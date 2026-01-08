#!/usr/bin/env python3
"""
Test Graphiti type system compatibility.

This script tests:
1. Whether SearchFilters.node_labels works with our entity_type property
2. Whether custom entity types are properly extracted when adding episodes
3. Compares Cypher-created entities vs Graphiti-native entities
"""

import asyncio
import sys
from datetime import datetime

sys.path.insert(0, "/deps/Roscoe/src")


async def test_search_filters():
    """Test if SearchFilters work with our existing entity_type property."""
    from roscoe.core.graphiti_client import get_graphiti, CASE_DATA_GROUP_ID
    from graphiti_core.search.search_filters import SearchFilters
    
    print("=" * 60)
    print("TEST 1: SearchFilters with node_labels")
    print("=" * 60)
    
    g = await get_graphiti()
    
    # Test 1a: Search with no filter
    print("\n1a. Search with NO filter:")
    results_no_filter = await g.search(
        query="Caryn McCay",
        group_ids=[CASE_DATA_GROUP_ID],
        num_results=5
    )
    print(f"   Results: {len(results_no_filter)}")
    for r in results_no_filter[:3]:
        print(f"   - {r.fact[:80]}...")
    
    # Test 1b: Search with node_labels filter for "Case"
    print("\n1b. Search with node_labels=['Case']:")
    try:
        search_filter = SearchFilters(node_labels=["Case"])
        results_case = await g.search_(
            query="Caryn McCay",
            group_ids=[CASE_DATA_GROUP_ID],
            search_filter=search_filter
        )
        print(f"   Edges: {len(results_case.edges)}")
        print(f"   Nodes: {len(results_case.nodes)}")
        for edge in results_case.edges[:3]:
            print(f"   - {edge.fact[:80]}...")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 1c: Search with node_labels filter for "Client"
    print("\n1c. Search with node_labels=['Client']:")
    try:
        search_filter = SearchFilters(node_labels=["Client"])
        results_client = await g.search_(
            query="Caryn McCay",
            group_ids=[CASE_DATA_GROUP_ID],
            search_filter=search_filter
        )
        print(f"   Edges: {len(results_client.edges)}")
        print(f"   Nodes: {len(results_client.nodes)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 1d: Search with node_labels filter for "MedicalProvider"
    print("\n1d. Search with node_labels=['MedicalProvider']:")
    try:
        search_filter = SearchFilters(node_labels=["MedicalProvider"])
        results_provider = await g.search_(
            query="medical treatment providers",
            group_ids=[CASE_DATA_GROUP_ID],
            search_filter=search_filter
        )
        print(f"   Edges: {len(results_provider.edges)}")
        print(f"   Nodes: {len(results_provider.nodes)}")
    except Exception as e:
        print(f"   ERROR: {e}")


async def test_entity_structure():
    """Compare Cypher-created entities vs Graphiti-extracted entities."""
    from roscoe.core.graphiti_client import run_cypher_query
    
    print("\n" + "=" * 60)
    print("TEST 2: Entity Structure Comparison")
    print("=" * 60)
    
    # Query Cypher-created entities
    print("\n2a. Sample Cypher-created Case entity:")
    try:
        cypher_cases = await run_cypher_query("""
            MATCH (n:Entity {entity_type: 'Case'})
            RETURN n.name, n.entity_type, n.uuid, keys(n) as properties
            LIMIT 2
        """)
        for row in cypher_cases:
            print(f"   Name: {row[0]}")
            print(f"   entity_type: {row[1]}")
            print(f"   Properties: {row[3]}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Query Graphiti-extracted entities (have summary)
    print("\n2b. Sample Graphiti-extracted entity (has summary):")
    try:
        graphiti_entities = await run_cypher_query("""
            MATCH (n:Entity)
            WHERE n.summary IS NOT NULL AND n.summary <> ''
            RETURN n.name, n.entity_type, n.summary, keys(n) as properties
            LIMIT 2
        """)
        for row in graphiti_entities:
            print(f"   Name: {row[0]}")
            print(f"   entity_type: {row[1]}")
            print(f"   Summary: {row[2][:100]}..." if row[2] else "   Summary: None")
            print(f"   Properties: {row[3]}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Check if node_labels are Neo4j labels or entity_type property
    print("\n2c. Check Neo4j labels on entities:")
    try:
        labels = await run_cypher_query("""
            MATCH (n)
            WITH DISTINCT labels(n) as lbls
            RETURN lbls
            LIMIT 10
        """)
        print(f"   Distinct label combinations:")
        for row in labels:
            print(f"   - {row[0]}")
    except Exception as e:
        print(f"   ERROR: {e}")


async def test_add_episode_with_types():
    """Test adding episode with custom entity types."""
    from roscoe.core.graphiti_client import (
        get_graphiti, ENTITY_TYPES_DICT, EDGE_TYPES_DICT, EDGE_TYPE_MAP
    )
    from graphiti_core.nodes import EpisodeType
    
    print("\n" + "=" * 60)
    print("TEST 3: Add Episode with Custom Types (to v2 namespace)")
    print("=" * 60)
    
    g = await get_graphiti()
    
    # Use a test namespace to avoid polluting production
    TEST_GROUP_ID = "roscoe_graph_v2"
    
    episode_body = """Case: Test-Investigation-Case-2025
On December 20, 2025, client John Smith was injured in a motor vehicle accident.
Attorney Aaron Whaley of Whaley Law Firm is representing John Smith.
John Smith is treating at Baptist Health Emergency Department for neck and back injuries.
The at-fault driver has State Farm Insurance with policy limits of $100,000.
Adjuster Jane Doe from State Farm is handling BI claim 12345678.
The PIP claim through Allstate (claim number 0987654321) has $10,000 in benefits.
"""
    
    print(f"\nAdding episode to namespace: {TEST_GROUP_ID}")
    print(f"Entity types: {len(ENTITY_TYPES_DICT)} types")
    print(f"Edge types: {len(EDGE_TYPES_DICT)} types")
    print(f"Edge type mappings: {len(EDGE_TYPE_MAP)} mappings")
    
    try:
        result = await g.add_episode(
            name="Test: Type Investigation - John Smith Case",
            episode_body=episode_body,
            source=EpisodeType.text,
            source_description="type investigation test",
            reference_time=datetime.now(),
            group_id=TEST_GROUP_ID,
            entity_types=ENTITY_TYPES_DICT,
            edge_types=EDGE_TYPES_DICT,
            edge_type_map=EDGE_TYPE_MAP,
        )
        
        print(f"\nResult type: {type(result)}")
        
        if hasattr(result, 'episode'):
            print(f"Episode UUID: {result.episode.uuid}")
            print(f"Episode group_id: {result.episode.group_id}")
        
        if hasattr(result, 'nodes'):
            print(f"\nNodes created: {len(result.nodes)}")
            for node in result.nodes[:5]:
                node_type = getattr(node, 'entity_type', 'Entity')
                print(f"  - {node.name} (type: {node_type})")
        
        if hasattr(result, 'edges'):
            print(f"\nEdges created: {len(result.edges)}")
            for edge in result.edges[:5]:
                edge_type = getattr(edge, 'name', 'RELATES_TO')
                print(f"  - {edge_type}: {edge.fact[:60]}...")
        
    except Exception as e:
        import traceback
        print(f"\nERROR: {e}")
        traceback.print_exc()


async def main():
    print("Graphiti Type System Investigation")
    print("=" * 60)
    
    await test_search_filters()
    await test_entity_structure()
    await test_add_episode_with_types()
    
    print("\n" + "=" * 60)
    print("INVESTIGATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
