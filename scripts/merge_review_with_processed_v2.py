#!/usr/bin/env python3
"""
Merge review file entities with processed episode file - Version 2 (Clean extraction).

This script properly extracts clean entity names without annotation text.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Import KNOWN_MAPPINGS from generate_review_docs
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "roscoe" / "scripts"))
try:
    from generate_review_docs import KNOWN_MAPPINGS, IGNORE_ENTITIES
except ImportError:
    print("⚠️  Could not import KNOWN_MAPPINGS - using empty dict")
    KNOWN_MAPPINGS = {}
    IGNORE_ENTITIES = set()


def parse_review_file(review_path: Path) -> Dict[str, Dict[str, Tuple[str, str]]]:
    """
    Parse review file to extract entity mappings.

    Returns:
        Dict mapping entity_type -> {proposed_name -> (actual_name, actual_type)}

    Handles formats:
    1. - [ ] Name — *✓ MATCHES: ActualName*
    2. - [ ] Name — *✓ MATCHES: ActualName (notes)*
    3. - [ ] Name — *✓ MATCHES: ActualName (→ TYPE, not ...)*
    4. - [ ] Name — *✓ MATCHES: ActualName (WHALEY STAFF → should be CaseManager)*
    """
    mappings: Dict[str, Dict[str, Tuple[str, str]]] = {}

    with open(review_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by entity type sections
    sections = re.split(r'### ([A-Za-z]+) \(\d+ consolidated\)', content)

    for i in range(1, len(sections), 2):
        entity_type = sections[i]
        section_content = sections[i + 1] if i + 1 < len(sections) else ""

        if entity_type not in mappings:
            mappings[entity_type] = {}

        lines = section_content.split('\n')
        current_proposed = None

        for line in lines:
            # Match main entity line: - [ ] ProposedName — *✓ MATCHES: ActualName ...*
            match = re.match(r'- \[ \] (.+?) — \*✓ MATCHES: (.+?)\*', line)
            if match:
                proposed_name = match.group(1).strip()
                match_info = match.group(2).strip()

                # Extract CLEAN actual name and type from match_info
                actual_name, actual_type = extract_clean_entity(match_info, entity_type)

                mappings[entity_type][proposed_name] = (actual_name, actual_type)
                current_proposed = proposed_name

            # Handle variant lines (↳ _variant_)
            elif line.strip().startswith('↳ _') and current_proposed:
                variant = line.strip()[3:-1]  # Remove "↳ _" and trailing "_"
                if current_proposed in mappings[entity_type]:
                    mappings[entity_type][variant] = mappings[entity_type][current_proposed]

    return mappings


def extract_clean_entity(match_info: str, default_type: str) -> Tuple[str, str]:
    """
    Extract clean entity name and type from match info.

    Examples:
    - "Bryce Koon (WHALEY ATTORNEY, not Attorney)" → ("Bryce Koon", "Attorney")
    - "Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)" → ("Sarena Tuttle", "CaseManager")
    - "Bryan Davenport (→ ATTORNEY, not law firm)" → ("Bryan Davenport", "Attorney")
    - "Jefferson County Circuit Court, Division II (Judge: Annie O'Connell)" → ("Jefferson County Circuit Court, Division II", "Court")
    - "Blackburn Domene & Burchett, PLLC (alias: BDB Law)" → ("Blackburn Domene & Burchett, PLLC", default_type)
    - "ActualName" → ("ActualName", default_type)
    """
    actual_type = default_type

    # Check for type override: "... → should be NewType"
    type_override = re.search(r'→ should be (\w+)', match_info)
    if type_override:
        actual_type = type_override.group(1)

    # Check for type correction: "... → TYPE, not ..."
    type_correction = re.search(r'→ ([A-Z]+),', match_info)
    if type_correction:
        actual_type = type_correction.group(1).title()

    # Extract name (everything before the first parenthesis, or whole string if no parens)
    name_match = re.match(r'([^(]+)', match_info)
    if name_match:
        actual_name = name_match.group(1).strip()
    else:
        actual_name = match_info

    return actual_name, actual_type


def should_ignore_entity(entity_type: str, entity_name: str, review_content: str) -> bool:
    """Check if entity should be ignored based on IGNORE_ENTITIES set."""
    return entity_name in IGNORE_ENTITIES


def merge_entities(processed_path: Path, review_path: Path, output_path: Path):
    """Merge entities from review file into processed file."""

    # Load processed JSON
    with open(processed_path, 'r', encoding='utf-8') as f:
        processed_data = json.load(f)

    # Load review file content for ignore checking
    with open(review_path, 'r', encoding='utf-8') as f:
        review_content = f.read()

    # Parse entity mappings
    entity_mappings = parse_review_file(review_path)

    # Statistics
    stats = {
        'total_replacements': 0,
        'by_type': {},
        'unmatched': [],
        'ignored': [],
        'episodes_processed': 0
    }

    # Process each episode
    for episode in processed_data.get('episodes', []):
        stats['episodes_processed'] += 1

        if 'proposed_relationships' not in episode:
            continue

        for rel_type, entities in episode['proposed_relationships'].items():
            if not isinstance(entities, list):
                continue

            # Filter and update entities
            updated_entities = []

            for entity_ref in entities:
                if not isinstance(entity_ref, dict):
                    continue

                entity_type = entity_ref.get('entity_type')
                proposed_name = entity_ref.get('entity_name')

                if not entity_type or not proposed_name:
                    continue

                # Check if should be ignored
                if should_ignore_entity(entity_type, proposed_name, review_content):
                    stats['ignored'].append((entity_type, proposed_name))
                    continue  # Skip this entity

                # Try review file mappings first
                if entity_type in entity_mappings and proposed_name in entity_mappings[entity_type]:
                    actual_name, actual_type = entity_mappings[entity_type][proposed_name]

                    # Update entity
                    if entity_ref['entity_name'] != actual_name:
                        entity_ref['entity_name'] = actual_name
                        stats['total_replacements'] += 1
                        key = f"{entity_type}→{actual_name}"
                        stats['by_type'][key] = stats['by_type'].get(key, 0) + 1

                    if entity_ref['entity_type'] != actual_type:
                        old_type = entity_ref['entity_type']
                        entity_ref['entity_type'] = actual_type
                        stats['total_replacements'] += 1
                        key = f"{old_type}→{actual_type}"
                        stats['by_type'][key] = stats['by_type'].get(key, 0) + 1

                    updated_entities.append(entity_ref)

                # Fallback: Try KNOWN_MAPPINGS for unmatched entities
                elif proposed_name in KNOWN_MAPPINGS:
                    actual_name = KNOWN_MAPPINGS[proposed_name]
                    entity_ref['entity_name'] = actual_name
                    stats['total_replacements'] += 1
                    key = f"KNOWN_MAP→{actual_name}"
                    stats['by_type'][key] = stats['by_type'].get(key, 0) + 1
                    updated_entities.append(entity_ref)

                else:
                    # Keep unmatched (but track for reporting)
                    stats['unmatched'].append((entity_type, proposed_name))
                    updated_entities.append(entity_ref)

            # Update episode with filtered entities
            episode['proposed_relationships'][rel_type] = updated_entities

    # Write merged file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)

    # Print statistics
    print(f"\n✓ Merged file created: {output_path}")
    print(f"\nStatistics:")
    print(f"  Episodes processed: {stats['episodes_processed']}")
    print(f"  Total replacements: {stats['total_replacements']}")
    print(f"  Entities ignored: {len(set(stats['ignored']))}")

    print(f"\n🔄 Sample Replacements:")
    for key, count in sorted(stats['by_type'].items())[:10]:
        print(f"  {key}: {count}")

    if stats['ignored']:
        unique_ignored = set(stats['ignored'])
        print(f"\n🚫 Ignored entities ({len(unique_ignored)}):")
        for entity_type, name in sorted(unique_ignored)[:10]:
            print(f"  {entity_type}: {name}")

    if stats['unmatched']:
        unique_unmatched = set(stats['unmatched'])
        print(f"\n⚠️  Unmatched entities ({len(unique_unmatched)}):")
        for entity_type, name in sorted(unique_unmatched)[:15]:
            print(f"  {entity_type}: {name}")


def main():
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
