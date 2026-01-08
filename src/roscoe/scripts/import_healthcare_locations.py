#!/usr/bin/env python3
"""
Import healthcare locations and link to HealthSystems.

Imports 1,369 locations from 5 health systems:
- Norton Healthcare (368 locations)
- UofL Health (345 locations)
- Baptist Health (467 locations)
- CHI Saint Joseph (152 locations)
- St. Elizabeth (419 locations)

Merges with existing medical_providers.json (773 entries).
"""

import json
import re
from pathlib import Path
from rapidfuzz import fuzz


def determine_health_system(name: str) -> str:
    """Determine parent HealthSystem from location name."""
    name_lower = name.lower()

    if "norton" in name_lower:
        return "Norton Healthcare"
    elif "uofl" in name_lower or "university of louisville" in name_lower or "u of l" in name_lower:
        return "UofL Health"
    elif "baptist" in name_lower:
        return "Baptist Health"
    elif "chi saint joseph" in name_lower or "st. joseph" in name_lower or "saint joseph" in name_lower:
        return "CHI Saint Joseph Health"
    elif "st. elizabeth" in name_lower or "st elizabeth" in name_lower or "stelizabeth" in name_lower:
        return "St. Elizabeth Healthcare"

    return None


def fuzzy_match_provider(new_name: str, existing_providers: list) -> tuple[bool, dict]:
    """
    Fuzzy match new provider against existing.

    Returns: (matched, existing_provider_entity)
    """
    new_norm = new_name.lower().strip()

    best_match = None
    best_score = 0

    for existing in existing_providers:
        existing_norm = existing['name'].lower().strip()

        # Exact match
        if new_norm == existing_norm:
            return True, existing

        # Fuzzy match
        score = fuzz.ratio(new_norm, existing_norm)
        if score > best_score:
            best_score = score
            best_match = existing

        # Substring match for locations with extra detail
        if len(new_norm) > 10 and len(existing_norm) > 10:
            if new_norm in existing_norm or existing_norm in new_norm:
                if score >= 75:
                    return True, existing

    # High threshold for medical providers (avoid false matches)
    if best_match and best_score >= 88:
        return True, best_match

    return False, None


def import_healthcare_locations():
    """Import all healthcare locations."""
    input_file = Path("/Volumes/X10 Pro/Roscoe/json-files/all_healthcare_locations.json")
    entities_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities")
    existing_file = entities_dir / "medical_providers.json"

    print("=" * 80)
    print("IMPORTING HEALTHCARE LOCATIONS")
    print("=" * 80)
    print()

    # Load new locations
    with open(input_file) as f:
        new_locations = json.load(f)

    print(f"Total locations in file: {len(new_locations)}")

    # Load existing providers
    existing_providers = []
    if existing_file.exists():
        with open(existing_file) as f:
            existing_providers = json.load(f)

    print(f"Existing providers: {len(existing_providers)}")
    print()

    # Track stats
    stats = {
        "matched": 0,
        "new": 0,
        "by_system": {
            "Norton Healthcare": 0,
            "UofL Health": 0,
            "Baptist Health": 0,
            "CHI Saint Joseph Health": 0,
            "St. Elizabeth Healthcare": 0,
            "Unknown": 0
        }
    }

    new_provider_entities = []
    matched_names = set()

    for location in new_locations:
        name = location.get("name", "").strip()
        if not name:
            continue

        # Determine parent system
        parent_system = determine_health_system(name)

        # Check if already exists
        matched, existing = fuzzy_match_provider(name, existing_providers)

        if matched:
            stats["matched"] += 1
            matched_names.add(existing['name'])
            # Keep existing (don't update)
            continue

        # Create new provider entity
        new_entity = {
            "card_type": "entity",
            "entity_type": "MedicalProvider",
            "name": name,
            "attributes": {
                "phone": location.get("phone", ""),
                "address": location.get("address", ""),
                "email": "",
                "fax": "",
                "specialty": "",
                "provider_type": "",
                "parent_system": parent_system if parent_system else ""
            },
            "source_id": "healthcare_systems_import",
            "source_file": "all_healthcare_locations.json"
        }

        new_provider_entities.append(new_entity)
        stats["new"] += 1

        if parent_system:
            stats["by_system"][parent_system] += 1
        else:
            stats["by_system"]["Unknown"] += 1

    # Merge
    merged = existing_providers + new_provider_entities

    # Save
    with open(existing_file, 'w') as f:
        json.dump(merged, f, indent=2)

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Matched existing: {stats['matched']}")
    print(f"Added new: {stats['new']}")
    print(f"Total providers: {len(merged)}")
    print()

    print("New providers by health system:")
    for system, count in sorted(stats['by_system'].items()):
        if count > 0:
            print(f"  {system}: {count}")

    print()
    print(f"✅ Updated medical_providers.json")
    print(f"   Before: {len(existing_providers)}")
    print(f"   After: {len(merged)}")
    print(f"   Net new: {stats['new']}")


if __name__ == "__main__":
    import_healthcare_locations()
