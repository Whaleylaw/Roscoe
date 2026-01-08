#!/usr/bin/env python3
"""
Consolidate duplicate medical provider folders for James Kiper case.
Uses canonical names from the database.
"""

import os
import sys
import shutil
from pathlib import Path
import json

# Provider consolidation mapping: canonical_name -> [folders_to_merge]
PROVIDER_MAPPING = {
    "Foundation Radiology": [
        "Foundation Radiology Group"
    ],
    "The State Pharmacy, Inc.": [
        "The State Pharmacy"
    ],
    "Southeastern Emergency Physician Services": [
        "Southeastern Emergency Physicians",
        "Southeastern Emergency Services",
        "Southeastern Emergency Services LLC"
    ],
    "Synergy Injury Care & Rehab Diagnostics": [
        "Synergy Injury Care",
        "Synergy Injury Care and Rehab",
        "Synergy Rehab"
    ],
    "UofL Health - Mary & Elizabeth Mary & Elizabeth Hospital": [
        "Mary Elizabeth Hospital",
        "Mary and Elizabeth Hospital",
        "UofL Health",
        "UofL Health - Mary & Elizabeth Hospital",
        "UofL Hospital",
        "UofL St Mary and Elizabeth Hospital"
    ]
}

def consolidate_folders(base_path: str, dry_run: bool = True):
    """Consolidate duplicate provider folders."""

    medical_records = Path(base_path) / "Medical Records"

    if not medical_records.exists():
        print(f"❌ Medical Records folder not found: {medical_records}")
        return False

    print(f"{'🔍 DRY RUN MODE' if dry_run else '✅ LIVE MODE'}\n")

    conflicts = []

    for canonical_name, folders_to_merge in PROVIDER_MAPPING.items():
        canonical_path = medical_records / canonical_name

        print(f"\n📁 Canonical: {canonical_name}")

        # Check if canonical folder exists, create if not
        if not canonical_path.exists():
            print(f"  ⚠️  Canonical folder doesn't exist, will create")
            if not dry_run:
                canonical_path.mkdir(parents=True, exist_ok=True)

        # Process each folder to merge
        for folder_name in folders_to_merge:
            source_path = medical_records / folder_name

            if not source_path.exists():
                print(f"  ⚠️  Folder not found: {folder_name}")
                continue

            # Get all files in source folder
            files = list(source_path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])

            print(f"  ← Merging: {folder_name} ({file_count} files)")

            if file_count == 0:
                print(f"    (empty, will remove)")
                if not dry_run:
                    shutil.rmtree(source_path)
                continue

            # Check for conflicts
            for file_path in files:
                if file_path.is_file():
                    relative_path = file_path.relative_to(source_path)
                    target_path = canonical_path / relative_path

                    if target_path.exists():
                        # Check if files are identical
                        if file_path.stat().st_size == target_path.stat().st_size:
                            print(f"    ⚠️  Duplicate (same size): {relative_path}")
                        else:
                            conflicts.append({
                                "source": str(file_path),
                                "target": str(target_path),
                                "canonical": canonical_name,
                                "folder": folder_name,
                                "file": str(relative_path)
                            })
                            print(f"    ⚠️  CONFLICT: {relative_path}")
                    else:
                        print(f"    ✓ Will move: {relative_path}")
                        if not dry_run:
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(file_path), str(target_path))

            # Remove empty source folder
            if not dry_run:
                try:
                    shutil.rmtree(source_path)
                    print(f"    ✓ Removed: {folder_name}")
                except OSError as e:
                    print(f"    ⚠️  Could not remove {folder_name}: {e}")

    # Report conflicts
    if conflicts:
        print(f"\n⚠️  {len(conflicts)} CONFLICTS FOUND:")
        print("\nConflicts need manual review:")
        for conflict in conflicts:
            print(f"\n  Canonical: {conflict['canonical']}")
            print(f"  From: {conflict['folder']}")
            print(f"  File: {conflict['file']}")
            print(f"  Source: {conflict['source']}")
            print(f"  Target: {conflict['target']}")

        # Save conflicts to JSON
        conflicts_file = Path(base_path) / "folder_consolidation_conflicts.json"
        with open(conflicts_file, 'w') as f:
            json.dump(conflicts, f, indent=2)
        print(f"\n💾 Conflicts saved to: {conflicts_file}")

        return False

    print("\n✅ No conflicts found!")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python consolidate_medical_folders.py <case_directory> [--live]")
        print("\nExample:")
        print("  python consolidate_medical_folders.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022")
        print("  python consolidate_medical_folders.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022 --live")
        sys.exit(1)

    case_dir = sys.argv[1]
    dry_run = "--live" not in sys.argv

    if not os.path.exists(case_dir):
        print(f"❌ Case directory not found: {case_dir}")
        sys.exit(1)

    success = consolidate_folders(case_dir, dry_run=dry_run)

    if dry_run:
        print("\n🔍 This was a dry run. Use --live flag to apply changes.")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
