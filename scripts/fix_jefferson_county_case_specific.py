#!/usr/bin/env python3
"""
Fix case-specific Jefferson County court references.

For Abby Sitgraves case (25-CI-000133), all court references should be
"Jefferson County Circuit Court, Division II"
"""

import json
from pathlib import Path


def fix_jefferson_county_references(merged_path: Path, case_name: str, correct_division: str):
    """Replace all Jefferson County court variants with the correct division."""

    with open(merged_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Variants to replace
    jefferson_variants = [
        "Jefferson 25-CI-00133",
        "Jefferson County",
        "Jefferson Circuit Court",
        "Jefferson (25-CI-000133)",
        "Jefferson County (25-CI-00133)",
    ]

    replacements = 0

    # Process each episode
    for episode in data.get('episodes', []):
        rels = episode.get('proposed_relationships', {})
        for rel_type, entities in rels.items():
            if not isinstance(entities, list):
                continue

            for entity_ref in entities:
                if not isinstance(entity_ref, dict):
                    continue

                entity_type = entity_ref.get('entity_type')
                entity_name = entity_ref.get('entity_name')

                # Only fix Court entities with Jefferson variants
                if entity_type == "Court" and entity_name in jefferson_variants:
                    entity_ref['entity_name'] = correct_division
                    replacements += 1

    # Save updated file
    with open(merged_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✓ Fixed {replacements} Jefferson County references")
    print(f"  All Court entities now reference: {correct_division}")
    print(f"  Updated file: {merged_path}")


def main():
    base_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes")
    case_name = "Abby-Sitgraves-MVA-7-13-2024"

    merged_path = base_dir / f"merged_{case_name}.json"
    correct_division = "Jefferson County Circuit Court, Division II"

    print(f"Processing: {case_name}")
    print(f"  Target division: {correct_division}")
    print(f"  File: {merged_path}")
    print()

    fix_jefferson_county_references(merged_path, case_name, correct_division)


if __name__ == "__main__":
    main()
