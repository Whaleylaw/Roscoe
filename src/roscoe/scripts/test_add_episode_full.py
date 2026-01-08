#!/usr/bin/env python3
"""Test full add_episode flow and capture results."""

import asyncio
import sys
sys.path.insert(0, "/deps/Roscoe/src")

async def test_add_episode():
    from datetime import datetime
    from roscoe.core.graphiti_client import get_graphiti, CASE_DATA_GROUP_ID
    from graphiti_core.nodes import EpisodeType
    
    print("Getting graphiti instance...")
    g = await get_graphiti()
    
    print(f"LLM Client: {type(g.llm_client).__name__}")
    print(f"Driver: {type(g.driver).__name__}")
    print(f"Database: {g.driver._database}")
    print(f"CASE_DATA_GROUP_ID: {CASE_DATA_GROUP_ID}")
    
    # Verify group_id matches database (this is the fix!)
    assert CASE_DATA_GROUP_ID == "roscoe_graph", f"Expected roscoe_graph, got {CASE_DATA_GROUP_ID}"
    print("VERIFIED: group_id matches database - episodes will go to roscoe_graph")
    
    episode_body = """Case: Caryn-McCay-MVA-7-30-2023
On September 21, 2023, paralegal Coleen Madayag contacted 
the client Caryn McCay at phone number 859-229-8183 to gather initial case information. 
She sent a Letter of Representation to Allstate Insurance for PIP claim 0723447272."""
    
    print(f"\nEpisode body:\n{episode_body}")
    print(f"\nGroup ID: {CASE_DATA_GROUP_ID}")
    print(f"Episode Type: {EpisodeType.text}")
    
    print("\n\nCalling add_episode...")
    try:
        result = await g.add_episode(
            name="Test: Caryn McCay intake (roscoe_graph)",
            episode_body=episode_body,
            source_description="test script",
            reference_time=datetime(2023, 9, 21),
            source=EpisodeType.text,
            group_id=CASE_DATA_GROUP_ID,
        )
        
        print(f"\n=== RESULTS ===")
        print(f"Result type: {type(result)}")
        
        if hasattr(result, 'episode'):
            print(f"\nEpisode UUID: {result.episode.uuid}")
            print(f"Episode group_id: {result.episode.group_id}")
        if hasattr(result, 'nodes'):
            print(f"\nNodes created: {len(result.nodes)}")
            for node in result.nodes:
                print(f"  - {node.name}")
        if hasattr(result, 'edges'):
            print(f"\nEdges created: {len(result.edges)}")
        if hasattr(result, 'episodic_edges'):
            print(f"\nEpisodic edges: {len(result.episodic_edges)}")
        
        print("\n=== SUCCESS: Episode added to roscoe_graph ===")
                
    except Exception as e:
        import traceback
        print(f"\nError: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_add_episode())
