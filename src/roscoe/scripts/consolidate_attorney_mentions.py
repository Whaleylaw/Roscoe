#!/usr/bin/env python3
"""
Consolidate Duplicate Attorney Mentions and Fix Staff Misclassifications

Analyzes all review documents to find:
1. Duplicate attorneys (same person, different name formats)
2. Whaley Law Firm staff incorrectly marked as Attorney

Creates mapping file for corrections.

Usage:
    python -m roscoe.scripts.consolidate_attorney_mentions
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from rapidfuzz import fuzz


# Known Whaley Law Firm staff (should be CaseManager, not Attorney)
WHALEY_STAFF = {
    "Sarena Tuttle": "paralegal",
    "Justin Chumbley": "case_manager",
    "Faye Gaither": "case_manager",
    "Jessa Galosmo": "case_manager",
    "Jessa": "case_manager",  # Common short form
    "Aries Penaflor": "case_manager",
    "Jessica Bottorff": "case_manager",
    "Aaron G. Whaley": "attorney",  # Keep as attorney
    "Aaron Whaley": "attorney",
    "Aaron Gregory Whaley": "attorney",
    "Bryce Koon": "attorney",
    "W. Bryce Koon": "attorney",
}


def normalize_attorney_name(name: str) -> str:
    """Normalize attorney name for comparison."""
    # Remove titles
    name = re.sub(r',?\s*(Esq\.?|Esquire|Jr\.?|Sr\.?|III|II)$', '', name, flags=re.IGNORECASE)
    # Remove middle initials for comparison
    name = re.sub(r'\s+[A-Z]\.?\s+', ' ', name)
    # Lowercase for comparison
    return name.strip().lower()


def are_likely_same_person(name1: str, name2: str) -> tuple[bool, int]:
    """Check if two attorney names likely refer to same person."""
    norm1 = normalize_attorney_name(name1)
    norm2 = normalize_attorney_name(name2)

    # Exact match after normalization
    if norm1 == norm2:
        return True, 100

    # Fuzzy match (high threshold)
    score = fuzz.ratio(norm1, norm2)
    if score >= 85:
        return True, score

    # Check if one is subset of other (e.g., "Sam Leifert" vs "Samuel Robert Leifert")
    if norm1 in norm2 or norm2 in norm1:
        # But make sure it's substantial (not just first name)
        if len(norm1) > 5 and len(norm2) > 5:
            return True, 90

    return False, score


def load_all_attorney_mentions(reviews_dir: Path) -> dict:
    """Load all attorney mentions from review documents."""
    all_mentions = defaultdict(set)  # case_name -> set of attorney names

    for review_file in reviews_dir.glob("review_*.md"):
        case_name = review_file.stem.replace('review_', '')

        with open(review_file) as f:
            content = f.read()

        # Extract attorney mentions (looking for ### Attorney section)
        attorney_section = re.search(r'### Attorney \(\d+ unique\)(.*?)(?=###|---|\Z)', content, re.DOTALL)

        if attorney_section:
            section_text = attorney_section.group(1)
            # Extract names from "- [ ] Name — *status*" format
            for match in re.finditer(r'- \[ \] (.+?) — \*', section_text):
                attorney_name = match.group(1).strip()
                all_mentions[case_name].add(attorney_name)

    return all_mentions


def find_duplicates_and_staff(all_mentions: dict) -> dict:
    """Find duplicate names and staff misclassifications."""
    results = {
        "duplicates": {},  # canonical_name -> [variants]
        "staff_misclassified": {},  # mentioned_name -> correct_type
        "stats": {}
    }

    # Find Whaley staff in attorney mentions
    for case_name, attorneys in all_mentions.items():
        for atty_name in attorneys:
            # Check if this is Whaley staff
            for staff_name, staff_role in WHALEY_STAFF.items():
                if fuzz.ratio(atty_name.lower(), staff_name.lower()) >= 85:
                    results["staff_misclassified"][atty_name] = {
                        "correct_name": staff_name,
                        "correct_type": "CaseManager" if staff_role != "attorney" else "Attorney",
                        "role": staff_role
                    }
                    break

    # Find duplicates (across all cases)
    all_unique = set()
    for attorneys in all_mentions.values():
        all_unique.update(attorneys)

    all_unique = sorted(all_unique)
    processed = set()

    for i, name1 in enumerate(all_unique):
        if name1 in processed:
            continue

        # Find all names that match this one
        matches = [name1]

        for name2 in all_unique[i+1:]:
            if name2 in processed:
                continue

            is_same, score = are_likely_same_person(name1, name2)
            if is_same:
                matches.append(name2)
                processed.add(name2)

        if len(matches) > 1:
            # Pick canonical name (longest version usually has full name)
            canonical = max(matches, key=len)
            results["duplicates"][canonical] = sorted(matches)

        processed.add(name1)

    # Stats
    results["stats"] = {
        "total_unique_mentions": len(all_unique),
        "duplicate_sets": len(results["duplicates"]),
        "staff_misclassified": len(results["staff_misclassified"]),
        "total_corrections": len(results["duplicates"]) + len(results["staff_misclassified"])
    }

    return results


def main():
    reviews_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/reviews")

    print("=" * 70)
    print("ATTORNEY MENTION CONSOLIDATION")
    print("=" * 70)
    print(f"Reviews directory: {reviews_dir}")
    print()

    # Load all mentions
    print("Loading attorney mentions from review documents...")
    all_mentions = load_all_attorney_mentions(reviews_dir)

    print(f"Found attorney mentions in {len(all_mentions)} cases")
    print()

    # Find duplicates and staff
    print("Analyzing for duplicates and staff misclassifications...")
    results = find_duplicates_and_staff(all_mentions)

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total unique attorney mentions: {results['stats']['total_unique_mentions']}")
    print(f"Duplicate sets found: {results['stats']['duplicate_sets']}")
    print(f"Staff misclassified: {results['stats']['staff_misclassified']}")
    print()

    if results["staff_misclassified"]:
        print("STAFF MISCLASSIFIED AS ATTORNEY:")
        for mention, correction in results["staff_misclassified"].items():
            print(f"  - {mention}")
            print(f"    → Should be: {correction['correct_name']} ({correction['correct_type']} - {correction['role']})")

    print()

    if results["duplicates"]:
        print(f"DUPLICATE ATTORNEY NAMES ({len(results['duplicates'])} sets):")
        for canonical, variants in results["duplicates"].items():
            if len(variants) > 1:
                print(f"\n  Canonical: {canonical}")
                for variant in variants:
                    if variant != canonical:
                        print(f"    ← {variant}")

    # Save mapping file
    output_file = reviews_dir / "attorney_mappings.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print(f"✅ Saved mapping file: {output_file}")


if __name__ == "__main__":
    main()
