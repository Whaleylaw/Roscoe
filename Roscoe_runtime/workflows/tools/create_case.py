#!/usr/bin/env python3
"""
create_case.py - Create case folder structure and initialize JSON files

This tool creates the complete folder structure for a new personal injury case,
including all JSON tracking files in the Case Information folder.

Usage:
    result = create_case("John Doe", "MVA", "01-15-2025")
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


# Base path for all case folders
ROSCOE_ROOT = Path(os.environ.get("ROSCOE_ROOT", Path(__file__).resolve().parents[2]))
CASES_BASE_PATH = os.environ.get("ROSCOE_CASES_BASE_PATH", str(ROSCOE_ROOT))

# Valid case types
VALID_CASE_TYPES = {"MVA", "SF", "WC"}

# Case type full names
CASE_TYPE_NAMES = {
    "MVA": "Motor Vehicle Accident",
    "SF": "Slip and Fall",
    "WC": "Workers' Compensation"
}


def create_case(client_name: str, case_type: str, accident_date: str) -> dict:
    """
    Create case folder structure and initialize all JSON files.
    
    Args:
        client_name: Client's full name (e.g., "John Doe")
        case_type: Case type code - "MVA", "SF", or "WC"
        accident_date: Date of accident in MM-DD-YYYY format
    
    Returns:
        dict: {
            "success": bool,
            "case_path": str (path to created folder),
            "case_name": str (folder name),
            "next_workflow": str,
            "error": str (only if success=False)
        }
    """
    # Normalize case type
    case_type = case_type.upper().replace("S&F", "SF").replace("S/F", "SF")
    
    # Validate inputs
    validation_error = _validate_inputs(client_name, case_type, accident_date)
    if validation_error:
        return {"success": False, "error": validation_error}
    
    # Generate folder name
    folder_name = _generate_folder_name(client_name, case_type, accident_date)
    case_path = os.path.join(CASES_BASE_PATH, folder_name)
    
    # Check if folder already exists
    if os.path.exists(case_path):
        return {
            "success": False,
            "error": f"Case folder already exists: {folder_name}"
        }
    
    try:
        # Create folder structure
        _create_folder_structure(case_path)
        
        # Create JSON files
        _create_json_files(case_path, client_name, case_type, accident_date)
        
        return {
            "success": True,
            "case_path": case_path,
            "case_name": folder_name,
            "next_workflow": "document_collection"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create case: {str(e)}"
        }


def _validate_inputs(client_name: str, case_type: str, accident_date: str) -> Optional[str]:
    """Validate all inputs and return error message if invalid."""
    
    # Validate client name
    if not client_name or len(client_name.strip()) < 2:
        return "Client name is required"
    
    name_parts = client_name.strip().split()
    if len(name_parts) < 2:
        return "Client name must include first and last name"
    
    # Validate case type
    if case_type not in VALID_CASE_TYPES:
        return f"Invalid case type: {case_type}. Must be one of: MVA, SF, WC"
    
    # Validate date format
    try:
        datetime.strptime(accident_date, "%m-%d-%Y")
    except ValueError:
        return f"Invalid date format: {accident_date}. Use MM-DD-YYYY"
    
    return None


def _generate_folder_name(client_name: str, case_type: str, accident_date: str) -> str:
    """Generate the case folder name from inputs."""
    
    # Clean and format client name
    name_parts = client_name.strip().split()
    formatted_name = "-".join(part.capitalize() for part in name_parts)
    
    # Combine into folder name
    return f"{formatted_name}-{case_type}-{accident_date}"


def _create_folder_structure(case_path: str) -> None:
    """Create all folders and subfolders for the case."""
    
    folders = [
        "Case Information",
        "Client",
        "Expenses",
        "Insurance/BI",
        "Insurance/PIP",
        "Investigation",
        "Liens",
        "Litigation/Correspondence",
        "Litigation/Discovery/Depositions",
        "Litigation/Discovery/Interrogatories",
        "Litigation/Experts",
        "Litigation/Mediation",
        "Litigation/Pleadings",
        "Litigation/Trial",
        "Medical Providers",
        "Negotiation-Settlement",
        "Reports"
    ]
    
    for folder in folders:
        folder_path = os.path.join(case_path, folder)
        os.makedirs(folder_path, exist_ok=True)


def _create_json_files(case_path: str, client_name: str, case_type: str, accident_date: str) -> None:
    """Create all JSON files in Case Information folder."""
    
    case_info_path = os.path.join(case_path, "Case Information")
    folder_name = os.path.basename(case_path)
    
    # Parse accident date
    accident_dt = datetime.strptime(accident_date, "%m-%d-%Y")
    
    # overview.json - pre-populated with case info
    overview_data = [{
        "jsonb_agg": [{
            "project_name": folder_name,
            "client_name": client_name,
            "case_type": case_type,
            "case_type_full": CASE_TYPE_NAMES.get(case_type, case_type),
            "case_summary": "",
            "current_status": "Intake",
            "last_status_update": datetime.now().isoformat(),
            "client_address": "",
            "client_phone": "",
            "client_email": "",
            "accident_date": accident_dt.strftime("%Y-%m-%d"),
            "total_medical_bills": 0,
            "total_expenses": 0,
            "total_liens": 0,
            "case_last_activity": datetime.now().isoformat(),
            "case_create_date": datetime.now().isoformat(),
            "phase": "onboarding",
            "case_role": "solo",
            "parent_project_name": None
        }]
    }]
    
    # contacts.json - empty template
    contacts_data = [{"jsonb_agg": []}]
    
    # insurance.json - empty template
    insurance_data = [{"jsonb_agg": []}]
    
    # liens.json - empty template
    liens_data = [{"jsonb_agg": []}]
    
    # expenses.json - empty template
    expenses_data = [{"jsonb_agg": []}]
    
    # medical_providers.json - empty template
    medical_providers_data = [{"jsonb_agg": []}]
    
    # notes.json - empty template
    notes_data = [{"jsonb_agg": []}]
    
    # litigation.json - empty template
    litigation_data = [{"jsonb_agg": []}]
    
    # pleadings.json - empty template
    pleadings_data = [{"jsonb_agg": []}]
    
    # workflow_state.json - initialized for Phase 0
    workflow_state_data = _create_workflow_state(case_type)
    
    # Write all JSON files
    json_files = {
        "overview.json": overview_data,
        "contacts.json": contacts_data,
        "insurance.json": insurance_data,
        "liens.json": liens_data,
        "expenses.json": expenses_data,
        "medical_providers.json": medical_providers_data,
        "notes.json": notes_data,
        "litigation.json": litigation_data,
        "pleadings.json": pleadings_data,
        "workflow_state.json": workflow_state_data
    }
    
    for filename, data in json_files.items():
        file_path = os.path.join(case_info_path, filename)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)


def _create_workflow_state(case_type: str) -> dict:
    """Create the initial workflow_state.json content."""
    
    # Base documents required for all case types
    documents_pending = [
        "new_client_information_sheet",
        "fee_agreement",
        "medical_authorization",
        "medical_treatment_questionnaire",
        "digital_signature_authorization"
    ]
    
    # Add case-type specific documents
    if case_type == "MVA":
        documents_pending.append("mva_accident_detail_sheet")
    elif case_type == "SF":
        documents_pending.append("sf_accident_detail_sheet")
    elif case_type == "WC":
        documents_pending.append("wage_salary_verification")
    
    return {
        "phase": "onboarding",
        "phase_number": 0,
        "case_type": case_type,
        "workflow_status": {
            "case_setup": "completed",
            "document_collection": "in_progress"
        },
        "landmarks": {
            "client_info_received": False,
            "contract_signed": False,
            "medical_auth_signed": False
        },
        "documents_received": [],
        "documents_pending": documents_pending,
        "blockers": [],
        "next_action": "Collect intake documents",
        "last_updated": datetime.now().isoformat()
    }


# For direct execution / testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 4:
        result = create_case(sys.argv[1], sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python create_case.py 'Client Name' 'MVA|SF|WC' 'MM-DD-YYYY'")
        print("Example: python create_case.py 'John Doe' 'MVA' '01-15-2025'")

