#!/usr/bin/env python3
"""
Convert location-based medical providers to facility-based structure.

OLD Structure:
- Separate node for each location
- Example: "UofL Health - Frazier Rehab - Downtown", "UofL Health - Frazier Rehab - Brownsboro"

NEW Structure:
- One node per main facility/program
- Locations stored as array property
- Example: ONE node "UofL Health – Frazier Rehabilitation Institute – Kleinert Kutz Hand Therapy"
  with locations property: [{location: "Downtown", ...}, {location: "Brownsboro", ...}]

This significantly consolidates the number of nodes while preserving all location detail.
"""

import json
from pathlib import Path
from collections import defaultdict
import re


def extract_main_facility(provider_name: str) -> tuple:
    """
    Extract main facility name from full provider name.

    Examples:
    - "UofL Health - Frazier Rehab - Downtown" → ("UofL Health - Frazier Rehab", "Downtown")
    - "UofL Physicians - Cardiology - Brownsboro" → ("UofL Physicians - Cardiology", "Brownsboro")
    - "Jewish Hospital" → ("Jewish Hospital", None)

    Returns: (main_facility, location)
    """

    # Split by " - "
    parts = provider_name.split(' - ')

    if len(parts) == 1:
        # No dashes - this is the main facility itself
        return (provider_name, None)

    # Check if last part is a location (geographic indicator)
    location_indicators = [
        'downtown', 'brownsboro', 'audubon', 'st. matthews', 'st matthews',
        'elizabethtown', 'shelbyville', 'frankfort', 'lexington', 'paducah',
        'owensboro', 'bowling green', 'louisville', 'west louisville',
        'jeffersonville', 'clarksville', 'madison', 'clark', 'corydon',
        'newburg', 'nulu', 'novak center', 'bluegrass', 'dixie', 'fern creek',
        'highlands', 'iroquois', 'lyndon', 'middletown', 'preston', 'springhurst',
        'taylorsville', 'crestwood', 'la grange', 'lagrange', 'bullitt county',
        'bardstown', 'campbellsville', 'scottsburg', 'sellersburg', 'anchorage',
        'at jewish hospital', 'at mary & elizabeth'
    ]

    last_part_lower = parts[-1].lower()

    # Check if last part is a location
    is_location = any(indicator in last_part_lower for indicator in location_indicators)

    if is_location:
        # Last part is location, everything before is main facility
        main_facility = ' - '.join(parts[:-1])
        location = parts[-1]
        return (main_facility, location)
    else:
        # Last part is not a location (it's part of the facility name)
        return (provider_name, None)


def convert_to_facility_structure(locations: list) -> list:
    """Convert location-based list to facility-based structure."""

    # Group by main facility
    by_facility = defaultdict(list)

    for loc in locations:
        name = loc.get('name', '')
        main_facility, location_name = extract_main_facility(name)

        by_facility[main_facility].append({
            'location_name': location_name,
            'address': loc.get('address', ''),
            'phone': loc.get('phone', ''),
            'full_name': name,
            'original_data': loc
        })

    # Convert to new structure
    facilities = []

    for facility_name, facility_locations in by_facility.items():
        # Build locations array
        locations_array = []

        for loc_data in facility_locations:
            location_entry = {
                'location': loc_data['location_name'] or 'Main',
                'address': loc_data['address'],
                'phone': loc_data['phone']
            }

            # Add any other attributes from original
            orig = loc_data['original_data']
            if orig.get('npi'):
                location_entry['npi'] = orig['npi']
            if orig.get('specialty'):
                location_entry['specialty'] = orig['specialty']

            locations_array.append(location_entry)

        # Create facility entity
        facility = {
            'card_type': 'entity',
            'entity_type': 'MedicalProvider',
            'name': facility_name,
            'attributes': {
                'parent_system': facility_locations[0]['original_data'].get('attributes', {}).get('parent_system', ''),
                'location_count': len(locations_array),
                'locations': locations_array  # Array of location objects
            },
            'source_id': f"facility_{len(facilities)}",
            'source_file': facility_locations[0]['original_data'].get('source_file', '')
        }

        facilities.append(facility)

    return facilities


def main():
    """Convert all health system rosters to facility-based structure."""

    systems = [
        ('UofL Health', '/Volumes/X10 Pro/Roscoe/json-files/uofl_health_locations.json'),
        ('Baptist Health', '/Volumes/X10 Pro/Roscoe/json-files/baptist_health_locations.json'),
        ('Norton Healthcare', '/Volumes/X10 Pro/Roscoe/json-files/norton_healthcare_locations.json'),
        ('CHI Saint Joseph Health', '/Volumes/X10 Pro/Roscoe/json-files/chi_saint_joseph_locations.json'),
        ('St. Elizabeth Healthcare', '/Volumes/X10 Pro/Roscoe/json-files/stelizabeth_locations.json'),
        ('Norton Children\'s Hospital', '/Volumes/X10 Pro/Roscoe/json-files/norton_childrens_locations_SCRAPED.json'),
    ]

    output_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/facility-based")
    output_dir.mkdir(exist_ok=True)

    print("="*70)
    print("CONVERTING TO FACILITY-BASED STRUCTURE")
    print("="*70)
    print()

    summary = []

    for system_name, input_file in systems:
        input_path = Path(input_file)

        if not input_path.exists():
            print(f"⚠️  {system_name}: File not found")
            continue

        print(f"Processing {system_name}...")

        with open(input_path, 'r', encoding='utf-8') as f:
            locations = json.load(f)

        print(f"  Input: {len(locations)} location-based providers")

        # Convert to facility-based
        facilities = convert_to_facility_structure(locations)

        print(f"  Output: {len(facilities)} facility-based providers")
        print(f"  Reduction: {len(locations) - len(facilities)} nodes saved")

        # Save to output file
        output_filename = system_name.lower().replace(' ', '_').replace("'", '') + '_facilities.json'
        output_file = output_dir / output_filename

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(facilities, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved to: {output_file.name}")
        print()

        summary.append({
            'system': system_name,
            'locations_before': len(locations),
            'facilities_after': len(facilities),
            'reduction': len(locations) - len(facilities),
            'file': output_file.name
        })

    # Print summary
    print("="*70)
    print("CONVERSION COMPLETE")
    print("="*70)
    print()

    total_before = sum(s['locations_before'] for s in summary)
    total_after = sum(s['facilities_after'] for s in summary)
    total_reduction = total_before - total_after

    print(f"Total locations (old structure): {total_before}")
    print(f"Total facilities (new structure): {total_after}")
    print(f"Node reduction: {total_reduction} ({total_reduction/total_before*100:.1f}%)")
    print()

    print("Summary by system:")
    for s in summary:
        print(f"  {s['system']}: {s['locations_before']} → {s['facilities_after']} (-{s['reduction']})")

    print(f"\n✅ Converted all 6 health systems to facility-based structure")
    print(f"\nOutput directory: {output_dir}")


if __name__ == "__main__":
    main()
