#!/usr/bin/env python3
"""
Update 6 HealthSystem nodes with new records_request and billing_request fields.

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/update_health_systems.py
"""

import os
from falkordb import FalkorDB


def update_health_systems():
    """Update HealthSystem nodes with new fields."""

    # Connect
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    print("="*70)
    print("UPDATING HEALTH SYSTEMS WITH NEW FIELDS")
    print("="*70)
    print()

    # Get all health systems
    result = graph.query("MATCH (h:HealthSystem) RETURN h.name ORDER BY h.name")

    systems = [row[0] for row in result.result_set] if result.result_set else []

    print(f"Found {len(systems)} HealthSystem nodes:")
    for s in systems:
        print(f"  - {s}")
    print()

    # Update each system
    for system_name in systems:
        print(f"Updating {system_name}...")

        query = """
        MATCH (h:HealthSystem {name: $name})
        SET
          h.records_request_method = null,
          h.records_request_url = null,
          h.records_request_address = null,
          h.records_request_fax = null,
          h.records_request_phone = null,
          h.records_request_notes = null,
          h.billing_request_method = null,
          h.billing_request_address = null,
          h.billing_request_phone = null,
          h.source = "health_system_roster",
          h.validation_state = "unverified"
        RETURN h.name
        """

        result = graph.query(query, {'name': system_name})

        if result.result_set:
            print(f"  ✓ Updated")
        else:
            print(f"  ⚠️  Failed to update")

    print()
    print("="*70)
    print("✅ HealthSystem updates complete")
    print("="*70)


if __name__ == "__main__":
    update_health_systems()
