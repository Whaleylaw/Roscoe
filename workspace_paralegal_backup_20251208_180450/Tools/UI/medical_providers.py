#!/usr/bin/env python3
"""
Medical Providers UI Script

Displays medical providers for a case (data only, no documents).
Can be used standalone or imported by other components.

For providers WITH documents, use medical_overview.py instead.

Usage:
    python medical_providers.py --project-name "Abby-Sitgraves-MVA-7-13-2024"

Output:
    JSON with component="MedicalProviderCard" and providers data
"""

import argparse
from pathlib import Path
from typing import Dict, Any, List

from _utils import (
    get_project_path,
    read_json_file,
    read_overview,
    get_client_name,
    get_accident_date,
    output_result,
    output_error,
)


def get_providers_data(project_name: str) -> List[Dict[str, Any]]:
    """
    Get medical providers data for a project (without documents).
    
    This function can be imported and used by other scripts.
    
    Args:
        project_name: The case folder name
        
    Returns:
        List of provider dictionaries
    """
    project_path = get_project_path(project_name)
    
    if not project_path.exists():
        return []
    
    providers_raw = read_json_file(project_path / "Case Information" / "medical_providers.json") or []
    
    providers = []
    for provider in providers_raw:
        if not isinstance(provider, dict):
            continue
        
        # Format dates of service
        dates_of_service = []
        if provider.get("date_treatment_started"):
            dates_of_service.append(provider["date_treatment_started"])
        if provider.get("date_treatment_completed") and provider.get("date_treatment_completed") != provider.get("date_treatment_started"):
            dates_of_service.append(provider["date_treatment_completed"])
        
        providers.append({
            "name": provider.get("provider_full_name", "Unknown Provider"),
            "specialty": None,
            "total_billed": provider.get("billed_amount", 0) or 0,
            "total_paid": provider.get("settlement_payment"),
            "dates_of_service": dates_of_service,
            "notes": provider.get("medical_provider_notes"),
        })
    
    # Sort by billed amount descending
    providers.sort(key=lambda x: x["total_billed"], reverse=True)
    
    return providers


def main():
    parser = argparse.ArgumentParser(description="Generate medical providers UI data")
    parser.add_argument("--project-name", required=True, help="Case folder name")
    parser.add_argument("--provider-name", help="Optional: Filter to a specific provider")
    args = parser.parse_args()
    
    project_path = get_project_path(args.project_name)
    
    if not project_path.exists():
        output_error(f"Project not found: {args.project_name}")
    
    providers = get_providers_data(args.project_name)
    
    # Filter to specific provider if requested
    if args.provider_name:
        search_lower = args.provider_name.lower()
        providers = [p for p in providers if search_lower in p["name"].lower()]
        
        if not providers:
            output_error(f"Provider '{args.provider_name}' not found in {args.project_name}")
    
    if not providers:
        output_error(f"No providers found for {args.project_name}")
    
    # Get client info for display
    overview = read_overview(project_path)
    client_name = get_client_name(overview, args.project_name)
    
    # Calculate totals
    total_billed = sum(p["total_billed"] for p in providers)
    total_paid = sum(p["total_paid"] or 0 for p in providers)
    
    output_result({
        "component": "MedicalProviderCard",
        "data": {
            "client_name": client_name,
            "case_name": args.project_name,
            "providers": providers,
            "total_billed": total_billed,
            "total_paid": total_paid if total_paid > 0 else None,
        },
    })


if __name__ == "__main__":
    main()

