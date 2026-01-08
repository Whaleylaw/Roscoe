#!/usr/bin/env python3
"""
Apply user annotations to review files.

Reads annotations, takes action, updates review to show action taken.
"""

import re
import json
from pathlib import Path
from collections import defaultdict


ENTITIES_DIR = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities")


def load_entity_file(entity_type: str) -> list:
    """Load entity JSON file."""
    type_to_file = {
        "Attorney": "attorneys.json",
        "Mediator": "mediators.json",
        "Witness": "witnesses.json",
        "Defendant": "defendants.json",
        "Organization": "organizations.json",
        "Vendor": "vendors.json",
        "Expert": "experts.json",
        "CourtClerk": "court_clerks.json",
        "LawFirm": "lawfirms.json",
    }

    filename = type_to_file.get(entity_type)
    if not filename:
        return []

    filepath = ENTITIES_DIR / filename
    if not filepath.exists():
        return []

    with open(filepath) as f:
        return json.load(f)


def save_entity_file(entity_type: str, data: list):
    """Save entity JSON file."""
    type_to_file = {
        "Attorney": "attorneys.json",
        "Mediator": "mediators.json",
        "Witness": "witnesses.json",
        "Defendant": "defendants.json",
        "Organization": "organizations.json",
        "Vendor": "vendors.json",
        "Expert": "experts.json",
        "CourtClerk": "court_clerks.json",
        "LawFirm": "lawfirms.json",
    }

    filename = type_to_file.get(entity_type)
    if not filename:
        return

    filepath = ENTITIES_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def process_annotation_line(line: str, case_name: str) -> str:
    """
    Process a single entity line with annotation.

    Returns: updated line with annotation replaced by action taken
    """
    # Parse entity line
    # Pattern: - [ ] Name — *status* annotation
    match = re.match(r'(- \[ \] (?:\*\*)?([^*—]+?)(?:\*\*)? — \*[^*]+\*)\s*(.+)', line)
    if not match:
        return line

    entity_prefix = match.group(1)
    entity_name = match.group(2).strip()
    annotation = match.group(3).strip()

    if not annotation:
        return line

    annotation_lower = annotation.lower()
    new_line = entity_prefix  # Start with original

    # Process "Ignore"
    if 'ignore' in annotation_lower and not 'don\'t' in annotation_lower:
        return entity_prefix + " ✓ IGNORED"

    # Process "Add as attorney"
    if re.search(r'add (as )?(an? )?attorney', annotation_lower):
        # Add to attorneys.json
        attorneys = load_entity_file("Attorney")
        existing_names = {a['name'] for a in attorneys}

        if entity_name not in existing_names:
            # Extract firm from annotation
            firm_name = ""
            firm_match = re.search(r'works? (at|for|with) ([A-Za-z, &.]+?)\.', annotation, re.IGNORECASE)
            if firm_match:
                firm_name = firm_match.group(2).strip()

            new_attorney = {
                "card_type": "entity",
                "entity_type": "Attorney",
                "name": entity_name,
                "attributes": {
                    "role": "defense_counsel" if "defense" in annotation_lower else "plaintiff_counsel" if "plaintiff" not in annotation_lower or "not defense" in annotation_lower else "defense_counsel",
                    "firm_name": firm_name,
                    "phone": "",
                    "email": ""
                },
                "source_id": "annotation_processing",
                "source_file": case_name
            }

            attorneys.append(new_attorney)
            save_entity_file("Attorney", attorneys)
            return entity_prefix + f" ✓ ADDED as Attorney (firm: {firm_name if firm_name else 'N/A'})"
        else:
            return entity_prefix + " ✓ Already added"

    # Process "Add as mediator"
    if re.search(r'add as (a )?mediator', annotation_lower):
        mediators = load_entity_file("Mediator")
        existing_names = {m['name'] for m in mediators}

        if entity_name not in existing_names:
            new_mediator = {
                "card_type": "entity",
                "entity_type": "Mediator",
                "name": entity_name,
                "attributes": {
                    "credentials": "Retired Judge" if "Hon." in entity_name or "Judge" in entity_name else "",
                    "phone": "",
                    "email": ""
                },
                "source_id": "annotation_processing",
                "source_file": case_name
            }

            mediators.append(new_mediator)
            save_entity_file("Mediator", mediators)
            return entity_prefix + " ✓ ADDED as Mediator"
        else:
            return entity_prefix + " ✓ Already added"

    # Process "Add as witness"
    if re.search(r'(add as )?(a )?witness', annotation_lower):
        witnesses = load_entity_file("Witness")
        existing_names = {w['name'] for w in witnesses}

        if entity_name not in existing_names:
            new_witness = {
                "card_type": "entity",
                "entity_type": "Witness",
                "name": entity_name,
                "attributes": {
                    "witness_type": "fact_witness",
                    "phone": "",
                    "email": ""
                },
                "source_id": "annotation_processing",
                "source_file": case_name
            }

            witnesses.append(new_witness)
            save_entity_file("Witness", witnesses)
            return entity_prefix + " ✓ ADDED as Witness"
        else:
            return entity_prefix + " ✓ Already added"

    # Process "She's a clerk"
    if 'clerk' in annotation_lower and 'court' in annotation_lower:
        clerks = load_entity_file("CourtClerk")
        existing_names = {c['name'] for c in clerks}

        if entity_name not in existing_names:
            court_match = re.search(r'(for|at) ([A-Za-z ]+(?:Circuit|District) Court)', annotation, re.IGNORECASE)
            court_name = court_match.group(2) if court_match else ""

            new_clerk = {
                "card_type": "entity",
                "entity_type": "CourtClerk",
                "name": entity_name,
                "attributes": {
                    "clerk_type": "circuit" if "circuit" in annotation_lower else "district",
                    "court_name": court_name,
                    "phone": "",
                    "email": ""
                },
                "source_id": "annotation_processing",
                "source_file": case_name
            }

            clerks.append(new_clerk)
            save_entity_file("CourtClerk", clerks)
            return entity_prefix + f" ✓ ADDED as CourtClerk ({court_name if court_name else 'N/A'})"

    # Keep annotation if not processed
    return line


