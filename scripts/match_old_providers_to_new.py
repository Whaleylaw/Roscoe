#!/usr/bin/env python3
"""
Match original case-data providers to new healthcare system providers.

Strategy:
- OLD providers: No PART_OF relationship (from case notes)
- NEW providers: Have PART_OF → HealthSystem (from healthcare import)

Find where new providers are better/more detailed versions of old ones.

DOES NOT MODIFY THE GRAPH - Read-only analysis.

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/match_old_providers_to_new.py
"""

import os
import re
from pathlib import Path
from falkordb import FalkorDB
from rapidfuzz import fuzz


def normalize_provider_name(name: str) -> str:
    """Normalize provider name for matching."""
    name = name.lower()
    # Remove common prefixes
    name = re.sub(r'^(uofl|university of louisville|st\.?|saint)\s+', '', name)
    # Remove health/healthcare/medical
    name = re.sub(r'\s+(health|healthcare|medical (group|center|associates))\s*-?\s*', ' ', name)
    # Remove "&" and "and"
    name = re.sub(r'\s+(&|and)\s+', ' ', name)
    # Remove apostrophes
    name = re.sub(r"'s?\b", '', name)
    # Remove dashes and periods
    name = re.sub(r'[-\.]', ' ', name)
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name)
    return name.strip()


def get_provider_info(graph, provider_name: str, provider_id: int):
    """Get detailed provider information."""

    # Check for PART_OF relationship
    query = """
    MATCH (p:MedicalProvider {name: $name})
    OPTIONAL MATCH (p)-[:PART_OF]->(h:HealthSystem)
    RETURN p.specialty, p.address, p.phone, h.name as health_system
    """

    result = graph.query(query, {'name': provider_name})

    info = {
        'name': provider_name,
        'id': provider_id,
        'specialty': None,
        'address': None,
        'phone': None,
        'health_system': None,
        'has_parent': False
    }

    if result.result_set:
        row = result.result_set[0]
        info['specialty'] = row[0] if row[0] else None
        info['address'] = row[1] if row[1] else None
        info['phone'] = row[2] if row[2] else None
        info['health_system'] = row[3] if row[3] else None
        info['has_parent'] = info['health_system'] is not None

    # Get case connections
    query = """
    MATCH (p:MedicalProvider {name: $name})<-[r:TREATING_AT]-(c:Case)
    RETURN count(c) as case_count, collect(c.name)[0..5] as sample_cases
    """

    result = graph.query(query, {'name': provider_name})
    if result.result_set:
        info['case_count'] = result.result_set[0][0]
        info['sample_cases'] = result.result_set[0][1] if len(result.result_set[0]) > 1 else []
    else:
        info['case_count'] = 0
        info['sample_cases'] = []

    return info


def find_best_match(old_provider: dict, new_providers: list) -> dict:
    """Find best matching new provider for an old provider."""

    old_name = old_provider['name']
    old_norm = normalize_provider_name(old_name)

    best_match = None
    best_score = 0
    best_reason = ""

    for new_provider in new_providers:
        new_name = new_provider['name']
        new_norm = normalize_provider_name(new_name)

        # Calculate similarity
        score = fuzz.ratio(old_norm, new_norm)

        # Also check if old name is substring of new name (e.g., "UofL Hospital" in "UofL Health - Mary & Elizabeth Hospital")
        substring_match = False
        if len(old_norm) >= 10 and old_norm in new_norm:
            score = max(score, 90)  # Boost score for substring matches
            substring_match = True

        # Prefer matches within same health system if known
        system_bonus = 0
        if old_provider['health_system'] and new_provider['health_system']:
            if old_provider['health_system'] == new_provider['health_system']:
                system_bonus = 10

        adjusted_score = score + system_bonus

        if adjusted_score > best_score:
            best_score = adjusted_score
            best_match = new_provider

            if substring_match:
                best_reason = f"Substring match ({score}%)"
            elif system_bonus > 0:
                best_reason = f"Same system + {score}% similarity"
            else:
                best_reason = f"{score}% similarity"

    if best_match and best_score >= 75:  # Lower threshold for matching
        return {
            'new_provider': best_match,
            'score': best_score,
            'reason': best_reason
        }

    return None


