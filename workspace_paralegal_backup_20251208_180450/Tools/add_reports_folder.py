#!/usr/bin/env python3
"""
Add Reports Folder to All Case Folders

Creates a "Reports/" directory in each case folder within the projects directory.

Usage:
    python add_reports_folder.py
"""

import os
from pathlib import Path


def add_reports_folders(projects_dir: Path, dry_run: bool = False):
    """
    Add Reports/ folder to all case directories.

    Args:
        projects_dir: Path to projects directory
        dry_run: If True, only print what would be done
    """
    stats = {
        'folders_created': 0,
        'already_exists': 0,
        'skipped': 0
    }

    print(f"\n{'DRY RUN - ' if dry_run else ''}Adding Reports/ folders to case directories")
    print("=" * 80)

    if not projects_dir.exists():
        print(f"❌ Error: Projects directory not found: {projects_dir}")
        return stats

    # Iterate through all subdirectories in projects
    for case_folder in sorted(projects_dir.iterdir()):
        if not case_folder.is_dir():
            continue

        # Skip hidden directories
        if case_folder.name.startswith('.'):
            continue

        reports_path = case_folder / "Reports"

        if reports_path.exists():
            print(f"✓ Already exists: {case_folder.name}/Reports/")
            stats['already_exists'] += 1
        else:
            if dry_run:
                print(f"Would create: {case_folder.name}/Reports/")
                stats['folders_created'] += 1
            else:
                try:
                    reports_path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Created: {case_folder.name}/Reports/")
                    stats['folders_created'] += 1
                except Exception as e:
                    print(f"❌ Error creating {case_folder.name}/Reports/: {e}")
                    stats['skipped'] += 1

    print("\n" + "=" * 80)
    print("Summary:")
    print(f"  Folders created: {stats['folders_created']}")
    print(f"  Already existed: {stats['already_exists']}")
    print(f"  Skipped (errors): {stats['skipped']}")

    return stats


def main():
    import sys

    dry_run = '--dry-run' in sys.argv

    # Default projects directory
    projects_dir = Path(__file__).parent.parent / "projects"

    # Allow override via command line
    if len(sys.argv) >= 2 and not sys.argv[1].startswith('--'):
        projects_dir = Path(sys.argv[1])

    print(f"Projects directory: {projects_dir}")

    stats = add_reports_folders(projects_dir, dry_run=dry_run)

    if dry_run:
        print("\n⚠️  This was a DRY RUN. No folders were created.")
        print("Run without --dry-run to actually create folders.")


if __name__ == "__main__":
    main()
