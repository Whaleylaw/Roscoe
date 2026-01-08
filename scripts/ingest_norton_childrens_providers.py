#!/usr/bin/env python3
"""
Ingest Norton Children's providers to FalkorDB.

Ingests 140 Norton Children's locations with deduplication.

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/ingest_norton_childrens_providers.py
"""

import json
import os
from pathlib import Path
from falkordb import FalkorDB


def ingest_norton_childrens():
    """Ingest Norton Children's providers with deduplication."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    # Load Norton Children's locations
    possible_paths = [
        Path("/app/workspace_paralegal/json-files/norton_childrens_locations.json"),
        Path("/mnt/workspace/json-files/norton_childrens_locations.json"),
    ]

    file_path = None
    for p in possible_paths:
        if p.exists():
            file_path = p
            break

    if not file_path:
        print("❌ norton_childrens_locations.json not found")
        return

    print("="*70)
    print("NORTON CHILDREN'S PROVIDERS INGESTION")
    print("="*70)
    print()

    # Pre-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_before = result.result_set[0][0]
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    rels_before = result.result_set[0][0]

    print(f"Nodes before: {nodes_before:,}")
    print(f"Relationships before: {rels_before:,}")

    # Get existing Norton Children's providers
    print("\nQuerying existing Norton Children's providers...")
    result = graph.query("MATCH (p:MedicalProvider) WHERE p.name CONTAINS \"Norton Children\" RETURN p.name")
    existing_names = set(row[0] for row in result.result_set) if result.result_set else set()
    print(f"✓ Found {len(existing_names)} existing Norton Children's providers\n")

    # Load new providers
    with open(file_path, 'r', encoding='utf-8') as f:
        all_providers = json.load(f)

    print(f"Loaded {len(all_providers)} providers from file")

    # Filter to only new ones
    new_providers = [p for p in all_providers if p['name'] not in existing_names]
    print(f"After deduplication: {len(new_providers)} NEW providers to ingest\n")

    stats = {
        'created': 0,
        'relationships': 0,
        'errors': [],
        'skipped': len(all_providers) - len(new_providers)
    }

    # Process new providers
    batch_size = 50
    total_batches = (len(new_providers) + batch_size - 1) // batch_size

    for i in range(0, len(new_providers), batch_size):
        batch = new_providers[i:i+batch_size]
        batch_num = (i // batch_size) + 1

        print(f"Batch {batch_num}/{total_batches} ({len(batch)} providers)...")

        for provider in batch:
            name = provider['name']
            attrs = provider.get('attributes', {})

            try:
                # Create provider node
                query = """
                MERGE (p:MedicalProvider {name: $name, group_id: $group_id})
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

                    # Create PART_OF relationship to Norton Children's Hospital
                    rel_query = """
                    MATCH (p:MedicalProvider {name: $provider_name})
                    MATCH (h:HealthSystem {name: "Norton Children's Hospital"})
                    MERGE (p)-[:PART_OF]->(h)
                    """

                    rel_params = {'provider_name': name}

                    try:
                        rel_result = graph.query(rel_query, rel_params)
                        if rel_result.relationships_created > 0:
                            stats['relationships'] += 1
                    except:
                        pass

            except Exception as e:
                error_msg = f"{name}: {str(e)}"
                stats['errors'].append(error_msg)

        print(f"  → Created: {stats['created']}, Relationships: {stats['relationships']}")

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

    # Count Norton Children's providers
    result = graph.query('MATCH (p:MedicalProvider)-[:PART_OF]->(h:HealthSystem {name: "Norton Children\'s Hospital"}) RETURN count(p)')
    norton_childrens_total = result.result_set[0][0]

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
    print(f"Providers created: {stats['created']}")
    print(f"Already existed (skipped): {stats['skipped']}")
    print(f"PART_OF relationships: {stats['relationships']}")
    print(f"Errors: {len(stats['errors'])}")
    print()
    print(f"Total Norton Children's providers in graph: {norton_childrens_total}")
    print(f"Expected: ~{len(all_providers)}")
    print()
    print(f"Abby Sitgraves relationships: {abby_rels} (should be 93)")

    if abby_rels != 93:
        print("\n⚠️  WARNING: Abby Sitgraves case relationships changed!")
        return False

    print("\n✅ Norton Children's providers ingested")
    return True


if __name__ == "__main__":
    ingest_norton_childrens()
