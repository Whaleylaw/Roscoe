#!/usr/bin/env python3
"""
Update entity JSON files to match new Graphiti schema.

Removes fields that are no longer in the schema:
- Case: total_medical_bills, total_expenses, total_liens, phase, case_summary, current_status, case_role
- Claims: insurance_notes
"""

import json
from pathlib import Path

ENTITIES_DIR = Path(__file__).parent / "entities"

def update_cases():
    """Update cases.json - remove computed fields."""
    cases_file = ENTITIES_DIR / "cases.json"
    with open(cases_file, 'r') as f:
        cases = json.load(f)

    fields_to_remove = [
        "total_medical_bills", "total_expenses", "total_liens",
        "phase", "case_summary", "current_status", "case_role"
    ]

    for case in cases:
        for field in fields_to_remove:
            case["attributes"].pop(field, None)

    with open(cases_file, 'w') as f:
        json.dump(cases, f, indent=2)

    print(f"✅ Updated {len(cases)} cases - removed computed fields")


def update_claims():
    """Update all claim JSON files - remove insurance_notes."""
    claim_files = [
        "pipclaim_claims.json",
        "biclaim_claims.json",
        "umclaim_claims.json",
        "uimclaim_claims.json",
        "wcclaim_claims.json",
    ]

    for claim_file in claim_files:
        file_path = ENTITIES_DIR / claim_file
        if not file_path.exists():
            print(f"⚠️  Skipping {claim_file} - file not found")
            continue

        with open(file_path, 'r') as f:
            claims = json.load(f)

        for claim in claims:
            # Remove insurance_notes
            claim["attributes"].pop("insurance_notes", None)

        with open(file_path, 'w') as f:
            json.dump(claims, f, indent=2)

        print(f"✅ Updated {len(claims)} claims in {claim_file}")


def update_insurance_claims():
    """Update insurance_claims.json - remove insurance_notes."""
    file_path = ENTITIES_DIR / "insurance_claims.json"
    if not file_path.exists():
        print(f"⚠️  Skipping insurance_claims.json - file not found")
        return

    with open(file_path, 'r') as f:
        claims = json.load(f)

    for claim in claims:
        claim["attributes"].pop("insurance_notes", None)

    with open(file_path, 'w') as f:
        json.dump(claims, f, indent=2)

    print(f"✅ Updated {len(claims)} claims in insurance_claims.json")


if __name__ == "__main__":
    print("Updating entity JSON files to match new schema...")
    print()

    update_cases()
    update_claims()
    update_insurance_claims()

    print()
    print("✅ All updates complete!")
    print("📦 Backups saved in: entities-backup-2025-12-21/")
