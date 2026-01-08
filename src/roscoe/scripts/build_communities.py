#!/usr/bin/env python3
"""Build and verify Graphiti communities."""

import asyncio
import sys

sys.path.insert(0, "/deps/Roscoe/src")


async def main():
    from roscoe.core.graphiti_client import get_graphiti
    
    # Use v2 graph which has proper Graphiti-created entities
    TEST_GROUP_ID = "roscoe_graph_v2"
    
    g = await get_graphiti()
    
    print("=" * 60)
    print("BUILDING COMMUNITIES")
    print("=" * 60)
    print(f"Group ID: {TEST_GROUP_ID}")
    print()
    
    print("Building communities...")
    try:
        await g.build_communities(group_ids=[TEST_GROUP_ID])
        print("Communities built successfully!")
    except Exception as e:
        import traceback
        print(f"Error building communities: {e}")
        traceback.print_exc()
        return
    
    # Verify communities were created
    print("\nChecking community nodes...")
    
    # Search that includes communities
    from graphiti_core.search.search_config import SearchConfig
    
    results = await g.search_(
        query="Caryn McCay case",
        group_ids=[TEST_GROUP_ID],
    )
    
    print(f"Search results:")
    print(f"  Edges: {len(results.edges)}")
    print(f"  Nodes: {len(results.nodes)}")
    print(f"  Episodes: {len(results.episodes)}")
    print(f"  Communities: {len(results.communities)}")
    
    if results.communities:
        print("\nCommunity summaries:")
        for comm in results.communities[:3]:
            print(f"  - {comm.summary[:100]}..." if hasattr(comm, 'summary') else f"  - {comm}")


if __name__ == "__main__":
    asyncio.run(main())
