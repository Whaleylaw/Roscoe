#!/usr/bin/env python3
"""
CourtListener Case Law Search Tool

Searches for legal opinions by keyword, court, date range, and precedential status.
Useful for legal research when writing briefs or responding to motions.

Usage:
    python search_case_law.py "negligence standard of care" --courts "kyctapp,ked,kwd" --precedential
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory (outside workspace)
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

API_KEY = os.getenv('COURTLISTENER_API_KEY')
BASE_URL = 'https://www.courtlistener.com/api/rest/v4'

# Kentucky courts mapping
KENTUCKY_COURTS = {
    'ky': 'Kentucky Supreme Court',
    'kyctapp': 'Kentucky Court of Appeals',
    'ked': 'U.S. District Court, Eastern District of Kentucky',
    'kwd': 'U.S. District Court, Western District of Kentucky',
    'ca6': 'U.S. Court of Appeals, Sixth Circuit'
}


def search_opinions(query, courts=None, after_date=None, before_date=None,
                   precedential=None, order_by='score', limit=20):
    """
    Search CourtListener for legal opinions.

    Args:
        query: Search query string (supports Boolean operators)
        courts: List of court IDs (e.g., ['ky', 'kyctapp', 'ked'])
        after_date: ISO date string (YYYY-MM-DD) for results after this date
        before_date: ISO date string (YYYY-MM-DD) for results before this date
        precedential: Filter by precedential status (True/False/None)
        order_by: Sort order ('score', '-dateFiled', 'citeCount')
        limit: Maximum results to return (default 20)

    Returns:
        dict: Search results with opinions
    """
    if not API_KEY:
        return {'error': 'COURTLISTENER_API_KEY not found in environment'}

    # Build query parameters
    params = {
        'q': query,
        'type': 'o',  # 'o' for opinions
        'order_by': order_by,
        'page_size': limit
    }

    if courts:
        # Convert list to comma-separated string
        params['court'] = ','.join(courts) if isinstance(courts, list) else courts

    if after_date:
        params['filed_after'] = after_date

    if before_date:
        params['filed_before'] = before_date

    if precedential is not None:
        params['stat'] = 'Published' if precedential else 'Unpublished'

    # Make API request
    headers = {'Authorization': f'Token {API_KEY}'}

    try:
        response = requests.get(
            f'{BASE_URL}/search/',
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        # Format results for readability
        results = {
            'count': data.get('count', 0),
            'query': query,
            'courts_searched': [KENTUCKY_COURTS.get(c, c) for c in (courts or [])],
            'opinions': []
        }

        for result in data.get('results', []):
            opinion = {
                'id': result.get('id'),
                'cluster_id': result.get('cluster_id'),
                'case_name': result.get('caseName'),
                'court': result.get('court'),
                'date_filed': result.get('dateFiled'),
                'citation': result.get('citation', []),
                'precedential_status': result.get('status'),
                'snippet': result.get('snippet'),
                'url': f"https://www.courtlistener.com{result.get('absolute_url', '')}",
                'opinion_url': result.get('download_url'),
                'cite_count': result.get('citeCount', 0)
            }
            results['opinions'].append(opinion)

        return results

    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}


def main():
    parser = argparse.ArgumentParser(
        description='Search CourtListener for legal opinions'
    )
    parser.add_argument('query', help='Search query (supports Boolean operators)')
    parser.add_argument('--courts', help='Comma-separated court IDs (e.g., ky,kyctapp,ked)')
    parser.add_argument('--after', help='Date after (YYYY-MM-DD)')
    parser.add_argument('--before', help='Date before (YYYY-MM-DD)')
    parser.add_argument('--precedential', action='store_true',
                       help='Only precedential opinions')
    parser.add_argument('--unpublished', action='store_true',
                       help='Only unpublished opinions')
    parser.add_argument('--order', default='score',
                       choices=['score', '-dateFiled', 'citeCount'],
                       help='Sort order')
    parser.add_argument('--limit', type=int, default=20,
                       help='Maximum results (default 20)')
    parser.add_argument('--json', action='store_true',
                       help='Output raw JSON')

    args = parser.parse_args()

    # Parse courts
    courts = args.courts.split(',') if args.courts else None

    # Handle precedential filter
    precedential = None
    if args.precedential:
        precedential = True
    elif args.unpublished:
        precedential = False

    # Execute search
    results = search_opinions(
        query=args.query,
        courts=courts,
        after_date=args.after,
        before_date=args.before,
        precedential=precedential,
        order_by=args.order,
        limit=args.limit
    )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        # Pretty print results
        if 'error' in results:
            print(f"ERROR: {results['error']}", file=sys.stderr)
            sys.exit(1)

        print(f"\nFound {results['count']} opinions for: {results['query']}")
        if results['courts_searched']:
            print(f"Courts: {', '.join(results['courts_searched'])}")
        print()

        for i, opinion in enumerate(results['opinions'], 1):
            print(f"{i}. {opinion['case_name']}")
            print(f"   Court: {opinion['court']}")
            print(f"   Date: {opinion['date_filed']}")
            if opinion['citation']:
                print(f"   Citation: {', '.join(opinion['citation'])}")
            print(f"   Status: {opinion['precedential_status']}")
            print(f"   Cited by: {opinion['cite_count']} cases")
            if opinion['snippet']:
                print(f"   Snippet: {opinion['snippet'][:200]}...")
            print(f"   URL: {opinion['url']}")
            print()


if __name__ == '__main__':
    main()
