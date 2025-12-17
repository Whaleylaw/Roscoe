#!/usr/bin/env python3
"""
Insurance Coverage Card UI Script

Displays details for a specific insurance coverage type (PIP, BI, UIM, etc.)
for a given case.

Usage:
    python insurance_coverage.py --project-name "Abby-Sitgraves-MVA-7-13-2024" --coverage-type "PIP"

Output:
    JSON with component="InsuranceCoverageCard" and coverage data
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import quote


def get_workspace_path() -> Path:
    """Get workspace path from environment or default."""
    return Path(os.environ.get("WORKSPACE_DIR", "/workspace"))


def generate_file_url(file_path: Path, workspace_path: Path, disposition: str = "inline") -> str:
    """Generate a local API URL for file access."""
    relative_path = file_path.relative_to(workspace_path)
    encoded_path = quote(str(relative_path), safe='')
    return f"/api/files?path={encoded_path}&disposition={disposition}"


def read_json_file(file_path: Path) -> Any:
    """Read a JSON file, handling nested database export format."""
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r') as f:
            raw = json.load(f)
        
        if isinstance(raw, list) and len(raw) > 0:
            first_item = raw[0]
            if isinstance(first_item, dict) and "jsonb_agg" in first_item:
                jsonb_data = first_item["jsonb_agg"]
                return jsonb_data if isinstance(jsonb_data, list) else [jsonb_data]
            return raw
        return raw
    except Exception as e:
        print(f"Warning: Failed to read {file_path}: {e}", file=sys.stderr)
        return None


def scan_insurance_files(project_path: Path, insurance_type: str, company_name: str, workspace_path: Path) -> List[Dict]:
    """Scan insurance documents for a specific type and company."""
    files = []
    insurance_path = project_path / "Insurance" / insurance_type / company_name
    
    if not insurance_path.exists():
        insurance_path = project_path / "Insurance" / insurance_type
        if not insurance_path.exists():
            return files
    
    def scan_dir(dir_path: Path):
        if not dir_path.exists():
            return
        for item in dir_path.iterdir():
            if item.is_file() and item.suffix.lower() in ['.pdf', '.md', '.eml', '.jpg', '.jpeg', '.png']:
                files.append({
                    "filename": item.name,
                    "view_url": generate_file_url(item, workspace_path, "inline"),
                    "download_url": generate_file_url(item, workspace_path, "attachment"),
                    "file_type": item.suffix.lower()[1:],
                })
            elif item.is_dir():
                scan_dir(item)
    
    scan_dir(insurance_path)
    return files


def get_adjuster_info(contacts_data: List[Dict], adjuster_name: str) -> Optional[Dict]:
    """Look up adjuster contact information."""
    if not adjuster_name:
        return None
    
    for contact in contacts_data:
        if not isinstance(contact, dict):
            continue
        if contact.get("full_name", "").lower() == adjuster_name.lower():
            return {
                "name": contact.get("full_name"),
                "email": contact.get("email"),
                "phone": contact.get("phone"),
                "address": contact.get("address"),
            }
    
    return {"name": adjuster_name, "email": None, "phone": None, "address": None}


def normalize_coverage_type(coverage_type: str) -> List[str]:
    """Return list of possible matches for the coverage type."""
    ct = coverage_type.upper()
    variants = [coverage_type]
    
    if ct == "PIP":
        variants.extend(["Personal Injury Protection (PIP)", "Personal Injury Protection", "PIP Coverage"])
    elif ct == "BI":
        variants.extend(["Bodily Injury (BI)", "Bodily Injury", "BI Coverage"])
    elif ct == "UIM":
        variants.extend(["Underinsured Motorist (UIM)", "Underinsured Motorist", "UIM Coverage"])
    elif ct == "UM":
        variants.extend(["Uninsured Motorist (UM)", "Uninsured Motorist", "UM Coverage"])
    elif ct == "MEDPAY":
        variants.extend(["Medical Payments (MedPay)", "Medical Payments", "MedPay"])
    elif ct == "PD":
        variants.extend(["Property Damage (PD)", "Property Damage", "PD Coverage"])
    
    return variants


def main():
    parser = argparse.ArgumentParser(description="Generate insurance coverage card UI data")
    parser.add_argument("--project-name", required=True, help="Case folder name")
    parser.add_argument("--coverage-type", required=True, help="Coverage type (e.g., PIP, BI, UIM)")
    args = parser.parse_args()
    
    workspace_path = get_workspace_path()
    project_path = workspace_path / "projects" / args.project_name
    
    if not project_path.exists():
        result = {"error": f"Project not found: {args.project_name}", "success": False}
        print(json.dumps(result))
        sys.exit(1)
    
    # Read insurance.json
    insurance_data = read_json_file(project_path / "Case Information" / "insurance.json") or []
    contacts_data = read_json_file(project_path / "Case Information" / "contacts.json") or []
    
    # Find matching coverage type
    type_variants = normalize_coverage_type(args.coverage_type)
    claims = []
    matched_type = None
    
    for insurance in insurance_data:
        if not isinstance(insurance, dict):
            continue
        
        ins_type = insurance.get("insurance_type", "")
        
        # Check if this matches our requested type
        if ins_type in type_variants or any(v.lower() in ins_type.lower() for v in type_variants):
            matched_type = ins_type
            company_name = insurance.get("insurance_company_name", "Unknown")
            adjuster_name = insurance.get("adjuster_name", "")
            adjuster = get_adjuster_info(contacts_data, adjuster_name) if adjuster_name else None
            documents = scan_insurance_files(project_path, ins_type, company_name, workspace_path)
            
            claims.append({
                "company_name": company_name,
                "claim_number": insurance.get("claim_number"),
                "adjuster": adjuster,
                "coverage_confirmation": insurance.get("coverage_confirmation"),
                "policy_limits": insurance.get("policy_limits"),
                "demanded_amount": insurance.get("demand_amount"),
                "current_offer": insurance.get("offer_amount"),
                "settlement_amount": insurance.get("settlement_amount"),
                "is_active_negotiation": insurance.get("is_active_negotiation", False),
                "notes": insurance.get("notes"),
                "documents": documents,
            })
    
    if not claims:
        result = {"error": f"No {args.coverage_type} coverage found for {args.project_name}", "success": False}
        print(json.dumps(result))
        sys.exit(1)
    
    result = {
        "component": "InsuranceCoverageCard",
        "data": {
            "type": matched_type or args.coverage_type,
            "claims": claims,
        },
        "success": True
    }
    
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()

