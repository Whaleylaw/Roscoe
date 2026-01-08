#!/usr/bin/env python3
"""
Test Episode Linking

Tests whether add_episode() correctly links to existing entities in the graph.
"""

import asyncio
from datetime import datetime


async def test_episode():
    """Test adding an episode and verify entity linking."""
    from roscoe.core.graphiti_client import add_case_episode, search_case, run_cypher_query
    
    print("=" * 60)
    print("TEST: Episode Linking")
    print("=" * 60)
    
    # Use an existing case
    case_name = "Abby-Sitgraves-MVA-7-13-2024"
    
    # First, check what entities exist for this case
    print(f"\n1. Checking existing entities for {case_name}...")
    
    query = """
    MATCH (c:Entity {name: $case_name, entity_type: 'Case'})
    OPTIONAL MATCH (c)-[r]->(related)
    RETURN c.name as case, type(r) as rel_type, related.name as related_name, related.entity_type as related_type
    LIMIT 20
    """
    results = await run_cypher_query(query, {"case_name": case_name})
    
    if results:
        print(f"   Found {len(results)} existing relationships:")
        for r in results[:10]:
            print(f"   - {r.get('rel_type')}: {r.get('related_name')} ({r.get('related_type')})")
    
    # Now add an episode that mentions existing entities
    print(f"\n2. Adding test episode...")
    
    # This episode mentions:
    # - The case name
    # - A known medical provider (we'll pick one from the existing data)
    # - A known insurer
    
    episode_body = f"""
    Case update for {case_name}:
    The client Abby Sitgraves had a follow-up appointment at Allstar Chiropractic today.
    Treatment is progressing well. The National Indemnity Company PIP claim is still pending.
    We received medical records from the provider and will submit them to the adjuster.
    """
    
    try:
        await add_case_episode(
            case_name=case_name,
            episode_name="Treatment Update",
            episode_body=episode_body,
            source="test",
            reference_time=datetime.now()
        )
        print("   Episode added successfully!")
    except Exception as e:
        print(f"   Error adding episode: {e}")
        return
    
    # Search to see if the episode is linked
    print(f"\n3. Searching for related information...")
    
    results = await search_case(
        query="What treatment is Abby Sitgraves receiving?",
        case_name=case_name,
        num_results=5
    )
    
    if results:
        print(f"   Found {len(results)} search results:")
        for i, r in enumerate(results[:3], 1):
            fact = getattr(r, 'fact', None) or str(r)
            print(f"   {i}. {fact[:100]}...")
    
    # Check if new relationships were created
    print(f"\n4. Checking for new relationships...")
    
    # Count edges in graph
    count_query = """
    MATCH (c:Entity {name: $case_name, entity_type: 'Case'})-[r]-()
    RETURN count(r) as relationship_count
    """
    counts = await run_cypher_query(count_query, {"case_name": case_name})
    if counts:
        print(f"   Case now has {counts[0].get('relationship_count')} relationships")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_episode())
