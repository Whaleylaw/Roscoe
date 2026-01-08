#!/usr/bin/env python3
"""
Update provider names in episode review files (SAFE - creates new files).

This script:
1. Loads provider name mapping (old → new)
2. Reads review files
3. Replaces old provider names with new Facility names
4. Saves to NEW files (.UPDATED suffix)
5. NEVER overwrites originals

Run this to preview changes, then manually approve.
"""

import json
import re
from pathlib import Path


def load_provider_mapping():
    """Load old → new provider name mapping."""

    mapping_file = Path("/Volumes/X10 Pro/Roscoe/provider_name_mapping.json")

    if not mapping_file.exists():
        print("⚠️  Mapping file not found. Run create_provider_name_mapping.py first.")
        return {}

    with open(mapping_file) as f:
        mapping = json.load(f)

    print(f"Loaded {len(mapping)} provider name mappings\n")
    return mapping


def update_review_file(review_file: Path, mapping: dict, dry_run: bool = True):
    """Update provider names in one review file."""

    with open(review_file, 'r') as f:
        content = f.read()

    # Track what changed
    changes = []

    # Replace each old name with new name
    updated_content = content

    for old_name, new_name in mapping.items():
        # Find occurrences
        pattern = re.escape(old_name)
        matches = re.findall(pattern, content)

        if matches:
            # Replace
            updated_content = updated_content.replace(old_name, new_name)
            changes.append({
                'old': old_name,
                'new': new_name,
                'count': len(matches)
            })

    if not changes:
        return None  # No changes needed

    # Save to new file (NEVER overwrite original)
    if not dry_run:
        output_file = review_file.parent / f"{review_file.name}.UPDATED"
        with open(output_file, 'w') as f:
            f.write(updated_content)

    return {
        'file': review_file.name,
        'changes': changes,
        'total_replacements': sum(c['count'] for c in changes)
    }


def main():
    """Update all review files (SAFE MODE - creates new files)."""

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Show changes without creating files')
    parser.add_argument('--execute', action='store_true', help='Create .UPDATED files')
    args = parser.parse_args()

    print("="*70)
    print("EPISODE REVIEW FILE UPDATE (SAFE MODE)")
    print("="*70)
    print()

    if args.dry_run:
        print("DRY RUN MODE - No files will be created")
    elif args.execute:
        print("EXECUTE MODE - Will create .UPDATED files")
    else:
        print("PREVIEW MODE - Showing what would change")
        args.dry_run = True

    print()

    # Load mapping
    mapping = load_provider_mapping()

    if not mapping:
        print("❌ No mapping available")
        return

    # Find all review files
    reviews_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/reviews")

    if not reviews_dir.exists():
        print(f"❌ Reviews directory not found: {reviews_dir}")
        return

    review_files = list(reviews_dir.glob("review_*.md"))

    print(f"Found {len(review_files)} review files\n")

    # Process each file
    results = []

    for review_file in sorted(review_files):
        result = update_review_file(review_file, mapping, dry_run=args.dry_run)

        if result:
            results.append(result)

    # Show summary
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print()

    if not results:
        print("✓ No changes needed - all names already match!")
    else:
        print(f"Files needing updates: {len(results)}")
        print()

        # Show first 10 files with changes
        print("Files with changes (showing first 10):")
        for i, result in enumerate(results[:10], 1):
            print(f"\n{i}. {result['file']}")
            print(f"   Total replacements: {result['total_replacements']}")
            for change in result['changes'][:3]:
                print(f"     {change['old']} → {change['new']} ({change['count']}x)")
            if len(result['changes']) > 3:
                print(f"     ... and {len(result['changes']) - 3} more")

        if len(results) > 10:
            print(f"\n... and {len(results) - 10} more files")

        print()
        print(f"Total files affected: {len(results)}")
        print(f"Total replacements: {sum(r['total_replacements'] for r in results)}")

    print()

    if args.dry_run:
        print("⚠️  DRY RUN - No files created")
        print("\nTo create .UPDATED files, run with: --execute")
    elif args.execute:
        print(f"✓ Created {len(results)} .UPDATED files")
        print("\nReview these files, then:")
        print("  1. If good, rename .UPDATED files to replace originals")
        print("  2. If issues, adjust mapping and re-run")
    else:
        print("Run with --dry-run or --execute")


if __name__ == "__main__":
    main()
