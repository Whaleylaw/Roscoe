#!/usr/bin/env python3
"""
Ingest doctors to FalkorDB.

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/ingest_doctors_direct.py

Ingests 20,732 Doctor entities from doctors.json.

NOTE: WORKS_AT relationships to MedicalProviders are NOT created yet
because doctor-to-facility matching is complex and requires additional logic.
"""

import json
import os
from pathlib import Path
from falkordb import FalkorDB


def ingest_doctors():
    """Ingest all doctors (nodes only, WORKS_AT relationships later)."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    # Try both possible paths
    possible_paths = [
        Path("/app/workspace_paralegal/json-files/memory-cards/entities/doctors.json"),
        Path("/mnt/workspace/json-files/memory-cards/entities/doctors.json"),
    ]

    file_path = None
    for p in possible_paths:
        if p.exists():
            file_path = p
            break

    if not file_path:
        print("❌ doctors.json not found")
        return

    print("="*70)
    print("DOCTORS INGESTION - PHASE 1f")
    print("="*70)
    print()

    # Pre-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_before = result.result_set[0][0]

    print(f"Nodes before: {nodes_before:,}\n")

    # Check for existing doctors
    result = graph.query("MATCH (d:Doctor) RETURN count(d)")
    existing_doctors = result.result_set[0][0] if result.result_set else 0
    print(f"Existing Doctor nodes: {existing_doctors}")

    # Load doctors
    print(f"\nLoading doctors from {file_path.name}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        doctors = json.load(f)

    print(f"✓ Loaded {len(doctors)} doctors\n")

    stats = {
        'created': 0,
        'matched': 0,
        'errors': []
    }

    # Process in large batches
    batch_size = 500
    total_batches = (len(doctors) + batch_size - 1) // batch_size

    for i in range(0, len(doctors), batch_size):
        batch = doctors[i:i+batch_size]
        batch_num = (i // batch_size) + 1

        print(f"Batch {batch_num}/{total_batches} ({len(batch)} doctors)...", end=' ')

        for doctor in batch:
            name = doctor['name']
            attrs = doctor.get('attributes', {})

            try:
                # Create doctor node (no WORKS_AT relationship yet)
                query = """
                MERGE (d:Doctor {name: $name, group_id: $group_id})
                ON CREATE SET d += $props, d.created_at = timestamp()
                ON MATCH SET d.updated_at = timestamp()
                RETURN d.name
                """

                params = {
                    'name': name,
                    'group_id': 'roscoe_graph',
                    'props': attrs
                }

                result = graph.query(query, params)

                if result.nodes_created > 0:
                    stats['created'] += 1
                else:
                    stats['matched'] += 1

            except Exception as e:
                error_msg = f"{name}: {str(e)}"
                stats['errors'].append(error_msg)

        print(f"Created: {stats['created']}, Matched: {stats['matched']}")

    print()

    # Post-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_after = result.result_set[0][0]

    nodes_added = nodes_after - nodes_before

    # Check Abby Sitgraves (canary)
    result = graph.query('MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-() RETURN count(r)')
    abby_rels = result.result_set[0][0]

    # Count doctors in graph
    result = graph.query("MATCH (d:Doctor) RETURN count(d)")
    total_doctors = result.result_set[0][0]

    print("="*70)
    print("INGESTION COMPLETE")
    print("="*70)
    print(f"Nodes before: {nodes_before:,}")
    print(f"Nodes after: {nodes_after:,}")
    print(f"Nodes added: {nodes_added:,}")
    print()
    print(f"Doctors created: {stats['created']:,}")
    print(f"Already existed: {stats['matched']:,}")
    print(f"Errors: {len(stats['errors'])}")
    print()
    print(f"Total Doctor nodes in graph: {total_doctors:,}")
    print(f"Expected: ~{len(doctors):,}")
    print()
    print(f"Abby Sitgraves relationships: {abby_rels} (should be 93)")

    if abby_rels != 93:
        print("\n⚠️  WARNING: Abby Sitgraves case relationships changed!")
        return False

    if stats['errors']:
        print("\n⚠️  Errors occurred (first 10):")
        for error in stats['errors'][:10]:
            print(f"  - {error}")

    print("\n✅ Phase 1f complete")
    print("\nNOTE: WORKS_AT relationships (Doctor → MedicalProvider) not created yet.")
    print("This requires doctor-to-facility matching logic (Phase 2).")

    return True


if __name__ == "__main__":
    ingest_doctors()
