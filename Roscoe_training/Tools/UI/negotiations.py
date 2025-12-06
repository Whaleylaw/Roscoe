#!/usr/bin/env python3
"""
Active Negotiations UI Script

Displays all insurance entries where is_active_negotiation is true.
Shows contact cards for insurance company and adjuster, claim details,
plus case financials (providers, liens, expenses).

Can be filtered to a specific case or show all active negotiations globally.

Usage:
    python negotiations.py                                    # All active negotiations
    python negotiations.py --project-name "Abby-Sitgraves-MVA" # Filter to one case

Output:
    JSON with component="NegotiationsView" and negotiation data
"""

import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

from _utils import (
    get_workspace_path,
    get_project_path,
    read_json_file,
    read_overview,
    get_client_name,
    output_result,
    output_error,
)
from medical_providers import get_providers_data
from liens import get_liens_data
from expenses import get_expenses_data


def get_master_insurance() -> List[Dict[str, Any]]:
    """Read master insurance list from Database."""
    workspace_path = get_workspace_path()
    insurance_path = workspace_path / "Database" / "master_lists" / "insurance.json"
    
    data = read_json_file(insurance_path)
    if not data:
        return []
    
    # Handle list format (no jsonb_agg wrapper in this file)
    if isinstance(data, list):
        return data
    return []


def get_master_directory() -> List[Dict[str, Any]]:
    """Read master contact directory."""
    workspace_path = get_workspace_path()
    directory_path = workspace_path / "Database" / "master_lists" / "Database_directory.json"
    
    data = read_json_file(directory_path)
    if not data:
        return []
    
    # Handle jsonb_agg wrapper
    if isinstance(data, list) and len(data) > 0:
        first = data[0]
        if isinstance(first, dict) and "jsonb_agg" in first:
            return first["jsonb_agg"]
        return data
    return []


def find_contact_in_directory(name: str, directory: List[Dict]) -> Optional[Dict[str, Any]]:
    """
    Search for a contact by name in the master directory.
    Returns normalized contact data for ContactCard.
    """
    if not name or not name.strip():
        return None
    
    name_lower = name.lower().strip()
    
    for contact in directory:
        if not isinstance(contact, dict):
            continue
        
        full_name = contact.get("full_name", "")
        if not full_name:
            continue
        
        # Exact match
        if full_name.lower() == name_lower:
            return normalize_contact(contact, name)
        
        # Partial match (name in full_name)
        if name_lower in full_name.lower():
            return normalize_contact(contact, name)
    
    # Not found - return basic contact with just the name
    return {
        "name": name,
        "roles": [],
        "company": None,
        "email": None,
        "phone": None,
        "address": None,
    }


def normalize_contact(contact: Dict, original_name: str) -> Dict[str, Any]:
    """Normalize contact data for ContactCard component."""
    return {
        "name": contact.get("full_name") or original_name,
        "roles": contact.get("roles", []),
        "company": contact.get("company") or contact.get("organization"),
        "email": contact.get("email"),
        "phone": contact.get("phone"),
        "fax": contact.get("fax"),
        "address": contact.get("address"),
    }


def get_active_negotiations(project_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all active negotiations from master insurance list.
    
    Args:
        project_filter: Optional project name to filter to a single case
        
    Returns:
        List of negotiation data dictionaries
    """
    master_insurance = get_master_insurance()
    master_directory = get_master_directory()
    
    # Filter to active negotiations
    active = [
        ins for ins in master_insurance
        if ins.get("is_active_negotiation") is True
    ]
    
    # Filter to specific project if requested
    if project_filter:
        project_lower = project_filter.lower()
        active = [
            ins for ins in active
            if (ins.get("project_name", "").lower() == project_lower or
                project_lower in ins.get("project_name", "").lower())
        ]
    
    negotiations = []
    
    for ins in active:
        project_name = ins.get("project_name", "Unknown")
        
        # Get client name from project overview
        project_path = get_project_path(project_name)
        overview = read_overview(project_path) if project_path.exists() else {}
        client_name = get_client_name(overview, project_name)
        
        # Look up contacts
        company_name = ins.get("insurance_company_name", "")
        adjuster_name = ins.get("insurance_adjuster_name", "")
        
        company_contact = find_contact_in_directory(company_name, master_directory)
        adjuster_contact = find_contact_in_directory(adjuster_name, master_directory)
        
        # If adjuster found, add role context
        if adjuster_contact and adjuster_name:
            adjuster_contact["roles"] = ["Insurance Adjuster"]
            if company_name:
                adjuster_contact["company"] = company_name
        
        # If company found, add role context
        if company_contact and company_name:
            company_contact["roles"] = ["Insurance Company"]
        
        # Get case financial data
        providers = get_providers_data(project_name) if project_path.exists() else []
        liens = get_liens_data(project_name) if project_path.exists() else []
        expenses = get_expenses_data(project_name) if project_path.exists() else []
        
        # Build claim details
        claim = {
            "claim_number": ins.get("claim_number"),
            "coverage_type": ins.get("insurance_type"),
            "coverage_confirmation": ins.get("coverage_confirmation"),
            "date_demand_sent": ins.get("date_demand_sent"),
            "demand_amount": ins.get("demanded_amount"),
            "demand_summary": ins.get("demand_summary"),
            "demand_negotiations": ins.get("demand_negotiations"),
            "current_offer": ins.get("current_offer"),
            "current_negotiation_status": ins.get("current_negotiation_status"),
            "settlement_amount": ins.get("settlement_amount"),
            "settlement_date": ins.get("settlement_date"),
            "notes": ins.get("insurance_notes"),
        }
        
        # Calculate totals
        total_medical = sum(p.get("total_billed", 0) or 0 for p in providers)
        total_liens = sum(l.get("original_amount", 0) or 0 for l in liens)
        total_expenses = sum(e.get("amount", 0) or 0 for e in expenses)
        
        negotiations.append({
            "project_name": project_name,
            "client_name": client_name,
            "coverage_type": ins.get("insurance_type", "Unknown"),
            "insurance_company": company_contact,
            "adjuster": adjuster_contact,
            "claim": claim,
            "providers": providers,
            "liens": liens,
            "expenses": expenses,
            "totals": {
                "medical_bills": total_medical,
                "liens": total_liens,
                "expenses": total_expenses,
            },
        })
    
    # Sort by project name
    negotiations.sort(key=lambda x: x["project_name"])
    
    return negotiations


def main():
    parser = argparse.ArgumentParser(description="Active Negotiations UI")
    parser.add_argument("--project-name", help="Optional: Filter to specific case")
    args = parser.parse_args()
    
    negotiations = get_active_negotiations(args.project_name)
    
    if not negotiations:
        if args.project_name:
            output_error(f"No active negotiations found for {args.project_name}")
        else:
            output_error("No active negotiations found")
    
    # Build title
    if args.project_name:
        title = f"Active Negotiations: {args.project_name}"
    else:
        title = f"Active Negotiations ({len(negotiations)} total)"
    
    output_result({
        "component": "NegotiationsView",
        "data": {
            "title": title,
            "count": len(negotiations),
            "negotiations": negotiations,
        },
    })


if __name__ == "__main__":
    main()

