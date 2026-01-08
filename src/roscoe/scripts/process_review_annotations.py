#!/usr/bin/env python3
"""
Process user annotations from review documents.

Parses annotations like:
- "Ignore" → add to ignore list
- "Add as attorney" → create attorney entity
- "Context" → add episode context
- "Works at X" → track law firm relationship
"""

import re
import json
from pathlib import Path
from collections import defaultdict


def parse_annotation(entity_name: str, annotation: str) -> dict:
    """
    Parse a single annotation and return action to take.

    Returns: {
        "action": "ignore"|"add"|"context"|"none",
        "entity_type": "Attorney"|"Mediator"|etc (if add),
        "attributes": {...} (if add),
        "notes": "..." (additional info)
    }
    """
    if not annotation:
        return {"action": "none"}

    annotation_lower = annotation.lower()

    # Check for ignore
    if 'ignore' in annotation_lower:
        return {"action": "ignore"}

    # Check for context request
    has_context = 'context' in annotation_lower

    # Check for "add" instructions
    result = {"action": "none", "context_requested": has_context}

    # Add as attorney
    if re.search(r'\b(add as )?(an? )?attorney\b', annotation_lower):
        result["action"] = "add"
        result["entity_type"] = "Attorney"
        result["attributes"] = {}

        # Extract law firm
        firm_match = re.search(r'works? (at|for|with) ([A-Za-z, &.]+?)(?:\.|$|works)', annotation, re.IGNORECASE)
        if firm_match:
            firm_name = firm_match.group(2).strip()
            firm_name = re.sub(r'\s+and\s+', ' & ', firm_name, flags=re.IGNORECASE)
            result["attributes"]["firm_name"] = firm_name

        return result

    # Add as mediator
    if re.search(r'\b(add as )?(a )?mediator\b', annotation_lower):
        result["action"] = "add"
        result["entity_type"] = "Mediator"
        result["attributes"] = {}
        return result

    # Add as court
    if re.search(r'add.*circuit court|add.*district court|county.*circuit court', annotation_lower):
        result["action"] = "add"
        result["entity_type"] = "Court"
        result["attributes"] = {}
        return result

    # Add as defendant
    if 'defendant' in annotation_lower and 'add' in annotation_lower:
        result["action"] = "add"
        result["entity_type"] = "Defendant"
        result["attributes"] = {}

        # Check if also organization
        if 'organization' in annotation_lower:
            result["also_organization"] = True

        return result

    # Add as organization
    if re.search(r'add.*(to|as) organization', annotation_lower):
        result["action"] = "add"
        result["entity_type"] = "Organization"
        result["attributes"] = {}
        return result

    # Add as vendor
    if re.search(r'add.*(to|as) vendor', annotation_lower):
        result["action"] = "add"
        result["entity_type"] = "Vendor"
        result["attributes"] = {}
        return result

    # Check for merge/consolidation notes
    if any(word in annotation_lower for word in ['same', 'match', 'combine', 'merge']):
        result["notes"] = annotation
        if has_context:
            result["action"] = "context"

    # Default: just context if requested
    if has_context and result["action"] == "none":
        result["action"] = "context"

    return result


def extract_annotations_from_review(review_file: Path) -> dict:
    """
    Extract all user annotations from a review file.

    Returns: dict with categorized annotations
    """
    with open(review_file) as f:
        content = f.read()

    results = {
        "ignore": [],
        "add": defaultdict(list),  # entity_type -> [entities]
        "context": [],
        "notes": []
    }

    # Find all entity lines with annotations
    # Pattern: - [ ] Name — *status* annotation
    pattern = r'- \[ \] (?:\*\*)?([^*—]+?)(?:\*\*)? — \*[^*]+\*\s*(.+?)(?=\n|$)'
    matches = re.findall(pattern, content, re.MULTILINE)

    for entity_name, annotation in matches:
        entity_name = entity_name.strip()
        annotation = annotation.strip()

        if not annotation:
            continue

        parsed = parse_annotation(entity_name, annotation)

        if parsed["action"] == "ignore":
            results["ignore"].append(entity_name)

        elif parsed["action"] == "add":
            entity_card = {
                "name": entity_name,
                "attributes": parsed.get("attributes", {}),
                "notes": annotation
            }
            if "also_organization" in parsed:
                entity_card["also_organization"] = True

            results["add"][parsed["entity_type"]].append(entity_card)

        elif parsed["action"] == "context":
            results["context"].append(entity_name)

        if "notes" in parsed:
            results["notes"].append(f"{entity_name}: {parsed['notes']}")

    return results


def main():
    reviews_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/reviews")

    # Files to process (Abigail-Whaley to Ashlee-Williams)
    review_files = [
        "review_Abigail-Whaley-MVA-10-24-2024.md",
        "review_Alma-Cristobal-MVA-2-15-2024.md",
        "review_Amy-Mills-Premise-04-26-2019.md",
        "review_Anella-Noble-MVA-01-03-2021.md",
        "review_Antonio-Lopez-MVA-11-14-2025.md",
        "review_Ashlee-Williams-MVA-08-29-2023.md"
    ]

    print("=" * 80)
    print("PROCESSING REVIEW ANNOTATIONS")
    print("=" * 80)
    print()

    all_ignore = set()
    all_add = defaultdict(list)
    all_context = set()
    all_notes = []

    for filename in review_files:
        review_file = reviews_dir / filename
        if not review_file.exists():
            print(f"⚠️  Skipping {filename} (not found)")
            continue

        print(f"Processing {filename}...")
        annotations = extract_annotations_from_review(review_file)

        all_ignore.update(annotations["ignore"])
        for entity_type, entities in annotations["add"].items():
            all_add[entity_type].extend(entities)
        all_context.update(annotations["context"])
        all_notes.extend(annotations["notes"])

        print(f"  - Ignore: {len(annotations['ignore'])}")
        print(f"  - Add: {sum(len(v) for v in annotations['add'].values())}")
        print(f"  - Context: {len(annotations['context'])}")
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    print(f"Total entities to ignore: {len(all_ignore)}")
    for entity in sorted(all_ignore)[:20]:
        print(f"  - {entity}")
    if len(all_ignore) > 20:
        print(f"  ... and {len(all_ignore) - 20} more")

    print()
    print("Entities to add:")
    for entity_type, entities in sorted(all_add.items()):
        print(f"  {entity_type}: {len(entities)}")
        for ent in entities[:5]:
            print(f"    - {ent['name']}")
        if len(entities) > 5:
            print(f"    ... and {len(entities) - 5} more")

    print()
    print(f"Context requested for: {len(all_context)} entities")
    for entity in sorted(all_context)[:10]:
        print(f"  - {entity}")

    # Save results
    output_file = reviews_dir / "annotation_processing_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "ignore": sorted(all_ignore),
            "add": dict(all_add),
            "context": sorted(all_context),
            "notes": all_notes
        }, f, indent=2)

    print()
    print(f"✅ Saved to: {output_file}")


if __name__ == "__main__":
    main()
