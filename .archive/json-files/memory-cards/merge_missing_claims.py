#!/usr/bin/env python3
"""
Merge missing claims from insurance_claims.json into specialized claim files.
"""

import json
from pathlib import Path

ENTITIES_DIR = Path(__file__).parent / "entities"

def merge_missing_pip_claims():
    """Find and merge missing PIP claims."""
    # Load both files
    with open(ENTITIES_DIR / "insurance_claims.json", 'r') as f:
        all_claims = json.load(f)

    with open(ENTITIES_DIR / "pipclaim_claims.json", 'r') as f:
        pip_claims = json.load(f)

    # Get existing PIP claim names
    existing_names = {claim["name"] for claim in pip_claims}

    # Find PIP claims from insurance_claims.json that aren't in pipclaim_claims.json
    missing_claims = [
        claim for claim in all_claims
        if claim["entity_type"] == "PIPClaim" and claim["name"] not in existing_names
    ]

    if missing_claims:
        print(f"Found {len(missing_claims)} missing PIP claims:")
        for claim in missing_claims:
            print(f"  - {claim['name']}")

        # Merge and sort by name
        merged = pip_claims + missing_claims
        merged.sort(key=lambda x: x["name"])

        # Write back
        with open(ENTITIES_DIR / "pipclaim_claims.json", 'w') as f:
            json.dump(merged, f, indent=2)

        print(f"\n✅ Merged {len(missing_claims)} PIP claims into pipclaim_claims.json")
        print(f"   Total PIP claims now: {len(merged)}")
    else:
        print("✅ No missing PIP claims - files are in sync")

    return len(missing_claims)


def verify_other_claim_types():
    """Verify other claim type counts match."""
    with open(ENTITIES_DIR / "insurance_claims.json", 'r') as f:
        all_claims = json.load(f)

    claim_type_counts = {}
    for claim in all_claims:
        claim_type = claim["entity_type"]
        claim_type_counts[claim_type] = claim_type_counts.get(claim_type, 0) + 1

    print("\nClaim type counts in insurance_claims.json:")
    for claim_type, count in sorted(claim_type_counts.items()):
        print(f"  {claim_type}: {count}")

    # Check specialized files
    specialized_files = {
        "BIClaim": "biclaim_claims.json",
        "UMClaim": "umclaim_claims.json",
        "UIMClaim": "uimclaim_claims.json",
        "WCClaim": "wcclaim_claims.json",
    }

    print("\nSpecialized file counts:")
    for claim_type, filename in specialized_files.items():
        file_path = ENTITIES_DIR / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                claims = json.load(f)
            expected = claim_type_counts.get(claim_type, 0)
            actual = len(claims)
            status = "✅" if actual == expected else f"⚠️  Expected {expected}"
            print(f"  {filename}: {actual} {status}")


if __name__ == "__main__":
    print("Merging missing claims from insurance_claims.json...\n")

    # Merge missing PIP claims
    missing_count = merge_missing_pip_claims()

    # Verify other claim types
    verify_other_claim_types()

    if missing_count > 0:
        print(f"\n✅ Merge complete! Added {missing_count} PIP claims.")

    print("\nReady to delete insurance_claims.json")
