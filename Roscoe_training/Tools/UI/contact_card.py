#!/usr/bin/env python3
"""
Contact Card UI Script

Displays contact information for a person. Searches:
1. Master contact directory first (Database/master_lists/Database_directory.json)
2. Project-specific contacts if project name provided

Usage:
    python contact_card.py --contact-name "Jordan Bahr"
    python contact_card.py --contact-name "Jordan Bahr" --project-name "Abby-Sitgraves-MVA-7-13-2024"

Output:
    JSON with component="ContactCard" and contact data
"""

import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

from _utils import (
    get_workspace_path,
    get_project_path,
    read_json_file,
    output_result,
    output_error,
)


def find_contact(contact_name: str, project_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Search for a contact by name.
    
    Searches master directory first, then project-specific contacts.
    Uses fuzzy matching (case-insensitive, partial match).
    """
    workspace_path = get_workspace_path()
    search_lower = contact_name.lower()
    
    # 1. Search master directory first
    master_path = workspace_path / "Database" / "master_lists" / "Database_directory.json"
    master_contacts = read_json_file(master_path) or []
    
    for contact in master_contacts:
        if not isinstance(contact, dict):
            continue
        
        # Try different name fields
        full_name = contact.get("full_name", "")
        if not full_name:
            first = contact.get("first_name", "")
            last = contact.get("last_name", "")
            full_name = f"{first} {last}".strip()
        
        if search_lower in full_name.lower():
            return normalize_contact(contact)
    
    # 2. Search project-specific contacts if project provided
    if project_name:
        project_path = get_project_path(project_name)
        contacts_path = project_path / "Case Information" / "contacts.json"
        project_contacts = read_json_file(contacts_path) or []
        
        for contact in project_contacts:
            if not isinstance(contact, dict):
                continue
            
            full_name = contact.get("full_name", "")
            if not full_name:
                first = contact.get("first_name", "")
                last = contact.get("last_name", "")
                full_name = f"{first} {last}".strip()
            
            if search_lower in full_name.lower():
                return normalize_contact(contact)
    
    return None


def normalize_contact(contact: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize contact data to a standard format for the UI."""
    # Build full name
    full_name = contact.get("full_name", "")
    if not full_name:
        first = contact.get("first_name", "")
        last = contact.get("last_name", "")
        full_name = f"{first} {last}".strip()
    
    # Build roles list
    roles = contact.get("roles", [])
    if isinstance(roles, str):
        roles = [roles]
    elif not roles:
        role = contact.get("role", "")
        if role:
            roles = [role]
    
    return {
        "name": full_name or "Unknown",
        "roles": roles,
        "company": contact.get("company") or contact.get("organization"),
        "email": contact.get("email"),
        "phone": contact.get("phone") or contact.get("phone_number"),
        "fax": contact.get("fax"),
        "address": contact.get("address"),
        "notes": contact.get("notes"),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate contact card UI data")
    parser.add_argument("--contact-name", required=True, help="Name to search for")
    parser.add_argument("--project-name", help="Optional: Project to search in")
    args = parser.parse_args()
    
    contact = find_contact(args.contact_name, args.project_name)
    
    if not contact:
        output_error(f"Contact not found: {args.contact_name}")
    
    output_result({
        "component": "ContactCard",
        "data": contact,
    })


if __name__ == "__main__":
    main()

