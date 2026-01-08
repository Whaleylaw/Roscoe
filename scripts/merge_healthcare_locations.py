#!/usr/bin/env python3
"""Merge all healthcare provider location JSON files into one consolidated file."""

import json
import os

base_dir = "/Volumes/X10 Pro/Roscoe/json-files"

# Define all source files
source_files = {
    "UofL Health": "uofl_health_locations.json",
    "Norton Healthcare": "norton_healthcare_locations.json",
    "Baptist Health": "baptist_health_locations.json",
    "St. Elizabeth Healthcare": "stelizabeth_locations.json",
    "CHI Saint Joseph Health": "chi_saint_joseph_locations.json"
}

print("Merging healthcare provider location files...")
print("=" * 60)

all_locations = []
stats_by_system = {}

for system_name, filename in source_files.items():
    filepath = os.path.join(base_dir, filename)

    if not os.path.exists(filepath):
        print(f"\n⚠️  {system_name}: File not found - {filename}")
        continue

    print(f"\n{system_name}:")
    print(f"  Loading {filename}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        locations = json.load(f)

    print(f"  Found {len(locations)} locations")

    # Add system identifier to each location
    for loc in locations:
        loc['healthcare_system'] = system_name

    all_locations.extend(locations)

    # Track statistics
    with_phone = sum(1 for loc in locations if loc.get('phone'))
    stats_by_system[system_name] = {
        "total": len(locations),
        "with_phone": with_phone
    }

print("\n" + "=" * 60)
print(f"Total locations across all systems: {len(all_locations)}")

# Save consolidated file
output_file = os.path.join(base_dir, "all_healthcare_locations.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_locations, f, indent=2, ensure_ascii=False)

print(f"\nConsolidated data saved to: {output_file}")

# Print statistics
print("\n" + "=" * 60)
print("Summary by Healthcare System:")
print("=" * 60)

for system_name, stats in stats_by_system.items():
    phone_pct = (stats['with_phone'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"\n{system_name}:")
    print(f"  Total locations: {stats['total']}")
    print(f"  With phone numbers: {stats['with_phone']} ({phone_pct:.1f}%)")

total_with_phone = sum(stats['with_phone'] for stats in stats_by_system.values())
total_locations = sum(stats['total'] for stats in stats_by_system.values())
overall_pct = (total_with_phone / total_locations * 100) if total_locations > 0 else 0

print("\n" + "=" * 60)
print(f"Overall Total: {total_locations} locations")
print(f"Overall with phones: {total_with_phone} ({overall_pct:.1f}%)")

# Show sample records
print("\n" + "=" * 60)
print("Sample records (first 5):")
print("=" * 60)

for i, loc in enumerate(all_locations[:5], 1):
    print(f"\n{i}. {loc['name']}")
    print(f"   System: {loc['healthcare_system']}")
    print(f"   Address: {loc['address']}")
    print(f"   Phone: {loc['phone'] if loc['phone'] else '(not available)'}")
