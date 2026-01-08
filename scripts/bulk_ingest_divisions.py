#!/usr/bin/env python3
"""
Bulk ingest all court divisions to FalkorDB.

Generates and executes Cypher queries for:
- 86 CircuitDivision
- 94 DistrictDivision
- 5 AppellateDistrict
- 7 SupremeCourtDistrict

Total: 192 divisions
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime


def escape_cypher(value):
    """Escape value for Cypher."""
    if value is None or value == "":
        return '""'
    value_str = str(value)
    value_str = value_str.replace('\\', '\\\\')
    value_str = value_str.replace('"', '\\"')
    return f'"{value_str}"'


def ingest_division_batch(divisions: list, entity_type: str, host: str = "roscoe-graphdb", port: int = 6379):
    """Ingest a batch of divisions via redis-cli."""

    stats = {'created': 0, 'matched': 0, 'errors': []}

    for div in divisions:
        name = div['name']
        attrs = div.get('attributes', {})

        # Build property list
        props = []
        for key, value in attrs.items():
            if value is not None and value != "":
                props.append(f'h.{key} = {escape_cypher(value)}')

        props.append('h.created_at = timestamp()')
        props_str = ', '.join(props)

        # Build Cypher
        query = f'MERGE (h:{entity_type} {{name: {escape_cypher(name)}, group_id: "roscoe_graph"}}) ON CREATE SET {props_str} ON MATCH SET h.updated_at = timestamp() RETURN h.name'

        # Execute via gcloud ssh
        cmd = [
            'gcloud', 'compute', 'ssh', 'roscoe-paralegal-vm',
            '--zone=us-central1-a',
            '--command',
            f'docker exec roscoe-graphdb redis-cli -p {port} GRAPH.QUERY roscoe_graph "{query}" --raw'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                output = result.stdout
                if "Nodes created: 1" in output:
                    stats['created'] += 1
                    print(f"  ✓ Created: {name}")
                elif name in output:
                    stats['matched'] += 1
                    print(f"  ⊙ Exists: {name}")
                else:
                    stats['errors'].append(f"{name}: Unexpected output")
                    print(f"  ⚠️  Unexpected: {name}")
            else:
                stats['errors'].append(f"{name}: {result.stderr[:100]}")
                print(f"  ❌ Error: {name}")

        except subprocess.TimeoutExpired:
            stats['errors'].append(f"{name}: Timeout")
            print(f"  ❌ Timeout: {name}")
        except Exception as e:
            stats['errors'].append(f"{name}: {str(e)}")
            print(f"  ❌ Exception: {name} - {str(e)}")

    return stats


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--entities-dir', type=str)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    # Find entities directory
    if args.entities_dir:
        entities_dir = Path(args.entities_dir)
    else:
        entities_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities")

    if not entities_dir.exists():
        print(f"❌ Directory not found: {entities_dir}")
        return

    # Load all division types
    division_files = [
        ("CircuitDivision", "circuit_divisions.json"),
        ("DistrictDivision", "district_divisions.json"),
        ("AppellateDistrict", "appellate_districts.json"),
        ("SupremeCourtDistrict", "supreme_court_districts.json"),
    ]

    print("="*70)
    print("COURT DIVISIONS INGESTION - PHASE 1b")
    print("="*70)
    print(f"Source: {entities_dir}")
    print()

    all_stats = {'created': 0, 'matched': 0, 'errors': []}

    for entity_type, filename in division_files:
        file_path = entities_dir / filename

        if not file_path.exists():
            print(f"⚠️  File not found: {filename}")
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            divisions = json.load(f)

        print(f"\n{entity_type}: {len(divisions)} entities")
        print("-" * 70)

        if args.dry_run:
            print(f"  Would ingest {len(divisions)} entities")
            for i, div in enumerate(divisions[:3], 1):
                print(f"    {i}. {div['name']}")
            if len(divisions) > 3:
                print(f"    ... and {len(divisions) - 3} more")
            continue

        # Ingest this type
        stats = ingest_division_batch(divisions, entity_type)

        # Update totals
        all_stats['created'] += stats['created']
        all_stats['matched'] += stats['matched']
        all_stats['errors'].extend(stats['errors'])

        print(f"\n  Created: {stats['created']}, Matched: {stats['matched']}, Errors: {len(stats['errors'])}")

    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Total created: {all_stats['created']}")
    print(f"Already existed: {all_stats['matched']}")
    print(f"Total errors: {len(all_stats['errors'])}")

    if all_stats['errors']:
        print("\nErrors (first 10):")
        for error in all_stats['errors'][:10]:
            print(f"  - {error}")

    if not args.dry_run:
        print("\n✅ Phase 1b complete - All court divisions ingested")


if __name__ == "__main__":
    main()
