#!/usr/bin/env python3
"""
Detect similar medical providers using fuzzy string matching.

Broader analysis than exact normalization - finds providers that are
similar but might not normalize to exactly the same string.

Examples caught:
- "Jewish Hospital" vs "Jewish Hospital ER"
- "Norton Hospital Downtown" vs "Norton Downtown Hospital"
- "UofL Health - X" vs "UofL Health X"

DOES NOT MODIFY THE GRAPH - Read-only analysis.

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/detect_similar_providers_fuzzy.py
"""

import os
from pathlib import Path
from falkordb import FalkorDB
from rapidfuzz import fuzz
from collections import defaultdict


def get_provider_details(graph, provider_name: str):
    """Get detailed information about a provider."""

    # Get provider properties
    query = """
    MATCH (p:MedicalProvider {name: $name})
    OPTIONAL MATCH (p)-[:PART_OF]->(h:HealthSystem)
    RETURN p.name, id(p), p.specialty, p.address, h.name as health_system
    """

    result = graph.query(query, {'name': provider_name})
    if not result.result_set:
        return None

    row = result.result_set[0]
    details = {
        'name': row[0],
        'id': row[1],
        'specialty': row[2] if len(row) > 2 else None,
        'address': row[3] if len(row) > 3 else None,
        'health_system': row[4] if len(row) > 4 else None
    }

    # Get case connections
    query = """
    MATCH (p:MedicalProvider {name: $name})<-[r]-(c:Case)
    RETURN count(c) as case_count, collect(c.name)[0..5] as sample_cases
    """

    result = graph.query(query, {'name': provider_name})
    if result.result_set:
        details['case_count'] = result.result_set[0][0]
        details['sample_cases'] = result.result_set[0][1] if len(result.result_set[0]) > 1 else []
    else:
        details['case_count'] = 0
        details['sample_cases'] = []

    return details


def find_similar_providers(providers: list, threshold: int = 85):
    """Find similar providers using fuzzy matching."""

    similar_groups = []
    processed = set()

    for i, provider1 in enumerate(providers):
        if provider1['name'] in processed:
            continue

        similar = [provider1]

        for provider2 in providers[i+1:]:
            if provider2['name'] in processed:
                continue

            # Calculate similarity score
            score = fuzz.ratio(provider1['name'].lower(), provider2['name'].lower())

            if score >= threshold:
                similar.append(provider2)
                processed.add(provider2['name'])

        if len(similar) > 1:
            similar_groups.append(similar)
            processed.add(provider1['name'])

    return similar_groups


