#!/usr/bin/env python3
"""
Create side-by-side mapping documents for old vs new providers.

For each of the 5 health systems, creates a document showing:
- OLD provider (from case data)
- Top 3-5 matches from NEW roster (from location JSON files)
- Match scores and addresses for comparison

Output: 5 mapping documents for manual review and decision.
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


def find_top_matches(old_name: str, new_providers: list, top_n: int = 5) -> list:
    """Find top N matches from new roster."""

    old_norm = normalize_provider_name(old_name)
    matches = []

    for new_provider in new_providers:
        new_name = new_provider.get('name', '')
        new_norm = normalize_provider_name(new_name)

        # Calculate similarity
        ratio_score = fuzz.ratio(old_norm, new_norm)
        partial_score = fuzz.partial_ratio(old_norm, new_norm)
        token_sort_score = fuzz.token_sort_ratio(old_norm, new_norm)

        # Best score across methods
        best_score = max(ratio_score, partial_score, token_sort_score)

        # Also check if old is substring of new
        if len(old_norm) >= 8 and old_norm in new_norm:
            best_score = max(best_score, 88)  # Boost substring matches

        matches.append({
            'provider': new_provider,
            'score': best_score,
            'ratio': ratio_score,
            'partial': partial_score,
            'token_sort': token_sort_score
        })

    # Sort by score descending
    matches.sort(key=lambda x: x['score'], reverse=True)

    return matches[:top_n]


def create_mapping_document(
    system_name: str,
    old_providers_file: Path,
    new_providers_file: Path,
    output_file: Path
):
    """Create mapping document for one health system."""

    # Load old providers from case data
    old_data_file = Path("/Volumes/X10 Pro/Roscoe/json-files/medical-providers.json")
    with open(old_data_file, 'r', encoding='utf-8') as f:
        all_old_providers = json.load(f)

    # Filter to this health system based on name matching
    def is_in_system(provider_name: str) -> bool:
        if not provider_name:
            return False
        name_lower = provider_name.lower()
        if system_name == "Norton Healthcare":
            return 'norton' in name_lower or 'kosair' in name_lower
        elif system_name == "UofL Health":
            return any(kw in name_lower for kw in ['uofl', 'university of louisville', 'u of l', 'jewish', 'mary & elizabeth', 'mary and elizabeth'])
        elif system_name == "Baptist Health":
            return 'baptist' in name_lower
        elif system_name == "CHI Saint Joseph Health":
            return any(kw in name_lower for kw in ['chi saint joseph', 'saint joseph', 'st joseph', 'st. joseph', 'flaget'])
        elif system_name == "St. Elizabeth Healthcare":
            return any(kw in name_lower for kw in ['st elizabeth', 'st. elizabeth', 'saint elizabeth'])
        return False

    old_system_providers = [p for p in all_old_providers if is_in_system(p.get('provider_full_name', ''))]

    # Group by provider name
    old_by_name = defaultdict(list)
    for provider in old_system_providers:
        name = provider.get('provider_full_name', '')
        if name:
            old_by_name[name].append(provider)

    # Load new providers from roster
    with open(new_providers_file, 'r', encoding='utf-8') as f:
        new_providers = json.load(f)

    # Generate mapping document
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {system_name} - Provider Mapping\n\n")
        f.write(f"**Old Providers (from case data):** {len(old_by_name)} unique names\n")
        f.write(f"**New Providers (from official roster):** {len(new_providers)}\n")
        f.write(f"**Purpose:** Map old generic providers to new detailed official providers\n\n")
        f.write("---\n\n")

        f.write("## Instructions\n\n")
        f.write("For each OLD provider below:\n\n")
        f.write("1. Review the top 5 suggested matches from the new roster\n")
        f.write("2. Compare addresses (if same address = same facility)\n")
        f.write("3. Mark your decision:\n")
        f.write("   - `[REPLACE]` - Replace old with new (specify which new provider ID)\n")
        f.write("   - `[KEEP OLD]` - No good match, keep the old provider\n")
        f.write("   - `[DELETE]` - Duplicate of another old provider, just delete\n\n")
        f.write("---\n\n")

        # Sort old providers by number of cases (most impact first)
        old_sorted = sorted(old_by_name.items(),
                           key=lambda x: len(set(e.get('project_name', '') for e in x[1])),
                           reverse=True)

        for idx, (old_name, entries) in enumerate(old_sorted, 1):
            # Get unique cases for this provider
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

            # Find top matches from new roster
            top_matches = find_top_matches(old_name, new_providers, top_n=5)

            f.write(f"**Top {len(top_matches)} Matches from New Roster:**\n\n")

            for match_idx, match in enumerate(top_matches, 1):
                new_provider = match['provider']
                score = match['score']

                f.write(f"{match_idx}. **{new_provider.get('name', 'Unknown')}** ({score:.0f}% match)\n")
                f.write(f"   - Address: {new_provider.get('address', 'N/A')}\n")
                if new_provider.get('phone'):
                    f.write(f"   - Phone: {new_provider.get('phone')}\n")
                if new_provider.get('npi'):
                    f.write(f"   - NPI: {new_provider.get('npi')}\n")
                f.write(f"   - Match breakdown: Ratio={match['ratio']}%, Partial={match['partial']}%, TokenSort={match['token_sort']}%\n")
                f.write("\n")

            f.write(f"**DECISION:**\n")
            f.write(f"- [ ] REPLACE with match #___ (specify which one above)\n")
            f.write(f"- [ ] KEEP OLD (no good match)\n")
            f.write(f"- [ ] DELETE (duplicate)\n\n")
            f.write(f"**Notes:**\n\n")
            f.write("---\n\n")

    return len(old_by_name), len(new_providers)


def main():
    """Create mapping documents for all 5 health systems."""

    systems = [
        {
            'name': 'Norton Healthcare',
            'new_file': Path("/Volumes/X10 Pro/Roscoe/json-files/norton_healthcare_locations.json"),
            'output': Path("/Volumes/X10 Pro/Roscoe/provider-mappings/NORTON_MAPPING.md")
        },
        {
            'name': 'UofL Health',
            'new_file': Path("/Volumes/X10 Pro/Roscoe/json-files/uofl_health_locations.json"),
            'output': Path("/Volumes/X10 Pro/Roscoe/provider-mappings/UOFL_MAPPING.md")
        },
        {
            'name': 'Baptist Health',
            'new_file': Path("/Volumes/X10 Pro/Roscoe/json-files/baptist_health_locations.json"),
            'output': Path("/Volumes/X10 Pro/Roscoe/provider-mappings/BAPTIST_MAPPING.md")
        },
        {
            'name': 'CHI Saint Joseph Health',
            'new_file': Path("/Volumes/X10 Pro/Roscoe/json-files/chi_saint_joseph_locations.json"),
            'output': Path("/Volumes/X10 Pro/Roscoe/provider-mappings/CHI_MAPPING.md")
        },
        {
            'name': 'St. Elizabeth Healthcare',
            'new_file': Path("/Volumes/X10 Pro/Roscoe/json-files/stelizabeth_locations.json"),
            'output': Path("/Volumes/X10 Pro/Roscoe/provider-mappings/STELIZABETH_MAPPING.md")
        }
    ]

    # Create output directory
    output_dir = Path("/Volumes/X10 Pro/Roscoe/provider-mappings")
    output_dir.mkdir(exist_ok=True)

    print("="*70)
    print("PROVIDER MAPPING DOCUMENT GENERATION")
    print("="*70)
    print()

    results = []

    for system in systems:
        print(f"Processing {system['name']}...")

        if not system['new_file'].exists():
            print(f"  ⚠️  File not found: {system['new_file']}")
            continue

        old_count, new_count = create_mapping_document(
            system['name'],
            None,  # Not needed, we load from medical-providers.json directly
            system['new_file'],
            system['output']
        )

        print(f"  ✓ {old_count} old providers → {new_count} new providers")
        print(f"  ✓ Saved to: {system['output'].name}")

        results.append({
            'system': system['name'],
            'old_count': old_count,
            'new_count': new_count,
            'file': system['output'].name
        })

        print()

    # Create summary document
    summary_file = output_dir / "_MAPPING_SUMMARY.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Provider Mapping Summary\n\n")
        f.write("**Date:** 2026-01-02\n")
        f.write("**Purpose:** Map old case-data providers to new official health system rosters\n\n")
        f.write("---\n\n")

        f.write("## Files Generated\n\n")
        f.write("Each file shows old providers side-by-side with suggested matches from new roster.\n\n")

        for result in results:
            f.write(f"### {result['system']}\n\n")
            f.write(f"- **File:** `{result['file']}`\n")
            f.write(f"- **Old providers:** {result['old_count']}\n")
            f.write(f"- **New provider roster:** {result['new_count']}\n\n")

        f.write("---\n\n")
        f.write("## How to Use\n\n")
        f.write("1. Open each mapping file\n")
        f.write("2. For each OLD provider, review the top 5 suggested matches\n")
        f.write("3. Compare addresses (same address = same facility)\n")
        f.write("4. Mark your decision in the checkboxes\n")
        f.write("5. Return the marked files for script generation\n\n")

        f.write("---\n\n")
        f.write("## Decision Guide\n\n")
        f.write("**[REPLACE]** - Use when:\n")
        f.write("- Same address as new provider\n")
        f.write("- New provider has more complete information\n")
        f.write("- Old name is abbreviated version of new name\n\n")

        f.write("**[KEEP OLD]** - Use when:\n")
        f.write("- No good match in new roster\n")
        f.write("- Old provider is independent (not in this health system)\n")
        f.write("- Addresses don't match any new providers\n\n")

        f.write("**[DELETE]** - Use when:\n")
        f.write("- Old provider is duplicate of another old provider\n")
        f.write("- Misspelled or data entry error\n\n")

    print("="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print(f"\nOutput directory: {output_dir}")
    print(f"\nFiles created: {len(results) + 1}")
    for result in results:
        print(f"  - {result['file']}")
    print(f"  - _MAPPING_SUMMARY.md")

    print("\n✅ Mapping documents ready for review")


if __name__ == "__main__":
    main()
