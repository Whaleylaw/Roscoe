#!/usr/bin/env python3
"""
Import Kentucky Court Personnel from directory JSON.

Creates entity cards for:
- Circuit Judges
- District Judges
- Court of Appeals Judges
- Supreme Court Justices
- Circuit Clerks
- Master Commissioners
- Court Administrators
- Pretrial Services (Organizations)
- Drug Courts (Organizations)
"""

import json
from pathlib import Path
import re


CATEGORY_TO_ENTITY_TYPE = {
    "Circuit Judges": "CircuitJudge",
    "District Judges": "DistrictJudge",
    "Court of Appeals Judges": "AppellateJudge",
    "Supreme Court Justices": "SupremeCourtJustice",
    "Circuit Clerks": "CourtClerk",
    "Master Commissioners": "MasterCommissioner",
    "Court Administrators": "CourtAdministrator",
    # Locations/offices -> Organizations
    "Pretrial Services Locations": "Organization",
    "Drug Court Locations": "Organization",
    "Court Designated Worker Program Locations": "Organization",
}


def parse_phone(phone_str: str) -> dict:
    """Extract phone and fax from phone string."""
    if not phone_str:
        return {"phone": "", "fax": ""}

    lines = phone_str.strip().split('\n')
    phone = ""
    fax = ""

    for line in lines:
        if '(Phone)' in line:
            phone = re.sub(r'\s*\(Phone\)\s*', '', line).strip()
        elif '(Fax)' in line:
            fax = re.sub(r'\s*\(Fax\)\s*', '', line).strip()

    return {"phone": phone, "fax": fax}


def convert_to_entity_card(entry: dict) -> dict:
    """Convert directory entry to entity card."""
    category = entry.get("Category")
    entity_type = CATEGORY_TO_ENTITY_TYPE.get(category)

    if not entity_type:
        return None

    # Skip "Vacant" entries
    if entry.get("Name") == "Vacant":
        return None

    phone_data = parse_phone(entry.get("Phone_Number", ""))

    # Build attributes based on entity type
    attributes = {
        "phone": phone_data["phone"],
        "fax": phone_data["fax"],
        "address": entry.get("Address", "").strip()
    }

    # Add type-specific attributes
    if entity_type in ["CircuitJudge", "DistrictJudge"]:
        attributes["county"] = entry.get("County", "")
        if entity_type == "CircuitJudge":
            attributes["circuit"] = entry.get("Area", "")
        else:
            attributes["district"] = entry.get("Area", "")

    elif entity_type == "CourtClerk":
        attributes["clerk_type"] = "circuit" if category == "Circuit Clerks" else "district"
        attributes["county"] = entry.get("County", "")

    elif entity_type == "MasterCommissioner":
        attributes["county"] = entry.get("County", "")

    elif entity_type == "CourtAdministrator":
        attributes["role"] = "court_administrator"

    elif entity_type == "Organization":
        # For pretrial services, drug courts, etc.
        attributes["organization_type"] = category.replace(" Locations", "").lower().replace(" ", "_")
        attributes["email"] = ""

    return {
        "card_type": "entity",
        "entity_type": entity_type,
        "name": entry.get("Name", "").strip(),
        "attributes": attributes,
        "source_id": "ky_court_directory",
        "source_file": "ky_court_directory_20251228_132858.json"
    }


def main():
    input_file = Path("/Volumes/X10 Pro/Roscoe/scripts/output/ky_court_directory_20251228_132858.json")
    output_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities")

    print("=" * 80)
    print("IMPORTING KENTUCKY COURT PERSONNEL")
    print("=" * 80)
    print()

    with open(input_file) as f:
        entries = json.load(f)

    print(f"Total entries in directory: {len(entries)}")
    print()

    # Group by entity type
    by_type = {
        "CircuitJudge": [],
        "DistrictJudge": [],
        "AppellateJudge": [],
        "SupremeCourtJustice": [],
        "CourtClerk": [],
        "MasterCommissioner": [],
        "CourtAdministrator": [],
        "Organization": []  # Pretrial, Drug Courts, etc.
    }

    skipped = 0

    for entry in entries:
        card = convert_to_entity_card(entry)
        if card:
            entity_type = card["entity_type"]
            by_type[entity_type].append(card)
        else:
            skipped += 1

    print("Entity counts:")
    for entity_type, cards in sorted(by_type.items()):
        if cards:
            print(f"  {entity_type}: {len(cards)}")

    print(f"\nSkipped (vacant or unknown): {skipped}")
    print()

    # Save to files
    for entity_type, cards in by_type.items():
        if not cards:
            continue

        # Convert entity type to filename (camelCase -> snake_case)
        filename = re.sub(r'(?<!^)(?=[A-Z])', '_', entity_type).lower() + "s.json"
        output_file = output_dir / filename

        # Load existing if present
        existing = []
        if output_file.exists():
            with open(output_file) as f:
                existing = json.load(f)

        # Merge (avoid duplicates by name)
        existing_names = {e["name"] for e in existing}
        new_cards = [c for c in cards if c["name"] not in existing_names]

        merged = existing + new_cards

        with open(output_file, 'w') as f:
            json.dump(merged, f, indent=2)

        print(f"✓ {filename}: Added {len(new_cards)}, Total {len(merged)}")

    print()
    print("✅ Import complete!")


if __name__ == "__main__":
    main()
