#!/usr/bin/env python3
"""
Medical Provider Card UI Script

Displays details for a specific medical provider including billing
and documents.

Usage:
    python medical_provider.py --project-name "Abby-Sitgraves-MVA-7-13-2024" --provider-name "Jewish Hospital"

Output:
    JSON with component="MedicalProviderCard" and provider data
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
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


def scan_medical_files(project_path: Path, provider_name: str, workspace_path: Path) -> Dict[str, List[Dict]]:
    """Scan medical records for files belonging to a provider."""
    categories: Dict[str, List[Dict]] = {
        "Medical Records": [],
        "Medical Bills": [],
        "Correspondence": [],
    }
    
    provider_variants = [
        provider_name.lower(),
        provider_name.lower().replace(" ", "-"),
        provider_name.lower().replace(" ", "_"),
    ]
    
    medical_records_path = project_path / "Medical Records"
    if medical_records_path.exists():
        for subfolder in medical_records_path.iterdir():
            if subfolder.is_dir():
                subfolder_lower = subfolder.name.lower()
                if any(v in subfolder_lower or subfolder_lower in v for v in provider_variants):
                    for item in subfolder.rglob("*"):
                        if item.is_file() and item.suffix.lower() in ['.pdf', '.md', '.eml', '.jpg', '.jpeg', '.png']:
                            file_entry = {
                                "filename": item.name,
                                "view_url": generate_file_url(item, workspace_path, "inline"),
                                "download_url": generate_file_url(item, workspace_path, "attachment"),
                                "file_type": item.suffix.lower()[1:],
                            }
                            
                            name_lower = item.name.lower()
                            if "bill" in name_lower or "invoice" in name_lower:
                                categories["Medical Bills"].append(file_entry)
                            elif "correspondence" in name_lower or item.suffix.lower() == ".eml":
                                categories["Correspondence"].append(file_entry)
                            else:
                                categories["Medical Records"].append(file_entry)
    
    return {k: v for k, v in categories.items() if v}


def main():
    parser = argparse.ArgumentParser(description="Generate medical provider card UI data")
    parser.add_argument("--project-name", required=True, help="Case folder name")
    parser.add_argument("--provider-name", required=True, help="Name of the medical provider")
    args = parser.parse_args()
    
    workspace_path = get_workspace_path()
    project_path = workspace_path / "projects" / args.project_name
    
    if not project_path.exists():
        result = {"error": f"Project not found: {args.project_name}", "success": False}
        print(json.dumps(result))
        sys.exit(1)
    
    # Read medical_providers.json
    providers_data = read_json_file(project_path / "Case Information" / "medical_providers.json") or []
    
    # Find matching provider
    search_lower = args.provider_name.lower()
    matched_provider = None
    
    for provider in providers_data:
        if not isinstance(provider, dict):
            continue
        provider_name = provider.get("provider_full_name", "")
        if search_lower in provider_name.lower() or provider_name.lower() in search_lower:
            matched_provider = provider
            break
    
    if not matched_provider:
        result = {"error": f"Provider '{args.provider_name}' not found in {args.project_name}", "success": False}
        print(json.dumps(result))
        sys.exit(1)
    
    provider_name = matched_provider.get("provider_full_name", args.provider_name)
    categories = scan_medical_files(project_path, provider_name, workspace_path)
    
    dates_of_service = []
    if matched_provider.get("date_treatment_started"):
        dates_of_service.append(matched_provider["date_treatment_started"])
    if matched_provider.get("date_treatment_completed") and matched_provider.get("date_treatment_completed") != matched_provider.get("date_treatment_started"):
        dates_of_service.append(matched_provider["date_treatment_completed"])
    
    result = {
        "component": "MedicalProviderCard",
        "data": {
            "name": provider_name,
            "specialty": None,
            "total_billed": matched_provider.get("billed_amount", 0) or 0,
            "total_paid": matched_provider.get("settlement_payment"),
            "dates_of_service": dates_of_service,
            "categories": categories,
            "notes": matched_provider.get("medical_provider_notes"),
        },
        "success": True
    }
    
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()

