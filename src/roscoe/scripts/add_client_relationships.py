#!/usr/bin/env python3
"""
Add Client-Level Relationships to Existing Graph

Creates bidirectional client-level relationships:
- Client -TREATED_BY-> MedicalProvider
- Client -HAS_INSURANCE_WITH-> Insurer
- Client -HAS_LIEN_FROM-> LienHolder

These relationships enable queries like "all providers this client has ever seen"
without traversing through Case entities.

Usage:
    python -m roscoe.scripts.add_client_relationships
"""

import asyncio


async def add_client_relationships():
    """Add client-level relationships to the graph."""
    from roscoe.core.graphiti_client import run_cypher_query
    
    print("=" * 60)
    print("ADDING CLIENT-LEVEL RELATIONSHIPS")
    print("=" * 60)
    
    total_relationships = 0
    
    # 1. Client -TREATED_BY-> MedicalProvider
    print("\n=== Client -TREATED_BY-> MedicalProvider ===")
    print("  Traversing: Client <-HAS_CLIENT- Case -TREATING_AT-> Provider")
    
    treated_by_query = """
    MATCH (client:Entity {entity_type: 'Client'})<-[:HAS_CLIENT]-(case:Entity {entity_type: 'Case'})-[:TREATING_AT]->(provider:Entity {entity_type: 'MedicalProvider'})
    MERGE (client)-[:TREATED_BY]->(provider)
    RETURN count(*) as created
    """
    result = await run_cypher_query(treated_by_query)
    treated_count = result[0].get('created', 0) if result else 0
    print(f"  Created {treated_count} relationships")
    total_relationships += treated_count
    
    # 2. Client -HAS_INSURANCE_WITH-> Insurer
    print("\n=== Client -HAS_INSURANCE_WITH-> Insurer ===")
    print("  Traversing: Client <-HAS_CLIENT- Case -HAS_CLAIM-> Claim -INSURED_BY-> Insurer")
    
    insurance_query = """
    MATCH (client:Entity {entity_type: 'Client'})<-[:HAS_CLIENT]-(case:Entity {entity_type: 'Case'})-[:HAS_CLAIM]->(claim:Entity {entity_type: 'InsuranceClaim'})-[:INSURED_BY]->(insurer:Entity {entity_type: 'Insurer'})
    MERGE (client)-[:HAS_INSURANCE_WITH]->(insurer)
    RETURN count(*) as created
    """
    result = await run_cypher_query(insurance_query)
    insurance_count = result[0].get('created', 0) if result else 0
    print(f"  Created {insurance_count} relationships")
    total_relationships += insurance_count
    
    # 3. Client -HAS_LIEN_FROM-> LienHolder
    print("\n=== Client -HAS_LIEN_FROM-> LienHolder ===")
    print("  Traversing: Client <-HAS_CLIENT- Case -HAS_LIEN-> Lien -HELD_BY-> LienHolder")
    
    lien_query = """
    MATCH (client:Entity {entity_type: 'Client'})<-[:HAS_CLIENT]-(case:Entity {entity_type: 'Case'})-[:HAS_LIEN]->(lien:Entity {entity_type: 'Lien'})-[:HELD_BY]->(holder:Entity {entity_type: 'LienHolder'})
    MERGE (client)-[:HAS_LIEN_FROM]->(holder)
    RETURN count(*) as created
    """
    result = await run_cypher_query(lien_query)
    lien_count = result[0].get('created', 0) if result else 0
    print(f"  Created {lien_count} relationships")
    total_relationships += lien_count
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  TREATED_BY relationships:        {treated_count}")
    print(f"  HAS_INSURANCE_WITH relationships: {insurance_count}")
    print(f"  HAS_LIEN_FROM relationships:      {lien_count}")
    print(f"  Total new relationships:          {total_relationships}")
    print("=" * 60)
    
    # Verify - show sample queries
    print("\n=== Verification Queries ===")
    
    # Check how many clients have TREATED_BY relationships
    verify_query = """
    MATCH (c:Entity {entity_type: 'Client'})-[:TREATED_BY]->(p:Entity {entity_type: 'MedicalProvider'})
    WITH c, count(p) as provider_count
    RETURN c.name as client, provider_count
    ORDER BY provider_count DESC
    LIMIT 5
    """
    result = await run_cypher_query(verify_query)
    if result:
        print("\nTop 5 clients by provider count:")
        for r in result:
            print(f"  {r.get('client')}: {r.get('provider_count')} providers")
    
    # Check clients with multiple insurers
    verify_insurers = """
    MATCH (c:Entity {entity_type: 'Client'})-[:HAS_INSURANCE_WITH]->(i:Entity {entity_type: 'Insurer'})
    WITH c, count(DISTINCT i) as insurer_count
    WHERE insurer_count > 1
    RETURN c.name as client, insurer_count
    ORDER BY insurer_count DESC
    LIMIT 5
    """
    result = await run_cypher_query(verify_insurers)
    if result:
        print("\nClients with multiple insurers:")
        for r in result:
            print(f"  {r.get('client')}: {r.get('insurer_count')} insurers")
    
    return total_relationships


def main():
    asyncio.run(add_client_relationships())


if __name__ == "__main__":
    main()
