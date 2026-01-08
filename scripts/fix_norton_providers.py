#!/usr/bin/env python3
"""
Fix Norton Healthcare providers in master list.

Remove old Norton providers not in source.
Add missing Norton Children's Maternal providers.
"""

import json
from pathlib import Path


def main():
    # Load master
    with open("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/medical_providers.json") as f:
        providers = json.load(f)

    # Load Norton source
    with open("/Volumes/X10 Pro/Roscoe/json-files/norton_healthcare_locations.json") as f:
        norton_source = json.load(f)

    source_norton_names = set(loc.get('name', '') for loc in norton_source)

    print(f"Total providers in master: {len(providers)}")
    print(f"Norton source unique names: {len(source_norton_names)}")
    print()

    # Remove Norton providers not in source
    cleaned = []
    removed_norton = []

    for p in providers:
        parent = p.get('attributes', {}).get('parent_system', '')
        name = p.get('name', '')

        if parent == 'Norton Healthcare':
            # Check if in source
            if name not in source_norton_names:
                # Old provider - remove
                removed_norton.append(name)
                continue

        cleaned.append(p)

    print(f"Removed {len(removed_norton)} old Norton providers")
    for name in sorted(removed_norton):
        print(f"  - {name}")

    # Add missing Norton Children's Maternal
    print(f"\nAdding Norton Children's Maternal providers...")

    norton_childrens_names = [
        "Norton Children's Maternal - Fetal Medicine - Bowling Green",
        "Norton Children's Maternal - Fetal Medicine - Downtown",
        "Norton Children's Maternal - Fetal Medicine - Paducah",
        "Norton Children's Maternal - Fetal Medicine - Perinatal Center - St. Matthews",
    ]

    for loc in norton_source:
        name = loc.get('name', '')
        if name in norton_childrens_names:
            # Check if already exists
            if name not in [p['name'] for p in cleaned]:
                entry = {
                    'card_type': 'entity',
                    'entity_type': 'MedicalProvider',
                    'name': name,
                    'attributes': {
                        'address': loc.get('address', ''),
                        'phone': loc.get('phone', ''),
                        'parent_system': 'Norton Children\'s Hospital'
                    },
                    'source_id': 'norton_source',
                    'source_file': 'norton_healthcare_locations.json'
                }
                cleaned.append(entry)
                print(f"  + {name}")

    # Add Norton Women's and Children's Hospital
    norton_womens = [loc for loc in norton_source if loc.get('name') == "Norton Women's and Children's Hospital"]
    if norton_womens:
        if "Norton Women's and Children's Hospital" not in [p['name'] for p in cleaned]:
            entry = {
                'card_type': 'entity',
                'entity_type': 'MedicalProvider',
                'name': "Norton Women's and Children's Hospital",
                'attributes': {
                    'address': norton_womens[0].get('address', ''),
                    'phone': norton_womens[0].get('phone', ''),
                    'parent_system': 'Norton Healthcare'
                },
                'source_id': 'norton_source',
                'source_file': 'norton_healthcare_locations.json'
            }
            cleaned.append(entry)
            print(f"  + Norton Women's and Children's Hospital")

    # Re-sort
    cleaned_sorted = sorted(cleaned, key=lambda p: p.get('name', '').lower())

    # Save
    with open("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/medical_providers.json", 'w') as f:
        json.dump(cleaned_sorted, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved")
    print(f"  Before: {len(providers)}")
    print(f"  After: {len(cleaned_sorted)}")
    print(f"  Net change: {len(cleaned_sorted) - len(providers)}")

    # Final verification
    by_system = {}
    for p in cleaned_sorted:
        parent = p.get('attributes', {}).get('parent_system', 'Independent')
        by_system[parent] = by_system.get(parent, 0) + 1

    print(f"\nFinal Norton counts:")
    print(f"  Norton Healthcare: {by_system.get('Norton Healthcare', 0)} (source: 367 unique)")
    print(f"  Norton Children's Hospital: {by_system.get('Norton Children\\'s Hospital', 0)}")


if __name__ == "__main__":
    main()
