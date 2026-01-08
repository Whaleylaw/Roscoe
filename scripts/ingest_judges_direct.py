#!/usr/bin/env python3
"""
Ingest judges to FalkorDB with PRESIDES_OVER relationships to divisions.

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/ingest_judges_direct.py

Ingests:
- 101 CircuitJudge → PRESIDES_OVER → CircuitDivision
- 94 DistrictJudge → PRESIDES_OVER → DistrictDivision
- 15 AppellateJudge → PRESIDES_OVER → AppellateDistrict
- 8 SupremeCourtJustice → PRESIDES_OVER → SupremeCourtDistrict

Total: 218 judges (was 316, revised after checking files)
"""

import json
import os
from pathlib import Path
from falkordb import FalkorDB


def ingest_judges():
    """Ingest all judges with PRESIDES_OVER relationships."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    # Find JSON files
    entities_dir = Path("/mnt/workspace/json-files/memory-cards/entities")

    judge_files = [
        ("CircuitJudge", "circuit_judges.json", "CircuitDivision"),
        ("DistrictJudge", "district_judges.json", "DistrictDivision"),
        ("AppellateJudge", "appellate_judges.json", "AppellateDistrict"),
        ("SupremeCourtJustice", "supreme_court_justices.json", "SupremeCourtDistrict"),
    ]

    print("="*70)
    print("JUDGES INGESTION - PHASE 1c")
    print("="*70)
    print()

    # Pre-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_before = result.result_set[0][0]
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    rels_before = result.result_set[0][0]

    print(f"Nodes before: {nodes_before:,}")
    print(f"Relationships before: {rels_before:,}\n")

    all_stats = {'created': 0, 'matched': 0, 'relationships': 0, 'errors': []}

    for entity_type, filename, division_type in judge_files:
        file_path = entities_dir / filename

        if not file_path.exists():
            print(f"⚠️  File not found: {filename}\n")
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            judges = json.load(f)

        print(f"{entity_type}: {len(judges)} entities")
        print("-" * 70)

        stats = {'created': 0, 'matched': 0, 'relationships': 0, 'missing_divisions': []}

        for judge in judges:
            name = judge['name']
            attrs = judge.get('attributes', {})

            try:
                # Create judge node
                query = f"""
                MERGE (j:{entity_type} {{name: $name, group_id: $group_id}})
                ON CREATE SET j += $props, j.created_at = timestamp()
                ON MATCH SET j.updated_at = timestamp()
                RETURN j.name, id(j)
                """

                params = {
                    'name': name,
                    'group_id': 'roscoe_graph',
                    'props': attrs
                }

                result = graph.query(query, params)

                if result.nodes_created > 0:
                    stats['created'] += 1
                    status = "Created"
                else:
                    stats['matched'] += 1
                    status = "Exists"

                # Create PRESIDES_OVER relationship to division
                # Find division name in attributes
                division_name = None

                if entity_type == "CircuitJudge":
                    # Circuit judges have division info in attributes
                    circuit = attrs.get('circuit', '')  # e.g., "Cir. 30, Div. 02"
                    county = attrs.get('county', '')

                    # Try to construct division name
                    if county and 'Div.' in circuit:
                        # Extract division number
                        import re
                        div_match = re.search(r'Div\.\s*(\d+)', circuit)
                        if div_match:
                            div_num = div_match.group(1).zfill(2)  # Zero-pad
                            # Handle multi-county circuits - use first county
                            first_county = county.split('/')[0].strip() if '/' in county else county
                            division_name = f"{first_county} County Circuit Court, Division {div_num.lstrip('0') if div_num != '01' else 'I'}"

                elif entity_type == "DistrictJudge":
                    # District judges have district info
                    district = attrs.get('district', '')
                    county = attrs.get('county', '')

                    if county:
                        # Most district courts don't have divisions in the name
                        # Check if division number specified
                        import re
                        div_match = re.search(r'Div\.\s*(\d+)', district)
                        if div_match:
                            div_num = div_match.group(1).zfill(2)
                            division_name = f"{county} County District Court, Division {div_num}"
                        else:
                            division_name = f"{county} County District Court"

                elif entity_type == "AppellateJudge":
                    # Appellate judges - use office from attributes
                    office = attrs.get('office', '')
                    if office:
                        division_name = f"Kentucky Court of Appeals, {office} Office"

                elif entity_type == "SupremeCourtJustice":
                    # Supreme Court justices - use district number
                    district_num = attrs.get('district', '')
                    if district_num:
                        division_name = f"Kentucky Supreme Court, District {district_num}"

                # Create PRESIDES_OVER relationship if division found
                if division_name:
                    rel_query = f"""
                    MATCH (j:{entity_type} {{name: $judge_name}})
                    MATCH (d:{division_type} {{name: $division_name}})
                    MERGE (j)-[:PRESIDES_OVER]->(d)
                    """

                    rel_params = {
                        'judge_name': name,
                        'division_name': division_name
                    }

                    try:
                        rel_result = graph.query(rel_query, rel_params)
                        if rel_result.relationships_created > 0:
                            stats['relationships'] += 1
                            print(f"  ✓ {status}: {name} → {division_name}")
                        else:
                            # Division not found
                            stats['missing_divisions'].append(f"{name} → {division_name}")
                            print(f"  ⊙ {status}: {name} (division not found: {division_name[:40]}...)")
                    except Exception as e:
                        stats['missing_divisions'].append(f"{name} → {division_name}: {str(e)}")
                        print(f"  ⊙ {status}: {name} (relationship error)")
                else:
                    print(f"  ⊙ {status}: {name} (no division info)")

            except Exception as e:
                error_msg = f"{name}: {str(e)}"
                all_stats['errors'].append(error_msg)
                print(f"  ❌ Error: {name[:40]}... - {str(e)[:50]}")

        all_stats['created'] += stats['created']
        all_stats['matched'] += stats['matched']
        all_stats['relationships'] += stats['relationships']

        print(f"\n  Summary: Created={stats['created']}, Matched={stats['matched']}, Relationships={stats['relationships']}")
        if stats['missing_divisions']:
            print(f"  Missing divisions: {len(stats['missing_divisions'])}")
        print()

    # Post-check
    result = graph.query("MATCH (n) RETURN count(n) as total")
    nodes_after = result.result_set[0][0]
    result = graph.query("MATCH ()-[r]->() RETURN count(r) as total")
    rels_after = result.result_set[0][0]

    nodes_added = nodes_after - nodes_before
    rels_added = rels_after - rels_before

    # Check Abby Sitgraves (canary)
    result = graph.query('MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-() RETURN count(r)')
    abby_rels = result.result_set[0][0]

    print("="*70)
    print("INGESTION COMPLETE")
    print("="*70)
    print(f"Nodes before: {nodes_before:,}")
    print(f"Nodes after: {nodes_after:,}")
    print(f"Nodes added: {nodes_added:,}")
    print()
    print(f"Relationships before: {rels_before:,}")
    print(f"Relationships after: {rels_after:,}")
    print(f"Relationships added: {rels_added:,}")
    print()
    print(f"Created: {all_stats['created']}")
    print(f"Already existed: {all_stats['matched']}")
    print(f"PRESIDES_OVER relationships: {all_stats['relationships']}")
    print(f"Errors: {len(all_stats['errors'])}")
    print()
    print(f"Abby Sitgraves relationships: {abby_rels} (should be 93)")

    if abby_rels != 93:
        print("\n⚠️  WARNING: Abby Sitgraves case relationships changed!")
        return False

    print("\n✅ Phase 1c complete")
    return True


if __name__ == "__main__":
    ingest_judges()
