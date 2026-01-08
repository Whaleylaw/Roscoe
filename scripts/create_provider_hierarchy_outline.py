#!/usr/bin/env python3
"""
Create hierarchical outline of Norton Healthcare locations.

Parses provider names to extract structure:
- Main Facility (e.g., "Norton Hospital", "Norton Surgical Specialists")
- Specialty/Department (e.g., "Emergency", "ENT & Audiology")
- Location (e.g., "Downtown", "Madison", "Brownsboro")

Output: Outline showing hierarchical organization
"""

import json
from pathlib import Path
from collections import defaultdict
import re


def parse_provider_hierarchy(provider_name: str) -> dict:
    """
    Parse provider name into hierarchical components.

    Examples:
    - "Norton Hospital - Emergency" → {main: "Norton Hospital", dept: "Emergency", location: None}
    - "Norton Surgical Specialists - ENT & Audiology - Madison" → {main: "Norton Surgical Specialists", dept: "ENT & Audiology", location: "Madison"}
    - "Norton Audubon Hospital" → {main: "Norton Audubon Hospital", dept: None, location: None}
    """

    # Split by " - " delimiter
    parts = [p.strip() for p in provider_name.split(' - ')]

    hierarchy = {
        'main': parts[0] if len(parts) >= 1 else provider_name,
        'dept': parts[1] if len(parts) >= 2 else None,
        'location': parts[2] if len(parts) >= 3 else None,
        'full_name': provider_name
    }

    # If only 2 parts, need to determine if part 2 is department or location
    # Heuristic: If part 2 is a city/area name (contains geographic indicators), it's a location
    if len(parts) == 2 and hierarchy['dept']:
        dept_lower = hierarchy['dept'].lower()
        location_indicators = ['downtown', 'brownsboro', 'audubon', 'madison', 'clark',
                               'shelbyville', 'elizabethtown', 'jeffersonville', 'louisville',
                               'st. matthews', 'st matthews', 'crestwood', 'la grange']

        if any(indicator in dept_lower for indicator in location_indicators):
            # It's actually a location, not a department
            hierarchy['location'] = hierarchy['dept']
            hierarchy['dept'] = None

    return hierarchy


def extract_main_facility(provider_name: str) -> str:
    """Extract the main facility name (before first dash)."""
    if ' - ' in provider_name:
        return provider_name.split(' - ')[0].strip()
    return provider_name


def build_hierarchy_tree(providers: list) -> dict:
    """Build hierarchical tree structure from provider list."""

    tree = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for provider in providers:
        name = provider.get('name', '')
        hierarchy = parse_provider_hierarchy(name)

        main = hierarchy['main']
        dept = hierarchy['dept'] or '_no_dept'
        location = hierarchy['location'] or '_no_location'

        tree[main][dept][location].append(provider)

    return tree


def create_outline_document(tree: dict, output_file: Path, system_name: str):
    """Generate outline document from hierarchy tree."""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {system_name} - Hierarchical Structure\n\n")
        f.write(f"**Total Main Facilities:** {len(tree)}\n")
        f.write(f"**Purpose:** Show organization structure for provider mapping\n\n")
        f.write("---\n\n")

        # Sort main facilities alphabetically
        for main_idx, main_facility in enumerate(sorted(tree.keys()), 1):
            departments = tree[main_facility]

            # Count total providers under this facility
            total_providers = sum(
                len(providers)
                for dept_dict in departments.values()
                for providers in dept_dict.values()
            )

            f.write(f"## {main_idx}. {main_facility}\n\n")
            f.write(f"**Total Locations:** {total_providers}\n\n")

            # Check if this facility has departments
            has_departments = len([k for k in departments.keys() if k != '_no_dept']) > 0

            if has_departments:
                # Organize by department
                for dept_name in sorted(departments.keys()):
                    if dept_name == '_no_dept':
                        # Locations without specific department
                        locations = departments[dept_name]
                        for location_name in sorted(locations.keys()):
                            if location_name == '_no_location':
                                continue  # Already shown at main level
                            providers = locations[location_name]
                            for provider in providers:
                                f.write(f"   - **{provider['name']}**\n")
                                if provider.get('address'):
                                    f.write(f"     - Address: {provider['address']}\n")
                    else:
                        # Department with locations
                        f.write(f"   ### {dept_name}\n\n")

                        locations = departments[dept_name]
                        for location_name in sorted(locations.keys()):
                            providers = locations[location_name]

                            if location_name == '_no_location':
                                # Department without specific location
                                for provider in providers:
                                    f.write(f"   - **{provider['name']}**\n")
                                    if provider.get('address'):
                                        f.write(f"     - {provider['address']}\n")
                            else:
                                # Department at specific location
                                f.write(f"   #### {location_name}\n\n")
                                for provider in providers:
                                    f.write(f"   - **{provider['name']}**\n")
                                    if provider.get('address'):
                                        f.write(f"     - {provider['address']}\n")
                                f.write("\n")

                        f.write("\n")
            else:
                # No departments, just locations
                locations = departments['_no_dept']
                for location_name in sorted(locations.keys()):
                    providers = locations[location_name]
                    for provider in providers:
                        if provider['name'] != main_facility:  # Don't repeat main name
                            f.write(f"   - **{provider['name']}**\n")
                            if provider.get('address'):
                                f.write(f"     - {provider['address']}\n")

            f.write("\n---\n\n")


