#!/usr/bin/env python3
"""
Create mapping of old MedicalProvider names to new Facility names.

This mapping will be used to update episode review files.
"""

import json
from pathlib import Path


def create_provider_mapping():
    """Create old → new provider name mapping."""

    # Load new facilities to get available names
    facilities_file = Path("/Volumes/X10 Pro/Roscoe/schema-final/entities/facilities.json")

    with open(facilities_file) as f:
        facilities = json.load(f)

    # Create index of facility names
    facility_names = set(fac['name'] for fac in facilities)

    print(f"Loaded {len(facility_names)} facility names from new structure\n")

    # Build mapping of common old names → new names
    mapping = {}

    # Pattern 1: Simple additions (health system prefix)
    simple_additions = {
        # UofL/Jewish
        "Jewish Hospital": "UofL Health – Jewish Hospital",
        "UofL Hospital": "UofL Health – UofL Hospital",
        "Mary & Elizabeth Hospital": "UofL Health – Mary & Elizabeth Hospital",
        "UofL Health - Mary & Elizabeth Hospital": "UofL Health – Mary & Elizabeth Hospital",
        "UofL Health - Mary & Elizabeth Mary & Elizabeth Hospital": "UofL Health – Mary & Elizabeth Hospital",
        "Saint Mary and Elizabeth Hospital": "UofL Health – Mary & Elizabeth Hospital",

        # Norton
        "Norton Hospital": "Norton Hospital",  # May exist as-is
        "Norton Audubon Hospital": "Norton Audubon Hospital",
        "Norton Brownsboro Hospital": "Norton Brownsboro Hospital",

        # Independent (usually same)
        "Foundation Radiology": "Foundation Radiology",
        "Starlite Chiropractic": "Starlite Chiropractic",
    }

    # Pattern 2: Dash character fixes (- to –)
    dash_fixes = [
        ("UofL Physicians - Orthopedics", "UofL Physicians – Orthopedics"),
        ("UofL Physicians - Podiatric Medicine & Surgery", "UofL Physicians – Podiatric Medicine & Surgery"),
        ("UofL Health - Urgent Care Plus - Buechel", "UofL Health – Urgent Care Plus – Buechel"),
        ("Baptist Health - Louisville", "Baptist Health Louisville"),  # Check actual name
    ]

    # Add simple additions
    for old_name, new_name in simple_additions.items():
        # Verify new name exists in facilities
        if new_name in facility_names:
            mapping[old_name] = new_name
            print(f"✓ {old_name} → {new_name}")
        else:
            print(f"⚠️  {old_name} → {new_name} (NOT FOUND IN GRAPH)")

    print()

    # Add dash fixes if they exist
    for old_name, new_name in dash_fixes:
        if new_name in facility_names:
            mapping[old_name] = new_name
            print(f"✓ {old_name} → {new_name}")
        else:
            print(f"⚠️  {old_name} → {new_name} (NOT FOUND IN GRAPH)")

    print()

    # Save mapping
    output_file = Path("/Volumes/X10 Pro/Roscoe/provider_name_mapping.json")

    with open(output_file, 'w') as f:
        json.dump(mapping, f, indent=2)

    print(f"✓ Saved {len(mapping)} mappings to: {output_file}")
    print()
    print("="*70)
    print(f"MAPPING CREATED: {len(mapping)} old → new name pairs")
    print("="*70)

    return mapping


if __name__ == "__main__":
    create_provider_mapping()
