#!/usr/bin/env python3
"""
Ingest court personnel to FalkorDB with WORKS_AT/APPOINTED_BY relationships.

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/ingest_court_personnel_direct.py

Ingests:
- 121 CourtClerk → WORKS_AT → Court
- 114 MasterCommissioner → APPOINTED_BY → Court
- 7 CourtAdministrator → WORKS_AT → Court

Total: 242 personnel
"""

import json
import os
from pathlib import Path
from falkordb import FalkorDB


def ingest_court_personnel():
    """Ingest all court personnel with relationships."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    # Find JSON files
    entities_dir = Path("/mnt/workspace/json-files/memory-cards/entities")

    personnel_files = [
        ("CourtClerk", "court_clerks.json", "WORKS_AT"),
        ("MasterCommissioner", "master_commissioners.json", "APPOINTED_BY"),
        ("CourtAdministrator", "court_administrators.json", "WORKS_AT"),
    ]

    print("="*70)
    print("COURT PERSONNEL INGESTION - PHASE 1d")
    print("="*70)
    print()

    # Pre-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_before = result.result_set[0][0]
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    rels_before = result.result_set[0][0]

    print(f"Nodes before: {nodes_before:,}")
    print(f"Relationships before: {rels_before:,}\n")

    all_stats = {'created': 0, 'matched': 0, 'relationships': 0, 'errors': []}

    for entity_type, filename, relationship_type in personnel_files:
        file_path = entities_dir / filename

        if not file_path.exists():
            print(f"⚠️  File not found: {filename}\n")
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            personnel = json.load(f)

        print(f"{entity_type}: {len(personnel)} entities")
        print("-" * 70)

        stats = {'created': 0, 'matched': 0, 'relationships': 0, 'missing_courts': []}

        for person in personnel:
            name = person['name']
            attrs = person.get('attributes', {})

            try:
                # Create personnel node
                query = f"""
                MERGE (p:{entity_type} {{name: $name, group_id: $group_id}})
                ON CREATE SET p += $props, p.created_at = timestamp()
                ON MATCH SET p.updated_at = timestamp()
                RETURN p.name
                """

                params = {
                    'name': name,
                    'group_id': 'roscoe_graph',
                    'props': attrs
                }

                result = graph.query(query, params)

                if result.nodes_created > 0:
                    stats['created'] += 1
                    status = "Created"
                else:
                    stats['matched'] += 1
                    status = "Exists"

                # Create WORKS_AT or APPOINTED_BY relationship to court
                court_name = attrs.get('court', '') or attrs.get('county', '')

                if court_name:
                    # Try to find court by name (may need normalization)
                    # For clerks, court name is like "Jefferson County Circuit Court"
                    # For commissioners, county is like "Jefferson"

                    if "County" not in court_name and court_name:
                        # Just county name - try to find circuit court
                        court_search = f"{court_name} County Circuit Court"
                    else:
                        court_search = court_name

                    rel_query = f"""
                    MATCH (p:{entity_type} {{name: $person_name}})
                    MATCH (c:Court {{name: $court_name}})
                    MERGE (p)-[:{relationship_type}]->(c)
                    """

                    rel_params = {
                        'person_name': name,
                        'court_name': court_search
                    }

                    try:
                        rel_result = graph.query(rel_query, rel_params)
                        if rel_result.relationships_created > 0:
                            stats['relationships'] += 1
                            print(f"  ✓ {status}: {name} → {court_search[:40]}")
                        else:
                            stats['missing_courts'].append(f"{name} → {court_search}")
                            print(f"  ⊙ {status}: {name} (court not found: {court_search[:40]})")
                    except Exception as e:
                        stats['missing_courts'].append(f"{name} → {court_search}: {str(e)}")
                        print(f"  ⊙ {status}: {name} (relationship error)")
                else:
                    print(f"  ⊙ {status}: {name} (no court info)")

            except Exception as e:
                error_msg = f"{name}: {str(e)}"
                all_stats['errors'].append(error_msg)
                print(f"  ❌ Error: {name[:40]}... - {str(e)[:50]}")

        all_stats['created'] += stats['created']
        all_stats['matched'] += stats['matched']
        all_stats['relationships'] += stats['relationships']

        print(f"\n  Summary: Created={stats['created']}, Matched={stats['matched']}, Relationships={stats['relationships']}")
        if stats['missing_courts']:
            print(f"  Missing courts: {len(stats['missing_courts'])}")
        print()

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

    print("="*70)
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
    print(f"Created: {all_stats['created']}")
    print(f"Already existed: {all_stats['matched']}")
    print(f"WORKS_AT/APPOINTED_BY relationships: {all_stats['relationships']}")
    print(f"Errors: {len(all_stats['errors'])}")
    print()
    print(f"Abby Sitgraves relationships: {abby_rels} (should be 93)")

    if abby_rels != 93:
        print("\n⚠️  WARNING: Abby Sitgraves case relationships changed!")
        return False

    print("\n✅ Phase 1d complete")
    return True


if __name__ == "__main__":
    ingest_court_personnel()
