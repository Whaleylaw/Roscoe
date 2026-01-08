#!/usr/bin/env python3
"""
Import Complete Structured Graph from Memory Card JSON Files

Imports:
1. All entity types (clients, providers, insurance, liens, etc.)
2. All relationships (HAS_CLIENT, TREATING_AT, HAS_CLAIM, etc.)

Usage:
    python -m roscoe.scripts.import_structured_graph
    python -m roscoe.scripts.import_structured_graph --entities-only
    python -m roscoe.scripts.import_structured_graph --relationships-only
"""

import json
import os
import re
from pathlib import Path
from falkordb import FalkorDB


# Map entity_type to label name
ENTITY_TYPE_MAP = {
    "Client": "Client",
    "MedicalProvider": "MedicalProvider",
    "Insurer": "Insurer",
    "Adjuster": "Adjuster",
    "PIPClaim": "PIPClaim",
    "BIClaim": "BIClaim",
    "UMClaim": "UMClaim",
    "UIMClaim": "UIMClaim",
    "WCClaim": "WCClaim",
    "Lien": "Lien",
    "LienHolder": "LienHolder",
    "Attorney": "Attorney",
    "Court": "Court",
    "Defendant": "Defendant",
    "Organization": "Organization",
    "Pleading": "Pleading",
    "Vendor": "Vendor",
    "Case": "Case",
}

# Map edge_type to relationship name
EDGE_TYPE_MAP = {
    "HasClient": "HAS_CLIENT",
    "HasClaim": "HAS_CLAIM",
    "TreatingAt": "TREATING_AT",
    "TreatedBy": "TREATED_BY",
    "InsuredBy": "INSURED_BY",
    "AssignedAdjuster": "ASSIGNED_ADJUSTER",
    "HandlesInsuranceClaim": "HANDLES_CLAIM",
    "HasLien": "HAS_LIEN",
    "HasLienFrom": "HAS_LIEN_FROM",
    "HeldBy": "HELD_BY",
    "Holds": "HOLDS",
    "PlaintiffIn": "PLAINTIFF_IN",
    "WorksAt": "WORKS_AT",
}


def import_entities(entities_dir: Path, db: FalkorDB) -> dict:
    """Import all entities from JSON files."""
    graph = db.select_graph("roscoe_graph")
    stats = {}

    entity_files = list(entities_dir.glob("*.json"))
    print(f"\nImporting entities from {len(entity_files)} files...")

    for entity_file in sorted(entity_files):
        if entity_file.name == "cases.json":
            continue  # Skip - already imported

        with open(entity_file) as f:
            entities = json.load(f)

        entity_count = 0

        for entity in entities:
            entity_type = entity.get("entity_type")
            name = entity.get("name")
            attrs = entity.get("attributes", {})

            if not entity_type or not name:
                continue

            # Get label from map
            label = ENTITY_TYPE_MAP.get(entity_type, entity_type)

            # Build property SET clause (exclude name - already in MERGE)
            props = ["n.group_id = 'roscoe_graph'"]
            params = {"name": name}

            for key, value in attrs.items():
                if value and isinstance(value, (str, int, float)):
                    safe_key = key.replace("-", "_").replace(" ", "_")
                    props.append(f"n.{safe_key} = ${safe_key}")
                    params[safe_key] = value

            props_str = ", ".join(props)

            query = f"MERGE (n:{label} {{name: $name}}) ON CREATE SET {props_str}"
            graph.query(query, params)
            entity_count += 1

        stats[entity_file.name] = entity_count
        print(f"  ✓ {entity_file.name}: {entity_count} entities")

    return stats


def import_relationships(relationships_dir: Path, db: FalkorDB) -> dict:
    """Import all relationships from JSON files."""
    graph = db.select_graph("roscoe_graph")
    stats = {}

    rel_files = list(relationships_dir.glob("*_relationships.json"))
    print(f"\nImporting relationships from {len(rel_files)} files...")

    for rel_file in sorted(rel_files):
        if rel_file.name == "all_relationships.json":
            continue  # Skip aggregate file

        with open(rel_file) as f:
            relationships = json.load(f)

        rel_count = 0

        for rel in relationships:
            edge_type = rel.get("edge_type")
            source = rel.get("source", {})
            target = rel.get("target", {})

            if not edge_type or not source.get("name") or not target.get("name"):
                continue

            # Get labels and relationship name
            source_label = ENTITY_TYPE_MAP.get(source.get("entity_type"), "Entity")
            target_label = ENTITY_TYPE_MAP.get(target.get("entity_type"), "Entity")
            rel_name = EDGE_TYPE_MAP.get(edge_type, edge_type.upper())

            query = f"""
            MATCH (source:{source_label} {{name: $source_name}})
            MATCH (target:{target_label} {{name: $target_name}})
            MERGE (source)-[:{rel_name}]->(target)
            """

            graph.query(query, {
                "source_name": source["name"],
                "target_name": target["name"]
            })
            rel_count += 1

        stats[rel_file.name] = rel_count
        print(f"  ✓ {rel_file.name}: {rel_count} relationships")

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Import structured graph from JSON')
    parser.add_argument('--entities-only', action='store_true', help='Import only entities')
    parser.add_argument('--relationships-only', action='store_true', help='Import only relationships')
    args = parser.parse_args()

    # Paths - try multiple locations
    possible_paths = [
        Path("/mnt/workspace/json-files/memory-cards"),
        Path("/home/aaronwhaley/json-files/memory-cards"),
        Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards"),
    ]

    json_base = None
    for path in possible_paths:
        if path.exists() and (path / "entities").exists():
            json_base = path
            break

    if not json_base:
        print(f"❌ Could not find JSON files in any of these locations:")
        for p in possible_paths:
            print(f"  - {p}")
        return

    entities_dir = json_base / "entities"
    relationships_dir = json_base / "relationships"

    print("=" * 70)
    print("STRUCTURED GRAPH IMPORT")
    print("=" * 70)
    print(f"Using JSON files from: {json_base}")
    print(f"Entities: {entities_dir}")
    print(f"Relationships: {relationships_dir}")
    print()

    # Connect to FalkorDB
    db = FalkorDB(
        host=os.getenv("FALKORDB_HOST", "roscoe-graphdb"),
        port=int(os.getenv("FALKORDB_PORT", "6379"))
    )

    # Import entities
    if not args.relationships_only:
        entity_stats = import_entities(entities_dir, db)
        total_entities = sum(entity_stats.values())
        print(f"\n✅ Imported {total_entities} total entities")

    # Import relationships
    if not args.entities_only:
        rel_stats = import_relationships(relationships_dir, db)
        total_rels = sum(rel_stats.values())
        print(f"\n✅ Imported {total_rels} total relationships")

    print()
    print("=" * 70)
    print("✅ IMPORT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
