#!/usr/bin/env python3
"""
Create missing structural relationships in the knowledge graph.

Phase 2: Structural Relationships
- Connect divisions to parent courts (PART_OF)
- Connect any other hierarchical relationships

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/create_structural_relationships.py
"""

import os
from falkordb import FalkorDB


def create_division_court_relationships():
    """Create PART_OF relationships from divisions to courts."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    print("="*70)
    print("STRUCTURAL RELATIONSHIPS - PHASE 2")
    print("="*70)
    print()

    # Pre-check
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    rels_before = result.result_set[0][0]
    print(f"Relationships before: {rels_before:,}\n")

    stats = {
        'circuit_divisions': 0,
        'district_divisions': 0,
        'appellate_districts': 0,
        'supreme_districts': 0,
        'errors': []
    }

    # 1. CircuitDivision → Court (PART_OF)
    print("Creating CircuitDivision → Court relationships...")
    print("-" * 70)

    query = """
    MATCH (div:CircuitDivision)
    WHERE div.court_name IS NOT NULL
    WITH div
    MATCH (c:Court {name: div.court_name})
    MERGE (div)-[:PART_OF]->(c)
    RETURN count(*) as created
    """

    try:
        result = graph.query(query)
        if result.result_set:
            created = result.result_set[0][0]
            stats['circuit_divisions'] = created
            print(f"✓ Created {created} CircuitDivision → Court relationships")
        else:
            print("⊙ No relationships created")
    except Exception as e:
        stats['errors'].append(f"CircuitDivision: {str(e)}")
        print(f"❌ Error: {str(e)}")

    print()

    # 2. DistrictDivision → Court (PART_OF)
    print("Creating DistrictDivision → Court relationships...")
    print("-" * 70)

    query = """
    MATCH (div:DistrictDivision)
    WHERE div.court_name IS NOT NULL
    WITH div
    MATCH (c:Court {name: div.court_name})
    MERGE (div)-[:PART_OF]->(c)
    RETURN count(*) as created
    """

    try:
        result = graph.query(query)
        if result.result_set:
            created = result.result_set[0][0]
            stats['district_divisions'] = created
            print(f"✓ Created {created} DistrictDivision → Court relationships")
        else:
            print("⊙ No relationships created")
    except Exception as e:
        stats['errors'].append(f"DistrictDivision: {str(e)}")
        print(f"❌ Error: {str(e)}")

    print()

    # 3. AppellateDistrict → Court of Appeals (PART_OF)
    print("Creating AppellateDistrict → Court relationships...")
    print("-" * 70)

    # All appellate districts are part of "Kentucky Court of Appeals"
    query = """
    MATCH (div:AppellateDistrict)
    MERGE (c:Court {name: "Kentucky Court of Appeals", group_id: "roscoe_graph"})
    ON CREATE SET c.created_at = timestamp()
    MERGE (div)-[:PART_OF]->(c)
    RETURN count(*) as created
    """

    try:
        result = graph.query(query)
        if result.result_set:
            created = result.result_set[0][0]
            stats['appellate_districts'] = created
            print(f"✓ Created {created} AppellateDistrict → Court relationships")
        else:
            print("⊙ No relationships created")
    except Exception as e:
        stats['errors'].append(f"AppellateDistrict: {str(e)}")
        print(f"❌ Error: {str(e)}")

    print()

    # 4. SupremeCourtDistrict → Supreme Court (PART_OF)
    print("Creating SupremeCourtDistrict → Court relationships...")
    print("-" * 70)

    # All supreme court districts are part of "Kentucky Supreme Court"
    query = """
    MATCH (div:SupremeCourtDistrict)
    MERGE (c:Court {name: "Kentucky Supreme Court", group_id: "roscoe_graph"})
    ON CREATE SET c.created_at = timestamp()
    MERGE (div)-[:PART_OF]->(c)
    RETURN count(*) as created
    """

    try:
        result = graph.query(query)
        if result.result_set:
            created = result.result_set[0][0]
            stats['supreme_districts'] = created
            print(f"✓ Created {created} SupremeCourtDistrict → Court relationships")
        else:
            print("⊙ No relationships created")
    except Exception as e:
        stats['errors'].append(f"SupremeCourtDistrict: {str(e)}")
        print(f"❌ Error: {str(e)}")

    print()

    # Post-check
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    rels_after = result.result_set[0][0]

    rels_added = rels_after - rels_before

    # Verify Abby Sitgraves (canary)
    result = graph.query('MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-() RETURN count(r)')
    abby_rels = result.result_set[0][0]

    # Count PART_OF relationships
    result = graph.query("MATCH ()-[r:PART_OF]->() RETURN count(r)")
    part_of_total = result.result_set[0][0]

    print("="*70)
    print("STRUCTURAL RELATIONSHIPS COMPLETE")
    print("="*70)
    print(f"Relationships before: {rels_before:,}")
    print(f"Relationships after: {rels_after:,}")
    print(f"Relationships added: {rels_added:,}")
    print()
    print(f"CircuitDivision → Court: {stats['circuit_divisions']}")
    print(f"DistrictDivision → Court: {stats['district_divisions']}")
    print(f"AppellateDistrict → Court: {stats['appellate_districts']}")
    print(f"SupremeCourtDistrict → Court: {stats['supreme_districts']}")
    print(f"Errors: {len(stats['errors'])}")
    print()
    print(f"Total PART_OF relationships: {part_of_total:,}")
    print(f"Abby Sitgraves relationships: {abby_rels} (should be 93)")

    if abby_rels != 93:
        print("\n⚠️  WARNING: Abby Sitgraves case relationships changed!")
        return False

    if stats['errors']:
        print("\nErrors:")
        for error in stats['errors']:
            print(f"  - {error}")

    print("\n✅ Phase 2 complete - All structural relationships created")
    return True


if __name__ == "__main__":
    create_division_court_relationships()
