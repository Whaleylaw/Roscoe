#!/usr/bin/env python3
"""
Complete the master provider list by adding all missing locations from source files.
Then deduplicate to ensure no duplicates.
"""

import json
from pathlib import Path
from collections import defaultdict


def format_provider_entry(name: str, source_data: dict, parent_system: str, source_file: str) -> dict:
    """Format a provider entry in standard entity card format."""

    entry = {
        'card_type': 'entity',
        'entity_type': 'MedicalProvider',
        'name': name,
        'attributes': {
            'parent_system': parent_system
        },
        'source_id': source_data.get('source_id', 'imported'),
        'source_file': source_file
    }

    # Add available attributes
    if source_data.get('address'):
        entry['attributes']['address'] = source_data['address']
    if source_data.get('phone'):
        entry['attributes']['phone'] = source_data['phone']
    if source_data.get('email'):
        entry['attributes']['email'] = source_data['email']
    if source_data.get('fax'):
        entry['attributes']['fax'] = source_data['fax']
    if source_data.get('specialty'):
        entry['attributes']['specialty'] = source_data['specialty']
    if source_data.get('provider_type'):
        entry['attributes']['provider_type'] = source_data['provider_type']
    if source_data.get('npi'):
        entry['attributes']['npi'] = source_data['npi']

    return entry


def add_missing_from_source(master_list: list, source_file: Path, system_name: str, add_prefix: bool = False) -> int:
    """Add missing providers from a source file to master list."""

    if not source_file.exists():
        print(f"  ⊙ Source file not found: {source_file}")
        return 0

    with open(source_file, 'r', encoding='utf-8') as f:
        source_locations = json.load(f)

    # Get existing names in master
    existing_names = set(p['name'] for p in master_list)

    added_count = 0

    for loc in source_locations:
        source_name = loc.get('name', '')
        if not source_name:
            continue

        # Add prefix if needed (for St. Elizabeth-style files)
        if add_prefix and not source_name.startswith(system_name):
            full_name = f"{system_name} - {source_name}"
        else:
            full_name = source_name

        # Skip if already in master
        if full_name in existing_names:
            continue

        # Create entry
        entry = format_provider_entry(full_name, loc, system_name, source_file.name)
        master_list.append(entry)
        added_count += 1
        existing_names.add(full_name)

    return added_count


def deduplicate_by_name(providers: list) -> list:
    """Deduplicate providers by name, keeping first occurrence."""

    seen = set()
    deduplicated = []
    duplicates = []

    for provider in providers:
        name = provider.get('name', '')

        if name in seen:
            duplicates.append(name)
            continue

        seen.add(name)
        deduplicated.append(provider)

    return deduplicated, duplicates


def main():
    """Complete and deduplicate master provider list."""

    print("="*70)
    print("COMPLETING MASTER PROVIDER LIST")
    print("="*70)
    print()

    # Load current master list
    master_file = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/medical_providers.json")

    print("Loading current master list...")
    with open(master_file, 'r', encoding='utf-8') as f:
        master = json.load(f)

    print(f"✓ Current master list: {len(master)} providers\n")

    # Add missing from each source file
    source_files = [
        ("Norton Healthcare", Path("/Volumes/X10 Pro/Roscoe/json-files/norton_healthcare_locations.json"), False),
        ("UofL Health", Path("/Volumes/X10 Pro/Roscoe/json-files/uofl_health_locations.json"), False),
        ("Baptist Health", Path("/Volumes/X10 Pro/Roscoe/json-files/baptist_health_locations.json"), False),
        ("CHI Saint Joseph Health", Path("/Volumes/X10 Pro/Roscoe/json-files/chi_saint_joseph_locations.json"), False),
        ("Norton Children's Hospital", Path("/Volumes/X10 Pro/Roscoe/json-files/norton_childrens_locations_SCRAPED.json"), False),
    ]

    print("Adding missing providers from source files:")
    print("-" * 70)

    total_added = 0

    for system_name, source_file, add_prefix in source_files:
        print(f"\n{system_name}:")
        print(f"  Source: {source_file.name}")

        added = add_missing_from_source(master, source_file, system_name, add_prefix)
        total_added += added

        print(f"  Added: {added} new providers")

    print()
    print(f"Total added: {total_added}")
    print(f"Master list now: {len(master)} providers")
    print()

    # Fix Norton Children's parent_system for existing entries
    print("Fixing Norton Children's parent_system...")
    fixed_count = 0
    for provider in master:
        name = provider.get('name', '')
        parent = provider.get('attributes', {}).get('parent_system', '')

        if 'norton children' in name.lower() and parent != 'Norton Children\'s Hospital':
            provider['attributes']['parent_system'] = 'Norton Children\'s Hospital'
            fixed_count += 1

    print(f"✓ Fixed parent_system for {fixed_count} Norton Children's entries\n")

    # Deduplicate
    print("="*70)
    print("DEDUPLICATING")
    print("="*70)
    print()

    deduplicated, duplicates = deduplicate_by_name(master)

    print(f"Before deduplication: {len(master)}")
    print(f"After deduplication: {len(deduplicated)}")
    print(f"Duplicates removed: {len(duplicates)}")

    if duplicates:
        print(f"\nFirst 10 duplicates removed:")
        for dup in duplicates[:10]:
            print(f"  - {dup}")
        if len(duplicates) > 10:
            print(f"  ... and {len(duplicates) - 10} more")

    print()

    # Sort alphabetically
    print("Sorting alphabetically...")
    sorted_providers = sorted(deduplicated, key=lambda p: p.get('name', '').lower())
    print(f"✓ Sorted {len(sorted_providers)} providers\n")

    # Save final version
    output_file = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/medical_providers.json")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_providers, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved to: {output_file.name}")

    # Final verification
    print()
    print("="*70)
    print("FINAL VERIFICATION")
    print("="*70)
    print()

    by_system = defaultdict(int)
    for p in sorted_providers:
        parent = p.get('attributes', {}).get('parent_system', 'Independent')
        by_system[parent] += 1

    print("Final counts by health system:")
    for system in sorted(by_system.keys()):
        if system != 'Independent':
            print(f"  {system}: {by_system[system]}")
    print(f"  Independent: {by_system.get('Independent', 0)}")
    print(f"\nTOTAL: {len(sorted_providers)}")

    print()
    print("✅ Master provider list complete and deduplicated!")


if __name__ == "__main__":
    main()
