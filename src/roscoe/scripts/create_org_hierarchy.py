#!/usr/bin/env python3
"""
Create Organization Hierarchy

Creates parent Organization nodes for healthcare systems and links
existing MedicalProvider/DirectoryEntry nodes via PART_OF relationships.

This enables queries like:
- "Which cases have we sent to any Norton facility?"
- "Total bills across all Jewish Hospital locations?"
- "Who handles lien negotiations for UofL Health?"

Usage:
    python -m roscoe.scripts.create_org_hierarchy
"""

import asyncio
from typing import Optional


# Define parent organizations and their matching patterns
# Format: { "Organization Name": ["pattern1", "pattern2", ...] }
HEALTHCARE_SYSTEMS = {
    "Norton Healthcare": [
        "Norton",
    ],
    "Baptist Health": [
        "Baptist Health",
    ],
    "UofL Health": [
        "UofL",
        "University of Louisville",
    ],
    "Appalachian Regional Healthcare (ARH)": [
        "ARH",
    ],
    "Jewish Hospital / UofL Health": [
        "Jewish Hospital",
        "Jewish",
    ],
    "CHI Saint Joseph Health": [
        "CHI Saint Joseph",
        "Saint Joseph",
    ],
    "Clark Regional Medical Center": [
        "Clark Regional",
    ],
    "UK HealthCare": [
        "UK Healthcare",
        "UK HealthCare",
    ],
    "Kindred Healthcare": [
        "Kindred",
    ],
    "Pikeville Medical Center": [
        "Pikeville Medical",
    ],
    "KORT Physical Therapy": [
        "KORT",
    ],
    "ProRehab Physical Therapy": [
        "ProRehab",
    ],
    "Results Physiotherapy": [
        "Results Physio",
    ],
    "Vitality Pain Center": [
        "Vitality",
    ],
}

# Additional insurance company hierarchies
INSURANCE_SYSTEMS = {
    "State Farm": [
        "State Farm",
    ],
    "Progressive": [
        "Progressive",
    ],
    "Kentucky Farm Bureau": [
        "Kentucky Farm Bureau",
        "KFB",
    ],
    "Allstate": [
        "Allstate",
    ],
    "GEICO": [
        "GEICO",
        "Geico",
    ],
    "Nationwide": [
        "Nationwide",
    ],
}


async def run_query(query: str, params: dict = None):
    """Execute a Cypher query."""
    from roscoe.core.graphiti_client import run_cypher_query
    try:
        return await run_cypher_query(query, params or {})
    except Exception as e:
        print(f"  Error: {e}")
        return []


async def create_organization(name: str, org_type: str = "HealthcareSystem") -> bool:
    """Create an Organization node."""
    query = """
    MERGE (o:Entity {name: $name, entity_type: 'Organization'})
    ON CREATE SET o.org_type = $org_type
    RETURN o.name as name
    """
    result = await run_query(query, {"name": name, "org_type": org_type})
    return bool(result)


async def link_entities_to_org(org_name: str, patterns: list[str], entity_types: list[str]) -> int:
    """
    Link existing entities to an organization based on name patterns.
    
    Args:
        org_name: Name of the parent organization
        patterns: List of name patterns to match
        entity_types: Entity types to search (e.g., ['MedicalProvider', 'DirectoryEntry'])
    
    Returns:
        Number of entities linked
    """
    total_linked = 0
    
    for pattern in patterns:
        for entity_type in entity_types:
            # Find entities matching pattern and create PART_OF relationship
            query = """
            MATCH (e:Entity {entity_type: $entity_type})
            WHERE toLower(e.name) CONTAINS toLower($pattern)
            AND e.name <> $org_name
            MATCH (o:Entity {name: $org_name, entity_type: 'Organization'})
            MERGE (e)-[:PART_OF]->(o)
            RETURN count(e) as linked
            """
            result = await run_query(query, {
                "entity_type": entity_type,
                "pattern": pattern,
                "org_name": org_name
            })
            if result:
                linked = result[0].get('linked', 0)
                total_linked += linked
    
    return total_linked


async def main():
    print("=" * 60)
    print("CREATING ORGANIZATION HIERARCHY")
    print("=" * 60)
    
    # Healthcare systems
    print("\n=== Healthcare Systems ===")
    for org_name, patterns in HEALTHCARE_SYSTEMS.items():
        # Create organization
        await create_organization(org_name, "HealthcareSystem")
        
        # Link medical providers and directory entries
        linked = await link_entities_to_org(
            org_name, 
            patterns, 
            ["MedicalProvider", "DirectoryEntry"]
        )
        print(f"  {org_name}: {linked} locations linked")
    
    # Insurance systems
    print("\n=== Insurance Systems ===")
    for org_name, patterns in INSURANCE_SYSTEMS.items():
        # Create organization
        await create_organization(org_name, "InsuranceSystem")
        
        # Link insurers and directory entries
        linked = await link_entities_to_org(
            org_name, 
            patterns, 
            ["Insurer", "DirectoryEntry"]
        )
        print(f"  {org_name}: {linked} entities linked")
    
    # Summary
    print("\n=== Summary ===")
    
    # Count organizations
    org_count = await run_query("""
        MATCH (o:Entity {entity_type: 'Organization'})
        RETURN count(o) as count
    """)
    print(f"Total Organizations: {org_count[0]['count'] if org_count else 0}")
    
    # Count PART_OF relationships
    part_of_count = await run_query("""
        MATCH ()-[r:PART_OF]->()
        RETURN count(r) as count
    """)
    print(f"Total PART_OF relationships: {part_of_count[0]['count'] if part_of_count else 0}")
    
    # Show sample hierarchy
    print("\n=== Sample: Norton Healthcare hierarchy ===")
    norton = await run_query("""
        MATCH (loc)-[:PART_OF]->(o:Entity {name: 'Norton Healthcare'})
        RETURN loc.name as location, loc.entity_type as type
        ORDER BY loc.name
        LIMIT 10
    """)
    for r in norton:
        print(f"  - {r['location']} ({r['type']})")
    
    print("\n" + "=" * 60)
    print("HIERARCHY CREATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
