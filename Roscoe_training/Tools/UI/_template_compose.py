#!/usr/bin/env python3
"""
TEMPLATE: Custom Composed UI View

Copy this file to create custom composed views that combine multiple modules.
Save your version to: Tools/UI/_generated/your_view_name.py

INSTRUCTIONS FOR AGENT:
1. Copy this template to Tools/UI/_generated/ with a descriptive name
2. Import only the modules you need (all available imports shown below)
3. Modify the main() function to build your custom composition
4. Add any custom filtering, sorting, or computed fields
5. Run with: render_ui_script("UI/_generated/your_script.py", ["--project-name", "Case-Name"])

OUTPUT FORMAT:
Your script should output JSON with:
{
    "component": "ComposedView",
    "data": {
        "title": "Your View Title",
        "subtitle": "Optional subtitle",
        "sections": [
            {"type": "snapshot", "data": {...}},
            {"type": "insurance", "data": [...]},
            ...
        ]
    }
}

AVAILABLE SECTION TYPES:
- "snapshot" -> CaseSnapshot component (single object)
- "insurance" -> InsuranceCoverageCard components (array of coverage types)
- "providers" -> MedicalProviderCard components (array of providers)
- "liens" -> LienCard components (array of liens)
- "expenses" -> ExpenseCard components (array of expenses)
- "contact" -> ContactCard component (single object)
- "custom" -> Raw HTML/text block (use "content" field)
"""

import argparse
import sys
from typing import Dict, Any, List, Optional

# ============================================================================
# AVAILABLE MODULES - Import what you need
# ============================================================================

# Case overview data (client info, status, financials)
from case_snapshot import get_snapshot_data

# Insurance coverage data (claims, adjusters, by coverage type)
from insurance import get_insurance_data

# Medical provider data (names, billed amounts, dates of service)
from medical_providers import get_providers_data

# Liens data (lienholder, amounts, status)
from liens import get_liens_data

# Expenses data (description, amount, vendor)
from expenses import get_expenses_data

# Contact lookup (from master directory or project contacts)
from contact_card import find_contact

# Shared utilities
from _utils import (
    get_workspace_path,
    get_project_path,
    read_json_file,
    read_overview,
    output_result,
    output_error,
)


# ============================================================================
# HELPER FUNCTIONS - Use these for common operations
# ============================================================================

def format_currency(amount: float) -> str:
    """Format a number as currency."""
    if amount is None:
        return "$0.00"
    return f"${amount:,.2f}"


def filter_by_amount(items: List[Dict], field: str, min_amount: float) -> List[Dict]:
    """Filter a list of dicts by minimum amount in a field."""
    return [item for item in items if (item.get(field) or 0) >= min_amount]


def sort_by_field(items: List[Dict], field: str, reverse: bool = False) -> List[Dict]:
    """Sort a list of dicts by a field."""
    return sorted(items, key=lambda x: x.get(field) or 0, reverse=reverse)


def compute_total(items: List[Dict], field: str) -> float:
    """Sum a field across a list of dicts."""
    return sum(item.get(field) or 0 for item in items)


