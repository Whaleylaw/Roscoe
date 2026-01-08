#!/usr/bin/env python3
"""
Get case overview from knowledge graph.

DEPLOYMENT PATH: /Tools/queries/get_case_overview.py (in GCS bucket whaley_law_firm)

This script queries the knowledge graph for basic case information.
Replaces: overview.json from legacy JSON-based system

Usage:
    python get_case_overview.py "Christopher-Lanier-MVA-6-28-2025"
    python get_case_overview.py "Christopher-Lanier-MVA-6-28-2025" --pretty
"""

import argparse
import json
import sys
import os
from falkordb import FalkorDB


def get_case_overview(case_name: str) -> dict:
    """
    Query knowledge graph for case overview.

    Returns:
        Dict with case basics, client info, phase, accident details
    """
    # Connect to graph
    host = os.getenv("FALKORDB_HOST", "localhost")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")

    # Query for case and client info
    query = """
        MATCH (case:Case {name: $case_name})
        OPTIONAL MATCH (case)-[:HAS_CLIENT]->(client:Client)
        OPTIONAL MATCH (case)-[:IN_PHASE]->(phase:Phase)
        RETURN case.name as case_name,
               case.case_type as accident_type,
               case.accident_date as accident_date,
               case.incident_date as incident_date,
               case.case_number as case_number,
               case.filing_date as filing_date,
               client.name as client_name,
               client.phone as client_phone,
               client.email as client_email,
               client.address as client_address,
               client.date_of_birth as client_dob,
               phase.name as current_phase,
               phase.display_name as phase_display
        LIMIT 1
    """

    result = graph.query(query, {"case_name": case_name})

    if not result.result_set:
        return {
            "success": False,
            "error": f"Case '{case_name}' not found in knowledge graph"
        }

    record = result.result_set[0]

    # Build response
    overview = {
        "success": True,
        "case_name": record[0],
        "accident_type": record[1] or "mva",
        "accident_date": record[2] or record[3],  # accident_date or incident_date
        "case_number": record[4],
        "filing_date": record[5],
        "client": {
            "name": record[6],
            "phone": record[7],
            "email": record[8],
            "address": record[9],
            "date_of_birth": record[10],
        },
        "current_phase": record[11] or "file_setup",
        "phase_display": record[12] or "File Setup",
    }

    # Get financial summary
    financial_query = """
        MATCH (case:Case {name: $case_name})
        OPTIONAL MATCH (case)-[:HAS_EXPENSE]->(expense:Expense)
        OPTIONAL MATCH (case)-[:HAS_LIEN]->(lien:Lien)
        OPTIONAL MATCH (case)-[:HAS_CLIENT]->(client:Client)-[:TREATED_AT]->(provider)
        WHERE provider:Facility OR provider:Location
        OPTIONAL MATCH (provider)<-[:FROM_PROVIDER]-(bill:Bill)
        RETURN sum(expense.amount) as total_expenses,
               sum(lien.amount) as total_liens,
               sum(bill.amount) as total_medical_bills,
               count(DISTINCT provider) as provider_count
    """

    fin_result = graph.query(financial_query, {"case_name": case_name})
    if fin_result.result_set:
        fin_record = fin_result.result_set[0]
        overview["financials"] = {
            "total_expenses": fin_record[0] or 0.0,
            "total_liens": fin_record[1] or 0.0,
            "total_medical_bills": fin_record[2] or 0.0,
            "provider_count": fin_record[3] or 0,
        }

    return overview


def main():
    parser = argparse.ArgumentParser(
        description="Get case overview from knowledge graph"
    )
    parser.add_argument("case_name", help="Case folder name (e.g., Christopher-Lanier-MVA-6-28-2025)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    try:
        result = get_case_overview(args.case_name)
        print(json.dumps(result, indent=2 if args.pretty else None))
        sys.exit(0 if result.get("success") else 1)
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Query failed: {str(e)}",
            "case_name": args.case_name
        }
        print(json.dumps(error_result, indent=2 if args.pretty else None))
        sys.exit(1)


if __name__ == "__main__":
    main()
