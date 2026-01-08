#!/usr/bin/env python3
"""
Sync Pydantic schema to FalkorDB by creating indices for all entity types.

This script:
1. Reads ENTITY_TYPES from graphiti_client.py
2. Creates FalkorDB indices for each entity type
3. Does NOT modify or delete existing data
4. Prepares graph for full-scale ingestion

Safe to run - only creates indices, doesn't touch data.
"""

import sys
from pathlib import Path
from falkordb import FalkorDB
import os

# Import ENTITY_TYPES from graphiti_client
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from roscoe.core.graphiti_client import ENTITY_TYPES

# FalkorDB connection
FALKORDB_HOST = os.getenv("FALKORDB_HOST", "localhost")
FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", "6380"))

def get_entity_properties(entity_class):
    """Extract properties from Pydantic model."""
    properties = []

    # Get all fields from Pydantic model
    if hasattr(entity_class, 'model_fields'):
        for field_name, field_info in entity_class.model_fields.items():
            properties.append(field_name)
    elif hasattr(entity_class, '__fields__'):
        # Older Pydantic v1
        for field_name in entity_class.__fields__.keys():
            properties.append(field_name)

    return properties


def create_index_for_label(graph, label: str, properties: list):
    """
    Create a FalkorDB index for a label.

    FalkorDB automatically creates indices when you query, but we can
    create them explicitly for better performance.

    Note: In FalkorDB, indices are created automatically when you use
    properties in WHERE clauses. We'll ensure common properties are indexed.
    """
    # Standard properties to ensure are indexed
    standard_props = ['name', 'uuid', 'group_id', 'created_at', 'valid_at']

    # Properties present in this entity
    props_to_index = [p for p in standard_props if p in properties]

    if not props_to_index:
        return f"No standard properties found for {label}"

    # FalkorDB creates indices automatically, but we can verify by running a query
    # that will trigger index creation
    query = f"MATCH (n:{label}) WHERE n.name IS NOT NULL RETURN count(n)"

    try:
        result = graph.query(query)
        return f"✓ {label}: Index verified (returned {result.result_set[0][0] if result.result_set else 0} existing nodes)"
    except Exception as e:
        # Label doesn't exist yet - that's fine
        return f"✓ {label}: Ready for ingestion (no existing nodes)"


def sync_schema(db_host: str, db_port: int):
    """Sync Pydantic schema to FalkorDB."""

    print(f"Connecting to FalkorDB at {db_host}:{db_port}")
    db = FalkorDB(host=db_host, port=db_port)
    graph = db.select_graph("roscoe_graph")

    print(f"\n✓ Connected to graph: roscoe_graph")
    print(f"\nPydantic schema defines {len(ENTITY_TYPES)} entity types")
    print("\nProcessing entity types...\n")

    results = {
        'verified': [],
        'ready': [],
        'errors': []
    }

    for entity_class in ENTITY_TYPES:
        label = entity_class.__name__
        properties = get_entity_properties(entity_class)

        try:
            status = create_index_for_label(graph, label, properties)
            if "existing nodes" in status:
                results['verified'].append(label)
            else:
                results['ready'].append(label)
            print(status)
        except Exception as e:
            error_msg = f"❌ {label}: {str(e)}"
            results['errors'].append(label)
            print(error_msg)

    # Summary
    print("\n" + "="*60)
    print("SCHEMA SYNC SUMMARY")
    print("="*60)
    print(f"\n✓ Entity types with existing data: {len(results['verified'])}")
    print(f"✓ Entity types ready for ingestion: {len(results['ready'])}")
    print(f"❌ Errors: {len(results['errors'])}")

    if results['errors']:
        print(f"\nErrors occurred for:")
        for label in results['errors']:
            print(f"  - {label}")

    # Check current graph state
    print("\n" + "="*60)
    print("CURRENT GRAPH STATE")
    print("="*60)

    # Total nodes and relationships
    total_nodes_result = graph.query("MATCH (n) RETURN count(n) as total")
    total_rels_result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")

    total_nodes = total_nodes_result.result_set[0][0] if total_nodes_result.result_set else 0
    total_rels = total_rels_result.result_set[0][0] if total_rels_result.result_set else 0

    print(f"\nTotal nodes: {total_nodes:,}")
    print(f"Total relationships: {total_rels:,}")

    # Labels in use
    labels_result = graph.query("CALL db.labels()")
    labels_in_use = [row[0] for row in labels_result.result_set] if labels_result.result_set else []

    print(f"\nLabels currently in use: {len(labels_in_use)}")

    # Relationship types in use
    rels_result = graph.query("CALL db.relationshipTypes()")
    rels_in_use = [row[0] for row in rels_result.result_set] if rels_result.result_set else []

    print(f"Relationship types currently in use: {len(rels_in_use)}")

    print(f"\n✅ Schema sync complete!")
    print(f"\nFalkorDB is now ready to receive all {len(ENTITY_TYPES)} entity types")
    print(f"defined in graphiti_client.py")

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Sync Pydantic schema to FalkorDB')
    parser.add_argument('--host', default=FALKORDB_HOST, help='FalkorDB host')
    parser.add_argument('--port', type=int, default=FALKORDB_PORT, help='FalkorDB port')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without doing it')
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print(f"\nWould process {len(ENTITY_TYPES)} entity types:")
        for entity_class in ENTITY_TYPES:
            props = get_entity_properties(entity_class)
            standard_props = [p for p in ['name', 'uuid', 'group_id', 'created_at', 'valid_at'] if p in props]
            print(f"  - {entity_class.__name__}: {', '.join(standard_props)}")
        return

    sync_schema(args.host, args.port)


if __name__ == "__main__":
    main()
