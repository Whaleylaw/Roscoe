#!/usr/bin/env python3
"""Test simple episode addition without custom types."""

import asyncio
from datetime import datetime
import sys
import os

sys.path.insert(0, "/deps/Roscoe/src")


async def test():
    from roscoe.core.graphiti_client import get_graphiti
    from graphiti_core.nodes import EpisodeType
    from graphiti_core.driver.falkordb_driver import FalkorDriver
    
    g = await get_graphiti()
    
    # Test 1: Add episode WITHOUT custom types
    print("Test 1: Add episode WITHOUT custom types")
    print("=" * 50)
    try:
        result = await g.add_episode(
            name="Test: Simple Episode (no types)",
            episode_body="John Smith was injured in a car accident on Highway 64. He is treating at Baptist Health Emergency Department.",
            source=EpisodeType.text,
            source_description="test",
            reference_time=datetime.now(),
            group_id="roscoe_graph_v2",
            # NO entity_types, edge_types, edge_type_map
        )
        print(f"SUCCESS! Nodes: {len(result.nodes)}, Edges: {len(result.edges)}")
        print("\nExtracted entities:")
        for node in result.nodes:
            print(f"  - {node.name}")
        print("\nExtracted relationships:")
        for edge in result.edges[:5]:
            print(f"  - {edge.fact[:70]}...")
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()
    
    # Check what labels were created in v2 graph
    print("\n" + "=" * 50)
    print("Checking labels in roscoe_graph_v2...")
    print("=" * 50)
    
    driver = FalkorDriver(
        host=os.getenv("FALKORDB_HOST", "localhost"),
        port=int(os.getenv("FALKORDB_PORT", "6379")),
        database="roscoe_graph_v2",
    )
    graph = await driver.get_graph()
    
    # Get labels
    result = await graph.query("MATCH (n) WITH DISTINCT labels(n) as lbls RETURN lbls")
    print(f"Labels: {result.result_set}")
    
    # Get sample entities
    result2 = await graph.query("MATCH (n:Entity) RETURN n.name, n.entity_type, labels(n) LIMIT 5")
    print(f"\nSample entities:")
    for row in result2.result_set:
        print(f"  - Name: {row[0]}, entity_type: {row[1]}, labels: {row[2]}")


if __name__ == "__main__":
    asyncio.run(test())
