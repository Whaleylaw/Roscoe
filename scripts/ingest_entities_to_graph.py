#!/usr/bin/env python3
"""
General-purpose entity ingestion script for FalkorDB.

Ingests entities from JSON "memory card" files to FalkorDB graph.

Usage:
    python3 ingest_entities_to_graph.py --entity-type CircuitDivision
    python3 ingest_entities_to_graph.py --entity-type DistrictDivision
    python3 ingest_entities_to_graph.py --entity-type Doctor --batch-size 1000
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime


def escape_for_cypher(value):
    """Escape value for Cypher query string."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Escape quotes and backslashes
        value = value.replace("\\", "\\\\")
        value = value.replace('"', '\\"')
        return f'"{value}"'
    return f'"{str(value)}"'


def build_cypher_query(entity_type: str, name: str, attributes: dict) -> str:
    """Build MERGE query for entity."""

    # Build property assignments for ON CREATE
    create_props = []
    for key, value in attributes.items():
        if value is not None and value != "":
            escaped_value = escape_for_cypher(value)
            create_props.append(f"  h.{key} = {escaped_value}")

    create_props.append(f"  h.created_at = timestamp()")

    create_props_str = ",\n".join(create_props) if create_props else "  h.created_at = timestamp()"

    # Build query
    name_escaped = escape_for_cypher(name)
    query = f"""MERGE (h:{entity_type} {{name: {name_escaped}, group_id: "roscoe_graph"}})
ON CREATE SET
{create_props_str}
ON MATCH SET
  h.updated_at = timestamp()
RETURN h.name"""

    return query


def load_entity_file(entity_type: str, entities_dir: Path) -> list:
    """Load entity JSON file."""

    # Map entity types to file names
    file_map = {
        "HealthSystem": "health_systems.json",
        "CircuitDivision": "circuit_divisions.json",
        "DistrictDivision": "district_divisions.json",
        "AppellateDistrict": "appellate_districts.json",
        "SupremeCourtDistrict": "supreme_court_districts.json",
        "CircuitJudge": "circuit_judges.json",
        "DistrictJudge": "district_judges.json",
        "AppellateJudge": "appellate_judges.json",
        "SupremeCourtJustice": "supreme_court_justices.json",
        "CourtClerk": "court_clerks.json",
        "Doctor": "doctors.json",
        "MedicalProvider": "medical_providers.json",
        "Court": "courts.json",
        "Attorney": "attorneys.json",
        "LawFirm": "lawfirms.json",
        "Insurer": "insurers.json",
        "Adjuster": "adjusters.json",
        "Client": "clients.json",
        "Defendant": "defendants.json",
        "Vendor": "vendors.json",
        "Expert": "experts.json",
        "Mediator": "mediators.json",
        "Witness": "witnesses.json",
        "Organization": "organizations.json",
        "LienHolder": "lienholders.json",
    }

    filename = file_map.get(entity_type)
    if not filename:
        raise ValueError(f"Unknown entity type: {entity_type}")

    file_path = entities_dir / filename
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def execute_via_redis_cli(query: str, host: str, port: int) -> tuple:
    """Execute Cypher via redis-cli (for VM execution)."""
    import subprocess

    # Escape query for shell
    query_escaped = query.replace('"', '\\"').replace('$', '\\$').replace('\n', ' ')

    cmd = f'docker exec roscoe-graphdb redis-cli -p {port} GRAPH.QUERY roscoe_graph "{query_escaped}" --raw'

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "Query timeout"
    except Exception as e:
        return False, str(e)


