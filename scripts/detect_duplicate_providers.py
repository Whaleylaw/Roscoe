#!/usr/bin/env python3
"""
Detect potential duplicate medical providers in the graph.

Uses fuzzy matching to find providers that may be duplicates due to:
- Name variations (Norton Hospital vs Norton Hospital Downtown)
- Formatting differences (UofL Health - X vs UofL Health X)
- Abbreviations (St. vs Saint)

DOES NOT MODIFY THE GRAPH - Read-only analysis.

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/detect_duplicate_providers.py
"""

import os
import re
import sys
from pathlib import Path
from falkordb import FalkorDB
from collections import defaultdict

# Import normalization logic
sys.path.insert(0, "/deps/roscoe/src/roscoe/scripts")
try:
    from generate_review_docs import normalize_hospital_name
except ImportError:
    # Fallback normalization
    def normalize_hospital_name(name: str) -> str:
        """Normalize hospital name for matching."""
        name = name.lower()
        # Remove common prefixes
        name = re.sub(r'^(uofl|university of louisville|st|saint)\s+', '', name)
        # Remove health/healthcare
        name = re.sub(r'\s+(health|healthcare|medical group|medical center)\s*-?\s*', ' ', name)
        # Remove & and "and"
        name = re.sub(r'\s+(&|and)\s+', ' ', name)
        # Remove apostrophes
        name = re.sub(r"'s?\b", '', name)
        # Remove punctuation except hyphens
        name = re.sub(r'[,\.]', '', name)
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name)
        return name.strip()


def get_provider_connection_info(graph, provider_name: str):
    """Get information about what this provider is connected to."""

    # Check if connected to any cases
    query = """
    MATCH (p:MedicalProvider {name: $name})<-[r]-(c:Case)
    RETURN count(c) as case_count, collect(c.name)[0..3] as sample_cases
    """

    result = graph.query(query, {'name': provider_name})
    if result.result_set:
        case_count = result.result_set[0][0]
        sample_cases = result.result_set[0][1] if len(result.result_set[0]) > 1 else []
        return {
            'case_count': case_count,
            'sample_cases': sample_cases,
            'connected': case_count > 0
        }

    return {'case_count': 0, 'sample_cases': [], 'connected': False}


