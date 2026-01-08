#!/usr/bin/env python3
"""
Deduplicate medical-providers-FINAL.json.

The current file has multiple entries per provider (one per case).
This consolidates to one entry per unique provider with aggregated data.
"""

import json
from pathlib import Path
from collections import defaultdict


def deduplicate_providers(providers: list) -> list:
    """Consolidate duplicate provider entries."""

    # Group by provider name
    by_provider = defaultdict(list)

    for entry in providers:
        provider_name = entry.get('provider_full_name', '')
        if provider_name:
            by_provider[provider_name].append(entry)

    # Consolidate each provider's entries
    deduplicated = []

    for provider_name in sorted(by_provider.keys()):
        entries = by_provider[provider_name]

        # Aggregate data from all entries
        consolidated = {
            'provider_full_name': provider_name,
            'entry_count': len(entries),
            'cases': sorted(set(e.get('project_name', '') for e in entries if e.get('project_name'))),
            'total_billed': sum(e.get('billed_amount', 0) or 0 for e in entries),
            'total_settlement': sum(e.get('settlement_payment', 0) or 0 for e in entries),
            'first_treatment': min([e.get('date_treatment_started', '') for e in entries if e.get('date_treatment_started')], default=None),
            'total_visits': sum(e.get('number_of_visits', 0) or 0 for e in entries)
        }

        # Keep first entry's metadata
        first_entry = entries[0]
        consolidated['sample_entry_id'] = first_entry.get('id')

        deduplicated.append(consolidated)

    return deduplicated


def main():
    """Deduplicate medical-providers-FINAL.json."""

    input_file = Path("/Volumes/X10 Pro/Roscoe/json-files/medical-providers-FINAL.json")

    print("Loading medical-providers-FINAL.json...")
    with open(input_file, 'r', encoding='utf-8') as f:
        providers = json.load(f)

    print(f"✓ Loaded {len(providers)} entries\n")

    # Deduplicate
    deduplicated = deduplicate_providers(providers)

    print(f"Unique providers: {len(deduplicated)}")
    print(f"Duplicate entries removed: {len(providers) - len(deduplicated)}\n")

    # Show top providers by case count
    print("Top 10 providers by case count:")
    sorted_by_cases = sorted(deduplicated, key=lambda x: len(x['cases']), reverse=True)

    for idx, provider in enumerate(sorted_by_cases[:10], 1):
        name = provider['provider_full_name']
        case_count = len(provider['cases'])
        total_billed = provider['total_billed']
        print(f"{idx}. {name[:50]:<50} - {case_count} cases, ${total_billed:,.2f}")

    # Save deduplicated version
    output_file = Path("/Volumes/X10 Pro/Roscoe/json-files/medical-providers-DEDUPLICATED.json")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(deduplicated, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved to: {output_file}")
    print(f"\n✅ Deduplicated: {len(providers)} entries → {len(deduplicated)} unique providers")


if __name__ == "__main__":
    main()
