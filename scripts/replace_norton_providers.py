#!/usr/bin/env python3
"""
Replace old Norton providers with new ones in the graph.

This script:
1. Loads replacement mappings from norton_replacements_FINAL.json
2. For each old → new mapping:
   - Finds all cases connected to old provider
   - Transfers relationships to new provider
   - Deletes old provider
3. Verifies no data loss

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/replace_norton_providers.py
"""

import json
import os
from pathlib import Path
from falkordb import FalkorDB


def replace_provider(graph, old_name: str, new_name: str, dry_run: bool = False):
    """Replace old provider with new provider, transferring all case relationships."""

    # Step 1: Check if old provider exists
    query = "MATCH (old:MedicalProvider {name: $old_name}) RETURN id(old), old.name"
    result = graph.query(query, {'old_name': old_name})

    if not result.result_set:
        return {'status': 'old_not_found', 'old_name': old_name}

    old_id = result.result_set[0][0]

    # Step 2: Get all cases connected to old provider
    query = """
    MATCH (c:Case)-[:TREATING_AT]->(old:MedicalProvider {name: $old_name})
    RETURN c.name, id(c)
    """
    result = graph.query(query, {'old_name': old_name})

    cases = [(row[0], row[1]) for row in result.result_set] if result.result_set else []

    if not cases:
        return {
            'status': 'no_cases',
            'old_name': old_name,
            'message': 'Old provider has no case connections'
        }

    # Step 3: Check if new provider exists
    query = "MATCH (new:MedicalProvider {name: $new_name}) RETURN id(new)"
    result = graph.query(query, {'new_name': new_name})

    new_exists = bool(result.result_set)

    if dry_run:
        return {
            'status': 'dry_run',
            'old_name': old_name,
            'old_id': old_id,
            'new_name': new_name,
            'new_exists': new_exists,
            'cases_affected': len(cases),
            'cases': [c[0] for c in cases]
        }

    # Step 4: Ensure new provider exists (should already be in graph from ingestion)
    if not new_exists:
        # New provider doesn't exist - this shouldn't happen if it's from the roster
        # But if it does, we need to abort
        return {
            'status': 'new_not_found',
            'old_name': old_name,
            'new_name': new_name,
            'error': 'New provider not found in graph'
        }

    # Step 5: Transfer all case relationships from old to new
    query = """
    MATCH (c:Case)-[r:TREATING_AT]->(old:MedicalProvider {name: $old_name})
    MATCH (new:MedicalProvider {name: $new_name})
    MERGE (c)-[:TREATING_AT]->(new)
    DELETE r
    RETURN count(*) as transferred
    """

    params = {'old_name': old_name, 'new_name': new_name}
    result = graph.query(query, params)

    transferred = result.result_set[0][0] if result.result_set else 0

    # Step 6: Delete old provider (only if it has no remaining relationships)
    query = """
    MATCH (old:MedicalProvider {name: $old_name})
    WHERE NOT (old)-[]-()
    DELETE old
    RETURN count(*) as deleted
    """

    result = graph.query(query, {'old_name': old_name})
    deleted = result.result_set[0][0] if result.result_set else 0

    return {
        'status': 'success',
        'old_name': old_name,
        'new_name': new_name,
        'cases_affected': len(cases),
        'relationships_transferred': transferred,
        'old_provider_deleted': deleted == 1,
        'cases': [c[0] for c in cases]
    }


