#!/usr/bin/env python3
"""
Import Whaley Law Firm Staff into Graph

Adds attorneys and case managers as entities, links them to Whaley Law Firm.

Usage:
    python -m roscoe.scripts.import_whaley_staff
"""

from falkordb import FalkorDB
import os


STAFF = [
    {"name": "Aaron G. Whaley", "type": "Attorney", "role": "plaintiff_counsel"},
    {"name": "Bryce Koon", "type": "Attorney", "role": "plaintiff_counsel"},
    {"name": "Sarena Tuttle", "type": "CaseManager", "role": "paralegal"},
    {"name": "Justin Chumbley", "type": "CaseManager", "role": "case_manager"},
    {"name": "Faye Gaither", "type": "CaseManager", "role": "case_manager"},
    {"name": "Jessa Galosmo", "type": "CaseManager", "role": "case_manager"},
    {"name": "Aries Penaflor", "type": "CaseManager", "role": "case_manager"},
    {"name": "Jessica Bottorff", "type": "CaseManager", "role": "case_manager"},
]


def import_staff():
    """Import staff members into graph."""
    db = FalkorDB(
        host=os.getenv("FALKORDB_HOST", "roscoe-graphdb"),
        port=int(os.getenv("FALKORDB_PORT", "6379"))
    )
    graph = db.select_graph("roscoe_graph")

    print("=" * 70)
    print("IMPORTING WHALEY LAW FIRM STAFF")
    print("=" * 70)
    print()

    # Create Whaley Law Firm if it doesn't exist
    firm_query = """
    MERGE (f:LawFirm {name: 'The Whaley Law Firm'})
    ON CREATE SET
      f.group_id = 'roscoe_graph',
      f.phone = '(502) 410-4000',
      f.address = '500 W. Jefferson Street, Suite 2400, Louisville, KY 40202'
    RETURN f.name
    """
    graph.query(firm_query)
    print("✓ Whaley Law Firm entity created/verified")
    print()

    print(f"Adding {len(STAFF)} staff members...")
    print()

    for staff in STAFF:
        entity_type = staff["type"]
        name = staff["name"]
        role = staff["role"]

        # Create staff entity
        create_query = f"""
        MERGE (s:{entity_type} {{name: $name}})
        ON CREATE SET
          s.group_id = 'roscoe_graph',
          s.firm_name = 'The Whaley Law Firm',
          s.role = $role
        RETURN s.name
        """
        graph.query(create_query, {'name': name, 'role': role})

        # Link to firm
        link_query = f"""
        MATCH (s:{entity_type} {{name: $name}})
        MATCH (f:LawFirm {{name: 'The Whaley Law Firm'}})
        MERGE (s)-[:WORKS_AT]->(f)
        """
        graph.query(link_query, {'name': name})

        print(f"  ✓ {name} ({entity_type} - {role})")

    print()
    print("=" * 70)
    print("✅ COMPLETE")
    print("=" * 70)
    print(f"Imported {len(STAFF)} staff members")
    print("All linked to The Whaley Law Firm via WORKS_AT relationships")


if __name__ == "__main__":
    import_staff()
