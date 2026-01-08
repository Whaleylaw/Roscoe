#!/usr/bin/env python3
"""
Apply manual consolidations to review documents.

Handles specific consolidations identified during review:
- Initials to full names (A. G. Whaley → Aaron G. Whaley)
- Nicknames (Greg Whaley → Aaron G. Whaley)
- Titles and variations (Mrs. Catron → Betsy R. Catron)
"""

from pathlib import Path
import json
import re
from collections import defaultdict
from roscoe.scripts.generate_review_docs import (
    load_global_entities,
    fuzzy_match_entity,
    check_whaley_staff,
    normalize_name,
    normalize_attorney_name
)
from roscoe.scripts.regenerate_all_reviews import (
    extract_entities_from_review,
    find_entity_context,
    regenerate_review
)

# Manual consolidation mappings
CONSOLIDATION_MAP = {
    # Aaron G. Whaley variants
    "A. G. Whaley": "Aaron G. Whaley",
    "AW": "Aaron G. Whaley",
    "Aaron": "Aaron G. Whaley",
    "Greg Whaley": "Aaron G. Whaley",

    # Betsy R. Catron variants
    "BK": "Betsy R. Catron",
    "Betsy": "Betsy R. Catron",
    "Mrs. Catron": "Betsy R. Catron",

    # Bryce Koon variants
    "Bryce Whaley": "Bryce Koon",

    # Thomas J. Knopf (Mediator) - will be reclassified
    "Hon. Thomas J. Knopf": "Hon. Thomas J. Knopf (Ret.)",
    "Hon. Thomas Knopf": "Hon. Thomas J. Knopf (Ret.)",
    "Hon. Judge Thomas Knopf": "Hon. Thomas J. Knopf (Ret.)",
    "Judge Knopf": "Hon. Thomas J. Knopf (Ret.)",
    "Knopf": "Hon. Thomas J. Knopf (Ret.)",
    "Thomas Knopf": "Hon. Thomas J. Knopf (Ret.)",

    # Doctor consolidations
    "Dr. Huff": "Dr. Wallace Huff",
    "Wallace L. Huff": "Dr. Wallace Huff",
    "Dr. Nazar": "Dr. Gregory Nazar",
    "Nazar": "Dr. Gregory Nazar",
    "Dr. Khalily": "Dr. Cyna Khalily",
    "Dr. Magone": "Dr. Kevin Magone, MD",
    "Dr. Manderino": "Dr. Lisa Manderino",
    "Dr. Orlando": "Marc Orlando",
}

# Entity type reclassifications
TYPE_CORRECTIONS = {
    "Hon. Thomas J. Knopf (Ret.)": ("Attorney", "Mediator"),  # From Attorney to Mediator
    "Thomas J. Knopf Mediation Services": ("Vendor", "Organization"),  # From Vendor to Organization
}

# Law firm consolidations (separate to avoid confusion)
LAWFIRM_CONSOLIDATIONS = {
    # WHT Law = Whaley Harrison & Thorne
    "canonical": "Whaley Harrison & Thorne, PLLC",
    "variants": [
        "WHT Law",
        "WHT Law (Vine Center)",
        "WHT Law (www.whtlaw.com)",
        "WHT Law (www.whtlaw.com / Vine Center)",
        "WHT Law Center",
        "WHT Law Firm",
        "Whaley Harrison & Thorne (WHT Law)",
        "www.whtlaw.com"
    ],
    "aliases": ["WHT Law"],
    "website": "www.whtlaw.com",
    "location": "Vine Center"
}

LAWFIRM_CONSOLIDATIONS_2 = {
    # Ward, Hocker & Thornton
    "canonical": "Ward, Hocker & Thornton, PLLC",
    "variants": [
        "Ward Hawker at Thornton"  # Hawker = typo for Hocker
    ]
}

# Knox Circuit Court consolidations
KNOX_COURT_VARIANTS = [
    "Knox",
    "Knox Cir II",
    "Knox Circuit Court",
    "Knox Circuit Court (Kentucky)",
    "Knox Circuit Court (Knox County, Kentucky)",
    "Knox Circuit Court, Division II",
    "Knox Circuit Court, Division II (Civil Action 20-CI-00112)",
    "Knox Circuit II",
    "Knox County",
    "Knox County Circuit Court",
    "Knox Division 2"
]


def apply_consolidation_to_review(review_file: Path, consolidation_map: dict) -> dict:
    """
    Apply consolidation mappings to a single review file.

    Returns: dict of changes made
    """
    changes = defaultdict(list)

    with open(review_file) as f:
        content = f.read()

    # Apply each consolidation
    for variant, canonical in consolidation_map.items():
        # Pattern: - [ ] variant — *status*
        pattern = re.escape(variant) + r'( — \*[^*]+\*)'
        matches = list(re.finditer(pattern, content))

        if matches:
            changes[canonical].append(variant)
            # Replace variant with canonical (preserve status)
            content = re.sub(pattern, canonical + r'\1', content)

    # Save updated review
    with open(review_file, 'w') as f:
        f.write(content)

    return changes


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=str, default="Amy-Mills-Premise-04-26-2019",
                       help='Case name to consolidate')
    args = parser.parse_args()

    reviews_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/reviews")
    review_file = reviews_dir / f"review_{args.case}.md"

    if not review_file.exists():
        print(f"❌ Review file not found: {review_file}")
        return

    print("=" * 80)
    print(f"APPLYING CONSOLIDATIONS: {args.case}")
    print("=" * 80)
    print()

    print("Applying consolidation mappings...")
    changes = apply_consolidation_to_review(review_file, CONSOLIDATION_MAP)

    if changes:
        print(f"\n✓ Consolidated {len(changes)} entities:")
        for canonical, variants in sorted(changes.items()):
            print(f"\n  {canonical}")
            for v in variants:
                print(f"    ← {v}")
    else:
        print("  No changes applied (variants already consolidated)")

    print()
    print(f"✅ Updated review: {review_file.name}")
    print()
    print("Next: Regenerate with regenerate_all_reviews.py to apply fuzzy matching")


if __name__ == "__main__":
    main()
