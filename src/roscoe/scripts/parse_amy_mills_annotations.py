#!/usr/bin/env python3
"""
Parse annotations from Amy Mills review and create entity cards.

Reads user annotations like:
- "Add as attorney"
- "Add as mediator"
- "Works at Ward, Hocker, and Thornton"
- "Context"
- "Ignore"

Creates entity JSON files based on annotations.
"""

import re
import json
from pathlib import Path
from collections import defaultdict


def parse_review_annotations(review_file: Path) -> dict:
    """
    Parse user annotations from review file.

    Returns: dict with structure:
    {
      "attorneys": [{name, firm, phone, email, ...}],
      "mediators": [{name, firm, ...}],
      "courts": [{name, ...}],
      "defendants": [{name, ...}],
      "ignore": [list of entity names to ignore]
    }
    """
    with open(review_file) as f:
        content = f.read()

    result = {
        "attorneys": [],
        "mediators": [],
        "courts": [],
        "defendants": [],
        "organizations": [],
        "lawfirms": [],
        "ignore": [],
        "context_requested": []
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

        annotation_lower = annotation.lower()

        # Check for "ignore"
        if 'ignore' in annotation_lower:
            result["ignore"].append(entity_name)
            continue

        # Check for "context"
        if 'context' in annotation_lower:
            result["context_requested"].append(entity_name)

        # Parse "Add as attorney" or "attorney" annotations
        if re.search(r'\b(add as )?(an? )?attorney\b', annotation_lower):
            entity = {"name": entity_name}

            # Check for law firm mention
            firm_match = re.search(r'works? (at|for|with) ([A-Za-z, &]+?)(?:\.|$)', annotation, re.IGNORECASE)
            if firm_match:
                firm_name = firm_match.group(2).strip()
                # Clean up firm name
                firm_name = re.sub(r'\s+and\s+', ' & ', firm_name, flags=re.IGNORECASE)
                entity["firm"] = firm_name

            result["attorneys"].append(entity)

        # Parse "Add as mediator"
        elif re.search(r'\b(add as )?(a )?mediator\b', annotation_lower):
            entity = {"name": entity_name}
            result["mediators"].append(entity)

        # Parse court additions
        elif re.search(r'add.*circuit court|county.*circuit court', annotation_lower):
            entity = {"name": entity_name}
            result["courts"].append(entity)

        # Parse defendant additions
        elif re.search(r'\bdefendant\b', annotation_lower):
            entity = {"name": entity_name}
            # Check if also organization
            if re.search(r'\borganization\b', annotation_lower):
                result["organizations"].append({"name": entity_name})
            result["defendants"].append(entity)

    return result


def main():
    review_file = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/reviews/review_Amy-Mills-Premise-04-26-2019.md")

    print("=" * 80)
    print("PARSING AMY MILLS ANNOTATIONS")
    print("=" * 80)
    print()

    annotations = parse_review_annotations(review_file)

    print(f"Attorneys to add: {len(annotations['attorneys'])}")
    for atty in annotations["attorneys"]:
        firm = atty.get('firm', 'Unknown')
        print(f"  - {atty['name']} (Firm: {firm})")

    print()
    print(f"Mediators to add: {len(annotations['mediators'])}")
    for med in annotations["mediators"]:
        print(f"  - {med['name']}")

    print()
    print(f"Courts to add: {len(annotations['courts'])}")
    for court in annotations["courts"]:
        print(f"  - {court['name']}")

    print()
    print(f"Defendants to add: {len(annotations['defendants'])}")
    for defendant in annotations["defendants"]:
        print(f"  - {defendant['name']}")

    print()
    print(f"Entities to ignore: {len(annotations['ignore'])}")
    for ign in annotations["ignore"][:10]:
        print(f"  - {ign}")
    if len(annotations["ignore"]) > 10:
        print(f"  ... and {len(annotations['ignore']) - 10} more")

    print()
    print(f"Context requested for: {len(annotations['context_requested'])}")
    for ctx in annotations["context_requested"][:10]:
        print(f"  - {ctx}")

    # Save results
    output_file = review_file.parent / "Amy-Mills-parsed-annotations.json"
    with open(output_file, 'w') as f:
        json.dump(annotations, f, indent=2)

    print()
    print(f"✅ Saved to: {output_file}")


if __name__ == "__main__":
    main()
