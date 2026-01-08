#!/usr/bin/env python3
"""
Get medical providers for a case from knowledge graph.

DEPLOYMENT PATH: /Tools/queries/get_case_providers.py (in GCS bucket whaley_law_firm)

This script queries the three-tier medical provider hierarchy.
Replaces: medical_providers.json from legacy JSON-based system

Usage:
    python get_case_providers.py "Christopher-Lanier-MVA-6-28-2025"
    python get_case_providers.py "Christopher-Lanier-MVA-6-28-2025" --pretty
"""

import argparse
import json
import sys
import os
from falkordb import FalkorDB


def get_case_providers(case_name: str) -> dict:
    """
    Query knowledge graph for medical providers using three-tier hierarchy.

    Returns:
        Dict with list of providers (Facility or Location entities) with hierarchy info
    """
    # Connect to graph
    host = os.getenv("FALKORDB_HOST", "localhost")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")

    # Query for providers through Client relationship
    query = """
        MATCH (case:Case {name: $case_name})-[:HAS_CLIENT]->(client:Client)-[:TREATED_AT]->(provider)
        WHERE provider:Facility OR provider:Location
        OPTIONAL MATCH (provider)-[:PART_OF]->(parent)
        WHERE parent:Facility OR parent:HealthSystem
        OPTIONAL MATCH (parent)-[:PART_OF]->(grandparent:HealthSystem)
        RETURN provider.name as name,
               labels(provider)[0] as provider_type,
               provider.specialty as specialty,
               provider.phone as phone,
               provider.fax as fax,
               provider.address as address,
               provider.records_request_method as records_method,
               provider.records_request_address as records_address,
               provider.records_request_phone as records_phone,
               provider.records_request_url as records_url,
               parent.name as parent_name,
               labels(parent)[0] as parent_type,
               grandparent.name as health_system
        ORDER BY provider.name
    """

    result = graph.query(query, {"case_name": case_name})

    if not result.result_set:
        return {
            "success": True,
            "case_name": case_name,
            "providers": [],
            "total_providers": 0,
            "message": "No providers found for this case"
        }

    providers = []
    for record in result.result_set:
        provider_data = {
            "name": record[0],
            "type": record[1],  # "Facility" or "Location"
            "specialty": record[2],
            "phone": record[3],
            "fax": record[4],
            "address": record[5],
            "records_request": {
                "method": record[6],
                "address": record[7],
                "phone": record[8],
                "url": record[9],
            },
            "parent": record[10],
            "parent_type": record[11],
            "health_system": record[12] or (record[10] if record[11] == "HealthSystem" else None),
        }

        # Clean up None values in nested dicts
        provider_data["records_request"] = {
            k: v for k, v in provider_data["records_request"].items() if v
        }
        if not provider_data["records_request"]:
            del provider_data["records_request"]

        # Clean up top-level None values
        provider_data = {k: v for k, v in provider_data.items() if v is not None and v != {}}

        providers.append(provider_data)

    return {
        "success": True,
        "case_name": case_name,
        "providers": providers,
        "total_providers": len(providers),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Get medical providers from knowledge graph"
    )
    parser.add_argument("case_name", help="Case folder name")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")

    args = parser.parse_args()

    try:
        result = get_case_providers(args.case_name)
        print(json.dumps(result, indent=2 if args.pretty else None))
        sys.exit(0)
    except Exception as e:
        error = {
            "success": False,
            "error": str(e),
            "case_name": args.case_name
        }
        print(json.dumps(error, indent=2 if args.pretty else None))
        sys.exit(1)


if __name__ == "__main__":
    main()
