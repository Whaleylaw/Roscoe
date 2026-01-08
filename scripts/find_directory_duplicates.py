#!/usr/bin/env python3
"""
Find duplicate entities in directory.json that also exist in specialized JSON files.
"""

import json
from pathlib import Path
from rapidfuzz import fuzz
from collections import defaultdict

def normalize_name(name: str) -> str:
    """Normalize entity name for comparison."""
    return name.lower().strip().replace(".", "").replace(",", "")

def fuzzy_match(name1: str, name2: str, threshold: int = 90) -> bool:
    """Check if two names match with fuzzy logic."""
    score = fuzz.ratio(normalize_name(name1), normalize_name(name2))
    return score >= threshold

def load_entity_names(file_path: Path) -> set:
    """Load all entity names from a JSON file."""
    if not file_path.exists():
        return set()

    with open(file_path) as f:
        data = json.load(f)

    names = set()
    for entity in data:
        if isinstance(entity, dict) and 'name' in entity:
            names.add(entity['name'])
            # Also add aliases if they exist
            if 'aliases' in entity and entity['aliases']:
                for alias in entity['aliases']:
                    names.add(alias)

    return names

def main():
    entities_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities")
    directory_file = Path("/Volumes/X10 Pro/Roscoe/json-files/directory.json")

    print("=" * 80)
    print("FINDING DIRECTORY DUPLICATES")
    print("=" * 80)
    print()

    # Load all specialized entity files
    specialized_files = {
        'adjusters': entities_dir / "adjusters.json",
        'attorneys': entities_dir / "attorneys.json",
        'lawfirms': entities_dir / "lawfirms.json",
        'vendors': entities_dir / "vendors.json",
        'lienholders': entities_dir / "lienholders.json",
        'insurers': entities_dir / "insurers.json",
        'medical_providers': entities_dir / "medical_providers.json",
        'courts': entities_dir / "courts.json",
        'circuit_divisions': entities_dir / "circuit_divisions.json",
        'district_divisions': entities_dir / "district_divisions.json",
        'defendants': entities_dir / "defendants.json",
        'organizations': entities_dir / "organizations.json",
        'mediators': entities_dir / "mediators.json",
        'experts': entities_dir / "experts.json",
        'witnesses': entities_dir / "witnesses.json",
    }

    # Load all specialized entities
    print("Loading specialized entity files...")
    specialized_entities = {}
    for category, file_path in specialized_files.items():
        names = load_entity_names(file_path)
        specialized_entities[category] = names
        print(f"  - {category}: {len(names)} entities")

    print()

    # Load directory.json
    print("Loading directory.json...")
    with open(directory_file) as f:
        directory_data = json.load(f)

    # Handle jsonb_agg wrapper structure
    if isinstance(directory_data, dict) and 'jsonb_agg' in directory_data:
        directory = directory_data['jsonb_agg']
    else:
        directory = directory_data

    print(f"  - {len(directory)} directory entries")
    print()

    # Find duplicates
    print("Finding duplicates (fuzzy matching with threshold 90)...")
    print()

    duplicates = defaultdict(list)  # category -> [(dir_entry, matched_name)]

    for dir_entry in directory:
        # Handle both 'name' and 'full_name' fields
        dir_name = dir_entry.get('name', '') or dir_entry.get('full_name', '')
        if not dir_name:
            continue

        # Check against each specialized category
        for category, specialized_names in specialized_entities.items():
            for spec_name in specialized_names:
                if fuzzy_match(dir_name, spec_name, threshold=90):
                    duplicates[category].append({
                        'directory_name': dir_name,
                        'specialized_name': spec_name,
                        'directory_id': dir_entry.get('uuid', dir_entry.get('source_id', 'N/A')),
                        'match_score': fuzz.ratio(normalize_name(dir_name), normalize_name(spec_name))
                    })
                    break  # Only match to one category

    # Report results
    total_duplicates = sum(len(matches) for matches in duplicates.values())
    print(f"FOUND {total_duplicates} DUPLICATES\n")

    for category in sorted(duplicates.keys()):
        matches = duplicates[category]
        if matches:
            print(f"\n{category.upper()} ({len(matches)} duplicates):")
            print("-" * 80)
            for match in sorted(matches, key=lambda x: x['directory_name']):
                dir_name = match['directory_name']
                spec_name = match['specialized_name']
                score = match['match_score']
                dir_id = match['directory_id']

                if dir_name == spec_name:
                    print(f"  ✓ EXACT: {dir_name} (dir_id: {dir_id})")
                else:
                    print(f"  ~ FUZZY ({score}): '{dir_name}' → '{spec_name}' (dir_id: {dir_id})")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total directory entries: {len(directory)}")
    print(f"Total duplicates found: {total_duplicates}")
    print(f"Unique entries remaining: {len(directory) - total_duplicates}")
    print()

    # Save duplicates to file for review
    output_file = entities_dir / "directory_duplicates_report.json"
    with open(output_file, 'w') as f:
        json.dump(dict(duplicates), f, indent=2)

    print(f"Full report saved to: {output_file}")

if __name__ == "__main__":
    main()
