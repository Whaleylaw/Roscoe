#!/usr/bin/env python3
"""
Extract Court entities from KY court directory.

Creates comprehensive Court entities from judge/clerk data,
including division information.
"""

import json
import re
from pathlib import Path
from collections import defaultdict


def extract_courts_from_directory(directory_file: Path) -> list[dict]:
    """
    Extract Court entities from directory.

    Strategy:
    - Use Circuit Judges to identify Circuit Courts with divisions
    - Use District Judges to identify District Courts
    - Derive court name from county + type
    """
    with open(directory_file) as f:
        entries = json.load(f)

    courts = {}  # court_key -> court_entity

    # Process Circuit Judges
    for entry in entries:
        if entry.get("Category") == "Circuit Judges" and entry.get("Name") != "Vacant":
            county = entry.get("County", "")
            area = entry.get("Area", "")  # e.g., "Cir. 30, Div. 07"
            address = entry.get("Address", "")

            if not county:
                continue

            # Extract primary county (first one in multi-county areas)
            primary_county = county.split("&")[0].split(",")[0].strip()

            # Create court key
            court_key = f"{primary_county} County Circuit Court"

            # Extract division info
            division = None
            circuit_num = None
            if area:
                # Parse "Cir. 30, Div. 07" or "Cir. 43, Div. 01"
                cir_match = re.search(r'Cir\.\s*(\d+)', area)
                div_match = re.search(r'Div\.\s*(\d+)', area)
                if cir_match:
                    circuit_num = cir_match.group(1)
                if div_match:
                    division = div_match.group(1)

            # Initialize or update court
            if court_key not in courts:
                courts[court_key] = {
                    "card_type": "entity",
                    "entity_type": "Court",
                    "name": court_key,
                    "attributes": {
                        "county": primary_county,
                        "state": "Kentucky",
                        "division": "Circuit",
                        "circuit_number": circuit_num,
                        "divisions": [],
                        "phone": "",
                        "email": "",
                        "address": ""
                    },
                    "source_id": "ky_court_directory",
                    "source_file": "ky_court_directory_20251228_132858.json"
                }

            # Add division if not already present
            if division and division not in courts[court_key]["attributes"]["divisions"]:
                courts[court_key]["attributes"]["divisions"].append(division)

            # Update address if more specific
            if address and "700 W. Jefferson" in address and not courts[court_key]["attributes"]["address"]:
                # Extract just the address line
                addr_lines = address.split('\n')
                if len(addr_lines) >= 2:
                    courts[court_key]["attributes"]["address"] = '\n'.join(addr_lines[1:])

    # Process District Judges
    for entry in entries:
        if entry.get("Category") == "District Judges" and entry.get("Name") != "Vacant":
            county = entry.get("County", "")
            area = entry.get("Area", "")  # e.g., "Dist. 18, Div. 01"
            address = entry.get("Address", "")

            if not county:
                continue

            # Extract primary county
            primary_county = county.split("&")[0].split(",")[0].strip()

            court_key = f"{primary_county} County District Court"

            # Extract district info
            division = None
            district_num = None
            if area:
                dist_match = re.search(r'Dist\.\s*(\d+)', area)
                div_match = re.search(r'Div\.\s*(\d+)', area)
                if dist_match:
                    district_num = dist_match.group(1)
                if div_match:
                    division = div_match.group(1)

            if court_key not in courts:
                courts[court_key] = {
                    "card_type": "entity",
                    "entity_type": "Court",
                    "name": court_key,
                    "attributes": {
                        "county": primary_county,
                        "state": "Kentucky",
                        "division": "District",
                        "district_number": district_num,
                        "divisions": [],
                        "phone": "",
                        "email": "",
                        "address": ""
                    },
                    "source_id": "ky_court_directory",
                    "source_file": "ky_court_directory_20251228_132858.json"
                }

            if division and division not in courts[court_key]["attributes"]["divisions"]:
                courts[court_key]["attributes"]["divisions"].append(division)

            if address and not courts[court_key]["attributes"]["address"]:
                addr_lines = address.split('\n')
                if len(addr_lines) >= 2:
                    courts[court_key]["attributes"]["address"] = '\n'.join(addr_lines[1:])

    # Sort divisions numerically
    for court in courts.values():
        if court["attributes"]["divisions"]:
            court["attributes"]["divisions"] = sorted(court["attributes"]["divisions"], key=lambda x: int(x))

    # Add statewide courts
    courts["Kentucky Court of Appeals"] = {
        "card_type": "entity",
        "entity_type": "Court",
        "name": "Kentucky Court of Appeals",
        "attributes": {
            "county": "Statewide",
            "state": "Kentucky",
            "division": "Appellate",
            "phone": "",
            "email": "",
            "address": "260 Democrat Drive, Frankfort, KY 40601"
        },
        "source_id": "ky_court_directory",
        "source_file": "ky_court_directory_20251228_132858.json"
    }

    courts["Kentucky Supreme Court"] = {
        "card_type": "entity",
        "entity_type": "Court",
        "name": "Kentucky Supreme Court",
        "attributes": {
            "county": "Statewide",
            "state": "Kentucky",
            "division": "Supreme",
            "phone": "",
            "email": "",
            "address": "700 Capitol Avenue, Frankfort, KY 40601"
        },
        "source_id": "ky_court_directory",
        "source_file": "ky_court_directory_20251228_132858.json"
    }

    return list(courts.values())


def main():
    directory_file = Path("/Volumes/X10 Pro/Roscoe/scripts/output/ky_court_directory_20251228_132858.json")
    output_file = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/courts.json")

    print("=" * 80)
    print("EXTRACTING COURTS FROM KY COURT DIRECTORY")
    print("=" * 80)
    print()

    courts = extract_courts_from_directory(directory_file)

    print(f"Extracted {len(courts)} courts")
    print()

    # Show Jefferson as example
    jeff_courts = [c for c in courts if "Jefferson" in c["name"]]
    for court in jeff_courts:
        divs = court["attributes"].get("divisions", [])
        print(f"{court['name']}")
        print(f"  Divisions: {len(divs)} - {divs if divs else 'N/A'}")
        print()

    # Save (REPLACE existing)
    with open(output_file, 'w') as f:
        json.dump(courts, f, indent=2)

    print(f"✅ Replaced {output_file}")
    print(f"   Total courts: {len(courts)}")


if __name__ == "__main__":
    main()