def ingest_entities(
    entity_type: str,
    entities_dir: Path,
    host: str,
    port: int,
    batch_size: int = 50,
    dry_run: bool = False,
    use_redis_cli: bool = False
):
    """Ingest entities to FalkorDB."""

    print(f"Loading {entity_type} entities...")
    entities = load_entity_file(entity_type, entities_dir)
    print(f"✓ Loaded {len(entities)} entities\n")

    if dry_run:
        print("DRY RUN MODE - showing first 5 entities\n")
        for i, entity in enumerate(entities[:5], 1):
            print(f"{i}. {entity['name']}")
        print(f"\n... and {len(entities) - 5} more")
        return

    stats = {
        'total': len(entities),
        'created': 0,
        'matched': 0,
        'errors': []
    }

    # Process in batches
    for i in range(0, len(entities), batch_size):
        batch = entities[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(entities) + batch_size - 1) // batch_size

        print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} entities)...")

        for entity in batch:
            name = entity['name']
            attrs = entity.get('attributes', {})

            try:
                query = build_cypher_query(entity_type, name, attrs)

                if use_redis_cli:
                    success, output = execute_via_redis_cli(query, host, port)
                    if success:
                        if "Nodes created: 1" in output:
                            stats['created'] += 1
                            print(f"  ✓ Created: {name}")
                        else:
                            stats['matched'] += 1
                            print(f"  ⊙ Exists: {name}")
                    else:
                        stats['errors'].append(f"{name}: {output}")
                        print(f"  ❌ Error: {name}")
                else:
                    # Placeholder - would use falkordb Python module here
                    print(f"  → Would create: {name}")

            except Exception as e:
                stats['errors'].append(f"{name}: {str(e)}")
                print(f"  ❌ Error: {name} - {str(e)}")

        print()

    return stats


def main():
    parser = argparse.ArgumentParser(description='Ingest entities to FalkorDB')
    parser.add_argument('--entity-type', required=True,
                       help='Entity type to ingest (e.g., CircuitDivision, Doctor)')
    parser.add_argument('--entities-dir', type=str,
                       help='Directory containing entity JSON files')
    parser.add_argument('--host', default='roscoe-graphdb',
                       help='FalkorDB host (default: roscoe-graphdb for VM)')
    parser.add_argument('--port', type=int, default=6379,
                       help='FalkorDB port (default: 6379 for VM)')
    parser.add_argument('--batch-size', type=int, default=50,
                       help='Batch size for ingestion (default: 50)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done')
    parser.add_argument('--use-redis-cli', action='store_true',
                       help='Execute via redis-cli (for VM without Python falkordb module)')
    args = parser.parse_args()

    # Find entities directory
    if args.entities_dir:
        entities_dir = Path(args.entities_dir)
    else:
        possible_dirs = [
            Path("/mnt/workspace/json-files/memory-cards/entities"),
            Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities"),
        ]
        entities_dir = None
        for d in possible_dirs:
            if d.exists():
                entities_dir = d
                break

        if not entities_dir:
            print("❌ Could not find entities directory")
            sys.exit(1)

    print("="*70)
    print(f"ENTITY INGESTION: {args.entity_type}")
    print("="*70)
    print(f"Source directory: {entities_dir}")
    print(f"FalkorDB: {args.host}:{args.port}")
    print(f"Batch size: {args.batch_size}")
    print()

    # Ingest
    stats = ingest_entities(
        entity_type=args.entity_type,
        entities_dir=entities_dir,
        host=args.host,
        port=args.port,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        use_redis_cli=args.use_redis_cli
    )

    if args.dry_run:
        print("✓ Dry run complete")
        return

    # Summary
    print("="*70)
    print("INGESTION SUMMARY")
    print("="*70)
    print(f"Total entities: {stats['total']}")
    print(f"Created: {stats['created']}")
    print(f"Already existed: {stats['matched']}")
    print(f"Errors: {len(stats['errors'])}")

    if stats['errors']:
        print("\nErrors (showing first 10):")
        for error in stats['errors'][:10]:
            print(f"  - {error}")

    if stats['errors']:
        sys.exit(1)
    else:
        print(f"\n✅ Successfully ingested {stats['created']} {args.entity_type} entities")
        sys.exit(0)


if __name__ == "__main__":
    main()