def detect_duplicates():
    """Detect potential duplicate medical providers."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    print("="*70)
    print("MEDICAL PROVIDER DUPLICATE DETECTION")
    print("="*70)
    print()

    # Get all medical providers
    print("Querying all MedicalProvider nodes...")
    result = graph.query("MATCH (p:MedicalProvider) RETURN p.name, id(p) ORDER BY p.name")

    providers = []
    for row in result.result_set:
        providers.append({'name': row[0], 'id': row[1]})

    print(f"✓ Found {len(providers)} MedicalProvider nodes\n")

    # Group by normalized name
    print("Analyzing for potential duplicates...")
    normalized_groups = defaultdict(list)

    for provider in providers:
        name = provider['name']
        normalized = normalize_hospital_name(name)
        normalized_groups[normalized].append(provider)

    # Find groups with multiple providers (potential duplicates)
    potential_duplicates = {k: v for k, v in normalized_groups.items() if len(v) > 1}

    print(f"✓ Found {len(potential_duplicates)} normalized names with multiple providers\n")

    # Get connection info for potential duplicates
    print("Checking case connections for potential duplicates...")
    duplicate_groups = []

    for normalized_name, provider_list in potential_duplicates.items():
        group = {
            'normalized_name': normalized_name,
            'providers': [],
            'total_cases_affected': 0
        }

        for provider in provider_list:
            conn_info = get_provider_connection_info(graph, provider['name'])
            provider_info = {
                'name': provider['name'],
                'id': provider['id'],
                'case_count': conn_info['case_count'],
                'sample_cases': conn_info['sample_cases'],
                'connected': conn_info['connected']
            }
            group['providers'].append(provider_info)
            group['total_cases_affected'] += conn_info['case_count']

        duplicate_groups.append(group)

    print(f"✓ Analyzed connections\n")

    # Sort by impact (most case connections first)
    duplicate_groups.sort(key=lambda x: x['total_cases_affected'], reverse=True)

    # Generate report
    print("="*70)
    print("DUPLICATE DETECTION REPORT")
    print("="*70)
    print()

    print(f"Total MedicalProvider nodes: {len(providers)}")
    print(f"Potential duplicate groups: {len(potential_duplicates)}")
    print(f"Total providers in duplicate groups: {sum(len(g['providers']) for g in duplicate_groups)}")
    print()

    # Summary by impact
    high_impact = [g for g in duplicate_groups if g['total_cases_affected'] > 0]
    low_impact = [g for g in duplicate_groups if g['total_cases_affected'] == 0]

    print(f"High Impact (connected to cases): {len(high_impact)} groups")
    print(f"Low Impact (not connected): {len(low_impact)} groups")
    print()

    # Write detailed report
    output_file = Path("/mnt/workspace/Reports/medical_provider_duplicates_report.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Medical Provider Duplicate Detection Report\n\n")
        f.write(f"**Date:** {import_datetime()}\n")
        f.write(f"**Total Providers:** {len(providers)}\n")
        f.write(f"**Potential Duplicate Groups:** {len(potential_duplicates)}\n\n")
        f.write("---\n\n")

        # High impact duplicates
        f.write(f"## High Impact Duplicates ({len(high_impact)} groups)\n\n")
        f.write("These providers are connected to active cases - deduplication requires care.\n\n")

        for i, group in enumerate(high_impact, 1):
            f.write(f"### {i}. Normalized: `{group['normalized_name']}`\n\n")
            f.write(f"**Total cases affected:** {group['total_cases_affected']}\n\n")
            f.write(f"**Providers in group:** {len(group['providers'])}\n\n")

            for provider in group['providers']:
                f.write(f"- **{provider['name']}** (ID: {provider['id']})\n")
                f.write(f"  - Cases: {provider['case_count']}\n")
                if provider['sample_cases']:
                    f.write(f"  - Sample cases: {', '.join(provider['sample_cases'])}\n")
                f.write("\n")

            f.write("**Recommended Action:** Review and decide which is canonical\n\n")
            f.write("---\n\n")

        # Low impact duplicates
        f.write(f"## Low Impact Duplicates ({len(low_impact)} groups)\n\n")
        f.write("These providers are NOT connected to any cases - safe to deduplicate.\n\n")

        for i, group in enumerate(low_impact, 1):
            f.write(f"### {i}. Normalized: `{group['normalized_name']}`\n\n")
            f.write(f"**Providers ({len(group['providers'])}):**\n")
            for provider in group['providers']:
                f.write(f"- {provider['name']} (ID: {provider['id']})\n")
            f.write("\n**Recommended Action:** Keep longest/most complete name, delete others\n\n")
            f.write("---\n\n")

        # Summary statistics
        f.write("## Summary Statistics\n\n")
        f.write(f"- Total providers: {len(providers)}\n")
        f.write(f"- Unique providers (after dedup): ~{len(providers) - sum(len(g['providers'])-1 for g in duplicate_groups)}\n")
        f.write(f"- Potential duplicates to remove: ~{sum(len(g['providers'])-1 for g in duplicate_groups)}\n")
        f.write(f"- High impact groups (need review): {len(high_impact)}\n")
        f.write(f"- Low impact groups (safe to auto-dedupe): {len(low_impact)}\n")

    print(f"✓ Detailed report written to: {output_file}")
    print()

    # Print summary to console
    print("="*70)
    print("TOP 20 HIGH-IMPACT DUPLICATE GROUPS")
    print("="*70)
    print()

    for i, group in enumerate(high_impact[:20], 1):
        print(f"{i}. Normalized: '{group['normalized_name']}' - {len(group['providers'])} providers, {group['total_cases_affected']} cases affected")
        for provider in group['providers']:
            status = f"({provider['case_count']} cases)" if provider['connected'] else "(not connected)"
            print(f"   - {provider['name']} {status}")
        print()

    print("="*70)
    print(f"✓ Full report: {output_file}")
    print("="*70)

    return len(potential_duplicates), len(high_impact), len(low_impact)


def import_datetime():
    """Helper to import datetime for report."""
    from datetime import datetime
    return datetime.now().isoformat()


if __name__ == "__main__":
    total, high, low = detect_duplicates()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total duplicate groups found: {total}")
    print(f"  - High impact (connected to cases): {high}")
    print(f"  - Low impact (not connected): {low}")
    print()
    print("✅ Duplicate detection complete")
    print("\n⚠️  NO CHANGES MADE - This was a read-only analysis")
    print("\nReview the report and decide on deduplication strategy.")
