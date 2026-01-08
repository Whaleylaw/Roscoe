#!/usr/bin/env python3
"""
Get liens for a case from knowledge graph.

DEPLOYMENT PATH: /Tools/queries/get_case_liens.py (in GCS bucket whaley_law_firm)

This script queries the knowledge graph for all liens on a case.
Replaces: liens.json from legacy JSON-based system

Usage:
    python get_case_liens.py "Christopher-Lanier-MVA-6-28-2025"
    python get_case_liens.py "Christopher-Lanier-MVA-6-28-2025" --pretty
"""

import argparse
import json
import sys
import os
from falkordb import FalkorDB


def get_case_liens(case_name: str) -> dict:
    """
    Query knowledge graph for all liens.

    Returns:
        Dict with list of liens with holder details
    """
    # Connect to graph
    host = os.getenv("FALKORDB_HOST", "localhost")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")

    # Query for liens and lien holders
    query = """
        MATCH (case:Case {name: $case_name})-[:HAS_LIEN]->(lien:Lien)
        OPTIONAL MATCH (lien)-[:HELD_BY]->(holder:LienHolder)
        OPTIONAL MATCH (lien)-[:FOR_PROVIDER]->(provider)
        WHERE provider:Facility OR provider:Location
        RETURN lien.name as lien_name,
               holder.name as holder_name,
               holder.lien_type as holder_type,
               holder.contact_name as contact_name,
               holder.phone as holder_phone,
               holder.email as holder_email,
               holder.address as holder_address,
               lien.lien_type as lien_type,
               lien.amount as amount,
               lien.original_amount as original_amount,
               lien.negotiated_amount as negotiated_amount,
               lien.final_amount as final_amount,
               lien.status as status,
               lien.date_filed as date_filed,
               lien.account_number as account_number,
               lien.reference_number as reference_number,
               provider.name as related_provider
        ORDER BY lien.amount DESC
    """

    result = graph.query(query, {"case_name": case_name})

    liens = []
    total_amount = 0
    total_negotiated = 0

    for record in result.result_set:
        lien_data = {
            "lien_name": record[0],
            "holder": {
                "name": record[1],
                "type": record[2],
                "contact_name": record[3],
                "phone": record[4],
                "email": record[5],
                "address": record[6],
            },
            "lien_type": record[7],
            "amount": record[8],
            "original_amount": record[9],
            "negotiated_amount": record[10],
            "final_amount": record[11],
            "status": record[12],
            "date_filed": record[13],
            "account_number": record[14],
            "reference_number": record[15],
            "related_provider": record[16],
        }

        # Calculate totals
        if lien_data.get("amount"):
            total_amount += lien_data["amount"]
        if lien_data.get("negotiated_amount"):
            total_negotiated += lien_data["negotiated_amount"]
        elif lien_data.get("final_amount"):
            total_negotiated += lien_data["final_amount"]

        # Clean up None values
        lien_data["holder"] = {k: v for k, v in lien_data["holder"].items() if v}
        lien_data = {k: v for k, v in lien_data.items() if v is not None and v != {}}

        liens.append(lien_data)

    return {
        "success": True,
        "case_name": case_name,
        "liens": liens,
        "total_liens": len(liens),
        "total_amount": total_amount,
        "total_negotiated": total_negotiated,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Get liens from knowledge graph"
    )
    parser.add_argument("case_name", help="Case folder name")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")

    args = parser.parse_args()

    try:
        result = get_case_liens(args.case_name)
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
