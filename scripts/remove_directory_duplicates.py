#!/usr/bin/env python3
"""
Remove duplicate entities from directory.json and save them to an archive file.
"""

import json
from pathlib import Path
from datetime import datetime
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
    archive_file = Path("/Volumes/X10 Pro/Roscoe/json-files/directory_duplicates_removed.json")

    print("=" * 80)
    print("REMOVING DUPLICATES FROM DIRECTORY.JSON")
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

    duplicates_to_remove = []  # List of dir_entry UUIDs to remove
    duplicates_archive = []  # Full dir_entry objects to archive
    duplicate_reasons = {}  # uuid -> (category, matched_name)

    for dir_entry in directory:
        # Handle both 'name' and 'full_name' fields
        dir_name = dir_entry.get('name', '') or dir_entry.get('full_name', '')
        dir_uuid = dir_entry.get('uuid', dir_entry.get('source_id'))

        if not dir_name:
            continue

        # Check against each specialized category
        is_duplicate = False
        for category, specialized_names in specialized_entities.items():
            for spec_name in specialized_names:
                if fuzzy_match(dir_name, spec_name, threshold=90):
                    duplicates_to_remove.append(dir_uuid)
                    duplicates_archive.append(dir_entry)
                    duplicate_reasons[dir_uuid] = (category, spec_name)
                    is_duplicate = True
                    break
            if is_duplicate:
                break

    # Report what will be removed
    total_duplicates = len(duplicates_to_remove)
    print(f"Found {total_duplicates} duplicates to remove")
    print()

    # Group by category for summary
    by_category = defaultdict(int)
    for uuid in duplicates_to_remove:
        category, _ = duplicate_reasons[uuid]
        by_category[category] += 1

    print("Breakdown by category:")
    for category in sorted(by_category.keys()):
        print(f"  - {category}: {by_category[category]}")

    print()

    # Create archive file with metadata
    archive_data = {
        "removed_date": datetime.now().isoformat(),
        "reason": "Duplicates found in specialized entity files (adjusters.json, attorneys.json, etc.)",
        "total_removed": total_duplicates,
        "breakdown_by_category": dict(by_category),
        "entries": duplicates_archive,
        "duplicate_reasons": {
            str(uuid): {"category": cat, "matched_to": name}
            for uuid, (cat, name) in duplicate_reasons.items()
        }
    }

    print(f"Saving {total_duplicates} duplicates to archive...")
    with open(archive_file, 'w') as f:
        json.dump(archive_data, f, indent=2)

    print(f"✓ Archive saved: {archive_file}")
    print()

    # Remove duplicates from directory
    uuids_to_remove = set(duplicates_to_remove)
    cleaned_directory = [
        entry for entry in directory
        if entry.get('uuid', entry.get('source_id')) not in uuids_to_remove
    ]

    print(f"Cleaning directory.json...")
    print(f"  Before: {len(directory)} entries")
    print(f"  After:  {len(cleaned_directory)} entries")
    print(f"  Removed: {len(directory) - len(cleaned_directory)} duplicates")
    print()

    # Save cleaned directory
    if isinstance(directory_data, dict) and 'jsonb_agg' in directory_data:
        # Preserve wrapper structure
        directory_data['jsonb_agg'] = cleaned_directory
        cleaned_data = directory_data
    else:
        cleaned_data = cleaned_directory

    with open(directory_file, 'w') as f:
        json.dump(cleaned_data, f, indent=2)

    print(f"✓ Cleaned directory.json saved")
    print()
    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Directory entries: {len(directory)} → {len(cleaned_directory)}")
    print(f"Archive file: {archive_file}")

if __name__ == "__main__":
    main()