def create_simple_outline(providers: list, output_file: Path, system_name: str):
    """Create simpler outline by main facility grouping."""

    # Group by main facility (first part before dash)
    by_facility = defaultdict(list)

    for provider in providers:
        name = provider.get('name', '')
        main_facility = extract_main_facility(name)
        by_facility[main_facility].append(provider)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {system_name} - Hierarchical Structure (Outline View)\n\n")
        f.write(f"**Total Main Facilities/Groups:** {len(by_facility)}\n")
        f.write(f"**Total Locations:** {len(providers)}\n\n")
        f.write("---\n\n")

        # Sort by facility name
        for roman_idx, main_facility in enumerate(sorted(by_facility.keys()), 1):
            facility_providers = by_facility[main_facility]

            # Convert to Roman numerals for top level
            roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
            roman_num = roman[roman_idx - 1] if roman_idx <= 10 else f"#{roman_idx}"

            f.write(f"{roman_num}. **{main_facility}** ({len(facility_providers)} locations)\n\n")

            # Group subloca tions by department/specialty (middle part)
            by_department = defaultdict(list)

            for provider in facility_providers:
                name = provider.get('name', '')
                hierarchy = parse_provider_hierarchy(name)

                # Key for grouping
                if hierarchy['dept'] and hierarchy['location']:
                    # Has both dept and location
                    key = hierarchy['dept']
                elif hierarchy['dept']:
                    # Has dept only
                    key = hierarchy['dept']
                elif hierarchy['location']:
                    # Has location only
                    key = f"General - {hierarchy['location']}"
                else:
                    # Main facility only
                    key = "_main"

                by_department[key].append(provider)

            # Sort and display departments
            dept_sorted = sorted([k for k in by_department.keys() if k != '_main']) + (['_main'] if '_main' in by_department else [])

            for dept_idx, dept_key in enumerate(dept_sorted, 1):
                dept_providers = by_department[dept_key]

                if dept_key == '_main':
                    # Main facility without sub-locations
                    for provider in dept_providers:
                        f.write(f"   A. **{provider['name']}**\n")
                        if provider.get('address'):
                            f.write(f"      - {provider['address']}\n")
                        if provider.get('phone'):
                            f.write(f"      - {provider['phone']}\n")
                        f.write("\n")
                else:
                    # Department or location group
                    letter = chr(ord('A') + dept_idx - 1)
                    f.write(f"   {letter}. **{dept_key}** ({len(dept_providers)} locations)\n\n")

                    for sub_idx, provider in enumerate(sorted(dept_providers, key=lambda p: p.get('name', '')), 1):
                        f.write(f"      {sub_idx}. {provider['name']}\n")
                        if provider.get('address'):
                            f.write(f"         - {provider['address']}\n")
                        if provider.get('phone'):
                            f.write(f"         - {provider['phone']}\n")
                        f.write("\n")

            f.write("\n")


def main():
    """Create hierarchy outlines for all 5 health systems."""

    systems = [
        {
            'name': 'Norton Healthcare',
            'file': Path("/Volumes/X10 Pro/Roscoe/json-files/norton_healthcare_locations.json")
        },
        {
            'name': 'UofL Health',
            'file': Path("/Volumes/X10 Pro/Roscoe/json-files/uofl_health_locations.json")
        },
        {
            'name': 'Baptist Health',
            'file': Path("/Volumes/X10 Pro/Roscoe/json-files/baptist_health_locations.json")
        },
        {
            'name': 'CHI Saint Joseph Health',
            'file': Path("/Volumes/X10 Pro/Roscoe/json-files/chi_saint_joseph_locations.json")
        },
        {
            'name': 'St. Elizabeth Healthcare',
            'file': Path("/Volumes/X10 Pro/Roscoe/json-files/stelizabeth_locations.json")
        }
    ]

    output_dir = Path("/Volumes/X10 Pro/Roscoe/provider-hierarchies")
    output_dir.mkdir(exist_ok=True)

    print("="*70)
    print("PROVIDER HIERARCHY OUTLINE GENERATION")
    print("="*70)
    print()

    for system in systems:
        if not system['file'].exists():
            print(f"⚠️  File not found: {system['file']}")
            continue

        print(f"Processing {system['name']}...")

        with open(system['file'], 'r', encoding='utf-8') as f:
            providers = json.load(f)

        # Create outline
        output_file = output_dir / f"{system['name'].lower().replace(' ', '_').replace('&', 'and')}_outline.md"
        create_simple_outline(providers, output_file, system['name'])

        print(f"  ✓ {len(providers)} locations")
        print(f"  ✓ Saved to: {output_file.name}")
        print()

    print("="*70)
    print("OUTLINE GENERATION COMPLETE")
    print("="*70)
    print(f"\nOutput directory: {output_dir}")
    print("\n✅ Hierarchical outlines created for all 5 systems")


if __name__ == "__main__":
    main()
