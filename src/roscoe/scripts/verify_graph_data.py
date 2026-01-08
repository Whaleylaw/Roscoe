#!/usr/bin/env python3
"""
Verify Graph Data for All Cases

Queries the graph for each case and outputs what data exists,
making it easy to compare against the source JSON files.

Usage:
    # Run inside roscoe-agents container
    python -m roscoe.scripts.verify_graph_data
    
    # Output to file
    python -m roscoe.scripts.verify_graph_data --output /mnt/workspace/graph_verification.json
    
    # Query specific case
    python -m roscoe.scripts.verify_graph_data --case "Muhammad-Alif-MVA-12-09-2022"
"""

import asyncio
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any


async def get_all_cases() -> List[str]:
    """Get list of all case names from the graph."""
    from roscoe.core.graphiti_client import run_cypher_query
    
    query = """
        MATCH (c:Entity {entity_type: 'Case'})
        RETURN c.name as case_name
        ORDER BY c.name
    """
    results = await run_cypher_query(query, {})
    return [r['case_name'] for r in results]


async def get_case_data(case_name: str) -> Dict[str, Any]:
    """Get all data for a single case from the graph."""
    from roscoe.core.graphiti_client import run_cypher_query
    
    data = {
        'case_name': case_name,
        'client': None,
        'insurance_claims': [],
        'medical_providers': [],
        'liens': [],
        'litigation': [],
        'counts': {},
    }
    
    # Get client
    client_query = """
        MATCH (case:Entity {entity_type: 'Case', name: $case_name})-[:HAS_CLIENT]->(client:Entity {entity_type: 'Client'})
        RETURN client.name as name, client.phone as phone, client.email as email
        LIMIT 1
    """
    client_results = await run_cypher_query(client_query, {"case_name": case_name})
    if client_results:
        data['client'] = client_results[0]
    
    # Get insurance claims
    insurance_query = """
        MATCH (case:Entity {entity_type: 'Case', name: $case_name})-[:HAS_CLAIM]->(claim:Entity {entity_type: 'InsuranceClaim'})
        OPTIONAL MATCH (claim)-[:INSURED_BY]->(insurer:Entity {entity_type: 'Insurer'})
        OPTIONAL MATCH (claim)-[:ASSIGNED_ADJUSTER]->(adjuster:Entity {entity_type: 'Adjuster'})
        RETURN claim.name as claim_number, 
               claim.claim_type as claim_type,
               insurer.name as insurer,
               adjuster.name as adjuster
    """
    insurance_results = await run_cypher_query(insurance_query, {"case_name": case_name})
    data['insurance_claims'] = insurance_results
    
    # Get medical providers (Case -TREATING_AT-> Provider)
    provider_query = """
        MATCH (case:Entity {entity_type: 'Case', name: $case_name})-[:TREATING_AT]->(provider:Entity {entity_type: 'MedicalProvider'})
        OPTIONAL MATCH (provider)-[:PART_OF]->(org:Entity {entity_type: 'Organization'})
        RETURN provider.name as name, 
               provider.specialty as specialty,
               org.name as parent_org
    """
    provider_results = await run_cypher_query(provider_query, {"case_name": case_name})
    data['medical_providers'] = provider_results
    
    # Get liens
    lien_query = """
        MATCH (case:Entity {entity_type: 'Case', name: $case_name})-[:HAS_LIEN]->(lien:Entity {entity_type: 'Lien'})
        OPTIONAL MATCH (lien)-[:HELD_BY]->(holder:Entity {entity_type: 'LienHolder'})
        RETURN lien.name as lien_id,
               holder.name as holder,
               lien.lien_type as lien_type,
               lien.amount as amount
    """
    lien_results = await run_cypher_query(lien_query, {"case_name": case_name})
    data['liens'] = lien_results
    
    # Get litigation contacts
    litigation_query = """
        MATCH (case:Entity {entity_type: 'Case', name: $case_name})-[r]->(entity:Entity)
        WHERE entity.entity_type IN ['Attorney', 'Defendant']
        RETURN entity.name as name, 
               entity.entity_type as type,
               entity.role as role
    """
    litigation_results = await run_cypher_query(litigation_query, {"case_name": case_name})
    data['litigation'] = litigation_results
    
    # Get client-level relationships (direct from client, not through case)
    if data['client'] and data['client'].get('name'):
        client_name = data['client']['name']
        
        # Client's total providers (across ALL cases)
        client_providers_query = """
            MATCH (c:Entity {entity_type: 'Client', name: $client_name})-[:TREATED_BY]->(p:Entity {entity_type: 'MedicalProvider'})
            RETURN count(p) as total_providers
        """
        result = await run_cypher_query(client_providers_query, {"client_name": client_name})
        data['client_total_providers'] = result[0].get('total_providers', 0) if result else 0
        
        # Client's total insurers (across ALL cases)
        client_insurers_query = """
            MATCH (c:Entity {entity_type: 'Client', name: $client_name})-[:HAS_INSURANCE_WITH]->(i:Entity {entity_type: 'Insurer'})
            RETURN count(DISTINCT i) as total_insurers
        """
        result = await run_cypher_query(client_insurers_query, {"client_name": client_name})
        data['client_total_insurers'] = result[0].get('total_insurers', 0) if result else 0
    else:
        data['client_total_providers'] = 0
        data['client_total_insurers'] = 0
    
    # Counts summary
    data['counts'] = {
        'has_client': data['client'] is not None,
        'insurance_claims': len(data['insurance_claims']),
        'medical_providers': len(data['medical_providers']),
        'liens': len(data['liens']),
        'litigation_contacts': len(data['litigation']),
        'client_total_providers': data['client_total_providers'],
        'client_total_insurers': data['client_total_insurers'],
    }
    
    return data


