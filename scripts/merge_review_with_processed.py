#!/usr/bin/env python3
"""
Merge review file entities with processed episode file.

This script:
1. Reads the processed episode JSON file
2. Reads the review markdown file to extract entity mappings
3. Replaces proposed entity names with actual matched entities
4. Outputs a merged JSON file with corrected entities
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


def parse_review_file(review_path: Path) -> Dict[str, Dict[str, Tuple[str, str]]]:
    """
    Parse review file to extract entity mappings.

    Returns:
        Dict mapping entity_type -> {proposed_name -> (actual_name, actual_type)}

    Example:
        {
            "Attorney": {
                "Sarena Tuttle": ("Sarena Tuttle", "CaseManager"),
                "W. Bryce Koon, Esq.": ("Bryce Koon", "Attorney")
            }
        }
    """
    mappings: Dict[str, Dict[str, Tuple[str, str]]] = {}

    with open(review_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by entity type sections (### EntityType)
    sections = re.split(r'### ([A-Za-z]+) \(\d+ consolidated\)', content)

    # Process pairs of (entity_type, section_content)
    for i in range(1, len(sections), 2):
        entity_type = sections[i]
        section_content = sections[i + 1] if i + 1 < len(sections) else ""

        if entity_type not in mappings:
            mappings[entity_type] = {}

        # Extract each entity line: - [ ] ProposedName — *✓ MATCHES: ActualName*
        # Pattern handles multiple formats:
        # 1. Simple match: - [ ] Name — *✓ MATCHES: ActualName*
        # 2. With notes: - [ ] Name — *✓ MATCHES: ActualName (WHALEY STAFF → should be CaseManager)*
        # 3. With variants: - [ ] Name — *✓ MATCHES: ActualName*\n      ↳ _variant_

        lines = section_content.split('\n')
        current_proposed = None

        for line in lines:
            # Match the main entity line
            match = re.match(r'- \[ \] (.+?) — \*✓ MATCHES: (.+?)\*', line)
            if match:
                proposed_name = match.group(1).strip()
                match_info = match.group(2).strip()

                # Extract actual name and type corrections
                # Format 1: "ActualName (WHALEY STAFF → should be CaseManager, not Attorney)"
                # Format 2: "ActualName (Judge: JudgeName)"
                # Format 3: "ActualName (→ ATTORNEY, not law firm)"
                # Format 4: "ActualName"

                actual_type = entity_type  # default to same type
                actual_name = match_info

                # Check for type correction patterns
                if " → should be " in match_info:
                    # Extract: "Name (... → should be NewType, not ...)"
                    type_match = re.search(r'→ should be (\w+)', match_info)
                    if type_match:
                        actual_type = type_match.group(1)
                    # Extract actual name before the parenthetical
                    name_match = re.match(r'(.+?)\s*\(', match_info)
                    if name_match:
                        actual_name = name_match.group(1).strip()

                elif " (→ " in match_info:
                    # Extract: "Name (→ TYPE, not ...)"
                    type_match = re.search(r'→ ([A-Z]+)', match_info)
                    if type_match:
                        actual_type = type_match.group(1).title()
                    name_match = re.match(r'(.+?)\s*\(', match_info)
                    if name_match:
                        actual_name = name_match.group(1).strip()

                elif " (Judge: " in match_info or " (alias: " in match_info:
                    # Extract name before parenthetical
                    name_match = re.match(r'(.+?)\s*\(', match_info)
                    if name_match:
                        actual_name = name_match.group(1).strip()

                mappings[entity_type][proposed_name] = (actual_name, actual_type)
                current_proposed = proposed_name

            # Check for variant lines (↳ _variant_)
            elif line.strip().startswith('↳ _') and current_proposed:
                variant = line.strip()[3:-1]  # Remove "↳ _" and trailing "_"
                if current_proposed in mappings[entity_type]:
                    # Map variant to same actual entity as consolidated entry
                    mappings[entity_type][variant] = mappings[entity_type][current_proposed]

    return mappings


def merge_entities(processed_path: Path, review_path: Path, output_path: Path):
    """
    Merge entities from review file into processed file.
    """
    # Load processed JSON
    with open(processed_path, 'r', encoding='utf-8') as f:
        processed_data = json.load(f)

    # Parse review file to get entity mappings
    entity_mappings = parse_review_file(review_path)

    # Statistics
    total_replacements = 0
    replacements_by_type = {}
    unmatched_entities = []

    # Process each episode
    for episode in processed_data.get('episodes', []):
        if 'proposed_relationships' not in episode:
            continue

        for rel_type, entities in episode['proposed_relationships'].items():
            if not isinstance(entities, list):
                continue

            for entity_ref in entities:
                if not isinstance(entity_ref, dict):
                    continue

                entity_type = entity_ref.get('entity_type')
                proposed_name = entity_ref.get('entity_name')

                if not entity_type or not proposed_name:
                    continue

                # Look up mapping
                if entity_type in entity_mappings and proposed_name in entity_mappings[entity_type]:
                    actual_name, actual_type = entity_mappings[entity_type][proposed_name]

                    # Update entity
                    if entity_ref['entity_name'] != actual_name:
                        entity_ref['entity_name'] = actual_name
                        total_replacements += 1
                        replacements_by_type[entity_type] = replacements_by_type.get(entity_type, 0) + 1

                    if entity_ref['entity_type'] != actual_type:
                        entity_ref['entity_type'] = actual_type
                        total_replacements += 1
                        replacements_by_type[f"{entity_type}→{actual_type}"] = \
                            replacements_by_type.get(f"{entity_type}→{actual_type}", 0) + 1
                else:
                    # Track unmatched for debugging
                    unmatched_entities.append((entity_type, proposed_name))

    # Write merged file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)

    # Print statistics
    print(f"\n✓ Merged file created: {output_path}")
    print(f"\nStatistics:")
    print(f"  Total replacements: {total_replacements}")
    print(f"\nReplacements by type:")
    for entity_type, count in sorted(replacements_by_type.items()):
        print(f"  {entity_type}: {count}")

    if unmatched_entities:
        print(f"\n⚠️  Unmatched entities ({len(unmatched_entities)}):")
        unique_unmatched = set(unmatched_entities)
        for entity_type, name in sorted(unique_unmatched):
            print(f"  {entity_type}: {name}")


def main():
    # File paths
    base_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes")
    case_name = "Abby-Sitgraves-MVA-7-13-2024"

    processed_path = base_dir / f"processed_{case_name}.json"
    review_path = base_dir / "reviews" / f"review_{case_name}.md"
    output_path = base_dir / f"merged_{case_name}.json"

    print(f"Processing: {case_name}")
    print(f"  Processed: {processed_path}")
    print(f"  Review: {review_path}")
    print(f"  Output: {output_path}")

    merge_entities(processed_path, review_path, output_path)


if __name__ == "__main__":
    main()
