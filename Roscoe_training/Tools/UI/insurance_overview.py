#!/usr/bin/env python3
"""
Insurance Overview UI Script

Insurance coverage overview WITH documents. Uses the modular insurance
component and adds document links from the file system.

For insurance WITHOUT documents, use insurance.py instead.

Usage:
    python insurance_overview.py --project-name "Abby-Sitgraves-MVA-7-13-2024"

Output:
    JSON with component="InsuranceOverview" and coverage + documents
"""

import argparse
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import modular components
from insurance import get_insurance_data
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


def normalize_coverage_type(coverage_type: str) -> List[str]:
    """
    Generate variations of a coverage type name for folder matching.
    """
    ct = coverage_type.lower()
    variations = [coverage_type, ct]
    
    if 'pip' in ct or 'personal injury protection' in ct:
        variations.extend(['pip', 'personal injury protection', 'personal injury protection (pip)'])
    elif 'bi' in ct or 'bodily injury' in ct:
        variations.extend(['bi', 'bodily injury', 'bodily injury (bi)'])
    elif 'uim' in ct or 'underinsured' in ct:
        variations.extend(['uim', 'underinsured', 'underinsured motorist', 'underinsured motorist (uim)'])
    elif 'um' in ct or 'uninsured' in ct:
        variations.extend(['um', 'uninsured', 'uninsured motorist', 'uninsured motorist (um)'])
    elif 'medpay' in ct or 'medical pay' in ct:
        variations.extend(['medpay', 'medical payments', 'medical payments (medpay)'])
    elif 'property' in ct or 'pd' in ct:
        variations.extend(['pd', 'property damage', 'property damage (pd)'])
    
    return variations


def find_coverage_folder(insurance_path: Path, coverage_type: str) -> Optional[Path]:
    """Find folder matching coverage type."""
    if not insurance_path.exists():
        return None
    
    variations = normalize_coverage_type(coverage_type)
    
    for folder in insurance_path.iterdir():
        if folder.is_dir():
            folder_lower = folder.name.lower()
            if any(v in folder_lower for v in variations):
                return folder
    
    return None


def find_company_folder(coverage_folder: Path, company_name: str) -> Optional[Path]:
    """Find folder matching company name within a coverage folder."""
    if not coverage_folder or not coverage_folder.exists():
        return None
    
    company_lower = company_name.lower()
    
    for folder in coverage_folder.iterdir():
        if folder.is_dir():
            folder_lower = folder.name.lower()
            # Check for partial match
            if company_lower in folder_lower or folder_lower in company_lower:
                return folder
            # Check individual words
            company_words = company_lower.split()
            if any(word in folder_lower for word in company_words if len(word) > 3):
                return folder
    
    return None


def get_insurance_documents(project_path: Path, coverage_type: str, company_name: str, workspace_path: Path) -> List[Dict]:
    """
    Scan Insurance folder for documents.
    
    Folder structure expected:
        Insurance/
        └── [Coverage Type]/
            └── [Company Name]/
                └── documents
    """
    documents = []
    
    insurance_folder = project_path / "Insurance"
    if not insurance_folder.exists():
        return documents
    
    # Try to find coverage type folder
    coverage_folder = find_coverage_folder(insurance_folder, coverage_type)
    
    if coverage_folder:
        # Try to find company folder within coverage
        company_folder = find_company_folder(coverage_folder, company_name)
        
        if company_folder:
            # Scan company folder
            for file in company_folder.rglob("*"):
                if file.is_file() and file.suffix.lower() in ['.pdf', '.md', '.txt', '.doc', '.docx']:
                    if file.name.startswith('.'):
                        continue
                    documents.append({
                        "filename": file.name,
                        "path": str(file.relative_to(project_path)),
                        "view_url": generate_file_url(file, workspace_path, "inline"),
                        "download_url": generate_file_url(file, workspace_path, "attachment"),
                        "file_type": file.suffix.lower().lstrip('.'),
                    })
        else:
            # No company subfolder, scan coverage folder directly
            for file in coverage_folder.rglob("*"):
                if file.is_file() and file.suffix.lower() in ['.pdf', '.md', '.txt', '.doc', '.docx']:
                    if file.name.startswith('.'):
                        continue
                    documents.append({
                        "filename": file.name,
                        "path": str(file.relative_to(project_path)),
                        "view_url": generate_file_url(file, workspace_path, "inline"),
                        "download_url": generate_file_url(file, workspace_path, "attachment"),
                        "file_type": file.suffix.lower().lstrip('.'),
                    })
    else:
        # Fallback: search entire Insurance folder by coverage type and company name
        search_terms = normalize_coverage_type(coverage_type) + [company_name.lower()]
        
        for file in insurance_folder.rglob("*"):
            if file.is_file() and file.suffix.lower() in ['.pdf', '.md', '.txt', '.doc', '.docx']:
                if file.name.startswith('.'):
                    continue
                
                name_lower = file.name.lower()
                path_lower = str(file.relative_to(project_path)).lower()
                
                if any(term in name_lower or term in path_lower for term in search_terms):
                    documents.append({
                        "filename": file.name,
                        "path": str(file.relative_to(project_path)),
                        "view_url": generate_file_url(file, workspace_path, "inline"),
                        "download_url": generate_file_url(file, workspace_path, "attachment"),
                        "file_type": file.suffix.lower().lstrip('.'),
                    })
    
    # Sort by filename
    documents.sort(key=lambda x: x["filename"])
    
    return documents


def main():
    parser = argparse.ArgumentParser(description="Generate insurance overview UI data")
    parser.add_argument("--project-name", required=True, help="Case folder name")
    args = parser.parse_args()
    
    workspace_path = get_workspace_path()
    project_path = get_project_path(args.project_name)
    
    if not project_path.exists():
        output_error(f"Project not found: {args.project_name}")
    
    # Get base insurance data from modular component
    insurance_by_type = get_insurance_data(args.project_name)
    
    if not insurance_by_type:
        output_error(f"No insurance found for {args.project_name}")
    
    # Convert to list and add documents to each coverage type
    coverage_list = []
    for type_name, claims in insurance_by_type.items():
        # Collect documents for this coverage type
        all_documents = []
        for claim in claims:
            company_name = claim.get("company_name", "")
            docs = get_insurance_documents(project_path, type_name, company_name, workspace_path)
            
            # Attach documents to the claim as well
            claim["documents"] = docs
            all_documents.extend(docs)
        
        # Deduplicate documents (same file might match multiple claims)
        seen_paths = set()
        unique_documents = []
        for doc in all_documents:
            if doc["path"] not in seen_paths:
                seen_paths.add(doc["path"])
                unique_documents.append(doc)
        
        coverage_list.append({
            "type": type_name,
            "claims": claims,
            "documents": unique_documents,
        })
    
    # Get client info
    overview = read_overview(project_path)
    client_name = get_client_name(overview, args.project_name)
    accident_date = get_accident_date(overview)
    
    output_result({
        "component": "InsuranceOverview",
        "data": {
            "client_name": client_name,
            "case_name": args.project_name,
            "accident_date": accident_date,
            "coverage_types": coverage_list,
        },
    })


if __name__ == "__main__":
    main()

