#!/usr/bin/env python3
"""
Update provider names in merged episode JSON files (SAFE - creates new files).

Updates entity names in proposed_relationships to match new Facility/Location names.
"""

import json
from pathlib import Path


def update_merged_file(merged_file: Path, mapping: dict, dry_run: bool = True):
    """Update provider names in one merged JSON file."""

    with open(merged_file, 'r') as f:
        data = json.load(f)

    changes = []
    total_replacements = 0

    # Update entity names in proposed_relationships
    for episode in data.get('episodes', []):
        for rel_type, entities in episode.get('proposed_relationships', {}).items():
            if not isinstance(entities, list):
                continue

            for entity_ref in entities:
                if not isinstance(entity_ref, dict):
                    continue

                entity_name = entity_ref.get('entity_name', '')

                # Check if this name needs mapping
                if entity_name in mapping:
                    new_name = mapping[entity_name]
                    entity_ref['entity_name'] = new_name
                    changes.append({
                        'old': entity_name,
                        'new': new_name
                    })
                    total_replacements += 1

    if not changes:
        return None  # No changes needed

    # Save to new file (NEVER overwrite original)
    if not dry_run:
        output_file = merged_file.parent / f"{merged_file.name}.UPDATED"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return {
        'file': merged_file.name,
        'total_replacements': total_replacements,
        'unique_changes': len(set(c['old'] for c in changes))
    }


def main():
    """Update merged episode files (SAFE MODE)."""

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Show changes without creating files')
    parser.add_argument('--execute', action='store_true', help='Create .UPDATED files')
    args = parser.parse_args()

    print("="*70)
    print("MERGED EPISODE FILE UPDATE (SAFE MODE)")
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
    mapping_file = Path("/Volumes/X10 Pro/Roscoe/provider_name_mapping.json")

    if not mapping_file.exists():
        print("❌ Mapping file not found")
        return

    with open(mapping_file) as f:
        mapping = json.load(f)

    print(f"Loaded {len(mapping)} provider name mappings\n")

    # Find merged files
    episodes_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes")

    merged_files = list(episodes_dir.glob("merged_*.json"))

    print(f"Found {len(merged_files)} merged files\n")

    # Process each file
    results = []

    for merged_file in sorted(merged_files):
        print(f"Processing {merged_file.name}...", end=' ')
        result = update_merged_file(merged_file, mapping, dry_run=args.dry_run)

        if result:
            results.append(result)
            print(f"✓ {result['total_replacements']} replacements")
        else:
            print("⊙ No changes needed")

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

        for result in results:
            print(f"  {result['file']}")
            print(f"    Replacements: {result['total_replacements']}")
            print(f"    Unique names changed: {result['unique_changes']}")
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
