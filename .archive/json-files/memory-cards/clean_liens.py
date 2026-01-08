#!/usr/bin/env python3
"""
Remove duplicated fields from liens.json.

Removes:
- lien_type (belongs on LienHolder)
- lienholder_name (that's the HELD_BY relationship)
"""

import json
from pathlib import Path

ENTITIES_DIR = Path(__file__).parent / "entities"

def clean_liens():
    """Remove lien_type and lienholder_name from Lien entities."""
    liens_file = ENTITIES_DIR / "liens.json"
    with open(liens_file, 'r') as f:
        liens = json.load(f)

    for lien in liens:
        # Remove duplicated fields
        lien["attributes"].pop("lien_type", None)
        lien["attributes"].pop("lienholder_name", None)

    with open(liens_file, 'w') as f:
        json.dump(liens, f, indent=2)

    print(f"✅ Cleaned {len(liens)} liens - removed lien_type and lienholder_name")
    print("   These fields now live on LienHolder entity (via HELD_BY relationship)")


if __name__ == "__main__":
    clean_liens()
