#!/usr/bin/env python3
"""
Get insurance claims for a case from knowledge graph.

DEPLOYMENT PATH: /Tools/queries/get_case_insurance.py (in GCS bucket whaley_law_firm)

This script queries the knowledge graph for all insurance claims on a case.
Replaces: insurance.json from legacy JSON-based system

Usage:
    python get_case_insurance.py "Christopher-Lanier-MVA-6-28-2025"
    python get_case_insurance.py "Christopher-Lanier-MVA-6-28-2025" --pretty
"""

import argparse
import json
import sys
import os
from falkordb import FalkorDB


def get_case_insurance(case_name: str) -> dict:
    """
    Query knowledge graph for all insurance claims.

    Returns:
        Dict with list of claims, each with policy, insurer, adjuster details
    """
    # Connect to graph
    host = os.getenv("FALKORDB_HOST", "localhost")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")

    # Query for insurance claims with policies and insurers
    query = """
        MATCH (case:Case {name: $case_name})-[:HAS_CLAIM]->(claim)
        WHERE claim:BIClaim OR claim:PIPClaim OR claim:UMClaim OR claim:UIMClaim OR claim:WCClaim
        OPTIONAL MATCH (claim)-[:UNDER_POLICY]->(policy:InsurancePolicy)
        OPTIONAL MATCH (policy)-[:WITH_INSURER]->(insurer:Insurer)
        OPTIONAL MATCH (claim)-[:HANDLED_BY]->(adjuster:Adjuster)
        RETURN claim.claim_number as claim_number,
               labels(claim)[0] as claim_type,
               policy.policy_number as policy_number,
               insurer.name as insurer_name,
               insurer.phone as insurer_phone,
               insurer.claims_address as insurer_address,
               adjuster.name as adjuster_name,
               adjuster.phone as adjuster_phone,
               adjuster.email as adjuster_email,
               policy.bi_limit as bi_limit,
               policy.pip_limit as pip_limit,
               policy.um_limit as um_limit,
               policy.uim_limit as uim_limit,
               policy.med_pay_limit as med_pay_limit,
               claim.status as claim_status,
               claim.date_filed as date_filed,
               claim.amount_demanded as demand_amount,
               claim.amount_offered as current_offer,
               claim.settlement_amount as settlement_amount,
               claim.denial_date as denial_date,
               claim.denial_reason as denial_reason
    """

    result = graph.query(query, {"case_name": case_name})

    claims = []
    for record in result.result_set:
        claim_data = {
            "claim_number": record[0],
            "claim_type": record[1],
            "policy_number": record[2],
            "insurer": {
                "name": record[3],
                "phone": record[4],
                "address": record[5],
            },
            "adjuster": {
                "name": record[6],
                "phone": record[7],
                "email": record[8],
            },
            "coverage": {
                "bi_limit": record[9],
                "pip_limit": record[10],
                "um_limit": record[11],
                "uim_limit": record[12],
                "med_pay_limit": record[13],
            },
            "claim_status": record[14],
            "date_filed": record[15],
            "demand_amount": record[16],
            "current_offer": record[17],
            "settlement_amount": record[18],
            "denial_date": record[19],
            "denial_reason": record[20],
        }

        # Clean up None values
        claim_data = {k: v for k, v in claim_data.items() if v is not None}

        claims.append(claim_data)

    return {
        "success": True,
        "case_name": case_name,
        "claims": claims,
        "total_claims": len(claims),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Get insurance claims from knowledge graph"
    )
    parser.add_argument("case_name", help="Case folder name")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")

    args = parser.parse_args()

    try:
        result = get_case_insurance(args.case_name)
        print(json.dumps(result, indent=2 if args.pretty else None))
        sys.exit(0 if result.get("success") else 1)
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
