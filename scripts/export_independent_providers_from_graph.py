#!/usr/bin/env python3
"""
Export independent provider information from graph.

For the 214 independent providers in medical-providers-DEDUPLICATED.json,
query the graph to get their complete information and create a clean
provider reference list (no case context).

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/export_independent_providers_from_graph.py
"""

import json
import os
from pathlib import Path
from falkordb import FalkorDB


def get_provider_from_graph(graph, provider_name: str) -> dict:
    """Query graph for provider information."""

    query = """
    MATCH (p:MedicalProvider {name: $name})
    OPTIONAL MATCH (p)-[:PART_OF]->(h:HealthSystem)
    RETURN p.name, id(p), p.specialty, p.address, p.phone, p.email,
           p.fax, p.provider_type, h.name as health_system
    """

    result = graph.query(query, {'name': provider_name})

    if not result.result_set:
        return None

    row = result.result_set[0]

    provider_info = {
        'name': row[0],
        'graph_id': row[1],
        'specialty': row[2] if len(row) > 2 and row[2] else None,
        'address': row[3] if len(row) > 3 and row[3] else None,
        'phone': row[4] if len(row) > 4 and row[4] else None,
        'email': row[5] if len(row) > 5 and row[5] else None,
        'fax': row[6] if len(row) > 6 and row[6] else None,
        'provider_type': row[7] if len(row) > 7 and row[7] else None,
        'health_system': row[8] if len(row) > 8 and row[8] else None,
        'in_graph': True
    }

    return provider_info


def main():
    """Export independent providers from graph."""

    # Connect to FalkorDB
    host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    print(f"Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")
    print("✓ Connected\n")

    # Load deduplicated provider list
    dedup_file_paths = [
        Path("/app/workspace_paralegal/json-files/medical-providers-DEDUPLICATED.json"),
        Path("/mnt/workspace/json-files/medical-providers-DEDUPLICATED.json"),
        Path("/tmp/medical-providers-DEDUPLICATED.json"),
    ]

    dedup_file = None
    for p in dedup_file_paths:
        if p.exists():
            dedup_file = p
            break

    if not dedup_file:
        print("❌ medical-providers-DEDUPLICATED.json not found")
        return

    print(f"Loading deduplicated providers from {dedup_file}...")
    with open(dedup_file, 'r', encoding='utf-8') as f:
        deduplicated = json.load(f)

    print(f"✓ Loaded {len(deduplicated)} unique providers\n")

    print("="*70)
    print("QUERYING GRAPH FOR PROVIDER INFORMATION")
    print("="*70)
    print()

    # Query graph for each provider
    provider_entities = []
    found_count = 0
    not_found_count = 0

    for idx, provider_data in enumerate(deduplicated, 1):
        provider_name = provider_data['provider_full_name']

        print(f"{idx}/{len(deduplicated)}: {provider_name[:50]}...", end=' ')

        # Query graph
        graph_info = get_provider_from_graph(graph, provider_name)

        if graph_info:
            # Provider found in graph
            found_count += 1

            # Create entity card
            entity_card = {
                'card_type': 'entity',
                'entity_type': 'MedicalProvider',
                'name': provider_name,
                'attributes': {
                    'specialty': graph_info['specialty'],
                    'address': graph_info['address'],
                    'phone': graph_info['phone'],
                    'email': graph_info['email'],
                    'fax': graph_info['fax'],
                    'provider_type': graph_info['provider_type'],
                    'parent_system': graph_info['health_system']
                },
                'source_id': str(graph_info['graph_id']),
                'source_file': 'graph_export',
                'metadata': {
                    'case_count': len(provider_data.get('cases', [])),
                    'total_cases': provider_data.get('cases', [])
                }
            }

            # Clean up None values
            entity_card['attributes'] = {k: v for k, v in entity_card['attributes'].items() if v is not None}

            provider_entities.append(entity_card)
            print("✓ Found")

        else:
            # Provider not in graph
            not_found_count += 1

            # Create entity card from dedup data only
            entity_card = {
                'card_type': 'entity',
                'entity_type': 'MedicalProvider',
                'name': provider_name,
                'attributes': {
                    'in_graph': False
                },
                'source_id': f"dedup_{idx}",
                'source_file': 'case_data_only',
                'metadata': {
                    'case_count': len(provider_data.get('cases', [])),
                    'total_cases': provider_data.get('cases', [])
                }
            }

            provider_entities.append(entity_card)
            print("⊙ Not in graph")

    print()

    # Save to output file
    output_file = Path("/mnt/workspace/json-files/memory-cards/entities/independent_providers.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(provider_entities, f, indent=2, ensure_ascii=False)

    print("="*70)
    print("EXPORT COMPLETE")
    print("="*70)
    print(f"Total unique providers: {len(deduplicated)}")
    print(f"Found in graph: {found_count}")
    print(f"Not in graph: {not_found_count}")
    print()
    print(f"✓ Saved to: {output_file}")
    print()
    print("✅ Independent providers exported from graph")


if __name__ == "__main__":
    main()
