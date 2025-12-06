#!/usr/bin/env python3
"""
Liens UI Script

Displays all liens for a case. Can be used standalone or imported
by other components like case_dashboard.

Usage:
    python liens.py --project-name "Abby-Sitgraves-MVA-7-13-2024"

Output:
    JSON with component="LienCard" and liens data array
"""

import argparse
from pathlib import Path
from typing import Dict, Any, List

from _utils import (
    get_project_path,
    read_json_file,
    read_overview,
    get_client_name,
    output_result,
    output_error,
)


def get_liens_data(project_name: str) -> List[Dict[str, Any]]:
    """
    Get liens data for a project.
    
    This function can be imported and used by other scripts.
    
    Args:
        project_name: The case folder name
        
    Returns:
        List of lien dictionaries
    """
    project_path = get_project_path(project_name)
    
    if not project_path.exists():
        return []
    
    liens_raw = read_json_file(project_path / "Case Information" / "liens.json") or []
    
    liens = []
    for lien in liens_raw:
        if not isinstance(lien, dict):
            continue
        liens.append({
            "lienholder_name": lien.get("lienholder_name", "Unknown"),
            "lien_type": lien.get("lien_type"),
            "original_amount": lien.get("final_amount") or lien.get("original_amount"),
            "negotiated_amount": lien.get("amount_owed"),
            "reduction_amount": lien.get("reduction_amount"),
            "paid_amount": lien.get("paid_amount"),
            "status": lien.get("status"),
            "date_received": lien.get("date_notice_received") or lien.get("date_received"),
            "date_resolved": lien.get("date_lien_paid") or lien.get("date_resolved"),
            "contact_name": lien.get("contact_name"),
            "contact_phone": lien.get("contact_phone"),
            "contact_email": lien.get("contact_email"),
            "notes": lien.get("notes"),
        })
    
    return liens


def main():
    parser = argparse.ArgumentParser(description="Generate liens UI data")
    parser.add_argument("--project-name", required=True, help="Case folder name")
    args = parser.parse_args()
    
    project_path = get_project_path(args.project_name)
    
    if not project_path.exists():
        output_error(f"Project not found: {args.project_name}")
    
    liens = get_liens_data(args.project_name)
    
    if not liens:
        output_error(f"No liens found for {args.project_name}")
    
    # Get client name for display
    overview = read_overview(project_path)
    client_name = get_client_name(overview, args.project_name)
    
    output_result({
        "component": "LienCard",
        "data": {
            "client_name": client_name,
            "case_name": args.project_name,
            "liens": liens,
        },
    })


if __name__ == "__main__":
    main()

