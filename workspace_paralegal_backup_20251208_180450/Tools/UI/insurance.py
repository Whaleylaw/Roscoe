#!/usr/bin/env python3
"""
Insurance UI Script

Displays insurance coverage for a case (data only, no documents).
Can be used standalone or imported by other components.

For insurance WITH documents, use insurance_overview.py instead.

Usage:
    python insurance.py --project-name "Abby-Sitgraves-MVA-7-13-2024"
    python insurance.py --project-name "Abby-Sitgraves-MVA-7-13-2024" --coverage-type "PIP"

Output:
    JSON with component="InsuranceCoverageCard" and coverage data
"""

import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

from _utils import (
    get_project_path,
    read_json_file,
    read_overview,
    get_client_name,
    output_result,
    output_error,
)


def get_adjuster_info(contacts_data: List[Dict], adjuster_name: str) -> Optional[Dict[str, Any]]:
    """Look up adjuster contact information from contacts data."""
    if not adjuster_name:
        return None
    
    adjuster_name_lower = adjuster_name.lower()
    
    for contact in contacts_data:
        if not isinstance(contact, dict):
            continue
        contact_name = contact.get("full_name", "")
        if contact_name.lower() == adjuster_name_lower:
            return {
                "name": contact.get("full_name"),
                "email": contact.get("email"),
                "phone": contact.get("phone"),
                "address": contact.get("address"),
            }
    
    # Not found - return basic info
    return {"name": adjuster_name, "email": None, "phone": None, "address": None}


def get_insurance_data(project_name: str, coverage_type_filter: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get insurance data for a project, grouped by coverage type.
    
    This function can be imported and used by other scripts.
    
    Args:
        project_name: The case folder name
        coverage_type_filter: Optional filter for specific coverage type (PIP, BI, UIM, etc.)
        
    Returns:
        Dictionary mapping coverage types to lists of claims
    """
    project_path = get_project_path(project_name)
    
    if not project_path.exists():
        return {}
    
    insurance_raw = read_json_file(project_path / "Case Information" / "insurance.json") or []
    contacts_raw = read_json_file(project_path / "Case Information" / "contacts.json") or []
    
    # Normalize coverage type filter
    type_variants = []
    if coverage_type_filter:
        ct = coverage_type_filter.upper()
        type_variants = [coverage_type_filter, ct]
        if ct == "PIP":
            type_variants.extend(["Personal Injury Protection (PIP)", "Personal Injury Protection"])
        elif ct == "BI":
            type_variants.extend(["Bodily Injury (BI)", "Bodily Injury"])
        elif ct == "UIM":
            type_variants.extend(["Underinsured Motorist (UIM)", "Underinsured Motorist"])
        elif ct == "UM":
            type_variants.extend(["Uninsured Motorist (UM)", "Uninsured Motorist"])
        elif ct == "MEDPAY":
            type_variants.extend(["Medical Payments (MedPay)", "Medical Payments", "MedPay"])
    
    coverage_types: Dict[str, List[Dict]] = {}
    
    for insurance in insurance_raw:
        if not isinstance(insurance, dict):
            continue
        
        ins_type = insurance.get("insurance_type", "Other")
        
        # Filter if requested
        if coverage_type_filter:
            if not any(v.lower() in ins_type.lower() for v in type_variants):
                continue
        
        company_name = insurance.get("insurance_company_name", "Unknown")
        adjuster_name = insurance.get("adjuster_name", "")
        adjuster = get_adjuster_info(contacts_raw, adjuster_name) if adjuster_name else None
        
        claim = {
            "company_name": company_name,
            "claim_number": insurance.get("claim_number"),
            "adjuster": adjuster,
            "coverage_confirmation": insurance.get("coverage_confirmation"),
            "policy_limits": insurance.get("policy_limits"),
            "demanded_amount": insurance.get("demand_amount"),
            "current_offer": insurance.get("offer_amount"),
            "settlement_amount": insurance.get("settlement_amount"),
            "settlement_date": insurance.get("settlement_date"),
            "is_active_negotiation": insurance.get("is_active_negotiation", False),
            "notes": insurance.get("notes"),
        }
        
        if ins_type not in coverage_types:
            coverage_types[ins_type] = []
        coverage_types[ins_type].append(claim)
    
    return coverage_types


def main():
    parser = argparse.ArgumentParser(description="Generate insurance UI data")
    parser.add_argument("--project-name", required=True, help="Case folder name")
    parser.add_argument("--coverage-type", help="Optional: Filter to specific coverage (PIP, BI, UIM, etc.)")
    args = parser.parse_args()
    
    project_path = get_project_path(args.project_name)
    
    if not project_path.exists():
        output_error(f"Project not found: {args.project_name}")
    
    coverage_types = get_insurance_data(args.project_name, args.coverage_type)
    
    if not coverage_types:
        if args.coverage_type:
            output_error(f"No {args.coverage_type} coverage found for {args.project_name}")
        else:
            output_error(f"No insurance found for {args.project_name}")
    
    # Get client info for display
    overview = read_overview(project_path)
    client_name = get_client_name(overview, args.project_name)
    
    # Convert to list format
    coverage_list = [
        {"type": type_name, "claims": claims}
        for type_name, claims in coverage_types.items()
    ]
    
    output_result({
        "component": "InsuranceCoverageCard",
        "data": {
            "client_name": client_name,
            "case_name": args.project_name,
            "coverage_types": coverage_list,
        },
    })


if __name__ == "__main__":
    main()

