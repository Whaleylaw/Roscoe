#!/usr/bin/env python3
"""
Ingest production data from JSON files into knowledge graph.

Reads from: /Volumes/X10 Pro/Roscoe/json-files/memory-cards/
Creates: All entity types and relationships using Direct Cypher

Uses Direct Cypher (NOT Graphiti) - all data is structured.

Entity Types (18):
- Case, Client, BIClaim, PIPClaim, UIMClaim, UMClaim, WCClaim
- Adjuster, Insurer, MedicalProvider, Lien, Lienholder
- Attorney, Court, Defendant, Organization, Pleading, Vendor

Relationship Types (13):
- HAS_CLIENT, PLAINTIFF_IN, HAS_CLAIM, INSURED_BY
- ASSIGNED_ADJUSTER, HANDLES_INSURANCE_CLAIM
- HAS_LIEN, HAS_LIEN_FROM, HELD_BY, HOLDS
- TREATED_BY, TREATING_AT, WORKS_AT
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import redis
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from roscoe.core.graphiti_client import CASE_DATA_GROUP_ID


# =============================================================================
# Direct FalkorDB Connection (No Graphiti)
# =============================================================================

def get_falkordb_connection():
    """Get direct FalkorDB connection without Graphiti."""
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))
    return redis.Redis(host=host, port=port, decode_responses=True)


async def run_direct_cypher(query: str, params: dict = None):
    """
    Execute Cypher query directly against FalkorDB.

    FalkorDB doesn't support parameterized queries like Neo4j.
    We need to inline values with proper escaping.

    Args:
        query: Cypher query string with $param placeholders
        params: Query parameters to substitute

    Returns:
        List of result dictionaries
    """
    client = get_falkordb_connection()

    # If params provided, substitute them into the query
    if params:
        # Sort keys in reverse order by length to avoid partial matches
        # This ensures $prop_10 gets replaced before $prop_1
        sorted_params = sorted(params.items(), key=lambda x: len(x[0]), reverse=True)

        for key, value in sorted_params:
            placeholder = f"${key}"

            # Format value based on type
            if value is None:
                formatted_value = "null"
            elif isinstance(value, bool):
                formatted_value = str(value).lower()
            elif isinstance(value, (int, float)):
                formatted_value = str(value)
            elif isinstance(value, str):
                # Escape quotes in strings
                escaped = value.replace("'", "\\'").replace('"', '\\"')
                formatted_value = f'"{escaped}"'
            else:
                # Default: convert to string and quote
                formatted_value = f'"{str(value)}"'

            query = query.replace(placeholder, formatted_value)

    # Execute query
    result = client.execute_command("GRAPH.QUERY", "roscoe_graph", query, "--compact")

    # Parse result
    if not result or len(result) < 2:
        return []

    # Result format: [header, rows, stats]
    header = result[0] if result else []
    rows = result[1] if len(result) > 1 else []

    # Convert to dict format
    parsed_results = []
    for row in rows:
        row_dict = {}
        for i, col_name in enumerate(header):
            # Extract column name (remove type info if present)
            col_key = col_name[0] if isinstance(col_name, list) else col_name
            row_dict[col_key] = row[i] if i < len(row) else None
        parsed_results.append(row_dict)

    return parsed_results


# =============================================================================
# Entity Type Mapping
# =============================================================================

ENTITY_FILES = {
    "Case": "cases.json",
    "Client": "clients.json",
    "BIClaim": "biclaim_claims.json",
    "PIPClaim": "pipclaim_claims.json",
    "UIMClaim": "uimclaim_claims.json",
    "UMClaim": "umclaim_claims.json",
    "WCClaim": "wcclaim_claims.json",
    "Adjuster": "adjusters.json",
    "Insurer": "insurers.json",
    "MedicalProvider": "medical_providers.json",
    "Lien": "liens.json",
    "LienHolder": "lienholders.json",  # Capital H to match relationship files
    "Attorney": "attorneys.json",
    "Court": "courts.json",
    "Defendant": "defendants.json",
    "Organization": "organizations.json",
    "Pleading": "pleadings.json",
    "Vendor": "vendors.json",
}

RELATIONSHIP_FILES = {
    "HAS_CLIENT": "hasclient_relationships.json",
    "PLAINTIFF_IN": "plaintiffin_relationships.json",
    "HAS_CLAIM": "hasclaim_relationships.json",
    "INSURED_BY": "insuredby_relationships.json",
    "ASSIGNED_ADJUSTER": "assignedadjuster_relationships.json",
    "HANDLES_INSURANCE_CLAIM": "handlesinsuranceclaim_relationships.json",
    "HAS_LIEN": "haslien_relationships.json",
    "HAS_LIEN_FROM": "haslienfrom_relationships.json",
    "HELD_BY": "heldby_relationships.json",
    "HOLDS": "holds_relationships.json",
    "TREATED_BY": "treatedby_relationships.json",
    "TREATING_AT": "treatingat_relationships.json",
    "WORKS_AT": "worksat_relationships.json",
}


# =============================================================================
# Entity Creation Functions
# =============================================================================

async def create_entity(
    name: str,
    entity_type: str,
    attributes: Dict[str, Any],
    source_id: str,
    source_file: str
) -> bool:
    """
    Create an entity node in the graph.

    Args:
        name: Entity name (unique identifier)
        entity_type: Type (Case, Client, etc.)
        attributes: Dictionary of entity attributes
        source_id: Source identifier from JSON
        source_file: Source file name

    Returns:
        True if created, False if error
    """
    try:
        # Generate Graphiti-required fields
        import uuid as uuid_lib
        import hashlib

        # uuid: Generate deterministic UUID from name (required by Graphiti for deduplication)
        name_hash = hashlib.md5(name.encode()).hexdigest()
        entity_uuid = str(uuid_lib.UUID(name_hash))

        # summary: Use name as summary (required by Graphiti EntityNode schema)
        summary = name

        # Build property dictionary with Graphiti-required fields
        props = {
            "name": name,
            "entity_type": entity_type,
            "uuid": entity_uuid,  # Graphiti-required
            "summary": summary,    # Graphiti-required
            "group_id": CASE_DATA_GROUP_ID,
            "created_at": datetime.now().isoformat(),
            "source_id": source_id,
            "source_file": source_file,
        }

        # Add all attributes (flatten the attributes dict)
        for key, value in attributes.items():
            # Skip None values
            if value is not None:
                props[key] = value

        # Build SET clause dynamically
        set_clauses = []
        params = {}
        for i, (key, value) in enumerate(props.items()):
            param_name = f"prop_{i}"
            set_clauses.append(f"e.{key} = ${param_name}")
            params[param_name] = value

        set_clause = ", ".join(set_clauses)

        # Create entity with MERGE (idempotent - won't duplicate)
        query = f"""
        MERGE (e:Entity {{name: $name}})
        SET {set_clause}
        """
        params["name"] = name

        await run_direct_cypher(query, params)
        return True

    except Exception as e:
        print(f"  ❌ Error creating {entity_type} '{name}': {e}")
        return False


async def load_entities(entities_dir: str):
    """Load all entities from JSON files."""
    print("\n" + "="*80)
    print("LOADING ENTITIES")
    print("="*80)

    total_entities = 0
    total_created = 0
    total_errors = 0

    for entity_type, filename in ENTITY_FILES.items():
        filepath = Path(entities_dir) / filename

        if not filepath.exists():
            print(f"⚠️  Skipping {entity_type}: File not found at {filepath}")
            continue

        print(f"\n📦 Loading {entity_type} entities from {filename}...")

        try:
            with open(filepath, 'r') as f:
                entities = json.load(f)

            created = 0
            errors = 0

            for entity in entities:
                name = entity.get("name")
                attributes = entity.get("attributes", {})
                source_id = entity.get("source_id", "")
                source_file = entity.get("source_file", "")

                if not name:
                    print(f"  ⚠️  Skipping entity with no name: {entity}")
                    errors += 1
                    continue

                success = await create_entity(
                    name=name,
                    entity_type=entity_type,
                    attributes=attributes,
                    source_id=source_id,
                    source_file=source_file
                )

                if success:
                    created += 1
                else:
                    errors += 1

                # Progress indicator every 50 entities
                if (created + errors) % 50 == 0:
                    print(f"  Progress: {created + errors}/{len(entities)} processed...")

            print(f"  ✅ Created {created} {entity_type} entities ({errors} errors)")
            total_entities += len(entities)
            total_created += created
            total_errors += errors

        except Exception as e:
            print(f"  ❌ Error loading {filename}: {e}")
            total_errors += 1

    print("\n" + "-"*80)
    print(f"📊 ENTITY SUMMARY: {total_created}/{total_entities} created ({total_errors} errors)")
    print("-"*80)


# =============================================================================
# Relationship Creation Functions
# =============================================================================

async def create_relationship(
    edge_type: str,
    source_type: str,
    source_name: str,
    target_type: str,
    target_name: str,
    attributes: Dict[str, Any],
    context: str
) -> bool:
    """
    Create a relationship between two entities.

    Args:
        edge_type: Relationship type (HAS_CLIENT, TREATED_BY, etc.)
        source_type: Source entity type
        source_name: Source entity name
        target_type: Target entity type
        target_name: Target entity name
        attributes: Relationship attributes
        context: Context string

    Returns:
        True if created, False if error
    """
    try:
        # Build relationship properties
        props = {
            "created_at": datetime.now().isoformat(),
            "context": context,
        }

        # Add all attributes
        for key, value in attributes.items():
            if value is not None:
                props[key] = value

        # Build SET clause dynamically
        set_clauses = []
        params = {
            "source_type": source_type,
            "source_name": source_name,
            "target_type": target_type,
            "target_name": target_name,
        }

        for i, (key, value) in enumerate(props.items()):
            param_name = f"prop_{i}"
            set_clauses.append(f"r.{key} = ${param_name}")
            params[param_name] = value

        set_clause = ", ".join(set_clauses) if set_clauses else ""

        # Create relationship (MERGE for idempotency)
        query = f"""
        MATCH (source:Entity {{entity_type: $source_type, name: $source_name}})
        MATCH (target:Entity {{entity_type: $target_type, name: $target_name}})
        MERGE (source)-[r:{edge_type}]->(target)
        """

        if set_clause:
            query += f"\nSET {set_clause}"

        await run_direct_cypher(query, params)
        return True

    except Exception as e:
        # Check if it's a "node not found" error (expected for some orphaned relationships)
        error_str = str(e).lower()
        if "match" in error_str or "not found" in error_str:
            # Silently skip - this is expected for relationships where entities don't exist
            return False
        else:
            print(f"  ❌ Error creating {edge_type} relationship: {e}")
            return False


async def load_relationships(relationships_dir: str):
    """Load all relationships from JSON files."""
    print("\n" + "="*80)
    print("LOADING RELATIONSHIPS")
    print("="*80)

    total_relationships = 0
    total_created = 0
    total_skipped = 0
    total_errors = 0

    for edge_type, filename in RELATIONSHIP_FILES.items():
        filepath = Path(relationships_dir) / filename

        if not filepath.exists():
            print(f"⚠️  Skipping {edge_type}: File not found at {filepath}")
            continue

        print(f"\n🔗 Loading {edge_type} relationships from {filename}...")

        try:
            with open(filepath, 'r') as f:
                relationships = json.load(f)

            created = 0
            skipped = 0
            errors = 0

            for rel in relationships:
                source = rel.get("source", {})
                target = rel.get("target", {})
                attributes = rel.get("attributes", {})
                context = rel.get("context", "")

                source_type = source.get("entity_type")
                source_name = source.get("name")
                target_type = target.get("entity_type")
                target_name = target.get("name")

                if not all([source_type, source_name, target_type, target_name]):
                    errors += 1
                    continue

                success = await create_relationship(
                    edge_type=edge_type,
                    source_type=source_type,
                    source_name=source_name,
                    target_type=target_type,
                    target_name=target_name,
                    attributes=attributes,
                    context=context
                )

                if success:
                    created += 1
                else:
                    skipped += 1

                # Progress indicator every 50 relationships
                if (created + skipped + errors) % 50 == 0:
                    print(f"  Progress: {created + skipped + errors}/{len(relationships)} processed...")

            print(f"  ✅ Created {created} {edge_type} relationships ({skipped} skipped, {errors} errors)")
            total_relationships += len(relationships)
            total_created += created
            total_skipped += skipped
            total_errors += errors

        except Exception as e:
            print(f"  ❌ Error loading {filename}: {e}")
            total_errors += 1

    print("\n" + "-"*80)
    print(f"📊 RELATIONSHIP SUMMARY: {total_created}/{total_relationships} created ({total_skipped} skipped, {total_errors} errors)")
    print("-"*80)


# =============================================================================
# Main Ingestion Function
# =============================================================================

async def ingest_all_production_data(
    entities_dir: str = "/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities",
    relationships_dir: str = "/Volumes/X10 Pro/Roscoe/json-files/memory-cards/relationships"
):
    """Main ingestion function."""
    start_time = datetime.now()

    print("\n" + "="*80)
    print("🚀 ROSCOE PRODUCTION DATA INGESTION")
    print("="*80)
    print(f"Start time: {start_time.isoformat()}")
    print(f"Entities directory: {entities_dir}")
    print(f"Relationships directory: {relationships_dir}")
    print(f"Target group: {CASE_DATA_GROUP_ID}")

    # Step 1: Load entities (must happen first)
    await load_entities(entities_dir)

    # Step 2: Load relationships (after entities exist)
    await load_relationships(relationships_dir)

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "="*80)
    print("✅ PRODUCTION DATA INGESTION COMPLETE!")
    print("="*80)
    print(f"End time: {end_time.isoformat()}")
    print(f"Duration: {duration:.2f} seconds")
    print("\nNext steps:")
    print("  1. Verify data with graph queries")
    print("  2. Test case lookups via agent tools")
    print("  3. Check relationship traversals")
    print("="*80 + "\n")


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import sys

    # Allow custom paths via command line
    if len(sys.argv) > 1:
        entities_dir = sys.argv[1]
        relationships_dir = sys.argv[2] if len(sys.argv) > 2 else entities_dir.replace("entities", "relationships")
    else:
        entities_dir = "/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities"
        relationships_dir = "/Volumes/X10 Pro/Roscoe/json-files/memory-cards/relationships"

    asyncio.run(ingest_all_production_data(entities_dir, relationships_dir))
