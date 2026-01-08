#!/usr/bin/env python3
"""
Delete all old medical providers marked for deletion in mapping files.

Parses all mapping files to find [x] DELETE or [x] DELETE (duplicate) marks
and removes those old providers from the graph.

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/delete_old_providers_bulk.py
"""

import os
import re
from pathlib import Path
from falkordb import FalkorDB


def parse_delete_decisions(mapping_file: Path) -> list:
    """Parse mapping file to extract providers marked for deletion."""

    if not mapping_file.exists():
        return []

    with open(mapping_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by provider sections
    sections = re.split(r'## (\d+)\. OLD: (.+?)$', content, flags=re.MULTILINE)

    to_delete = []

    # Process in groups of 3
    for i in range(1, len(sections), 3):
        if i + 2 >= len(sections):
            break

        section_num = sections[i]
        old_name = sections[i + 1].strip()
        section_content = sections[i + 2]

        # Check if marked for deletion
        delete_patterns = [
            r'\[x\s*\]\s*DELETE',
            r'\[\s*x\]\s*DELETE',
            r'\[x\]\s*DELETE'
        ]

        is_delete = any(re.search(pattern, section_content, re.IGNORECASE) for pattern in delete_patterns)

        if is_delete:
            to_delete.append(old_name)

    return to_delete


def main():
    """Delete all old providers marked for deletion."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    # Find mapping files (try multiple locations)
    mapping_dirs = [
        Path("/app/provider-mappings"),
        Path("/app/workspace_paralegal/provider-mappings"),
        Path("/mnt/workspace/provider-mappings"),
    ]

    mapping_dir = None
    for d in mapping_dirs:
        if d.exists():
            mapping_dir = d
            break

    if not mapping_dir:
        print("❌ Mapping directory not found")
        return

    # Parse all mapping files
    mapping_files = [
        "NORTON_MAPPING.md",
        "UOFL_MAPPING_FACILITY_BASED.md",
        "BAPTIST_MAPPING.md",
        "CHI_MAPPING.md",
        "STELIZABETH_MAPPING.md"
    ]

    all_to_delete = []

    print("="*70)
    print("PARSING DELETE DECISIONS FROM MAPPING FILES")
    print("="*70)
    print()

    for filename in mapping_files:
        file_path = mapping_dir / filename
        if not file_path.exists():
            print(f"⊙ {filename}: Not found")
            continue

        to_delete = parse_delete_decisions(file_path)
        print(f"✓ {filename}: {len(to_delete)} providers marked for deletion")

        if to_delete:
            for name in to_delete:
                print(f"    - {name[:60]}")

        all_to_delete.extend(to_delete)
        print()

    print(f"Total providers to delete: {len(all_to_delete)}\n")

    if not all_to_delete:
        print("⊙ No providers marked for deletion")
        return

    # Pre-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_before = result.result_set[0][0]
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    rels_before = result.result_set[0][0]

    # Canary check
    result = graph.query('MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-() RETURN count(r)')
    abby_before = result.result_set[0][0]

    print(f"Nodes before: {nodes_before:,}")
    print(f"Relationships before: {rels_before:,}")
    print(f"Abby Sitgraves relationships: {abby_before}\n")

    print("="*70)
    print("DELETING OLD PROVIDERS")
    print("="*70)
    print()

    # Delete all marked providers
    deleted_count = 0
    not_found_count = 0
    errors = []

    for idx, provider_name in enumerate(all_to_delete, 1):
        print(f"{idx}/{len(all_to_delete)}: {provider_name[:60]}...", end=' ')

        try:
            # Use DETACH DELETE to remove node and all its relationships
            query = """
            MATCH (p:MedicalProvider {name: $name})
            DETACH DELETE p
            RETURN count(*) as deleted
            """

            result = graph.query(query, {'name': provider_name})

            if result.result_set and result.result_set[0][0] > 0:
                deleted_count += 1
                print("✓ Deleted")
            else:
                not_found_count += 1
                print("⊙ Not found")

        except Exception as e:
            errors.append(f"{provider_name}: {str(e)}")
            print(f"❌ Error")

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
    print("DELETION COMPLETE")
    print("="*70)
    print(f"Nodes before: {nodes_before:,}")
    print(f"Nodes after: {nodes_after:,}")
    print(f"Nodes deleted: {nodes_before - nodes_after}")
    print()
    print(f"Relationships before: {rels_before:,}")
    print(f"Relationships after: {rels_after:,}")
    print(f"Relationships deleted: {rels_before - rels_after}")
    print()
    print(f"Providers deleted: {deleted_count}")
    print(f"Providers not found (already deleted): {not_found_count}")
    print(f"Errors: {len(errors)}")
    print()
    print(f"Abby Sitgraves relationships before: {abby_before}")
    print(f"Abby Sitgraves relationships after: {abby_after}")

    if abby_after != abby_before:
        print(f"\n⚠️  WARNING: Abby Sitgraves relationship count changed by {abby_after - abby_before}")
    else:
        print(f"\n✅ Abby Sitgraves case intact")

    if errors:
        print(f"\nErrors:")
        for err in errors[:10]:
            print(f"  - {err}")

    print("\n✅ Old provider deletion complete")


if __name__ == "__main__":
    main()
