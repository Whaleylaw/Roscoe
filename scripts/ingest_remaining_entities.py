#!/usr/bin/env python3
"""
Ingest all remaining entities from JSON files.

Phase 1g: Final Entity Ingestion
- Courts (106 total, ~83 new)
- Experts (2)
- Mediators (3)
- Witnesses (1)

Then reconnect ALL divisions to courts.

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/ingest_remaining_entities.py
"""

import json
import os
from pathlib import Path
from falkordb import FalkorDB


def ingest_entities_generic(graph, entity_type: str, file_path: Path):
    """Generic entity ingestion."""

    if not file_path.exists():
        return {'created': 0, 'matched': 0, 'errors': []}

    with open(file_path, 'r', encoding='utf-8') as f:
        entities = json.load(f)

    stats = {'created': 0, 'matched': 0, 'errors': []}

    print(f"{entity_type}: {len(entities)} entities")
    print("-" * 70)

    for entity in entities:
        name = entity['name']
        attrs = entity.get('attributes', {})

        try:
            query = f"""
            MERGE (e:{entity_type} {{name: $name, group_id: $group_id}})
            ON CREATE SET e += $props, e.created_at = timestamp()
            ON MATCH SET e.updated_at = timestamp()
            RETURN e.name
            """

            params = {
                'name': name,
                'group_id': 'roscoe_graph',
                'props': attrs
            }

            result = graph.query(query, params)

            if result.nodes_created > 0:
                stats['created'] += 1
                print(f"  ✓ Created: {name}")
            else:
                stats['matched'] += 1
                print(f"  ⊙ Exists: {name}")

        except Exception as e:
            error_msg = f"{name}: {str(e)}"
            stats['errors'].append(error_msg)
            print(f"  ❌ Error: {name[:40]}")

    print(f"\n  Summary: Created={stats['created']}, Matched={stats['matched']}")
    print()

    return stats


def reconnect_all_divisions(graph):
    """Reconnect ALL divisions to courts now that all courts exist."""

    print("="*70)
    print("RECONNECTING ALL DIVISIONS TO COURTS")
    print("="*70)
    print()

    stats = {}

    # 1. CircuitDivision → Court
    print("CircuitDivision → Court...")
    query = """
    MATCH (div:CircuitDivision)
    WHERE div.court_name IS NOT NULL
    WITH div
    MATCH (c:Court {name: div.court_name})
    MERGE (div)-[:PART_OF]->(c)
    RETURN count(*) as created
    """

    result = graph.query(query)
    stats['circuit'] = result.result_set[0][0] if result.result_set else 0
    print(f"  ✓ {stats['circuit']} relationships\n")

    # 2. DistrictDivision → Court
    print("DistrictDivision → Court...")
    query = """
    MATCH (div:DistrictDivision)
    WHERE div.court_name IS NOT NULL
    WITH div
    MATCH (c:Court {name: div.court_name})
    MERGE (div)-[:PART_OF]->(c)
    RETURN count(*) as created
    """

    result = graph.query(query)
    stats['district'] = result.result_set[0][0] if result.result_set else 0
    print(f"  ✓ {stats['district']} relationships\n")

    # 3. AppellateDistrict → Court
    print("AppellateDistrict → Court of Appeals...")
    query = """
    MATCH (div:AppellateDistrict)
    MATCH (c:Court {name: "Kentucky Court of Appeals"})
    MERGE (div)-[:PART_OF]->(c)
    RETURN count(*) as created
    """

    result = graph.query(query)
    stats['appellate'] = result.result_set[0][0] if result.result_set else 0
    print(f"  ✓ {stats['appellate']} relationships\n")

    # 4. SupremeCourtDistrict → Supreme Court
    print("SupremeCourtDistrict → Supreme Court...")
    query = """
    MATCH (div:SupremeCourtDistrict)
    MATCH (c:Court {name: "Kentucky Supreme Court"})
    MERGE (div)-[:PART_OF]->(c)
    RETURN count(*) as created
    """

    result = graph.query(query)
    stats['supreme'] = result.result_set[0][0] if result.result_set else 0
    print(f"  ✓ {stats['supreme']} relationships\n")

    total = sum(stats.values())
    print(f"Total Division → Court relationships: {total}")

    return stats


def main():
    """Ingest all remaining entities."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    entities_dir = Path("/mnt/workspace/json-files/memory-cards/entities")

    print("="*70)
    print("REMAINING ENTITIES INGESTION - PHASE 1g")
    print("="*70)
    print()

    # Pre-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_before = result.result_set[0][0]
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    rels_before = result.result_set[0][0]

    print(f"Nodes before: {nodes_before:,}")
    print(f"Relationships before: {rels_before:,}\n")

    all_stats = {'created': 0, 'matched': 0, 'errors': []}

    # Ingest each entity type
    entity_files = [
        ("Court", "courts.json"),
        ("Expert", "experts.json"),
        ("Mediator", "mediators.json"),
        ("Witness", "witnesses.json"),
    ]

    for entity_type, filename in entity_files:
        file_path = entities_dir / filename

        if not file_path.exists():
            print(f"⚠️  File not found: {filename}\n")
            continue

        stats = ingest_entities_generic(graph, entity_type, file_path)

        all_stats['created'] += stats['created']
        all_stats['matched'] += stats['matched']
        all_stats['errors'].extend(stats['errors'])

    # Reconnect all divisions now that all courts exist
    division_stats = reconnect_all_divisions(graph)

    # Post-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_after = result.result_set[0][0]
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    rels_after = result.result_set[0][0]

    nodes_added = nodes_after - nodes_before
    rels_added = rels_after - rels_before

    # Check Abby Sitgraves (canary)
    result = graph.query('MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-() RETURN count(r)')
    abby_rels = result.result_set[0][0]

    # Count courts
    result = graph.query("MATCH (c:Court) RETURN count(c)")
    total_courts = result.result_set[0][0]

    # Count Division → Court relationships
    result = graph.query("MATCH (div)-[:PART_OF]->(c:Court) WHERE labels(div)[0] CONTAINS 'Division' RETURN count(*)")
    div_court_rels = result.result_set[0][0]

    print("\n" + "="*70)
    print("INGESTION COMPLETE")
    print("="*70)
    print(f"Nodes before: {nodes_before:,}")
    print(f"Nodes after: {nodes_after:,}")
    print(f"Nodes added: {nodes_added:,}")
    print()
    print(f"Relationships before: {rels_before:,}")
    print(f"Relationships after: {rels_after:,}")
    print(f"Relationships added: {rels_added:,}")
    print()
    print(f"Courts created: {all_stats['created']}")
    print(f"Courts existed: {all_stats['matched']}")
    print(f"Total Court nodes: {total_courts}")
    print()
    print(f"Division → Court relationships: {div_court_rels}")
    print(f"Errors: {len(all_stats['errors'])}")
    print()
    print(f"Abby Sitgraves relationships: {abby_rels} (should be 93)")

    if abby_rels != 93:
        print("\n⚠️  WARNING: Abby Sitgraves case relationships changed!")
        return False

    print("\n✅ Phase 1g complete - All remaining entities ingested")
    print(f"✅ All {div_court_rels} divisions now connected to courts")

    return True


if __name__ == "__main__":
    main()
