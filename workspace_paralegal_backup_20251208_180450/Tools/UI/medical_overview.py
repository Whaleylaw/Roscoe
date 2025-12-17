#!/usr/bin/env python3
"""
Medical Overview UI Script

Medical treatment overview WITH documents. Uses the modular medical_providers
component and adds document links from the file system.

For providers WITHOUT documents, use medical_providers.py instead.

Usage:
    python medical_overview.py --project-name "Abby-Sitgraves-MVA-7-13-2024"

Output:
    JSON with component="MedicalTreatmentOverview" and providers + documents
"""

import argparse
import os
from pathlib import Path
from typing import Dict, Any, List

# Import modular components
from medical_providers import get_providers_data
from _utils import (
    get_workspace_path,
    get_project_path,
    read_overview,
    get_client_name,
    get_accident_date,
    generate_file_url,
    output_result,
    output_error,
)


def find_provider_folder(medical_records_path: Path, provider_name: str) -> Path | None:
    """
    Find the folder for a provider by matching the name.
    Handles partial matches and common variations.
    """
    if not medical_records_path.exists():
        return None
    
    provider_lower = provider_name.lower()
    
    # Try exact match first
    for folder in medical_records_path.iterdir():
        if folder.is_dir() and folder.name.lower() == provider_lower:
            return folder
    
    # Try partial match
    for folder in medical_records_path.iterdir():
        if folder.is_dir():
            folder_lower = folder.name.lower()
            # Check if provider name is in folder name or vice versa
            if provider_lower in folder_lower or folder_lower in provider_lower:
                return folder
            # Handle common abbreviations
            if "uofl" in provider_lower and "university of louisville" in folder_lower:
                return folder
            if "university of louisville" in provider_lower and "uofl" in folder_lower:
                return folder
    
    return None


def get_provider_documents(project_path: Path, provider_name: str, workspace_path: Path) -> Dict[str, List[Dict]]:
    """
    Scan Medical Records folder for documents belonging to a provider.
    
    Folder structure expected:
        Medical Records/
        └── [Provider Name]/
            ├── Medical Bills/
            ├── Medical Records/
            └── Medical Requests/
    
    Returns dict with:
        - records: List of medical record documents
        - bills: List of billing documents
        - requests: List of request/correspondence documents
    """
    categories: Dict[str, List[Dict]] = {
        "records": [],
        "bills": [],
        "requests": [],
    }
    
    medical_folder = project_path / "Medical Records"
    provider_folder = find_provider_folder(medical_folder, provider_name)
    
    if not provider_folder:
        return categories
    
    # Scan the provider's subfolders
    for subfolder in provider_folder.iterdir():
        if not subfolder.is_dir():
            continue
        
        subfolder_lower = subfolder.name.lower()
        
        # Determine category based on subfolder name
        if "bill" in subfolder_lower:
            category = "bills"
        elif "request" in subfolder_lower or "correspondence" in subfolder_lower:
            category = "requests"
        else:
            # Default to records (includes "Medical Records" subfolder)
            category = "records"
        
        # Scan files in the subfolder
        for file in subfolder.rglob("*"):
            if file.is_file() and file.suffix.lower() in ['.pdf', '.md', '.txt', '.doc', '.docx']:
                # Skip .DS_Store and other hidden files
                if file.name.startswith('.'):
                    continue
                    
                doc = {
                    "filename": file.name,
                    "path": str(file.relative_to(project_path)),
                    "view_url": generate_file_url(file, workspace_path, "inline"),
                    "download_url": generate_file_url(file, workspace_path, "attachment"),
                    "file_type": file.suffix.lower().lstrip('.'),
                }
                categories[category].append(doc)
    
    # Sort each category by filename
    for cat in categories:
        categories[cat].sort(key=lambda x: x["filename"])
    
    return categories


def main():
    parser = argparse.ArgumentParser(description="Generate medical overview UI data")
    parser.add_argument("--project-name", required=True, help="Case folder name")
    args = parser.parse_args()
    
    workspace_path = get_workspace_path()
    project_path = get_project_path(args.project_name)
    
    if not project_path.exists():
        output_error(f"Project not found: {args.project_name}")
    
    # Get base provider data from modular component
    providers = get_providers_data(args.project_name)
    
    if not providers:
        output_error(f"No medical providers found for {args.project_name}")
    
    # Enhance each provider with documents from folder structure
    for provider in providers:
        docs = get_provider_documents(project_path, provider["name"], workspace_path)
        provider["categories"] = docs
        
        # Also set legacy "documents" field for backwards compatibility
        provider["documents"] = {
            "records": docs.get("records", []),
            "bills": docs.get("bills", []),
        }
    
    # Get client info
    overview = read_overview(project_path)
    client_name = get_client_name(overview, args.project_name)
    accident_date = get_accident_date(overview)
    
    # Calculate totals
    total_billed = sum(p["total_billed"] for p in providers)
    total_paid = sum(p.get("total_paid") or 0 for p in providers)
    
    output_result({
        "component": "MedicalTreatmentOverview",
        "data": {
            "client_name": client_name,
            "case_name": args.project_name,
            "accident_date": accident_date,
            "providers": providers,
            "total_billed": total_billed,
            "total_paid": total_paid if total_paid > 0 else None,
        },
    })


if __name__ == "__main__":
    main()