def main():
    """Execute Norton provider replacements."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    # Load replacements (try multiple locations)
    possible_paths = [
        Path("/tmp/norton_replacements_FINAL.json"),
        Path("/home/aaronwhaley/norton_replacements_FINAL.json"),
        Path("/app/norton_replacements_FINAL.json"),
    ]

    replacements_file = None
    for p in possible_paths:
        if p.exists():
            replacements_file = p
            break

    if not replacements_file:
        print(f"❌ Replacements file not found in any of: {possible_paths}")
        return

    with open(replacements_file, 'r', encoding='utf-8') as f:
        replacements = json.load(f)

    print("="*70)
    print("NORTON PROVIDER REPLACEMENT")
    print("="*70)
    print(f"\nTotal replacements to execute: {len(replacements)}\n")

    # Pre-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_before = result.result_set[0][0]
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    rels_before = result.result_set[0][0]

    print(f"Nodes before: {nodes_before:,}")
    print(f"Relationships before: {rels_before:,}")

    # Canary check
    result = graph.query('MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-() RETURN count(r)')
    abby_before = result.result_set[0][0]
    print(f"Abby Sitgraves relationships: {abby_before}\n")

    # Execute replacements
    results = []

    for idx, repl in enumerate(replacements, 1):
        old_name = repl['old_name']
        new_name = repl['new_name']
        note = repl.get('note', '')

        print(f"{idx}. OLD: {old_name[:50]}")
        print(f"   NEW: {new_name[:50]}")

        # Skip if same name (nothing to do)
        if old_name == new_name:
            print(f"   ⊙ Same name - verifying exists")
            query = "MATCH (p:MedicalProvider {name: $name}) RETURN id(p)"
            result = graph.query(query, {'name': old_name})
            if result.result_set:
                print(f"   ✓ Provider exists\n")
                results.append({'status': 'same_name', 'old_name': old_name})
            else:
                print(f"   ⚠️  Provider not found in graph\n")
                results.append({'status': 'not_found', 'old_name': old_name})
            continue

        # Execute replacement
        result = replace_provider(graph, old_name, new_name, dry_run=False)

        if result['status'] == 'success':
            print(f"   ✓ Transferred {result['relationships_transferred']} relationships")
            print(f"   ✓ Deleted old provider: {result['old_provider_deleted']}")
            print(f"   Cases: {', '.join(result['cases'][:3])}")
            if len(result['cases']) > 3:
                print(f"          ... and {len(result['cases']) - 3} more")
        elif result['status'] == 'no_cases':
            print(f"   ⊙ {result['message']}")
        elif result['status'] == 'old_not_found':
            print(f"   ⚠️  Old provider not found in graph")
        elif result['status'] == 'new_not_found':
            print(f"   ❌ New provider not found in graph!")
        else:
            print(f"   ⚠️  {result.get('status', 'unknown')}")

        results.append(result)
        print()

    # Post-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_after = result.result_set[0][0]
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    rels_after = result.result_set[0][0]

    # Canary check
    result = graph.query('MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-() RETURN count(r)')
    abby_after = result.result_set[0][0]

    print("="*70)
    print("REPLACEMENT COMPLETE")
    print("="*70)
    print(f"Nodes before: {nodes_before:,}")
    print(f"Nodes after: {nodes_after:,}")
    print(f"Nodes deleted: {nodes_before - nodes_after}")
    print()
    print(f"Relationships before: {rels_before:,}")
    print(f"Relationships after: {rels_after:,}")
    print(f"Relationship changes: {rels_after - rels_before:+d}")
    print()
    print(f"Abby Sitgraves relationships before: {abby_before}")
    print(f"Abby Sitgraves relationships after: {abby_after}")

    if abby_after != abby_before:
        print(f"\n⚠️  WARNING: Abby Sitgraves relationship count changed!")

    # Summary
    successful = [r for r in results if r.get('status') == 'success']
    same_name = [r for r in results if r.get('status') == 'same_name']
    errors = [r for r in results if r.get('status') not in ['success', 'same_name', 'no_cases']]

    print(f"\nSummary:")
    print(f"  Successful replacements: {len(successful)}")
    print(f"  Same name (no change needed): {len(same_name)}")
    print(f"  Errors: {len(errors)}")

    if errors:
        print(f"\n  Errors:")
        for err in errors:
            print(f"    - {err.get('old_name', 'Unknown')}: {err.get('status', 'unknown')}")

    print("\n✅ Norton provider replacement complete")


if __name__ == "__main__":
    main()
