#!/usr/bin/env python3
"""
Expenses UI Script

Displays all expenses for a case. Can be used standalone or imported
by other components like case_dashboard.

Usage:
    python expenses.py --project-name "Abby-Sitgraves-MVA-7-13-2024"

Output:
    JSON with component="ExpenseCard" and expenses data array
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


def get_expenses_data(project_name: str) -> List[Dict[str, Any]]:
    """
    Get expenses data for a project.
    
    This function can be imported and used by other scripts.
    
    Args:
        project_name: The case folder name
        
    Returns:
        List of expense dictionaries
    """
    project_path = get_project_path(project_name)
    
    if not project_path.exists():
        return []
    
    expenses_raw = read_json_file(project_path / "Case Information" / "expenses.json") or []
    
    expenses = []
    for expense in expenses_raw:
        if not isinstance(expense, dict):
            continue
        expenses.append({
            "description": expense.get("description", ""),
            "category": expense.get("category"),
            "vendor": expense.get("payable_to") or expense.get("vendor"),
            "amount": expense.get("amount", 0) or 0,
            "date_incurred": expense.get("date") or expense.get("date_incurred"),
            "date_paid": expense.get("date_paid"),
            "status": expense.get("status"),
            "reimbursable": expense.get("reimbursable"),
            "notes": expense.get("notes"),
        })
    
    return expenses


def main():
    parser = argparse.ArgumentParser(description="Generate expenses UI data")
    parser.add_argument("--project-name", required=True, help="Case folder name")
    args = parser.parse_args()
    
    project_path = get_project_path(args.project_name)
    
    if not project_path.exists():
        output_error(f"Project not found: {args.project_name}")
    
    expenses = get_expenses_data(args.project_name)
    
    if not expenses:
        output_error(f"No expenses found for {args.project_name}")
    
    # Get client name for display
    overview = read_overview(project_path)
    client_name = get_client_name(overview, args.project_name)
    
    output_result({
        "component": "ExpenseCard",
        "data": {
            "client_name": client_name,
            "case_name": args.project_name,
            "expenses": expenses,
        },
    })


if __name__ == "__main__":
    main()

