#!/usr/bin/env python3
"""
Import all cases from caselist.json into FalkorDB

Creates Case and Client entities with proper relationships.

Usage:
    python -m roscoe.scripts.import_cases_from_json
    python -m roscoe.scripts.import_cases_from_json --dry-run
"""

import json
import asyncio
import argparse
import os
from pathlib import Path


async def import_cases(dry_run: bool = False):
    """Import cases from caselist.json."""
    from falkordb import FalkorDB
    from datetime import datetime

    workspace = Path(os.getenv("WORKSPACE_DIR", "/mnt/workspace"))
    caselist_path = workspace / "Database" / "caselist.json"

    print("=" * 70)
    print("IMPORTING CASES FROM CASELIST.JSON")
    print("=" * 70)
    print(f"Caselist: {caselist_path}")
    print()

    if not caselist_path.exists():
        print(f"❌ Caselist not found: {caselist_path}")
        return

    with open(caselist_path) as f:
        caselist = json.load(f)

    print(f"Found {len(caselist)} cases")
    print()

    if dry_run:
        print("[DRY RUN] Would create:")
        for case in caselist[:5]:
            print(f"  - Case: {case.get('project_name')}")
            print(f"    Client: {case.get('client_name')}")
        print(f"  ... and {len(caselist) - 5} more")
        return

    # Connect to FalkorDB
    db = FalkorDB(host=os.getenv("FALKORDB_HOST", "roscoe-graphdb"),
                  port=int(os.getenv("FALKORDB_PORT", "6379")))
    graph = db.select_graph("roscoe_graph")

    print("Creating Case and Client entities...")

    now = datetime.now().isoformat()

    for i, case in enumerate(caselist, 1):
        case_name = case.get("project_name")
        client_name = case.get("client_name")
        case_type = case.get("case_type", "MVA")
        accident_date = case.get("accident_date")

        if not case_name:
            continue

        # Create Case entity with label
        case_query = """
        MERGE (c:Case {name: $case_name})
        ON CREATE SET
          c.case_type = $case_type,
          c.accident_date = $accident_date,
          c.group_id = 'roscoe_graph',
          c.created_at = $now
        RETURN c.name
        """
        graph.query(case_query, {
            'case_name': case_name,
            'case_type': case_type,
            'accident_date': accident_date,
            'now': now
        })

        # Create Client entity and relationship if client_name exists
        if client_name:
            client_query = """
            MERGE (client:Client {name: $client_name})
            ON CREATE SET
              client.group_id = 'roscoe_graph',
              client.created_at = $now

            WITH client
            MATCH (case:Case {name: $case_name})
            MERGE (case)-[:HAS_CLIENT]->(client)
            RETURN client.name
            """
            graph.query(client_query, {
                'client_name': client_name,
                'case_name': case_name,
                'now': now
            })

        if i % 10 == 0:
            print(f"  Progress: {i}/{len(caselist)} cases imported...")

    print()
    print("=" * 70)
    print("✅ IMPORT COMPLETE")
    print("=" * 70)
    print(f"Total cases imported: {len(caselist)}")
    print()


def main():
    parser = argparse.ArgumentParser(description='Import cases from caselist.json')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without importing')
    args = parser.parse_args()

    asyncio.run(import_cases(args.dry_run))


if __name__ == "__main__":
    main()