# ============================================================================
# MAIN FUNCTION - Customize this for your view
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Custom composed UI view")
    parser.add_argument("--project-name", required=True, help="Case folder name")
    # Add any additional arguments your view needs:
    # parser.add_argument("--min-amount", type=float, default=0, help="Minimum amount filter")
    # parser.add_argument("--coverage-type", help="Filter to specific coverage type")
    args = parser.parse_args()
    
    project_path = get_project_path(args.project_name)
    if not project_path.exists():
        output_error(f"Project not found: {args.project_name}")
    
    # ========================================
    # BUILD YOUR CUSTOM VIEW
    # ========================================
    
    # Example: Get case snapshot
    snapshot = get_snapshot_data(args.project_name)
    if "error" in snapshot:
        output_error(snapshot["error"])
    
    # Example: Get liens and filter to large ones
    liens = get_liens_data(args.project_name)
    # large_liens = filter_by_amount(liens, "original_amount", 500)
    
    # Example: Get insurance data
    insurance_by_type = get_insurance_data(args.project_name)
    insurance_list = [
        {"type": type_name, "claims": claims}
        for type_name, claims in insurance_by_type.items()
    ]
    
    # Example: Get providers sorted by billed amount
    providers = get_providers_data(args.project_name)
    # providers = sort_by_field(providers, "total_billed", reverse=True)
    
    # Example: Get expenses
    expenses = get_expenses_data(args.project_name)
    
    # Example: Compute custom totals
    # total_liens = compute_total(liens, "original_amount")
    # total_bills = compute_total(providers, "total_billed")
    
    # ========================================
    # BUILD SECTIONS ARRAY
    # ========================================
    
    sections = []
    
    # Add snapshot section (always first for context)
    sections.append({
        "type": "snapshot",
        "data": snapshot,
    })
    
    # Add insurance section (if any)
    if insurance_list:
        sections.append({
            "type": "insurance",
            "title": "Insurance Coverage",  # Optional section title
            "data": insurance_list,
        })
    
    # Add providers section (if any)
    if providers:
        sections.append({
            "type": "providers",
            "title": "Medical Providers",
            "data": providers,
        })
    
    # Add liens section (if any)
    if liens:
        sections.append({
            "type": "liens",
            "title": "Liens",
            "data": liens,
        })
    
    # Add expenses section (if any)
    if expenses:
        sections.append({
            "type": "expenses",
            "title": "Expenses",
            "data": expenses,
        })
    
    # Example: Add a custom text section
    # sections.append({
    #     "type": "custom",
    #     "title": "Notes",
    #     "content": "Custom analysis or notes here...",
    # })
    
    # ========================================
    # OUTPUT RESULT
    # ========================================
    
    output_result({
        "component": "ComposedView",
        "data": {
            "title": f"Case Overview: {snapshot.get('client_name', args.project_name)}",
            "subtitle": f"Accident Date: {snapshot.get('accident_date', 'Unknown')}",
            "sections": sections,
        },
    })


if __name__ == "__main__":
    main()


# ============================================================================
# EXAMPLE CUSTOM VIEWS (copy and modify as needed)
# ============================================================================

"""
EXAMPLE 1: Settlement Summary View
----------------------------------
Focus on financials for settlement discussions.

sections = [
    {"type": "snapshot", "data": snapshot},
    {"type": "custom", "title": "Settlement Summary", "content": f'''
        Total Medical Bills: {format_currency(total_bills)}
        Total Liens: {format_currency(total_liens)}
        Net to Client: {format_currency(total_bills - total_liens)}
    '''},
    {"type": "liens", "title": "Outstanding Liens", "data": liens},
]


EXAMPLE 2: Deposition Prep View
-------------------------------
Provider details for deposition preparation.

providers = sort_by_field(providers, "total_billed", reverse=True)
sections = [
    {"type": "snapshot", "data": snapshot},
    {"type": "providers", "title": "Treating Providers (by billing)", "data": providers},
    {"type": "custom", "title": "Key Dates", "content": f'''
        Accident: {snapshot.get('accident_date')}
        First Treatment: [from chronology]
        Last Treatment: [from chronology]
    '''},
]


EXAMPLE 3: Insurance Focus View
-------------------------------
All insurance details for coverage analysis.

sections = [
    {"type": "snapshot", "data": snapshot},
    {"type": "insurance", "title": "Coverage Details", "data": insurance_list},
]
# Then look up each adjuster as a contact
for coverage in insurance_list:
    for claim in coverage.get("claims", []):
        if claim.get("adjuster", {}).get("name"):
            contact = find_contact(claim["adjuster"]["name"], args.project_name)
            if contact:
                sections.append({
                    "type": "contact",
                    "title": f"{coverage['type']} Adjuster",
                    "data": contact,
                })


EXAMPLE 4: Filtered Liens View
------------------------------
Only liens over a certain amount.

large_liens = filter_by_amount(liens, "original_amount", 1000)
sections = [
    {"type": "snapshot", "data": snapshot},
    {"type": "liens", "title": f"Large Liens (>{format_currency(1000)})", "data": large_liens},
    {"type": "custom", "content": f"Showing {len(large_liens)} of {len(liens)} total liens"},
]
"""

