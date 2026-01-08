#!/usr/bin/env python3
"""
Parse hierarchical outline files to extract Facility → Location structure.

Uses existing outline files:
- norton_healthcare_outline.md
- uofl_health_outline.md
- baptist_health_outline.md
- chi_saint_joseph_health_outline.md
- st._elizabeth_healthcare_outline.md

Extracts:
- Facility names (Roman numerals / #N)
- Location names (numbered items under letters)
- Addresses and phones for each location
"""

import re
import json
from pathlib import Path
from collections import defaultdict


def parse_outline_file(outline_file: Path, system_name: str) -> dict:
    """Parse one outline file to extract facilities and locations."""

    with open(outline_file, 'r', encoding='utf-8') as f:
        content = f.read()

    facilities = []
    current_facility = None
    current_locations = []

    lines = content.split('\n')

    for i, line in enumerate(lines):
        # Check for facility line (Roman numeral or #N format)
        # Pattern: I. **Facility Name** (N locations)
        # or: #N. **Facility Name** (N locations)
        facility_match = re.match(r'^(?:I+|#\d+)\.\s+\*\*(.+?)\*\*\s+\((\d+)\s+location', line)

        if facility_match:
            # Save previous facility if exists
            if current_facility:
                facilities.append({
                    'name': current_facility,
                    'parent_system': system_name,
                    'locations': current_locations
                })

            # Start new facility
            current_facility = facility_match.group(1).strip()
            location_count = int(facility_match.group(2))
            current_locations = []
            continue

        # Check for location line
        # Pattern 1: 1. Location Name (numbered item - Norton style)
        # Pattern 2: A. **Location Name** (letter heading - UofL style)
        location_numbered = re.match(r'^\s+\d+\.\s+(.+)$', line)
        location_lettered = re.match(r'^\s+[A-Z]+\.\s+\*\*(.+?)\*\*\s*$', line)

        if (location_numbered or location_lettered) and current_facility:
            if location_numbered:
                location_name = location_numbered.group(1).strip()
            else:
                location_name = location_lettered.group(1).strip()

            # Get address and phone from next lines
            address = None
            phone = None

            # Look ahead for address (starts with - )
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('- '):
                address = lines[i + 1].strip()[2:].strip()

            # Look ahead for phone
            if i + 2 < len(lines) and lines[i + 2].strip().startswith('- '):
                phone = lines[i + 2].strip()[2:].strip()

            current_locations.append({
                'name': location_name,
                'address': address,
                'phone': phone
            })

    # Save last facility
    if current_facility:
        facilities.append({
            'name': current_facility,
            'parent_system': system_name,
            'locations': current_locations
        })

    return {
        'system': system_name,
        'facilities': facilities,
        'total_facilities': len(facilities),
        'total_locations': sum(len(f['locations']) for f in facilities)
    }


def main():
    """Parse all hierarchical outline files."""

    outline_dir = Path("/Volumes/X10 Pro/Roscoe/provider-hierarchies")

    outline_files = [
        ("Norton Healthcare", outline_dir / "norton_healthcare_outline.md"),
        ("UofL Health", outline_dir / "uofl_health_outline.md"),
        ("Baptist Health", outline_dir / "baptist_health_outline.md"),
        ("CHI Saint Joseph Health", outline_dir / "chi_saint_joseph_health_outline.md"),
        ("St. Elizabeth Healthcare", outline_dir / "st._elizabeth_healthcare_outline.md"),
    ]

    print("="*70)
    print("PARSING HIERARCHICAL OUTLINE FILES")
    print("="*70)
    print()

    all_systems = []
    total_facilities = 0
    total_locations = 0

    for system_name, outline_file in outline_files:
        if not outline_file.exists():
            print(f"⚠️  {system_name}: Outline not found")
            continue

        print(f"Parsing {system_name}...")
        result = parse_outline_file(outline_file, system_name)

        print(f"  Facilities: {result['total_facilities']}")
        print(f"  Locations: {result['total_locations']}")

        all_systems.append(result)
        total_facilities += result['total_facilities']
        total_locations += result['total_locations']

        print()

    print("="*70)
    print("PARSING COMPLETE")
    print("="*70)
    print(f"\nTotal facilities across all systems: {total_facilities}")
    print(f"Total locations across all systems: {total_locations}")

    # Save parsed data
    output_file = Path("/Volumes/X10 Pro/Roscoe/parsed_hierarchy.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_systems, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved to: {output_file}")

    # Show sample
    print(f"\nSample - Norton Orthopedic Institute:")
    for system in all_systems:
        if system['system'] == 'Norton Healthcare':
            for facility in system['facilities']:
                if 'Orthopedic Institute' in facility['name'] and facility['name'] == 'Norton Orthopedic Institute':
                    print(f"  Facility: {facility['name']}")
                    print(f"  Locations: {len(facility['locations'])}")
                    for loc in facility['locations'][:3]:
                        print(f"    - {loc['name']}")
                        print(f"      {loc['address']}")
                    if len(facility['locations']) > 3:
                        print(f"    ... and {len(facility['locations']) - 3} more")
                    break
            break

    print(f"\n✅ Hierarchical parsing complete!")


if __name__ == "__main__":
    main()
