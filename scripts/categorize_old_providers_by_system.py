#!/usr/bin/env python3
"""
Categorize old medical providers by health system.

Reads json-files/medical-providers.json (old case data providers)
and categorizes them into the 5 major health systems:
1. Norton Healthcare
2. UofL Health
3. Baptist Health
4. CHI Saint Joseph Health
5. St. Elizabeth Healthcare

Outputs 5 markdown files, one for each system.
"""

import json
import re
from pathlib import Path
from collections import defaultdict


def categorize_provider(provider_name: str) -> str:
    """Determine which health system a provider belongs to."""

    name_lower = provider_name.lower()

    # Norton Healthcare
    norton_keywords = ['norton', 'kosair']
    if any(keyword in name_lower for keyword in norton_keywords):
        return "Norton Healthcare"

    # UofL Health
    uofl_keywords = ['uofl', 'university of louisville', 'u of l', 'jewish hospital', 'peace hospital',
                     'jewish', 'mary & elizabeth', 'mary and elizabeth', 'shelbyville hospital']
    if any(keyword in name_lower for keyword in uofl_keywords):
        return "UofL Health"

    # Baptist Health
    baptist_keywords = ['baptist']
    if any(keyword in name_lower for keyword in baptist_keywords):
        return "Baptist Health"

    # CHI Saint Joseph Health
    chi_keywords = ['chi saint joseph', 'saint joseph', 'st joseph', 'st. joseph', 'flaget']
    if any(keyword in name_lower for keyword in chi_keywords):
        return "CHI Saint Joseph Health"

    # St. Elizabeth Healthcare
    st_elizabeth_keywords = ['st elizabeth', 'st. elizabeth', 'saint elizabeth', 'stelizabeth']
    if any(keyword in name_lower for keyword in st_elizabeth_keywords):
        return "St. Elizabeth Healthcare"

    # Not part of the 5 major systems
    return "Other"


