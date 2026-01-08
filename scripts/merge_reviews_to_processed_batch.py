#!/usr/bin/env python3
"""
Apply review mappings to processed files to create merged files (batch version).

Uses corrected review files (.UPDATED if exists, otherwise original .md)
to update entity names in processed_*.json files.

Creates merged_*.json files (NEVER overwrites).
"""

import json
import re
from pathlib import Path
from collections import defaultdict


def parse_review_file(review_file: Path):
    """Parse review file to extract entity mappings."""

    with open(review_file, 'r') as f:
        content = f.read()

    mappings = defaultdict(dict)

    # Find all entity type sections
    sections = re.findall(r'### (\w+) \(.*?\)(.*?)(?=###|\Z)', content, re.DOTALL)

    for entity_type, section_content in sections:
        # Extract entity lines with MATCHES
        lines = re.findall(r'- \[ \] (.+?) — \*✓ MATCHES: (.+?)\*', section_content)

        for proposed_name, match_info in lines:
            proposed_name = proposed_name.strip()

            # Extract actual name from match_info
            # Handle patterns like: "ActualName (notes)"
            actual_name = match_info.split('(')[0].strip()

            mappings[entity_type][proposed_name] = actual_name

    return mappings


def apply_mappings_to_processed(processed_file: Path, mappings: dict, dry_run: bool = False):
    """Apply review mappings to processed file."""

    with open(processed_file) as f:
        data = json.load(f)

    replacements = 0

    # Update entity names in episodes
    for episode in data.get('episodes', []):
        for rel_type, entities in episode.get('proposed_relationships', {}).items():
            if not isinstance(entities, list):
                continue

            for entity_ref in entities:
                if not isinstance(entity_ref, dict):
                    continue

                entity_type = entity_ref.get('entity_type')
                proposed_name = entity_ref.get('entity_name')

                if not entity_type or not proposed_name:
                    continue

                # Check if we have a mapping for this
                if entity_type in mappings and proposed_name in mappings[entity_type]:
                    actual_name = mappings[entity_type][proposed_name]
                    entity_ref['entity_name'] = actual_name
                    replacements += 1

    if dry_run or replacements == 0:
        return replacements

    # Save to merged file
    case_name = data.get('case_name', 'unknown')
    output_file = processed_file.parent / f"merged_{case_name}.json"

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return replacements


def main():
    """Batch process all files."""

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Preview without creating files')
    parser.add_argument('--execute', action='store_true', help='Create merged files')
    args = parser.parse_args()

    print("="*70)
    print("BATCH MERGE: REVIEWS → PROCESSED → MERGED")
    print("="*70)
    print()

    if args.dry_run:
        print("DRY RUN MODE")
    elif args.execute:
        print("EXECUTE MODE - Will create merged_*.json files")
    else:
        print("PREVIEW MODE")
        args.dry_run = True

    print()

    # Find processed files
    episodes_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes")
    reviews_dir = episodes_dir / "reviews"

    processed_files = sorted(episodes_dir.glob("processed_*.json"))

    print(f"Found {len(processed_files)} processed files")
    print()

    results = []

    for processed_file in processed_files:
        case_name = processed_file.name.replace("processed_", "").replace(".json", "")

        # Find corresponding review file (prefer .UPDATED if exists)
        review_updated = reviews_dir / f"review_{case_name}.md.UPDATED"
        review_original = reviews_dir / f"review_{case_name}.md"

        if review_updated.exists():
            review_file = review_updated
            review_type = "UPDATED"
        elif review_original.exists():
            review_file = review_original
            review_type = "original"
        else:
            print(f"⊙ {case_name}: No review file")
            continue

        # Parse review
        mappings = parse_review_file(review_file)

        # Apply to processed
        replacements = apply_mappings_to_processed(processed_file, mappings, dry_run=args.dry_run)

        if replacements > 0:
            print(f"✓ {case_name}: {replacements} replacements ({review_type})")
            results.append({
                'case': case_name,
                'replacements': replacements,
                'review_type': review_type
            })
        else:
            print(f"⊙ {case_name}: No changes")

    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Processed files: {len(processed_files)}")
    print(f"Merged files created: {len(results)}")
    print(f"Total replacements: {sum(r['replacements'] for r in results)}")
    print()

    if args.dry_run:
        print("⚠️  DRY RUN - No files created")
        print("\nRun with --execute to create merged files")
    else:
        print("✓ Created merged_*.json files in episodes/")


if __name__ == "__main__":
    main()