def analyze_duplicates():
    """Find and analyze similar medical providers."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    print("="*70)
    print("FUZZY MEDICAL PROVIDER DUPLICATE DETECTION")
    print("="*70)
    print()

    # Get all medical providers
    print("Querying all MedicalProvider nodes...")
    result = graph.query("MATCH (p:MedicalProvider) RETURN p.name, id(p) ORDER BY p.name")

    providers = []
    for row in result.result_set:
        providers.append({'name': row[0], 'id': row[1]})

    print(f"✓ Found {len(providers)} MedicalProvider nodes\n")

    # Find similar providers
    print("Running fuzzy matching (threshold: 85%)...")
    similar_groups = find_similar_providers(providers, threshold=85)
    print(f"✓ Found {len(similar_groups)} groups of similar providers\n")

    # Get detailed info for each group
    print("Fetching detailed information...")
    detailed_groups = []

    for group in similar_groups:
        detailed_group = []
        total_cases = 0

        for provider in group:
            details = get_provider_details(graph, provider['name'])
            if details:
                detailed_group.append(details)
                total_cases += details['case_count']

        if detailed_group:
            detailed_groups.append({
                'providers': detailed_group,
                'total_cases': total_cases,
                'provider_count': len(detailed_group)
            })

    print(f"✓ Analyzed {len(detailed_groups)} groups\n")

    # Sort by impact
    detailed_groups.sort(key=lambda x: x['total_cases'], reverse=True)

    # Categorize
    high_impact = [g for g in detailed_groups if g['total_cases'] > 0]
    low_impact = [g for g in detailed_groups if g['total_cases'] == 0]

    print("="*70)
    print("FUZZY MATCHING RESULTS")
    print("="*70)
    print(f"Total groups found: {len(detailed_groups)}")
    print(f"High impact (connected to cases): {len(high_impact)}")
    print(f"Low impact (not connected): {len(low_impact)}")
    print()

    # Write report
    output_file = Path("/mnt/workspace/Reports/medical_provider_fuzzy_duplicates_report.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        from datetime import datetime
        f.write("# Medical Provider Fuzzy Duplicate Detection Report\n\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n")
        f.write(f"**Total Providers:** {len(providers)}\n")
        f.write(f"**Similarity Threshold:** 85%\n")
        f.write(f"**Similar Groups Found:** {len(detailed_groups)}\n\n")
        f.write("---\n\n")

        # High impact
        f.write(f"## High Impact Similar Providers ({len(high_impact)} groups)\n\n")
        f.write("These providers are connected to active cases.\n\n")

        for i, group in enumerate(high_impact, 1):
            f.write(f"### {i}. Group ({group['provider_count']} providers, {group['total_cases']} cases)\n\n")

            for provider in group['providers']:
                f.write(f"#### {provider['name']}\n\n")
                f.write(f"- **ID:** {provider['id']}\n")
                f.write(f"- **Cases:** {provider['case_count']}\n")
                if provider['sample_cases']:
                    f.write(f"- **Sample Cases:** {', '.join(provider['sample_cases'])}\n")
                if provider['specialty']:
                    f.write(f"- **Specialty:** {provider['specialty']}\n")
                if provider['address']:
                    f.write(f"- **Address:** {provider['address']}\n")
                if provider['health_system']:
                    f.write(f"- **Health System:** {provider['health_system']}\n")
                f.write("\n")

            f.write("**Decision Needed:**\n")
            f.write("- [ ] Keep all (different locations/departments)\n")
            f.write("- [ ] Merge into one (same entity, name variation)\n")
            f.write("- [ ] Other action\n\n")
            f.write("---\n\n")

        # Low impact
        f.write(f"## Low Impact Similar Providers ({len(low_impact)} groups)\n\n")
        f.write("These providers are NOT connected to any cases - safe to auto-merge.\n\n")

        for i, group in enumerate(low_impact, 1):
            f.write(f"### {i}. Group ({group['provider_count']} providers)\n\n")

            for provider in group['providers']:
                f.write(f"- **{provider['name']}** (ID: {provider['id']})\n")
                if provider['address']:
                    f.write(f"  - Address: {provider['address']}\n")
                if provider['health_system']:
                    f.write(f"  - System: {provider['health_system']}\n")

            f.write("\n**Recommended:** Keep longest name, delete others\n\n")
            f.write("---\n\n")

        # Statistics
        f.write("## Summary\n\n")
        total_duplicates = sum(g['provider_count'] - 1 for g in detailed_groups)
        f.write(f"- Total providers: {len(providers)}\n")
        f.write(f"- Providers in duplicate groups: {sum(g['provider_count'] for g in detailed_groups)}\n")
        f.write(f"- Potential duplicates to merge: {total_duplicates}\n")
        f.write(f"- Estimated unique providers after dedup: ~{len(providers) - total_duplicates}\n")
        f.write(f"- High impact merges (need review): {len(high_impact)}\n")
        f.write(f"- Low impact merges (safe to auto): {len(low_impact)}\n")

    print(f"✓ Detailed fuzzy matching report: {output_file}\n")

    # Print high-impact groups to console
    if high_impact:
        print("="*70)
        print("HIGH-IMPACT DUPLICATE GROUPS (REQUIRE REVIEW)")
        print("="*70)
        print()

        for i, group in enumerate(high_impact, 1):
            print(f"{i}. {group['provider_count']} providers, {group['total_cases']} cases affected:")
            for provider in group['providers']:
                conn_status = f"({provider['case_count']} cases)" if provider['case_count'] > 0 else "(not connected)"
                addr_info = f" | {provider['address'][:40]}..." if provider['address'] else ""
                print(f"   - {provider['name']} {conn_status}{addr_info}")
            print()

    print("="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nTotal similar groups: {len(detailed_groups)}")
    print(f"  - High impact: {len(high_impact)} (require manual review)")
    print(f"  - Low impact: {len(low_impact)} (safe to auto-merge)")
    print(f"\nPotential duplicates to merge: ~{sum(g['provider_count'] - 1 for g in detailed_groups)}")
    print(f"Estimated providers after dedup: ~{len(providers) - sum(g['provider_count'] - 1 for g in detailed_groups)}")

    return detailed_groups, high_impact, low_impact


if __name__ == "__main__":
    all_groups, high, low = analyze_duplicates()

    print("\n✅ Fuzzy duplicate detection complete")
    print("⚠️  NO CHANGES MADE - Read-only analysis")
    print("\nReports generated:")
    print("  - /mnt/workspace/Reports/medical_provider_duplicates_report.md (exact normalization)")
    print("  - /mnt/workspace/Reports/medical_provider_fuzzy_duplicates_report.md (fuzzy matching)")
