#!/usr/bin/env python3
"""
Case Snapshot UI Script

Provides a quick overview/snapshot of a case including:
- Client name, accident date
- Case summary and current status
- Phase and timeline info
- Financial totals (medical bills, liens, expenses)
- Client contact information

This is a reusable component that can be displayed standalone
or composed into larger views like case_dashboard.

Usage:
    python case_snapshot.py --project-name "Abby-Sitgraves-MVA-7-13-2024"

Output:
    JSON with component="CaseSnapshot" and snapshot data
"""

import argparse
from pathlib import Path
from typing import Dict, Any

# Import shared utilities
from _utils import (
    get_project_path,
    read_overview,
    get_client_name,
    get_accident_date,
    output_result,
    output_error,
)


def get_snapshot_data(project_name: str) -> Dict[str, Any]:
    """
    Get case snapshot data for a project.
    
    This function can be imported and used by other scripts (like case_dashboard).
    
    Args:
        project_name: The case folder name
        
    Returns:
        Dictionary with snapshot data or error info
    """
    project_path = get_project_path(project_name)
    
    if not project_path.exists():
        return {"error": f"Project not found: {project_name}"}
    
    # Read overview
    overview = read_overview(project_path)
    
    # Build snapshot data
    return {
        "client_name": get_client_name(overview, project_name),
        "case_name": project_name,
        "accident_date": get_accident_date(overview),
        
        # Status & Phase
        "case_summary": overview.get("case_summary", ""),
        "current_status": overview.get("current_status", ""),
        "last_status_update": overview.get("last_status_update", ""),
        "phase": overview.get("phase", ""),
        
        # Timeline
        "case_create_date": overview.get("case_create_date", ""),
        "case_last_activity": overview.get("case_last_activity", ""),
        
        # Financials
        "total_medical_bills": overview.get("total_medical_bills", 0),
        "total_liens": overview.get("total_liens", 0),
        "total_expenses": overview.get("total_expenses", 0),
        
        # Client Contact
        "client_address": overview.get("client_address", ""),
        "client_phone": overview.get("client_phone", ""),
        "client_email": overview.get("client_email", ""),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate case snapshot UI data")
    parser.add_argument("--project-name", required=True, help="Case folder name")
    args = parser.parse_args()
    
    data = get_snapshot_data(args.project_name)
    
    if "error" in data:
        output_error(data["error"])
    
    output_result({
        "component": "CaseSnapshot",
        "data": data,
    })


if __name__ == "__main__":
    main()