def process_review_file(review_file: Path) -> dict:
    """Process all annotations in a review file and update it."""
    case_name = review_file.stem.replace('review_', '')

    with open(review_file) as f:
        lines = f.readlines()

    updated_lines = []
    actions = {"added": 0, "ignored": 0, "processed": 0}

    for line in lines:
        if line.strip().startswith('- [ ]'):
            updated_line = process_annotation_line(line.rstrip('\n'), case_name)
            if '✓ ADDED' in updated_line:
                actions["added"] += 1
            elif '✓ IGNORED' in updated_line:
                actions["ignored"] += 1
            elif '✓ PROCESSED' in updated_line:
                actions["processed"] += 1
            updated_lines.append(updated_line + '\n')
        else:
            updated_lines.append(line)

    # Save updated review
    with open(review_file, 'w') as f:
        f.writelines(updated_lines)

    return actions


def main():
    reviews_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/reviews")

    review_files = [
        "review_Abby-Sitgraves-MVA-7-13-2024.md",
        "review_Abigail-Whaley-MVA-10-24-2024.md",
        "review_Alma-Cristobal-MVA-2-15-2024.md",
        "review_Amy-Mills-Premise-04-26-2019.md",
        "review_Anella-Noble-MVA-01-03-2021.md",
        "review_Antonio-Lopez-MVA-11-14-2025.md",
        "review_Ashlee-Williams-MVA-08-29-2023.md"
    ]

    print("=" * 80)
    print("APPLYING USER ANNOTATIONS")
    print("=" * 80)
    print()

    total_actions = {"added": 0, "ignored": 0, "processed": 0}

    for filename in review_files:
        review_file = reviews_dir / filename
        if not review_file.exists():
            print(f"⚠️  Skipping {filename}")
            continue

        print(f"Processing {filename}...")
        actions = process_review_file(review_file)

        total_actions["added"] += actions["added"]
        total_actions["ignored"] += actions["ignored"]
        total_actions["processed"] += actions["processed"]

        print(f"  ✓ Added: {actions['added']}, Ignored: {actions['ignored']}, Processed: {actions['processed']}")

    print()
    print("=" * 80)
    print("TOTAL")
    print("=" * 80)
    print(f"  Added: {total_actions['added']}")
    print(f"  Ignored: {total_actions['ignored']}")
    print(f"  Processed: {total_actions['processed']}")
    print()
    print("✅ All annotations applied to entity files and review documents updated")


if __name__ == "__main__":
    main()
