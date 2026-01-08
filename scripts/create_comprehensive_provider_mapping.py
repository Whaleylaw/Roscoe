#!/usr/bin/env python3
"""
Create comprehensive mapping of ALL provider names in review files to Facility names in graph.

Matches 400 unique provider names from reviews to 1,163 Facilities.
"""

import json
from pathlib import Path
from rapidfuzz import fuzz
import re


def normalize_name(name):
    """Normalize provider name for matching."""
    name = name.lower()
    # Remove common prefixes
    name = re.sub(r'^(uofl|university of louisville|st\.?|saint)\s+', '', name)
    # Remove health/healthcare
    name = re.sub(r'\s+(health|healthcare|medical group)\s*-?\s*', ' ', name)
    # Remove dashes and punctuation
    name = re.sub(r'[-–]', ' ', name)
    name = re.sub(r'[,\.]', '', name)
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name)
    return name.strip()


def find_best_facility_match(provider_name, facility_names):
    """Find best matching Facility name."""

    provider_norm = normalize_name(provider_name)

    best_match = None
    best_score = 0

    for facility_name in facility_names:
        facility_norm = normalize_name(facility_name)

        # Exact match after normalization
        if provider_norm == facility_norm:
            return facility_name, 100

        # Calculate similarity
        ratio = fuzz.ratio(provider_norm, facility_norm)
        partial = fuzz.partial_ratio(provider_norm, facility_norm)
        token_sort = fuzz.token_sort_ratio(provider_norm, facility_norm)

        score = max(ratio, partial, token_sort)

        # Boost if provider name is substring of facility
        if len(provider_norm) >= 8 and provider_norm in facility_norm:
            score = max(score, 90)

        if score > best_score:
            best_score = score
            best_match = facility_name

    return best_match, best_score


def main():
    """Create comprehensive provider mapping."""

    print("="*70)
    print("COMPREHENSIVE PROVIDER NAME MAPPING")
    print("="*70)
    print()

    # Load all provider names from review files
    with open("/Volumes/X10 Pro/Roscoe/all_review_provider_names.json") as f:
        review_provider_names = json.load(f)

    print(f"Provider names from review files: {len(review_provider_names)}")

    # Load all Facility names from graph
    with open("/Volumes/X10 Pro/Roscoe/schema-final/entities/facilities.json") as f:
        facilities = json.load(f)

    facility_names = [fac['name'] for fac in facilities]

    print(f"Facility names in graph: {len(facility_names)}")
    print()

    # Create comprehensive mapping
    mapping = {}
    high_confidence = []
    medium_confidence = []
    low_confidence = []
    no_match = []

    for provider_name in review_provider_names:
        # Skip if starts with ** (header markers)
        if provider_name.startswith('**'):
            continue

        # Find best match
        best_match, score = find_best_facility_match(provider_name, facility_names)

        if score >= 95:
            # High confidence match
            mapping[provider_name] = best_match
            high_confidence.append((provider_name, best_match, score))
        elif score >= 75:
            # Medium confidence - needs review
            medium_confidence.append((provider_name, best_match, score))
        elif score >= 60:
            # Low confidence
            low_confidence.append((provider_name, best_match, score))
        else:
            # No good match
            no_match.append(provider_name)

    print(f"High confidence matches (≥95%): {len(high_confidence)}")
    print(f"Medium confidence (75-94%): {len(medium_confidence)}")
    print(f"Low confidence (60-74%): {len(low_confidence)}")
    print(f"No match (<60%): {len(no_match)}")
    print()

    # Show samples
    print("Sample high confidence matches:")
    for provider, facility, score in high_confidence[:10]:
        print(f"  {provider[:40]:<40} → {facility[:40]:<40} ({score:.0f}%)")

    if len(high_confidence) > 10:
        print(f"  ... and {len(high_confidence) - 10} more")

    print()

    if medium_confidence:
        print("Medium confidence matches (REVIEW THESE):")
        for provider, facility, score in medium_confidence[:10]:
            print(f"  {provider[:40]:<40} → {facility[:40]:<40} ({score:.0f}%)")

        if len(medium_confidence) > 10:
            print(f"  ... and {len(medium_confidence) - 10} more")

    # Save mappings
    output_file = Path("/Volumes/X10 Pro/Roscoe/comprehensive_provider_mapping.json")

    output_data = {
        'high_confidence': mapping,
        'medium_confidence': {p: f for p, f, s in medium_confidence},
        'low_confidence': {p: f for p, f, s in low_confidence},
        'no_match': no_match
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✓ Saved to: {output_file}")
    print()
    print("="*70)
    print(f"HIGH CONFIDENCE MAPPING: {len(mapping)} pairs ready to use")
    print("="*70)
    print()
    print("Review medium_confidence matches and add to mapping if correct")


if __name__ == "__main__":
    main()
