#!/usr/bin/env python3
"""
Ingest Facility and Location hierarchy to FalkorDB.

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/ingest_facility_location_hierarchy.py
"""

import json
import os
from pathlib import Path
from falkordb import FalkorDB


def ingest_hierarchy():
    """Ingest complete Facility/Location hierarchy."""

    # Connect
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    # Load entity files from mounted workspace
    base_path = Path("/mnt/workspace/schema-final/entities")

    print("="*70)
    print("INGESTING FACILITY/LOCATION HIERARCHY")
    print("="*70)
    print()

    # Pre-check
    result = graph.query("MATCH (n) RETURN count(n)")
    nodes_before = result.result_set[0][0]
    result = graph.query("MATCH ()-[r]->() RETURN count(r)")
    rels_before = result.result_set[0][0]

    print(f"Nodes before: {nodes_before:,}")
    print(f"Relationships before: {rels_before:,}\n")

    # Ingest Facilities
    print("Ingesting Facilities...")
    facilities_file = base_path / "facilities.json"

    with open(facilities_file) as f:
        facilities = json.load(f)

    print(f"  Loading {len(facilities)} facilities...")

    facility_count = 0
    for facility in facilities:
        name = facility['name']
        attrs = facility.get('attributes', {})

        try:
            query = """
            MERGE (f:Facility {name: $name, group_id: $group_id})
            ON CREATE SET f += $attrs, f.created_at = timestamp()
            RETURN f.name
            """

            params = {
                'name': name,
                'group_id': 'roscoe_graph',
                'attrs': attrs
            }

            result = graph.query(query, params)

            if result.nodes_created > 0:
                facility_count += 1

        except Exception as e:
            print(f"  ❌ Error creating {name[:40]}: {str(e)[:50]}")

        if facility_count % 100 == 0:
            print(f"    Created: {facility_count}...")

    print(f"  ✓ Created {facility_count} Facility nodes\n")

    # Ingest Locations
    print("Ingesting Locations...")
    locations_file = base_path / "locations.json"

    with open(locations_file) as f:
        locations = json.load(f)

    print(f"  Loading {len(locations)} locations...")

    location_count = 0
    for location in locations:
        name = location['name']
        attrs = location.get('attributes', {})

        try:
            query = """
            MERGE (l:Location {name: $name, group_id: $group_id})
            ON CREATE SET l += $attrs, l.created_at = timestamp()
            RETURN l.name
            """

            params = {
                'name': name,
                'group_id': 'roscoe_graph',
                'attrs': attrs
            }

            result = graph.query(query, params)

            if result.nodes_created > 0:
                location_count += 1

        except Exception as e:
            print(f"  ❌ Error creating {name[:40]}: {str(e)[:50]}")

        if location_count % 200 == 0:
            print(f"    Created: {location_count}...")

    print(f"  ✓ Created {location_count} Location nodes\n")

    # Create hierarchy relationships
    print("Creating hierarchy relationships...")
    relationships_file = base_path / "hierarchy_relationships.json"

    with open(relationships_file) as f:
        relationships = json.load(f)

    # Location → Facility relationships
    loc_to_fac = relationships['location_to_facility']

    print(f"  Creating {len(loc_to_fac)} Location → Facility relationships...")

    loc_rel_count = 0
    for rel in loc_to_fac:
        loc_name = rel['location']
        fac_name = rel['facility']

        try:
            query = """
            MATCH (l:Location {name: $loc_name})
            MATCH (f:Facility {name: $fac_name})
            MERGE (l)-[:PART_OF]->(f)
            """

            params = {'loc_name': loc_name, 'fac_name': fac_name}
            result = graph.query(query, params)

            if result.relationships_created > 0:
                loc_rel_count += 1

        except Exception as e:
            pass  # Continue even if some fail

        if loc_rel_count % 200 == 0 and loc_rel_count > 0:
            print(f"    Created: {loc_rel_count}...")

    print(f"  ✓ Created {loc_rel_count} Location → Facility relationships\n")

    # Facility → HealthSystem relationships
    fac_to_sys = relationships['facility_to_health_system']

    print(f"  Creating {len(fac_to_sys)} Facility → HealthSystem relationships...")

    fac_rel_count = 0
    for rel in fac_to_sys:
        fac_name = rel['facility']
        sys_name = rel['health_system']

        try:
            query = """
            MATCH (f:Facility {name: $fac_name})
            MATCH (h:HealthSystem {name: $sys_name})
            MERGE (f)-[:PART_OF]->(h)
            """

            params = {'fac_name': fac_name, 'sys_name': sys_name}
            result = graph.query(query, params)

            if result.relationships_created > 0:
                fac_rel_count += 1

        except Exception as e:
            pass

        if fac_rel_count % 50 == 0 and fac_rel_count > 0:
            print(f"    Created: {fac_rel_count}...")

    print(f"  ✓ Created {fac_rel_count} Facility → HealthSystem relationships\n")

    # Post-check
    result = graph.query("MATCH (n) RETURN count(n)")
    nodes_after = result.result_set[0][0]
    result = graph.query("MATCH ()-[r]->() RETURN count(r)")
    rels_after = result.result_set[0][0]

    # Canary
    result = graph.query('MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-() RETURN count(r)')
    abby_after = result.result_set[0][0]

    # Count new entities
    result = graph.query("MATCH (f:Facility) RETURN count(f)")
    total_facilities = result.result_set[0][0]
    result = graph.query("MATCH (l:Location) RETURN count(l)")
    total_locations = result.result_set[0][0]

    print("="*70)
    print("MIGRATION COMPLETE")
    print("="*70)
    print(f"Nodes before: {nodes_before:,}")
    print(f"Nodes after: {nodes_after:,}")
    print(f"Net change: {nodes_after - nodes_before:+,}")
    print()
    print(f"Relationships before: {rels_before:,}")
    print(f"Relationships after: {rels_after:,}")
    print(f"Net change: {rels_after - rels_before:+,}")
    print()
    print(f"Facilities created: {total_facilities:,}")
    print(f"Locations created: {total_locations:,}")
    print(f"Location → Facility rels: {loc_rel_count:,}")
    print(f"Facility → HealthSystem rels: {fac_rel_count:,}")
    print()
    print(f"Abby Sitgraves relationships: {abby_after}")
    print()
    print("✅ Hierarchy migration complete!")


if __name__ == "__main__":
    ingest_hierarchy()
