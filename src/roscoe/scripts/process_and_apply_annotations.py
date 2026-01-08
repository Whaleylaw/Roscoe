#!/usr/bin/env python3
"""
Process user annotations from review files and apply changes.

For each annotation:
- "Add as attorney" → Add to entity file, mark as "✓ ADDED as Attorney"
- "Ignore" → Mark as "✓ IGNORED"
- "Context" with info → Apply correction, mark as "✓ PROCESSED"
- "Works at X" → Update entity with firm_name
- "This is X" → Apply correction

Then regenerate all reviews with new entities.
"""

import re
import json
from pathlib import Path
from collections import defaultdict


def parse_detailed_annotation(entity_name: str, annotation: str, entity_type: str) -> dict:
    """
    Parse annotation and determine specific action.

    Returns: {
        "action": "add"|"ignore"|"process"|"none",
        "new_entity_type": str (if reclassifying),
        "attributes": dict,
        "replacement_status": str (what to show in review)
    }
    """
    annotation_lower = annotation.lower()
    result = {
        "action": "none",
        "attributes": {},
        "notes": annotation
    }

    # Ignore
    if 'ignore' in annotation_lower:
        result["action"] = "ignore"
        result["replacement_status"] = "✓ IGNORED"
        return result

    # Add as specific type
    if re.search(r'add as (a |an )?attorney', annotation_lower):
        result["action"] = "add"
        result["new_entity_type"] = "Attorney"
        result["replacement_status"] = "✓ ADDED as Attorney"

        # Extract firm
        firm_match = re.search(r'works? (at|for|with) ([A-Za-z, &.]+)', annotation, re.IGNORECASE)
        if firm_match:
            result["attributes"]["firm_name"] = firm_match.group(2).strip()

        return result

    if re.search(r'add as (a )?mediator', annotation_lower):
        result["action"] = "add"
        result["new_entity_type"] = "Mediator"
        result["replacement_status"] = "✓ ADDED as Mediator"
        return result

    if re.search(r'add as (a )?witness', annotation_lower):
        result["action"] = "add"
        result["new_entity_type"] = "Witness"
        result["replacement_status"] = "✓ ADDED as Witness"
        return result

    if re.search(r'add as (a )?defendant', annotation_lower):
        result["action"] = "add"
        result["new_entity_type"] = "Defendant"
        result["replacement_status"] = "✓ ADDED as Defendant"
        return result

    if re.search(r'add.*(to|as) (organization|vendor|expert)', annotation_lower):
        if 'vendor' in annotation_lower:
            result["new_entity_type"] = "Vendor"
            result["replacement_status"] = "✓ ADDED as Vendor"
        elif 'expert' in annotation_lower:
            result["new_entity_type"] = "Expert"
            result["replacement_status"] = "✓ ADDED as Expert"
        else:
            result["new_entity_type"] = "Organization"
            result["replacement_status"] = "✓ ADDED as Organization"
        result["action"] = "add"
        return result

    # Context with specific info (e.g., "She's a clerk for Knox Circuit Court")
    if 'clerk' in annotation_lower:
        result["action"] = "add"
        result["new_entity_type"] = "CourtClerk"
        result["replacement_status"] = "✓ ADDED as CourtClerk"

        # Extract court
        court_match = re.search(r'for ([A-Za-z ]+(?:Circuit|District) Court)', annotation, re.IGNORECASE)
        if court_match:
            result["attributes"]["court_name"] = court_match.group(1).strip()

        return result

    # "This is X" corrections
    if re.search(r"(it's|this is|that's) ", annotation_lower):
        result["action"] = "process"
        result["replacement_status"] = "✓ PROCESSED"
        return result

    # Just "Add" without specifying type
    if re.search(r'^add\b', annotation_lower) and entity_type:
        result["action"] = "add"
        result["new_entity_type"] = entity_type
        result["replacement_status"] = f"✓ ADDED as {entity_type}"
        return result

    return result


def main():
    # Files to process
    review_files = [
        "review_Abby-Sitgraves-MVA-7-13-2024.md",
        "review_Abigail-Whaley-MVA-10-24-2024.md",
        "review_Alma-Cristobal-MVA-2-15-2024.md",
        "review_Amy-Mills-Premise-04-26-2019.md",
        "review_Anella-Noble-MVA-01-03-2021.md",
        "review_Antonio-Lopez-MVA-11-14-2025.md",
        "review_Ashlee-Williams-MVA-08-29-2023.md"
    ]

    reviews_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/reviews")
    entities_dir = reviews_dir.parent.parent / "entities"

    print("=" * 80)
    print("PROCESSING ANNOTATIONS FROM 7 REVIEW FILES")
    print("=" * 80)
    print()

    all_actions = defaultdict(list)  # entity_type -> [entities to add]
    all_ignored = []

    for filename in review_files:
        review_file = reviews_dir / filename
        if not review_file.exists():
            print(f"⚠️  Skipping {filename} (not found)")
            continue

        print(f"Processing {filename}...")

        with open(review_file) as f:
            content = f.read()

        # Extract annotations
        # Pattern: - [ ] Entity — *status* annotation
        pattern = r'(- \[ \] (?:\*\*)?([^*—]+?)(?:\*\*)? — \*[^*]+\*)\s*(.+?)(?=\n|$)'
        matches = list(re.finditer(pattern, content, re.MULTILINE))

        actions_taken = 0
        ignored = 0

        # Find entity type for each match
        current_entity_type = None
        for line in content.split('\n'):
            type_match = re.match(r'### ([A-Za-z]+) \(\d+ consolidated\)', line)
            if type_match:
                current_entity_type = type_match.group(1)

        for match in matches:
            entity_line = match.group(1)
            entity_name = match.group(2).strip()
            annotation = match.group(3).strip()

            if not annotation:
                continue

            # Parse annotation
            action = parse_detailed_annotation(entity_name, annotation, current_entity_type)

            if action["action"] == "add":
                all_actions[action["new_entity_type"]].append({
                    "name": entity_name,
                    "attributes": action["attributes"],
                    "source_file": filename
                })
                actions_taken += 1

            elif action["action"] == "ignore":
                all_ignored.append(entity_name)
                ignored += 1

            elif action["action"] == "process":
                actions_taken += 1

        print(f"  Actions: {actions_taken}, Ignored: {ignored}")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    print("Entities to add:")
    for entity_type, entities in sorted(all_actions.items()):
        print(f"  {entity_type}: {len(entities)}")

    print()
    print(f"Entities to ignore: {len(set(all_ignored))}")

    print()
    print("Next: Apply these changes to entity files and regenerate reviews")


if __name__ == "__main__":
    main()