async def verify_all_cases(output_file: str = None, single_case: str = None):
    """Verify data for all cases or a single case."""
    
    if single_case:
        cases = [single_case]
    else:
        cases = await get_all_cases()
    
    print(f"\n{'='*60}")
    print(f"GRAPH DATA VERIFICATION")
    print(f"{'='*60}")
    print(f"Total cases: {len(cases)}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    results = []
    summary = {
        'total_cases': len(cases),
        'cases_with_client': 0,
        'cases_with_insurance': 0,
        'cases_with_providers': 0,
        'cases_with_liens': 0,
        'cases_with_litigation': 0,
        'total_claims': 0,
        'total_providers': 0,
        'total_liens': 0,
    }
    
    for i, case_name in enumerate(cases):
        data = await get_case_data(case_name)
        results.append(data)
        
        # Update summary
        counts = data['counts']
        if counts['has_client']:
            summary['cases_with_client'] += 1
        if counts['insurance_claims'] > 0:
            summary['cases_with_insurance'] += 1
            summary['total_claims'] += counts['insurance_claims']
        if counts['medical_providers'] > 0:
            summary['cases_with_providers'] += 1
            summary['total_providers'] += counts['medical_providers']
        if counts['liens'] > 0:
            summary['cases_with_liens'] += 1
            summary['total_liens'] += counts['liens']
        if counts['litigation_contacts'] > 0:
            summary['cases_with_litigation'] += 1
        
        # Print progress
        client_name = data['client']['name'] if data['client'] else 'NO CLIENT'
        print(f"[{i+1:3}/{len(cases)}] {case_name}")
        print(f"         Client: {client_name}")
        print(f"         Claims: {counts['insurance_claims']}, Providers: {counts['medical_providers']}, Liens: {counts['liens']}, Litigation: {counts['litigation_contacts']}")
        # Show client-level totals if different from case-level
        if counts.get('client_total_providers', 0) > counts['medical_providers']:
            print(f"         (Client history: {counts['client_total_providers']} providers across all cases)")
        print()
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total cases:              {summary['total_cases']}")
    print(f"Cases with client:        {summary['cases_with_client']} ({100*summary['cases_with_client']/summary['total_cases']:.1f}%)")
    print(f"Cases with insurance:     {summary['cases_with_insurance']} ({100*summary['cases_with_insurance']/summary['total_cases']:.1f}%)")
    print(f"Cases with providers:     {summary['cases_with_providers']} ({100*summary['cases_with_providers']/summary['total_cases']:.1f}%)")
    print(f"Cases with liens:         {summary['cases_with_liens']} ({100*summary['cases_with_liens']/summary['total_cases']:.1f}%)")
    print(f"Cases with litigation:    {summary['cases_with_litigation']} ({100*summary['cases_with_litigation']/summary['total_cases']:.1f}%)")
    print(f"\nTotal insurance claims:   {summary['total_claims']}")
    print(f"Total medical providers:  {summary['total_providers']}")
    print(f"Total liens:              {summary['total_liens']}")
    print(f"{'='*60}\n")
    
    # Output to file if specified
    if output_file:
        output = {
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'cases': results,
        }
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"Results written to: {output_file}")
    
    return results, summary


def main():
    parser = argparse.ArgumentParser(description='Verify graph data for all cases')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--case', '-c', help='Query specific case name')
    args = parser.parse_args()
    
    asyncio.run(verify_all_cases(
        output_file=args.output,
        single_case=args.case
    ))


if __name__ == "__main__":
    main()
