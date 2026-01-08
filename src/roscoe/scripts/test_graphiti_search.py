#!/usr/bin/env python3
"""Test Graphiti search functionality."""

import asyncio
import sys
sys.path.insert(0, "/deps/Roscoe/src")

async def test_search():
    from roscoe.core.graphiti_client import get_graphiti, CASE_DATA_GROUP_ID
    
    print("Initializing Graphiti...")
    g = await get_graphiti()
    
    # Test basic search
    print("\n=== Testing graphiti.search() ===")
    print(f"Query: What happened with Caryn McCay and Allstate Insurance?")
    print(f"Group ID: {CASE_DATA_GROUP_ID}")
    print()
    
    try:
        results = await g.search(
            query="What happened with Caryn McCay and Allstate Insurance?",
            group_ids=[CASE_DATA_GROUP_ID],
            num_results=5
        )
        
        print(f"Result type: {type(results)}")
        print(f"Number of results: {len(results)}")
        print()
        
        for i, edge in enumerate(results[:5]):
            print(f"--- Result {i+1} ---")
            print(f"  Fact: {edge.fact}")
            if hasattr(edge, "source_node_uuid") and edge.source_node_uuid:
                print(f"  Source UUID: {edge.source_node_uuid[:12]}...")
            if hasattr(edge, "target_node_uuid") and edge.target_node_uuid:
                print(f"  Target UUID: {edge.target_node_uuid[:12]}...")
            if hasattr(edge, "created_at"):
                print(f"  Created: {edge.created_at}")
            print()
            
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
    
    # Test advanced search (search_)
    print("\n=== Testing graphiti.search_() ===")
    try:
        from graphiti_core.search.search_config import SearchConfig, SearchResults
        
        advanced_results = await g.search_(
            query="Coleen Madayag sent letter to Allstate",
            group_ids=[CASE_DATA_GROUP_ID],
        )
        
        print(f"Result type: {type(advanced_results)}")
        
        if hasattr(advanced_results, "edges"):
            print(f"Edges: {len(advanced_results.edges)}")
        if hasattr(advanced_results, "nodes"):
            print(f"Nodes: {len(advanced_results.nodes)}")
        if hasattr(advanced_results, "episodes"):
            print(f"Episodes: {len(advanced_results.episodes)}")
        if hasattr(advanced_results, "communities"):
            print(f"Communities: {len(advanced_results.communities)}")
            
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search())
