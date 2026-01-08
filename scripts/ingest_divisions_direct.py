#!/usr/bin/env python3
"""
Ingest court divisions to FalkorDB using falkordb Python module.

Run this inside the roscoe-agents container or anywhere with falkordb installed:
  docker exec roscoe-agents python3 /deps/Roscoe/scripts/ingest_divisions_direct.py
"""

import json
import os
from pathlib import Path
from falkordb import FalkorDB


def ingest_divisions():
    """Ingest all court divisions."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    # Find JSON files
    entities_dir = Path("/mnt/workspace/json-files/memory-cards/entities")
    if not entities_dir.exists():
        print(f"❌ Directory not found: {entities_dir}")
        return

    division_files = [
        ("CircuitDivision", "circuit_divisions.json"),
        ("DistrictDivision", "district_divisions.json"),
        ("AppellateDistrict", "appellate_districts.json"),
        ("SupremeCourtDistrict", "supreme_court_districts.json"),
    ]

    all_stats = {'created': 0, 'matched': 0, 'errors': []}

    print("="*70)
    print("COURT DIVISIONS INGESTION - PHASE 1b")
    print("="*70)
    print()

    # Pre-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_before = result.result_set[0][0]
    print(f"Nodes before: {nodes_before:,}\n")

    for entity_type, filename in division_files:
        file_path = entities_dir / filename

        if not file_path.exists():
            print(f"⚠️  File not found: {filename}\n")
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            divisions = json.load(f)

        print(f"{entity_type}: {len(divisions)} entities")
        print("-" * 70)

        stats = {'created': 0, 'matched': 0}

        for div in divisions:
            name = div['name']
            attrs = div.get('attributes', {})

            # Build property map
            props = {'name': name, 'group_id': 'roscoe_graph'}
            props.update({k: v for k, v in attrs.items() if v is not None and v != ""})

            try:
                # Use parameterized query
                query = f"""
                MERGE (h:{entity_type} {{name: $name, group_id: $group_id}})
                ON CREATE SET h += $props, h.created_at = timestamp()
                ON MATCH SET h.updated_at = timestamp()
                RETURN h.name
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
                all_stats['errors'].append(error_msg)
                print(f"  ❌ Error: {name[:50]}... - {str(e)[:50]}")

        all_stats['created'] += stats['created']
        all_stats['matched'] += stats['matched']

        print(f"\n  Summary: Created={stats['created']}, Matched={stats['matched']}")
        print()

    # Post-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_after = result.result_set[0][0]
    added = nodes_after - nodes_before

    # Check Abby Sitgraves (canary)
    result = graph.query('MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-() RETURN count(r)')
    abby_rels = result.result_set[0][0]

    print("="*70)
    print("INGESTION COMPLETE")
    print("="*70)
    print(f"Nodes before: {nodes_before:,}")
    print(f"Nodes after: {nodes_after:,}")
    print(f"Nodes added: {added:,}")
    print(f"Expected: 192")
    print()
    print(f"Created: {all_stats['created']}")
    print(f"Already existed: {all_stats['matched']}")
    print(f"Errors: {len(all_stats['errors'])}")
    print()
    print(f"Abby Sitgraves relationships: {abby_rels} (should be 93)")

    if abby_rels != 93:
        print("\n⚠️  WARNING: Abby Sitgraves case relationships changed!")
        return False

    if all_stats['errors']:
        print("\n⚠️  Errors occurred:")
        for error in all_stats['errors'][:10]:
            print(f"  - {error}")

    print("\n✅ Phase 1b complete")
    return True


if __name__ == "__main__":
    ingest_divisions()
