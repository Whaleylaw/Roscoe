#!/usr/bin/env python3
"""
CourtListener Citation Explorer

Navigates citation networks to find cases that cite a given opinion and cases cited by that opinion.
Useful for building comprehensive legal research around key precedents.

Usage:
    python explore_citations.py 12345 --depth 2
    python explore_citations.py --citation "123 F.3d 456"
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict

# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

API_KEY = os.getenv('COURTLISTENER_API_KEY')
BASE_URL = 'https://www.courtlistener.com/api/rest/v4'


def get_cluster_by_citation(citation_str):
    """
    Find a cluster (case) by citation string.

    Args:
        citation_str: Citation like "123 F.3d 456" or "123 Ky. 789"

    Returns:
        dict: Cluster data or error
    """
    if not API_KEY:
        return {'error': 'COURTLISTENER_API_KEY not found'}

    headers = {'Authorization': f'Token {API_KEY}'}
    params = {'cite': citation_str}

    try:
        response = requests.get(
            f'{BASE_URL}/clusters/',
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if data.get('count', 0) > 0:
            return data['results'][0]
        else:
            return {'error': f'No cases found for citation: {citation_str}'}

    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}


def get_citing_opinions(cluster_id, limit=100):
    """
    Get all opinions that cite this cluster.

    Args:
        cluster_id: The cluster ID to find citations to
        limit: Maximum results

    Returns:
        list: Opinions that cite this cluster
    """
    if not API_KEY:
        return {'error': 'COURTLISTENER_API_KEY not found'}

    headers = {'Authorization': f'Token {API_KEY}'}
    params = {
        'cites': cluster_id,
        'page_size': limit
    }

    try:
        response = requests.get(
            f'{BASE_URL}/opinions/',
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        citing_opinions = []
        for opinion in data.get('results', []):
            citing_opinions.append({
                'id': opinion.get('id'),
                'cluster_id': opinion.get('cluster'),
                'case_name': opinion.get('cluster_name'),
                'court': opinion.get('court'),
                'date_filed': opinion.get('date_filed'),
                'type': opinion.get('type'),
                'url': f"https://www.courtlistener.com{opinion.get('absolute_url', '')}"
            })

        return citing_opinions

    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}


def get_cited_opinions(cluster_id):
    """
    Get all opinions cited by this cluster.

    Args:
        cluster_id: The cluster ID to find citations from

    Returns:
        list: Opinions cited by this cluster
    """
    if not API_KEY:
        return {'error': 'COURTLISTENER_API_KEY not found'}

    headers = {'Authorization': f'Token {API_KEY}'}

    try:
        # First get the cluster details
        response = requests.get(
            f'{BASE_URL}/clusters/{cluster_id}/',
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        cluster = response.json()

        # Get opinions in this cluster
        sub_opinions = cluster.get('sub_opinions', [])

        cited_opinions = []
        for opinion_url in sub_opinions:
            # Get opinion details
            opinion_resp = requests.get(opinion_url, headers=headers, timeout=30)
            opinion_resp.raise_for_status()
            opinion = opinion_resp.json()

            # Get opinions this opinion cites
            for cited_url in opinion.get('opinions_cited', []):
                cited_resp = requests.get(cited_url, headers=headers, timeout=30)
                cited_resp.raise_for_status()
                cited = cited_resp.json()

                cited_opinions.append({
                    'id': cited.get('id'),
                    'cluster_id': cited.get('cluster'),
                    'case_name': cited.get('cluster_name'),
                    'court': cited.get('court'),
                    'date_filed': cited.get('date_filed'),
                    'url': f"https://www.courtlistener.com{cited.get('absolute_url', '')}"
                })

        return cited_opinions

    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}


def explore_citation_network(cluster_id, depth=1, max_per_level=50):
    """
    Recursively explore citation network.

    Args:
        cluster_id: Starting cluster ID
        depth: How many levels to explore (1 = immediate citations only)
        max_per_level: Maximum cases to explore per level

    Returns:
        dict: Citation network data
    """
    if not API_KEY:
        return {'error': 'COURTLISTENER_API_KEY not found'}

    headers = {'Authorization': f'Token {API_KEY}'}

    try:
        # Get root case info
        response = requests.get(
            f'{BASE_URL}/clusters/{cluster_id}/',
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        root = response.json()

        network = {
            'root_case': {
                'id': root.get('id'),
                'case_name': root.get('case_name'),
                'court': root.get('court'),
                'date_filed': root.get('date_filed'),
                'citations': root.get('citations', []),
                'url': f"https://www.courtlistener.com{root.get('absolute_url', '')}"
            },
            'citing_cases': [],
            'cited_cases': [],
            'network_depth': depth
        }

        # Get cases citing this one
        citing = get_citing_opinions(cluster_id, limit=max_per_level)
        if isinstance(citing, list):
            network['citing_cases'] = citing[:max_per_level]

        # Get cases cited by this one
        cited = get_cited_opinions(cluster_id)
        if isinstance(cited, list):
            network['cited_cases'] = cited[:max_per_level]

        # If depth > 1, recursively explore (limited to prevent explosion)
        if depth > 1:
            network['second_level_citing'] = []
            for case in network['citing_cases'][:10]:  # Limit to top 10
                sub_citing = get_citing_opinions(case['cluster_id'], limit=20)
                if isinstance(sub_citing, list):
                    network['second_level_citing'].extend(sub_citing[:20])

        return network

    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}


def main():
    parser = argparse.ArgumentParser(
        description='Explore CourtListener citation networks'
    )
    parser.add_argument('cluster_id', nargs='?', type=int,
                       help='Cluster ID to explore')
    parser.add_argument('--citation', help='Citation string (e.g., "123 F.3d 456")')
    parser.add_argument('--depth', type=int, default=1,
                       help='Depth of citation exploration (default 1)')
    parser.add_argument('--limit', type=int, default=50,
                       help='Maximum cases per level (default 50)')
    parser.add_argument('--json', action='store_true',
                       help='Output raw JSON')

    args = parser.parse_args()

    # Get cluster ID from citation if provided
    cluster_id = args.cluster_id
    if args.citation:
        cluster = get_cluster_by_citation(args.citation)
        if 'error' in cluster:
            print(f"ERROR: {cluster['error']}", file=sys.stderr)
            sys.exit(1)
        cluster_id = cluster.get('id')

    if not cluster_id:
        parser.print_help()
        sys.exit(1)

    # Explore citation network
    network = explore_citation_network(cluster_id, depth=args.depth, max_per_level=args.limit)

    if args.json:
        print(json.dumps(network, indent=2))
    else:
        # Pretty print results
        if 'error' in network:
            print(f"ERROR: {network['error']}", file=sys.stderr)
            sys.exit(1)

        root = network['root_case']
        print(f"\n{'='*80}")
        print(f"ROOT CASE: {root['case_name']}")
        print(f"Court: {root['court']}")
        print(f"Date: {root['date_filed']}")
        if root['citations']:
            print(f"Citations: {', '.join(root['citations'])}")
        print(f"URL: {root['url']}")
        print(f"{'='*80}\n")

        print(f"CASES CITING THIS OPINION ({len(network['citing_cases'])} found):")
        print("-" * 80)
        for i, case in enumerate(network['citing_cases'][:20], 1):
            print(f"{i}. {case['case_name']}")
            print(f"   Court: {case['court']} | Date: {case['date_filed']}")
            print(f"   URL: {case['url']}")
            print()

        print(f"\nCASES CITED BY THIS OPINION ({len(network['cited_cases'])} found):")
        print("-" * 80)
        for i, case in enumerate(network['cited_cases'][:20], 1):
            print(f"{i}. {case['case_name']}")
            print(f"   Court: {case['court']} | Date: {case['date_filed']}")
            print(f"   URL: {case['url']}")
            print()

        if args.depth > 1 and 'second_level_citing' in network:
            print(f"\nSECOND-LEVEL CITATIONS ({len(network['second_level_citing'])} found):")
            print("-" * 80)
            for i, case in enumerate(network['second_level_citing'][:10], 1):
                print(f"{i}. {case['case_name']}")
                print(f"   Court: {case['court']} | Date: {case['date_filed']}")
                print()


if __name__ == '__main__':
    main()
