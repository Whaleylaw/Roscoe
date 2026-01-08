#!/usr/bin/env python3
"""Test with full types from graphiti_client.py."""

import asyncio
from datetime import datetime
import sys

sys.path.insert(0, "/deps/Roscoe/src")


async def test():
    from roscoe.core.graphiti_client import (
        get_graphiti, ENTITY_TYPES_DICT, EDGE_TYPES_DICT, EDGE_TYPE_MAP
    )
    from graphiti_core.nodes import EpisodeType
    
    g = await get_graphiti()
    
    print("=" * 60)
    print("TEST: Full Types from graphiti_client.py")
    print("=" * 60)
    print(f"Entity types: {len(ENTITY_TYPES_DICT)}")
    print(f"Edge types: {len(EDGE_TYPES_DICT)}")
    print(f"Edge type mappings: {len(EDGE_TYPE_MAP)}")
    print()
    
    episode = """
    Case Caryn-McCay-MVA-7-30-2023 is a motor vehicle accident case.
    Client Caryn McCay was injured on July 30, 2023.
    She is treating at Baptist Health for neck and back pain.
    State Farm Insurance has the BI claim number 12345678.
    Attorney Aaron Whaley of Whaley Law Firm represents her.
    """
    
    try:
        result = await g.add_episode(
            name="Test: Full Types from graphiti_client",
            episode_body=episode,
            source=EpisodeType.text,
            source_description="test",
            reference_time=datetime.now(),
            group_id="roscoe_graph_v2",
            entity_types=ENTITY_TYPES_DICT,
            edge_types=EDGE_TYPES_DICT,
            edge_type_map=EDGE_TYPE_MAP,
        )
        print(f"SUCCESS! Nodes: {len(result.nodes)}, Edges: {len(result.edges)}")
        print("\nExtracted entities:")
        for node in result.nodes:
            print(f"  - {node.name}")
    except Exception as e:
        import traceback
        print(f"FAILED: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
