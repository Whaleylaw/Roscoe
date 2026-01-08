#!/usr/bin/env python3
"""
Create Appellate and Supreme Court district entities.

Kentucky has:
- 7 Supreme Court Districts (geographic regions)
- Court of Appeals has regional offices

Maps justices/judges to districts based on office location.
"""

import json
from pathlib import Path


# Kentucky Supreme Court Districts (7 total)
# Based on geographic regions - justices are elected from these
SUPREME_COURT_DISTRICTS = {
    "1": {"region": "Western KY", "counties": "Paducah area", "city": "Paducah"},
    "2": {"region": "North Central KY", "counties": "Louisville/Jefferson", "city": "Louisville"},
    "3": {"region": "Northern KY", "counties": "Kenton/Campbell/Boone", "city": "Covington"},
    "4": {"region": "Bluegrass", "counties": "Fayette/Lexington", "city": "Lexington"},
    "5": {"region": "Eastern KY", "counties": "Boyd/Greenup area", "city": "Catlettsburg"},
    "6": {"region": "South Central KY", "counties": "Bowling Green area", "city": "Bowling Green"},
    "7": {"region": "Capital", "counties": "Franklin/Frankfort", "city": "Frankfort"}
}

# Court of Appeals Regional Offices
APPELLATE_DISTRICTS = {
    "Lexington": {"region": "Central KY", "counties": "Lexington area"},
    "Louisville": {"region": "Louisville Metro", "counties": "Jefferson"},
    "Covington": {"region": "Northern KY", "counties": "Kenton/Campbell"},
    "Frankfort": {"region": "Capital", "counties": "Franklin"},
    "Paducah": {"region": "Western KY", "counties": "McCracken"}
}


def map_justice_to_district(address: str) -> str:
    """Map Supreme Court justice to district based on office location."""
    address_lower = address.lower()

    if "paducah" in address_lower:
        return "1"
    elif "louisville" in address_lower or "jefferson" in address_lower:
        return "2"
    elif "covington" in address_lower or "kenton" in address_lower:
        return "3"
    elif "lexington" in address_lower or "fayette" in address_lower:
        return "4"
    elif "catlettsburg" in address_lower or "boyd" in address_lower:
        return "5"
    elif "bowling green" in address_lower or "warren" in address_lower:
        return "6"
    elif "frankfort" in address_lower or "capital" in address_lower:
        return "7"

    return "7"  # Default to Capital district


def map_appellate_judge_to_office(address: str) -> str:
    """Map Court of Appeals judge to regional office."""
    address_lower = address.lower()

    if "lexington" in address_lower or "fayette" in address_lower:
        return "Lexington"
    elif "louisville" in address_lower or "jefferson" in address_lower:
        return "Louisville"
    elif "covington" in address_lower or "newport" in address_lower or "campbell" in address_lower:
        return "Covington"
    elif "paducah" in address_lower:
        return "Paducah"
    else:
        return "Frankfort"  # Default


def main():
    entities_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities")

    print("=" * 80)
    print("CREATING APPELLATE & SUPREME COURT DISTRICTS")
    print("=" * 80)
    print()

    # Create Supreme Court Districts
    supreme_districts = []
    supreme_mappings = {}

    for district_num, info in SUPREME_COURT_DISTRICTS.items():
        district_name = f"Kentucky Supreme Court, District {district_num}"
        supreme_districts.append({
            "card_type": "entity",
            "entity_type": "SupremeCourtDistrict",
            "name": district_name,
            "attributes": {
                "district_number": district_num,
                "region": info["region"],
                "counties": info["counties"]
            },
            "source_id": "ky_supreme_court_structure",
            "source_file": "supreme_court_justices.json"
        })
        supreme_mappings[district_name] = []

    # Map justices to districts
    with open(entities_dir / "supreme_court_justices.json") as f:
        justices = json.load(f)

    print(f"Processing {len(justices)} Supreme Court justices...")
    for justice in justices:
        address = justice['attributes'].get('address', '')
        district_num = map_justice_to_district(address)
        district_name = f"Kentucky Supreme Court, District {district_num}"

        if district_name in supreme_mappings:
            supreme_mappings[district_name].append(justice['name'])

    # Create Court of Appeals Districts
    appellate_districts = []
    appellate_mappings = {}

    for office, info in APPELLATE_DISTRICTS.items():
        district_name = f"Kentucky Court of Appeals, {office} Office"
        appellate_districts.append({
            "card_type": "entity",
            "entity_type": "AppellateDistrict",
            "name": district_name,
            "attributes": {
                "district_number": office,
                "region": info["region"],
                "counties": info["counties"]
            },
            "source_id": "ky_appeals_court_structure",
            "source_file": "appellate_judges.json"
        })
        appellate_mappings[district_name] = []

    # Map appellate judges to offices
    with open(entities_dir / "appellate_judges.json") as f:
        app_judges = json.load(f)

    print(f"Processing {len(app_judges)} Court of Appeals judges...")
    for judge in app_judges:
        address = judge['attributes'].get('address', '')
        office = map_appellate_judge_to_office(address)
        district_name = f"Kentucky Court of Appeals, {office} Office"

        if district_name in appellate_mappings:
            appellate_mappings[district_name].append(judge['name'])

    # Save
    with open(entities_dir / "supreme_court_districts.json", 'w') as f:
        json.dump(supreme_districts, f, indent=2)

    with open(entities_dir / "appellate_districts.json", 'w') as f:
        json.dump(appellate_districts, f, indent=2)

    # Update mappings file
    with open(entities_dir / "judge_division_mappings.json") as f:
        mappings = json.load(f)

    mappings["supreme_court_justices"] = supreme_mappings
    mappings["appellate_judges"] = appellate_mappings

    with open(entities_dir / "judge_division_mappings.json", 'w') as f:
        json.dump(mappings, f, indent=2)

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Supreme Court Districts created: {len(supreme_districts)}")
    print(f"Court of Appeals Offices created: {len(appellate_districts)}")
    print()

    print("Kentucky Supreme Court Districts:")
    for district_name, justices in sorted(supreme_mappings.items()):
        print(f"  {district_name}: {', '.join(justices) if justices else 'No justice mapped'}")

    print()
    print("Court of Appeals Offices:")
    for office_name, judges in sorted(appellate_mappings.items()):
        print(f"  {office_name}: {len(judges)} judges")

    print()
    print("✅ Created:")
    print(f"   - supreme_court_districts.json (7 districts)")
    print(f"   - appellate_districts.json (5 regional offices)")
    print(f"   - Updated judge_division_mappings.json")


if __name__ == "__main__":
    main()
