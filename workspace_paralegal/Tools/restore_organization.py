#!/usr/bin/env python3
"""
Restore Organization from Filenames

Reads the category field from properly-named files and moves them
back to their correct bucket folders.

Usage:
    python restore_organization.py <case_directory_path>
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Category mapping: filename category -> folder name
CATEGORY_MAPPING = {
    'Case Information': 'Case Information',
    'Client': 'Client',
    'Investigation': 'Investigation',
    'Medical Record': 'Medical Records',
    'Medical Records': 'Medical Records',
    'Insurance': 'Insurance',
    'Lien': 'Lien',
    'Expense': 'Expenses',
    'Expenses': 'Expenses',
    'Negotiation Settlement': 'Negotiation Settlement',
    'Litigation': 'Litigation',
}

# All valid bucket folders
BUCKETS = [
    'Case Information',
    'Client',
    'Investigation',
    'Medical Records',
    'Insurance',
    'Lien',
    'Expenses',
    'Negotiation Settlement',
    'Litigation',
]


def extract_category_from_filename(filename: str) -> str | None:
    """
    Extract category from properly-formatted filename.

    Format: YYYY-MM-DD - Client Name - Category - Originator - Description.ext

    Returns category or None if can't parse.
    """
    # Split on " - " (space-dash-space)
    parts = filename.split(' - ')

    if len(parts) >= 3:
        # Category is the 3rd field (index 2)
        category = parts[2]
        return category

    return None


def get_target_folder(category: str) -> str | None:
    """Map category from filename to folder name."""
    return CATEGORY_MAPPING.get(category)


def restore_organization(case_dir: Path, dry_run: bool = False) -> Dict:
    """
    Restore organization by moving files to folders based on filename category.

    Args:
        case_dir: Path to case directory
        dry_run: If True, only print what would be done

    Returns:
        dict with statistics
    """
    stats = {
        'files_moved': 0,
        'files_skipped': 0,
        'errors': 0,
        'unparseable': []
    }

    if not case_dir.exists():
        print(f"❌ Error: Directory not found: {case_dir}")
        return stats

    print(f"\n{'DRY RUN - ' if dry_run else ''}Restoring organization: {case_dir.name}")
    print("=" * 80)

    # Create bucket directories
    for bucket in BUCKETS:
        bucket_path = case_dir / bucket
        if not bucket_path.exists():
            bucket_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {bucket}/")

    print()

    # Get all files in root
    files_to_move = []
    for item in case_dir.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            files_to_move.append(item)

    print(f"Found {len(files_to_move)} files in root to organize\n")

    # Process each file
    for file_path in sorted(files_to_move):
        filename = file_path.name

        # Extract category from filename
        category = extract_category_from_filename(filename)

        if not category:
            print(f"⚠️  Cannot parse: {filename}")
            stats['unparseable'].append(filename)
            stats['files_skipped'] += 1
            continue

        # Get target folder
        target_folder = get_target_folder(category)

        if not target_folder:
            print(f"⚠️  Unknown category '{category}': {filename}")
            stats['unparseable'].append(filename)
            stats['files_skipped'] += 1
            continue

        # Determine destination
        dest_path = case_dir / target_folder / filename

        if dry_run:
            print(f"Would move: {filename}")
            print(f"         → {target_folder}/")
            stats['files_moved'] += 1
        else:
            try:
                shutil.move(str(file_path), str(dest_path))
                print(f"✅ Moved: {filename}")
                print(f"      → {target_folder}/")
                stats['files_moved'] += 1
            except Exception as e:
                print(f"❌ Error moving {filename}: {e}")
                stats['errors'] += 1

    print("\n" + "=" * 80)
    print("Summary:")
    print(f"  Files moved: {stats['files_moved']}")
    print(f"  Files skipped: {stats['files_skipped']}")
    print(f"  Errors: {stats['errors']}")

    if stats['unparseable']:
        print(f"\n⚠️  {len(stats['unparseable'])} files could not be organized:")
        for filename in stats['unparseable'][:10]:  # Show first 10
            print(f"    - {filename}")
        if len(stats['unparseable']) > 10:
            print(f"    ... and {len(stats['unparseable']) - 10} more")

    return stats


def main():
    if len(sys.argv) < 2:
        print("Usage: python restore_organization.py <case_directory_path> [--dry-run]")
        print("\nExample:")
        print('  python restore_organization.py "/path/to/Abby-Sitgraves-MVA-7-13-2024"')
        sys.exit(1)

    case_dir_input = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    case_dir = Path(case_dir_input)

    if not case_dir.exists():
        print(f"❌ Error: Directory not found: {case_dir}")
        sys.exit(1)

    if not case_dir.is_dir():
        print(f"❌ Error: Not a directory: {case_dir}")
        sys.exit(1)

    # Run restoration
    stats = restore_organization(case_dir, dry_run=dry_run)

    if dry_run:
        print("\n⚠️  This was a DRY RUN. No files were moved.")
        print("Run without --dry-run to actually move files.")


if __name__ == "__main__":
    main()
