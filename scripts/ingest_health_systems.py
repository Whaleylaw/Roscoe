#!/usr/bin/env python3
"""
Ingest Health Systems to FalkorDB.

Phase 1a: Test ingestion with 5 health system entities.

This script:
1. Reads health_systems.json
2. Creates HealthSystem nodes in FalkorDB
3. Uses MERGE to avoid duplicates
4. Verifies ingestion

Safe to run - uses MERGE, won't create duplicates.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from falkordb import FalkorDB


def get_db_connection(host: str = None, port: int = None):
    """Connect to FalkorDB."""
    host = host or os.getenv("FALKORDB_HOST", "localhost")
    port = port or int(os.getenv("FALKORDB_PORT", "6380"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected to roscoe_graph\n")

    return graph


def verify_graph_integrity(graph):
    """Check current graph state before ingestion."""
    print("="*60)
    print("PRE-INGESTION VERIFICATION")
    print("="*60)

    # Count nodes
    result = graph.query("MATCH (n) RETURN count(n) as total")
    total_nodes = result.result_set[0][0] if result.result_set else 0
    print(f"Total nodes: {total_nodes:,}")

    # Count relationships
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    total_rels = result.result_set[0][0] if result.result_set else 0
    print(f"Total relationships: {total_rels:,}")

    # Check for existing HealthSystem nodes
    result = graph.query("MATCH (h:HealthSystem) RETURN count(h) as total")
    existing_health_systems = result.result_set[0][0] if result.result_set else 0
    print(f"Existing HealthSystem nodes: {existing_health_systems}")

    # Check Abby Sitgraves case (canary)
    result = graph.query('MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-() RETURN count(r) as total')
    abby_rels = result.result_set[0][0] if result.result_set else 0
    print(f"Abby Sitgraves relationships: {abby_rels} (canary check)")

    print()

    return {
        'total_nodes': total_nodes,
        'total_rels': total_rels,
        'existing_health_systems': existing_health_systems,
        'abby_rels': abby_rels
    }


def ingest_health_systems(graph, json_file: Path, dry_run: bool = False):
    """Ingest health systems from JSON file."""

    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        health_systems = json.load(f)

    print(f"Loaded {len(health_systems)} health systems from {json_file.name}")
    print()

    if dry_run:
        print("DRY RUN MODE - No changes will be made\n")

    stats = {
        'created': 0,
        'skipped': 0,
        'errors': []
    }

    for hs in health_systems:
        name = hs['name']
        attrs = hs.get('attributes', {})

        # Build properties
        props = {
            'name': name,
            'group_id': 'roscoe_graph',
            'created_at': datetime.now().isoformat()
        }

        # Add optional attributes
        if attrs.get('medical_records_endpoint'):
            props['medical_records_endpoint'] = attrs['medical_records_endpoint']
        if attrs.get('billing_endpoint'):
            props['billing_endpoint'] = attrs['billing_endpoint']
        if attrs.get('phone'):
            props['phone'] = attrs['phone']
        if attrs.get('fax'):
            props['fax'] = attrs['fax']
        if attrs.get('email'):
            props['email'] = attrs['email']
        if attrs.get('address'):
            props['address'] = attrs['address']
        if attrs.get('website'):
            props['website'] = attrs['website']

        # Build Cypher query using MERGE (safe - won't duplicate)
        # MERGE matches on name + group_id, creates if doesn't exist
        query = f"""
        MERGE (h:HealthSystem {{name: $name, group_id: $group_id}})
        ON CREATE SET
          h.medical_records_endpoint = $medical_records_endpoint,
          h.billing_endpoint = $billing_endpoint,
          h.phone = $phone,
          h.fax = $fax,
          h.email = $email,
          h.address = $address,
          h.website = $website,
          h.created_at = $created_at
        ON MATCH SET
          h.updated_at = $created_at
        RETURN h.name, id(h) as node_id
        """

        params = {
            'name': props['name'],
            'group_id': props['group_id'],
            'medical_records_endpoint': props.get('medical_records_endpoint', ''),
            'billing_endpoint': props.get('billing_endpoint', ''),
            'phone': props.get('phone', ''),
            'fax': props.get('fax', ''),
            'email': props.get('email', ''),
            'address': props.get('address', ''),
            'website': props.get('website', ''),
            'created_at': props['created_at']
        }

        if dry_run:
            print(f"Would create: {name}")
            continue

        try:
            result = graph.query(query, params)
            if result.result_set:
                node_name = result.result_set[0][0]
                node_id = result.result_set[0][1]

                # Check if created or matched
                if result.nodes_created > 0:
                    stats['created'] += 1
                    print(f"✓ Created: {node_name} (id: {node_id})")
                else:
                    stats['skipped'] += 1
                    print(f"⊙ Already exists: {node_name} (id: {node_id})")
            else:
                stats['errors'].append(f"No result for {name}")
                print(f"⚠️  No result returned for {name}")

        except Exception as e:
            stats['errors'].append(f"{name}: {str(e)}")
            print(f"❌ Error creating {name}: {str(e)}")

    return stats


def verify_post_ingestion(graph, pre_stats: dict):
    """Verify ingestion didn't break anything."""
    print("\n" + "="*60)
    print("POST-INGESTION VERIFICATION")
    print("="*60)

    # Count nodes
    result = graph.query("MATCH (n) RETURN count(n) as total")
    total_nodes = result.result_set[0][0] if result.result_set else 0
    nodes_added = total_nodes - pre_stats['total_nodes']
    print(f"Total nodes: {total_nodes:,} (+{nodes_added})")

    # Count relationships
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    total_rels = result.result_set[0][0] if result.result_set else 0
    rels_change = total_rels - pre_stats['total_rels']
    print(f"Total relationships: {total_rels:,} ({rels_change:+d})")

    # Count HealthSystem nodes
    result = graph.query("MATCH (h:HealthSystem) RETURN count(h) as total")
    health_systems = result.result_set[0][0] if result.result_set else 0
    hs_added = health_systems - pre_stats['existing_health_systems']
    print(f"HealthSystem nodes: {health_systems} (+{hs_added})")

    # Check Abby Sitgraves case (canary)
    result = graph.query('MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-() RETURN count(r) as total')
    abby_rels = result.result_set[0][0] if result.result_set else 0
    abby_change = abby_rels - pre_stats['abby_rels']
    print(f"Abby Sitgraves relationships: {abby_rels} ({abby_change:+d} - should be 0)")

    # List all health systems
    result = graph.query("MATCH (h:HealthSystem) RETURN h.name ORDER BY h.name")
    if result.result_set:
        print(f"\nHealthSystem entities in graph:")
        for row in result.result_set:
            print(f"  - {row[0]}")

    print()

    # Verify no data loss
    if abby_change != 0:
        print("⚠️  WARNING: Abby Sitgraves relationships changed! This should not happen.")
        return False

    if rels_change != 0:
        print("⚠️  WARNING: Relationship count changed! This should not happen for HealthSystem ingestion.")
        return False

    print("✅ Data integrity verified - no existing data affected")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Ingest Health Systems to FalkorDB')
    parser.add_argument('--json-file', type=str, help='Path to health_systems.json')
    parser.add_argument('--host', help='FalkorDB host')
    parser.add_argument('--port', type=int, help='FalkorDB port')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    args = parser.parse_args()

    # Find JSON file
    if args.json_file:
        json_file = Path(args.json_file)
    else:
        possible_paths = [
            Path("/mnt/workspace/json-files/memory-cards/entities/health_systems.json"),
            Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/health_systems.json"),
        ]
        json_file = None
        for p in possible_paths:
            if p.exists():
                json_file = p
                break

        if not json_file:
            print("❌ Could not find health_systems.json")
            sys.exit(1)

    print("="*60)
    print("HEALTH SYSTEMS INGESTION - PHASE 1a")
    print("="*60)
    print(f"Source: {json_file}")
    print()

    # Connect to graph
    graph = get_db_connection(args.host, args.port)

    # Pre-check
    pre_stats = verify_graph_integrity(graph)

    # Ingest
    print("="*60)
    print("INGESTION")
    print("="*60)
    print()

    stats = ingest_health_systems(graph, json_file, dry_run=args.dry_run)

    if args.dry_run:
        print(f"\n✓ Dry run complete - no changes made")
        return

    # Report
    print("\n" + "="*60)
    print("INGESTION SUMMARY")
    print("="*60)
    print(f"Created: {stats['created']}")
    print(f"Already existed: {stats['skipped']}")
    print(f"Errors: {len(stats['errors'])}")

    if stats['errors']:
        print("\nErrors:")
        for error in stats['errors']:
            print(f"  - {error}")

    # Post-check
    integrity_ok = verify_post_ingestion(graph, pre_stats)

    if integrity_ok:
        print("="*60)
        print("✅ PHASE 1a COMPLETE - HEALTH SYSTEMS INGESTED")
        print("="*60)
        sys.exit(0)
    else:
        print("="*60)
        print("⚠️  PHASE 1a COMPLETE WITH WARNINGS")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