def analyze_old_vs_new():
    """Match old providers to new providers."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    print("="*70)
    print("OLD vs NEW PROVIDER MATCHING")
    print("="*70)
    print()

    # Get OLD providers (no PART_OF relationship)
    print("Querying OLD providers (no PART_OF relationship)...")
    query = """
    MATCH (p:MedicalProvider)
    WHERE NOT (p)-[:PART_OF]->(:HealthSystem)
    RETURN p.name, id(p)
    ORDER BY p.name
    """

    result = graph.query(query)
    old_providers = []
    for row in result.result_set:
        old_providers.append({'name': row[0], 'id': row[1]})

    print(f"✓ Found {len(old_providers)} OLD providers (from case data)\n")

    # Get NEW providers (have PART_OF relationship)
    print("Querying NEW providers (with PART_OF → HealthSystem)...")
    query = """
    MATCH (p:MedicalProvider)-[:PART_OF]->(h:HealthSystem)
    RETURN p.name, id(p), h.name
    ORDER BY p.name
    """

    result = graph.query(query)
    new_providers = []
    for row in result.result_set:
        new_providers.append({'name': row[0], 'id': row[1], 'health_system': row[2]})

    print(f"✓ Found {len(new_providers)} NEW providers (from healthcare systems)\n")

    # Get detailed info for old providers
    print("Fetching detailed information for OLD providers...")
    old_providers_detailed = []
    for provider in old_providers:
        info = get_provider_info(graph, provider['name'], provider['id'])
        old_providers_detailed.append(info)

    print(f"✓ Analyzed {len(old_providers_detailed)} OLD providers\n")

    # Filter to only OLD providers that are connected to cases
    old_connected = [p for p in old_providers_detailed if p['case_count'] > 0]
    old_not_connected = [p for p in old_providers_detailed if p['case_count'] == 0]

    print(f"  - Connected to cases: {len(old_connected)}")
    print(f"  - Not connected: {len(old_not_connected)}\n")

    # Get detailed info for new providers
    print("Fetching detailed information for NEW providers...")
    new_providers_detailed = []
    for provider in new_providers:
        info = get_provider_info(graph, provider['name'], provider['id'])
        new_providers_detailed.append(info)

    print(f"✓ Analyzed {len(new_providers_detailed)} NEW providers\n")

    # Match old to new
    print("Matching OLD providers to NEW providers...")
    matches = []

    for old_provider in old_connected:  # Focus on connected ones first
        match = find_best_match(old_provider, new_providers_detailed)
        if match:
            matches.append({
                'old': old_provider,
                'new': match['new_provider'],
                'score': match['score'],
                'reason': match['reason']
            })

    print(f"✓ Found {len(matches)} potential matches\n")

    # Sort by case impact (most cases first)
    matches.sort(key=lambda x: x['old']['case_count'], reverse=True)

    # Generate report
    output_file = Path("/mnt/workspace/Reports/old_to_new_provider_mapping.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        from datetime import datetime
        f.write("# Old Provider → New Provider Mapping\n\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n")
        f.write(f"**Old Providers (from case data):** {len(old_connected)} connected to cases\n")
        f.write(f"**New Providers (from healthcare systems):** {len(new_providers_detailed)}\n")
        f.write(f"**Potential Matches Found:** {len(matches)}\n\n")
        f.write("---\n\n")

        f.write("## Strategy\n\n")
        f.write("**OLD providers** were created from case notes (e.g., 'UofL Hospital', 'Norton Radiology').\n\n")
        f.write("**NEW providers** are from official healthcare system rosters with complete info:\n")
        f.write("- Full official names\n")
        f.write("- Complete addresses\n")
        f.write("- Parent health system links\n")
        f.write("- Department/specialty info\n\n")
        f.write("**Goal:** Replace old generic providers with new detailed ones.\n\n")
        f.write("---\n\n")

        # Write matches by system
        by_system = {}
        for match in matches:
            system = match['new']['health_system'] or "Unknown"
            if system not in by_system:
                by_system[system] = []
            by_system[system].append(match)

        for system in ["Norton Healthcare", "UofL Health", "Baptist Health", "St. Elizabeth Healthcare", "CHI Saint Joseph Health", "Unknown"]:
            if system not in by_system:
                continue

            system_matches = by_system[system]
            f.write(f"## {system} ({len(system_matches)} matches)\n\n")

            for i, match in enumerate(system_matches, 1):
                old = match['old']
                new = match['new']

                f.write(f"### {i}. {old['name']}\n\n")
                f.write(f"**OLD Provider:**\n")
                f.write(f"- Name: {old['name']}\n")
                f.write(f"- ID: {old['id']}\n")
                f.write(f"- Cases: {old['case_count']}\n")
                if old['sample_cases']:
                    f.write(f"- Sample Cases: {', '.join(old['sample_cases'][:3])}\n")
                if old['specialty']:
                    f.write(f"- Specialty: {old['specialty']}\n")
                if old['address']:
                    f.write(f"- Address: {old['address']}\n")
                f.write(f"- Health System: {old['health_system'] or 'None'}\n")
                f.write("\n")

                f.write(f"**NEW Provider (suggested replacement):**\n")
                f.write(f"- Name: {new['name']}\n")
                f.write(f"- ID: {new['id']}\n")
                f.write(f"- Health System: {new['health_system']}\n")
                if new['specialty']:
                    f.write(f"- Specialty: {new['specialty']}\n")
                if new['address']:
                    f.write(f"- Address: {new['address']}\n")
                if new['phone']:
                    f.write(f"- Phone: {new['phone']}\n")
                f.write("\n")

                f.write(f"**Match Quality:** {match['score']:.0f}% - {match['reason']}\n\n")

                f.write(f"**Decision:**\n")
                f.write(f"- [ ] REPLACE old with new (update {old['case_count']} case relationships)\n")
                f.write(f"- [ ] KEEP BOTH (different entities)\n")
                f.write(f"- [ ] REVIEW (need more info)\n\n")
                f.write("---\n\n")

        # Summary statistics
        f.write("## Summary Statistics\n\n")
        f.write(f"- Total old providers (connected to cases): {len(old_connected)}\n")
        f.write(f"- Potential matches found: {len(matches)}\n")
        f.write(f"- Old providers without matches: {len(old_connected) - len(matches)}\n")
        f.write(f"- Total cases affected if all replaced: {sum(m['old']['case_count'] for m in matches)}\n")
        f.write("\n")

        # By system
        f.write("### Matches by Health System\n\n")
        for system, system_matches in by_system.items():
            total_cases = sum(m['old']['case_count'] for m in system_matches)
            f.write(f"- **{system}**: {len(system_matches)} matches, {total_cases} cases affected\n")

    print(f"✓ Report written to: {output_file}\n")

    # Print summary to console
    print("="*70)
    print("MATCHING SUMMARY")
    print("="*70)
    print(f"Old providers (from case data): {len(old_connected)}")
    print(f"New providers (from healthcare systems): {len(new_providers_detailed)}")
    print(f"Potential matches found: {len(matches)}")
    print()

    print("Top 20 matches by case impact:")
    print("-" * 70)
    for i, match in enumerate(matches[:20], 1):
        old = match['old']
        new = match['new']
        print(f"{i}. OLD: {old['name'][:40]:<40} ({old['case_count']} cases)")
        print(f"   NEW: {new['name'][:40]:<40} [{new['health_system']}]")
        print(f"   Match: {match['score']:.0f}% - {match['reason']}")
        print()

    print("="*70)
    print(f"✓ Full report: {output_file}")
    print("="*70)

    # Also create a CSV for easy review
    csv_file = Path("/mnt/workspace/Reports/old_to_new_mapping.csv")
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("old_name,old_id,old_cases,new_name,new_id,new_system,match_score,decision\n")
        for match in matches:
            old = match['old']
            new = match['new']
            f.write(f'"{old["name"]}",{old["id"]},{old["case_count"]},"{new["name"]}",{new["id"]},"{new["health_system"] or ""}",{match["score"]:.0f},\n')

    print(f"\n✓ CSV export: {csv_file}")

    return matches, old_connected, new_providers_detailed


if __name__ == "__main__":
    matches, old_providers, new_providers = analyze_old_vs_new()

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nTotal old providers: {len(old_providers)}")
    print(f"Total new providers: {len(new_providers)}")
    print(f"Potential replacements: {len(matches)}")
    print()
    print("✅ Matching complete")
    print("⚠️  NO CHANGES MADE - Read-only analysis")
    print("\nReview the report and mark your decisions.")
