#!/usr/bin/env python3
"""
Create a new medical-providers.json with only remaining providers.

Removes all entries that were deleted from the graph (Norton, UofL, Baptist, etc.)
and saves the remaining independent providers.
"""

import json
import re
from pathlib import Path


def parse_deleted_providers(mapping_file: Path) -> list:
    """Parse mapping file to extract provider names marked for deletion."""

    if not mapping_file.exists():
        return []

    with open(mapping_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by provider sections
    sections = re.split(r'## (\d+)\. OLD: (.+?)$', content, flags=re.MULTILINE)

    deleted = []

    for i in range(1, len(sections), 3):
        if i + 2 >= len(sections):
            break

        old_name = sections[i + 1].strip()
        section_content = sections[i + 2]

        # Check if marked for deletion
        delete_patterns = [
            r'\[x\s*\]\s*DELETE',
            r'\[\s*x\]\s*DELETE',
            r'\[x\]\s*DELETE'
        ]

        is_delete = any(re.search(pattern, section_content, re.IGNORECASE) for pattern in delete_patterns)

        if is_delete:
            deleted.append(old_name)

    return deleted


def main():
    """Create new medical-providers.json with remaining providers."""

    # Load original medical-providers.json
    original_file = Path("/Volumes/X10 Pro/Roscoe/json-files/medical-providers.json")

    print("Loading original medical-providers.json...")
    with open(original_file, 'r', encoding='utf-8') as f:
        all_providers = json.load(f)

    print(f"✓ Loaded {len(all_providers)} total provider entries\n")

    # Parse all mapping files to get deleted provider names
    mapping_dir = Path("/Volumes/X10 Pro/Roscoe/provider-mappings")

    mapping_files = [
        "NORTON_MAPPING.md",
        "UOFL_MAPPING_FACILITY_BASED.md",
        # Add other mapping files when they're created/marked
    ]

    all_deleted = set()

    print("Parsing mapping files for deletions...")
    for filename in mapping_files:
        file_path = mapping_dir / filename

        if not file_path.exists():
            print(f"⊙ {filename}: Not found, skipping")
            continue

        deleted = parse_deleted_providers(file_path)
        print(f"✓ {filename}: {len(deleted)} providers marked for deletion")

        all_deleted.update(deleted)

    print(f"\nTotal unique providers to remove: {len(all_deleted)}\n")

    # Show what we're removing
    print("Providers being removed:")
    for name in sorted(all_deleted):
        print(f"  - {name}")
    print()

    # Filter out deleted providers
    remaining_providers = []

    for provider in all_providers:
        provider_name = provider.get('provider_full_name', '')

        if provider_name in all_deleted:
            # Skip this one - it's been deleted
            continue

        remaining_providers.append(provider)

    print("="*70)
    print("FILTERING COMPLETE")
    print("="*70)
    print(f"Original entries: {len(all_providers)}")
    print(f"Deleted entries: {len(all_providers) - len(remaining_providers)}")
    print(f"Remaining entries: {len(remaining_providers)}")
    print()

    # Count by health system for remaining
    norton_remaining = len([p for p in remaining_providers if p.get('provider_full_name') and 'norton' in p.get('provider_full_name', '').lower()])
    uofl_remaining = len([p for p in remaining_providers if p.get('provider_full_name') and any(kw in p.get('provider_full_name', '').lower() for kw in ['uofl', 'jewish', 'university of louisville'])])
    baptist_remaining = len([p for p in remaining_providers if p.get('provider_full_name') and 'baptist' in p.get('provider_full_name', '').lower()])

    print("Remaining by health system:")
    print(f"  Norton: {norton_remaining}")
    print(f"  UofL: {uofl_remaining}")
    print(f"  Baptist: {baptist_remaining}")
    print(f"  Other (independent): {len(remaining_providers) - norton_remaining - uofl_remaining - baptist_remaining}")
    print()

    # Save to new file
    output_file = Path("/Volumes/X10 Pro/Roscoe/json-files/medical-providers-REMAINING.json")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(remaining_providers, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved to: {output_file}")
    print(f"\n✅ Created medical-providers-REMAINING.json with {len(remaining_providers)} entries")


if __name__ == "__main__":
    main()