def main():
    # Load old medical providers
    json_file = Path("/Volumes/X10 Pro/Roscoe/json-files/medical-providers.json")

    print("Loading old medical providers from case data...")
    with open(json_file, 'r', encoding='utf-8') as f:
        providers = json.load(f)

    print(f"✓ Loaded {len(providers)} providers\n")

    # Categorize by health system
    by_system = defaultdict(list)

    for provider in providers:
        name = provider.get('provider_full_name', '')
        if not name:
            continue

        system = categorize_provider(name)
        by_system[system].append(provider)

    # Print summary
    print("="*70)
    print("CATEGORIZATION SUMMARY")
    print("="*70)
    print()

    for system in ["Norton Healthcare", "UofL Health", "Baptist Health", "CHI Saint Joseph Health", "St. Elizabeth Healthcare", "Other"]:
        count = len(by_system.get(system, []))
        if count > 0:
            print(f"{system}: {count} providers")

    print()

    # Generate files for each of the 5 major systems
    output_dir = Path("/Volumes/X10 Pro/Roscoe/old-providers-by-system")
    output_dir.mkdir(exist_ok=True)

    systems_to_output = [
        "Norton Healthcare",
        "UofL Health",
        "Baptist Health",
        "CHI Saint Joseph Health",
        "St. Elizabeth Healthcare"
    ]

    for system_name in systems_to_output:
        system_providers = by_system.get(system_name, [])

        if not system_providers:
            print(f"⊙ No providers found for {system_name}")
            continue

        # Sort by provider name
        system_providers.sort(key=lambda p: p.get('provider_full_name', ''))

        # Group by provider name (may have multiple cases)
        by_provider_name = defaultdict(list)
        for provider in system_providers:
            name = provider.get('provider_full_name', '')
            by_provider_name[name].append(provider)

        # Generate markdown file
        filename = system_name.lower().replace(" ", "_").replace("&", "and") + "_old_providers.md"
        output_file = output_dir / filename

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {system_name} - Old Providers from Case Data\n\n")
            f.write(f"**Total Provider Entries:** {len(system_providers)}\n")
            f.write(f"**Unique Provider Names:** {len(by_provider_name)}\n")
            f.write(f"**Source:** json-files/medical-providers.json (case data)\n\n")
            f.write("---\n\n")

            f.write("## Provider List\n\n")
            f.write("Each provider below was extracted from case notes and may have multiple entries if treated multiple clients.\n\n")

            for provider_name in sorted(by_provider_name.keys()):
                entries = by_provider_name[provider_name]
                f.write(f"### {provider_name}\n\n")
                f.write(f"**Entries:** {len(entries)}\n\n")

                # Get unique cases
                cases = list(set(e.get('project_name', '') for e in entries if e.get('project_name')))
                if cases:
                    f.write(f"**Cases ({len(cases)}):**\n")
                    for case in sorted(cases):
                        f.write(f"- {case}\n")
                    f.write("\n")

                # Show details from first entry
                first_entry = entries[0]

                if first_entry.get('billed_amount'):
                    total_billed = sum(e.get('billed_amount', 0) for e in entries if e.get('billed_amount'))
                    f.write(f"**Total Billed:** ${total_billed:,.2f}\n\n")

                # Show any available metadata
                sample = entries[0]
                metadata = []
                if sample.get('date_treatment_started'):
                    metadata.append(f"Treatment Started: {sample['date_treatment_started']}")
                if sample.get('date_medical_records_received'):
                    metadata.append(f"Records Received: {sample['date_medical_records_received']}")

                if metadata:
                    f.write(f"**Sample Entry Details:**\n")
                    for item in metadata:
                        f.write(f"- {item}\n")
                    f.write("\n")

                f.write("---\n\n")

        print(f"✓ Created: {output_file}")

    # Also create a summary file
    summary_file = output_dir / "_SUMMARY.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Old Medical Providers - Summary by Health System\n\n")
        f.write(f"**Source:** json-files/medical-providers.json\n")
        f.write(f"**Total Providers:** {len(providers)}\n")
        f.write(f"**Total Unique Names:** {sum(len(by_provider_name) for system_name in systems_to_output for by_provider_name in [defaultdict(list)] if True)}\n\n")
        f.write("---\n\n")

        f.write("## Breakdown by Health System\n\n")

        for system_name in systems_to_output:
            system_providers = by_system.get(system_name, [])
            by_provider_name = defaultdict(list)
            for provider in system_providers:
                name = provider.get('provider_full_name', '')
                by_provider_name[name].append(provider)

            unique_names = len(by_provider_name)
            total_entries = len(system_providers)
            total_cases = len(set(p.get('project_name', '') for p in system_providers if p.get('project_name')))

            f.write(f"### {system_name}\n\n")
            f.write(f"- Unique provider names: {unique_names}\n")
            f.write(f"- Total entries: {total_entries}\n")
            f.write(f"- Cases affected: {total_cases}\n")
            f.write(f"- File: `{system_name.lower().replace(' ', '_').replace('&', 'and')}_old_providers.md`\n\n")

        # Other providers
        other_providers = by_system.get("Other", [])
        other_by_name = defaultdict(list)
        for provider in other_providers:
            name = provider.get('provider_full_name', '')
            other_by_name[name].append(provider)

        f.write(f"### Other (Independent Providers)\n\n")
        f.write(f"- Unique provider names: {len(other_by_name)}\n")
        f.write(f"- Total entries: {len(other_providers)}\n")
        f.write(f"- These are independent clinics, chiropractors, imaging centers, etc.\n")
        f.write(f"- Not part of the 5 major health systems\n\n")

        f.write("---\n\n")
        f.write("## Files Generated\n\n")
        for system_name in systems_to_output:
            filename = system_name.lower().replace(" ", "_").replace("&", "and") + "_old_providers.md"
            f.write(f"- `{filename}`\n")

    print(f"✓ Created summary: {summary_file}")

    print("\n" + "="*70)
    print("CATEGORIZATION COMPLETE")
    print("="*70)
    print(f"\nOutput directory: {output_dir}")
    print("\nFiles created:")
    for system_name in systems_to_output:
        system_count = len(by_system.get(system_name, []))
        unique_count = len(set(p.get('provider_full_name', '') for p in by_system.get(system_name, [])))
        filename = system_name.lower().replace(" ", "_").replace("&", "and") + "_old_providers.md"
        if system_count > 0:
            print(f"  - {filename} ({unique_count} unique providers, {system_count} entries)")

    print()
    print("✅ Categorization complete")


if __name__ == "__main__":
    main()
