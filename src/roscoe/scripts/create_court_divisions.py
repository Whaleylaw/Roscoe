#!/usr/bin/env python3
"""
Create Division entities from judge data.

Extracts divisions from circuit_judges.json, district_judges.json, etc.
Creates Division entities and links judges via PRESIDES_OVER.
"""

import json
import re
from pathlib import Path
from collections import defaultdict


def parse_circuit_division(area_str: str, county: str) -> tuple[str, str, str]:
    """
    Parse circuit division from Area field.

    Example: "Cir. 30, Div. 02" → ("30", "02", "Jefferson County Circuit Court, Division II")

    Returns: (circuit_num, division_num, division_name)
    """
    if not area_str:
        return None, None, None

    # Parse "Cir. 30, Div. 02" or "Cir. 18, Div. 01"
    cir_match = re.search(r'Cir\.\s*(\d+)', area_str)
    div_match = re.search(r'Div\.\s*(\d+)', area_str)

    if not cir_match or not div_match:
        return None, None, None

    circuit_num = cir_match.group(1)
    division_num = div_match.group(1)

    # Extract primary county
    primary_county = county.split('&')[0].split(',')[0].strip()

    # Convert division number to Roman numerals for name
    div_int = int(division_num)
    roman_map = {
        1: "I", 2: "II", 3: "III", 4: "IV", 5: "V",
        6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X",
        11: "XI", 12: "XII", 13: "XIII", 14: "XIV", 15: "XV", 16: "XVI"
    }
    roman = roman_map.get(div_int, division_num)

    division_name = f"{primary_county} County Circuit Court, Division {roman}"

    return circuit_num, division_num, division_name


def parse_district_division(area_str: str, county: str) -> tuple[str, str, str]:
    """
    Parse district division from Area field.

    Example: "Dist. 30, Div. 01" → ("30", "01", "Jefferson County District Court, Division 1")
    """
    if not area_str:
        return None, None, None

    dist_match = re.search(r'Dist\.\s*(\d+)', area_str)
    div_match = re.search(r'Div\.\s*(\d+)', area_str)

    if not dist_match:
        return None, None, None

    district_num = dist_match.group(1)
    division_num = div_match.group(1) if div_match else None

    primary_county = county.split('&')[0].split(',')[0].strip()

    if division_num:
        division_name = f"{primary_county} County District Court, Division {division_num}"
    else:
        division_name = f"{primary_county} County District Court"

    return district_num, division_num, division_name


def create_divisions_from_judges():
    """Extract division entities from judge data."""
    entities_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities")

    # Track divisions and their judges
    circuit_divisions = {}  # division_name -> {division_entity, judges: []}
    district_divisions = {}

    # Process Circuit Judges
    with open(entities_dir / "circuit_judges.json") as f:
        circuit_judges = json.load(f)

    print(f"Processing {len(circuit_judges)} circuit judges...")
    for judge in circuit_judges:
        circuit_num, division_num, division_name = parse_circuit_division(
            judge['attributes'].get('circuit', ''),
            judge['attributes'].get('county', '')
        )

        if division_name:
            if division_name not in circuit_divisions:
                # Create division entity
                primary_county = division_name.split(' County')[0]
                circuit_divisions[division_name] = {
                    "entity": {
                        "card_type": "entity",
                        "entity_type": "CircuitDivision",
                        "name": division_name,
                        "attributes": {
                            "division_number": division_num,
                            "circuit_number": circuit_num,
                            "court_name": f"{primary_county} County Circuit Court",
                            "local_rules": "",
                            "scheduling_preferences": "",
                            "mediation_required": None
                        },
                        "source_id": "extracted_from_judges",
                        "source_file": "circuit_judges.json"
                    },
                    "judges": []
                }

            circuit_divisions[division_name]["judges"].append(judge['name'])

    # Process District Judges
    with open(entities_dir / "district_judges.json") as f:
        district_judges = json.load(f)

    print(f"Processing {len(district_judges)} district judges...")
    for judge in district_judges:
        district_num, division_num, division_name = parse_district_division(
            judge['attributes'].get('district', ''),
            judge['attributes'].get('county', '')
        )

        if division_name:
            if division_name not in district_divisions:
                primary_county = division_name.split(' County')[0]
                district_divisions[division_name] = {
                    "entity": {
                        "card_type": "entity",
                        "entity_type": "DistrictDivision",
                        "name": division_name,
                        "attributes": {
                            "division_number": division_num,
                            "district_number": district_num,
                            "court_name": f"{primary_county} County District Court"
                        },
                        "source_id": "extracted_from_judges",
                        "source_file": "district_judges.json"
                    },
                    "judges": []
                }

            district_divisions[division_name]["judges"].append(judge['name'])

    # Save division entities
    circuit_div_entities = [v["entity"] for v in circuit_divisions.values()]
    district_div_entities = [v["entity"] for v in district_divisions.values()]

    with open(entities_dir / "circuit_divisions.json", 'w') as f:
        json.dump(circuit_div_entities, f, indent=2)

    with open(entities_dir / "district_divisions.json", 'w') as f:
        json.dump(district_div_entities, f, indent=2)

    # Save judge-division mappings for relationship creation
    judge_mappings = {
        "circuit_judges": {div_name: data["judges"] for div_name, data in circuit_divisions.items()},
        "district_judges": {div_name: data["judges"] for div_name, data in district_divisions.items()}
    }

    with open(entities_dir / "judge_division_mappings.json", 'w') as f:
        json.dump(judge_mappings, f, indent=2)

    return circuit_div_entities, district_div_entities, judge_mappings


def main():
    print("=" * 80)
    print("CREATING COURT DIVISION ENTITIES")
    print("=" * 80)
    print()

    circuit_divs, district_divs, mappings = create_divisions_from_judges()

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Circuit Divisions created: {len(circuit_divs)}")
    print(f"District Divisions created: {len(district_divs)}")
    print()

    # Show Jefferson as example
    jeff_circuit = [d for d in circuit_divs if "Jefferson" in d["name"]]
    jeff_district = [d for d in district_divs if "Jefferson" in d["name"]]

    print("Jefferson County Circuit Court Divisions:")
    for div in sorted(jeff_circuit, key=lambda x: x["attributes"]["division_number"]):
        judges = mappings["circuit_judges"][div["name"]]
        print(f"  {div['name']}: {judges[0] if judges else 'No judge'}")

    print()
    print("Jefferson County District Court Divisions:")
    for div in sorted(jeff_district, key=lambda x: x["attributes"]["division_number"]):
        judges = mappings["district_judges"][div["name"]]
        print(f"  {div['name']}: {judges[0] if judges else 'No judge'}")

    print()
    print("✅ Division entities created:")
    print(f"   - circuit_divisions.json ({len(circuit_divs)} divisions)")
    print(f"   - district_divisions.json ({len(district_divs)} divisions)")
    print(f"   - judge_division_mappings.json (for creating PRESIDES_OVER relationships)")


if __name__ == "__main__":
    main()
