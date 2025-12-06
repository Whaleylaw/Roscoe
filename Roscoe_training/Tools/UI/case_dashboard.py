#!/usr/bin/env python3
"""
Case Dashboard UI Script

Comprehensive case dashboard that COMPOSES from modular components:
- case_snapshot: Client info, status, financial totals
- insurance: Coverage types and claims (no documents)
- medical_providers: Treatment providers (no documents)
- liens: All liens
- expenses: All expenses

This demonstrates the modular architecture - each section is a reusable
component that can be displayed independently or composed together.

Usage:
    python case_dashboard.py --project-name "Abby-Sitgraves-MVA-7-13-2024"

Output:
    JSON with component="CaseDashboard" and composed data from all modules
"""

import argparse
import sys
from pathlib import Path

# Import modular components
from case_snapshot import get_snapshot_data
from insurance import get_insurance_data
from medical_providers import get_providers_data
from liens import get_liens_data
from expenses import get_expenses_data
from _utils import (
    get_project_path,
    output_result,
    output_error,
)


def main():
    parser = argparse.ArgumentParser(description="Generate case dashboard UI data")
    parser.add_argument("--project-name", required=True, help="Case folder name")
    args = parser.parse_args()
    
    project_path = get_project_path(args.project_name)
    
    if not project_path.exists():
        output_error(f"Project not found: {args.project_name}")
    
    # ========================================
    # COMPOSE from modular components
    # ========================================
    
    # 1. Case Snapshot (header section)
    snapshot = get_snapshot_data(args.project_name)
    if "error" in snapshot:
        output_error(snapshot["error"])
    
    # 2. Insurance Coverage (without documents)
    insurance_by_type = get_insurance_data(args.project_name)
    insurance_list = [
        {"type": type_name, "claims": claims}
        for type_name, claims in insurance_by_type.items()
    ]
    
    # 3. Medical Providers (without documents)
    providers = get_providers_data(args.project_name)
    
    # 4. Liens
    liens = get_liens_data(args.project_name)
    
    # 5. Expenses
    expenses = get_expenses_data(args.project_name)
    
    # ========================================
    # Output composed dashboard
    # ========================================
    output_result({
        "component": "CaseDashboard",
        "data": {
            # Snapshot data (flattened for header)
            "client_name": snapshot["client_name"],
            "case_name": snapshot["case_name"],
            "accident_date": snapshot["accident_date"],
            "case_summary": snapshot["case_summary"],
            "current_status": snapshot["current_status"],
            "last_status_update": snapshot["last_status_update"],
            "phase": snapshot["phase"],
            "total_medical_bills": snapshot["total_medical_bills"],
            "total_liens": snapshot["total_liens"],
            "total_expenses": snapshot["total_expenses"],
            "client_address": snapshot["client_address"],
            "client_phone": snapshot["client_phone"],
            "client_email": snapshot["client_email"],
            
            # Accordion sections (arrays for expansion)
            "insurance": insurance_list,
            "providers": providers,
            "liens": liens,
            "expenses": expenses,
        },
    })


if __name__ == "__main__":
    main()

