#!/usr/bin/env python3
"""
Regenerate UofL mapping using facility-based structure.

Uses the consolidated facility structure (169 facilities vs 345 locations)
for much clearer matching.
"""

import json
import re
from pathlib import Path
from rapidfuzz import fuzz
from collections import defaultdict


def normalize_provider_name(name: str) -> str:
    """Normalize provider name for matching."""
    name = name.lower()
    # Remove common prefixes
    name = re.sub(r'^(uofl|university of louisville|st\.?|saint)\s+', '', name)
    # Remove health/healthcare
    name = re.sub(r'\s+(health|healthcare|medical (group|center|associates|physicians))\s*-?\s*', ' ', name)
    # Remove "&", "and", "-"
    name = re.sub(r'\s+(&|and|-)\s+', ' ', name)
    # Remove apostrophes and periods
    name = re.sub(r"['\.]", '', name)
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name)
    return name.strip()


def find_top_matches(old_name: str, new_facilities: list, top_n: int = 5) -> list:
    """Find top N matches from new facility-based roster."""

    old_norm = normalize_provider_name(old_name)
    matches = []

    for facility in new_facilities:
        facility_name = facility.get('name', '')
        facility_norm = normalize_provider_name(facility_name)

        # Calculate similarity
        ratio_score = fuzz.ratio(old_norm, facility_norm)
        partial_score = fuzz.partial_ratio(old_norm, facility_norm)
        token_sort_score = fuzz.token_sort_ratio(old_norm, facility_norm)

        # Best score
        best_score = max(ratio_score, partial_score, token_sort_score)

        # Substring boost
        if len(old_norm) >= 8 and old_norm in facility_norm:
            best_score = max(best_score, 88)

        matches.append({
            'facility': facility,
            'score': best_score,
            'ratio': ratio_score,
            'partial': partial_score,
            'token_sort': token_sort_score
        })

    # Sort by score descending
    matches.sort(key=lambda x: x['score'], reverse=True)

    return matches[:top_n]


def main():
    """Regenerate UofL mapping with facility-based structure."""

    # Load old providers from case data
    old_data_file = Path("/Volumes/X10 Pro/Roscoe/json-files/medical-providers.json")
    with open(old_data_file, 'r', encoding='utf-8') as f:
        all_old_providers = json.load(f)

    # Filter to UofL system
    uofl_keywords = ['uofl', 'university of louisville', 'u of l', 'jewish hospital',
                     'jewish', 'mary & elizabeth', 'mary and elizabeth']

    old_uofl = []
    for p in all_old_providers:
        name = p.get('provider_full_name', '')
        if name:
            name_lower = name.lower()
            if any(kw in name_lower for kw in uofl_keywords):
                old_uofl.append(p)

    # Group by provider name
    old_by_name = defaultdict(list)
    for provider in old_uofl:
        name = provider.get('provider_full_name', '')
        if name:
            old_by_name[name].append(provider)

    # Load NEW facility-based providers
    new_facilities_file = Path("/Volumes/X10 Pro/Roscoe/json-files/facility-based/uofl_health_facilities.json")
    with open(new_facilities_file, 'r', encoding='utf-8') as f:
        new_facilities = json.load(f)

    print("="*70)
    print("REGENERATING UOFL MAPPING WITH FACILITY-BASED STRUCTURE")
    print("="*70)
    print()
    print(f"Old providers (case data): {len(old_by_name)}")
    print(f"New facilities (consolidated): {len(new_facilities)}")
    print(f"Reduction in new roster: {345 - len(new_facilities)} nodes")
    print()

    # Generate mapping document
    output_file = Path("/Volumes/X10 Pro/Roscoe/provider-mappings/UOFL_MAPPING_FACILITY_BASED.md")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# UofL Health - Provider Mapping (Facility-Based)\n\n")
        f.write(f"**Old Providers (from case data):** {len(old_by_name)} unique names\n")
        f.write(f"**New Facilities (consolidated roster):** {len(new_facilities)}\n")
        f.write(f"**Structure:** Facility-level nodes with locations as properties\n")
        f.write(f"**Reduction:** 345 locations → 169 facilities (51% consolidation)\n\n")
        f.write("---\n\n")

        f.write("## Instructions\n\n")
        f.write("For each OLD provider:\n\n")
        f.write("1. Review the suggested facility matches\n")
        f.write("2. Check if locations array includes the right location\n")
        f.write("3. Mark your decision:\n")
        f.write("   - `[REPLACE]` - Replace with facility (will match to facility node)\n")
        f.write("   - `[KEEP OLD]` - No good match\n")
        f.write("   - `[DELETE]` - Duplicate\n\n")
        f.write("---\n\n")

        # Sort by case count
        old_sorted = sorted(old_by_name.items(),
                           key=lambda x: len(set(e.get('project_name', '') for e in x[1])),
                           reverse=True)

        for idx, (old_name, entries) in enumerate(old_sorted, 1):
            cases = sorted(set(e.get('project_name', '') for e in entries if e.get('project_name')))
            total_billed = sum(e.get('billed_amount', 0) for e in entries if e.get('billed_amount'))

            f.write(f"## {idx}. OLD: {old_name}\n\n")
            f.write(f"**Entries:** {len(entries)}\n\n")
            f.write(f"**Cases ({len(cases)}):**\n")
            for case in cases:
                f.write(f"- {case}\n")
            f.write("\n")

            if total_billed > 0:
                f.write(f"**Total Billed:** ${total_billed:,.2f}\n\n")

            # Find top matches
            top_matches = find_top_matches(old_name, new_facilities, top_n=5)

            f.write(f"**Top {len(top_matches)} Facility Matches:**\n\n")

            for match_idx, match in enumerate(top_matches, 1):
                facility = match['facility']
                score = match['score']
                facility_name = facility.get('name', '')
                location_count = facility['attributes'].get('location_count', 0)

                f.write(f"{match_idx}. **{facility_name}** ({score:.0f}% match)\n")
                f.write(f"   - Locations: {location_count}\n")

                # Show first 3 locations
                locations = facility['attributes'].get('locations', [])
                for loc_idx, loc in enumerate(locations[:3], 1):
                    loc_name = loc.get('location', 'Main')
                    loc_addr = loc.get('address', 'N/A')
                    f.write(f"   - {loc_name}: {loc_addr}\n")

                if location_count > 3:
                    f.write(f"   - ... and {location_count - 3} more locations\n")

                f.write(f"   - Match breakdown: Ratio={match['ratio']:.0f}%, Partial={match['partial']:.0f}%, TokenSort={match['token_sort']:.0f}%\n")
                f.write("\n")

            f.write("**DECISION:**\n")
            f.write("- [ ] REPLACE with match #___ (specify which one above)\n")
            f.write("- [ ] KEEP OLD (no good match)\n")
            f.write("- [ ] DELETE (duplicate)\n\n")
            f.write("**Notes:**\n\n")
            f.write("---\n\n")

    print(f"✓ Generated: {output_file}")
    print(f"\n✅ UofL mapping regenerated with facility-based structure")
    print(f"\nFile: {output_file}")


if __name__ == "__main__":
    main()
