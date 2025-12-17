#!/usr/bin/env python3
"""
CourtListener Case Finder by Attorney

Finds all dockets where a specific attorney is listed.
Useful for tracking your own cases across multiple courts.

Usage:
    python find_my_cases.py "John Smith" --courts "ked,kwd"
    python find_my_cases.py "Smith, John" --state-courts
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote

# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

API_KEY = os.getenv('COURTLISTENER_API_KEY')
BASE_URL = 'https://www.courtlistener.com/api/rest/v4'

# Kentucky courts
KENTUCKY_FEDERAL_COURTS = ['ked', 'kwd', 'ca6']
KENTUCKY_STATE_COURTS = ['ky', 'kyctapp']
KENTUCKY_CIRCUIT_COURTS = [
    'kycirbourbon', 'kycirbullitt', 'kycirbreckinridge', 'kycircalloway',
    'kycircchristian', 'kycirbetsy', 'kycircfayette', 'kycircjefferson'
    # Add more as needed
]


def search_dockets_by_attorney(attorney_name, courts=None, case_status=None, limit=100):
    """
    Search for dockets where attorney is listed.

    Args:
        attorney_name: Attorney name (can be "First Last" or "Last, First")
        courts: List of court IDs to search
        case_status: Filter by case status (e.g., 'Open', 'Closed')
        limit: Maximum results to return

    Returns:
        dict: Search results with dockets
    """
    if not API_KEY:
        return {'error': 'COURTLISTENER_API_KEY not found'}

    headers = {'Authorization': f'Token {API_KEY}'}

    # Build search query for attorney
    # CourtListener searches parties and attorneys in docket entries
    params = {
        'q': f'attorney:"{attorney_name}"',
        'type': 'r',  # RECAP (federal court records)
        'order_by': '-dateFiled',
        'page_size': limit
    }

    if courts:
        params['court'] = ','.join(courts) if isinstance(courts, list) else courts

    try:
        response = requests.get(
            f'{BASE_URL}/search/',
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        results = {
            'count': data.get('count', 0),
            'attorney_name': attorney_name,
            'courts_searched': courts or 'all',
            'dockets': []
        }

        for result in data.get('results', []):
            docket = {
                'id': result.get('docket_id'),
                'case_name': result.get('caseName'),
                'case_number': result.get('docketNumber'),
                'court': result.get('court'),
                'date_filed': result.get('dateFiled'),
                'date_terminated': result.get('dateTerminated'),
                'status': 'Closed' if result.get('dateTerminated') else 'Open',
                'judge': result.get('assignedTo'),
                'nature_of_suit': result.get('nature_of_suit'),
                'url': f"https://www.courtlistener.com{result.get('absolute_url', '')}"
            }

            # Filter by status if requested
            if case_status and docket['status'] != case_status:
                continue

            results['dockets'].append(docket)

        return results

    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}


def get_attorney_dockets_direct(attorney_name, courts=None, limit=100):
    """
    Alternative method: Search dockets directly by attorney field.

    Args:
        attorney_name: Attorney name
        courts: List of court IDs
        limit: Maximum results

    Returns:
        dict: Docket results
    """
    if not API_KEY:
        return {'error': 'COURTLISTENER_API_KEY not found'}

    headers = {'Authorization': f'Token {API_KEY}'}

    # Search dockets where attorney appears in attorney field
    params = {
        'attorney': attorney_name,
        'order_by': '-date_filed',
        'page_size': limit
    }

    if courts:
        params['court'] = ','.join(courts) if isinstance(courts, list) else courts

    try:
        response = requests.get(
            f'{BASE_URL}/dockets/',
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        results = {
            'count': data.get('count', 0),
            'attorney_name': attorney_name,
            'courts_searched': courts or 'all',
            'dockets': []
        }

        for docket in data.get('results', []):
            results['dockets'].append({
                'id': docket.get('id'),
                'case_name': docket.get('case_name'),
                'case_number': docket.get('docket_number'),
                'court': docket.get('court'),
                'date_filed': docket.get('date_filed'),
                'date_terminated': docket.get('date_terminated'),
                'status': 'Closed' if docket.get('date_terminated') else 'Open',
                'judge': docket.get('assigned_to_str'),
                'nature_of_suit': docket.get('nature_of_suit'),
                'cause': docket.get('cause'),
                'url': f"https://www.courtlistener.com{docket.get('absolute_url', '')}"
            })

        return results

    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}


def main():
    parser = argparse.ArgumentParser(
        description='Find cases by attorney name'
    )
    parser.add_argument('attorney_name', help='Attorney name (e.g., "John Smith" or "Smith, John")')
    parser.add_argument('--courts', help='Comma-separated court IDs (e.g., ked,kwd)')
    parser.add_argument('--federal', action='store_true',
                       help='Search Kentucky federal courts only (E.D. Ky, W.D. Ky, 6th Cir)')
    parser.add_argument('--state', action='store_true',
                       help='Search Kentucky state courts only (KY Supreme, KY CoA)')
    parser.add_argument('--status', choices=['Open', 'Closed'],
                       help='Filter by case status')
    parser.add_argument('--limit', type=int, default=100,
                       help='Maximum results (default 100)')
    parser.add_argument('--method', choices=['search', 'direct'], default='search',
                       help='Search method (default: search)')
    parser.add_argument('--json', action='store_true',
                       help='Output raw JSON')

    args = parser.parse_args()

    # Determine courts to search
    courts = None
    if args.courts:
        courts = args.courts.split(',')
    elif args.federal:
        courts = KENTUCKY_FEDERAL_COURTS
    elif args.state:
        courts = KENTUCKY_STATE_COURTS

    # Execute search
    if args.method == 'direct':
        results = get_attorney_dockets_direct(
            attorney_name=args.attorney_name,
            courts=courts,
            limit=args.limit
        )
    else:
        results = search_dockets_by_attorney(
            attorney_name=args.attorney_name,
            courts=courts,
            case_status=args.status,
            limit=args.limit
        )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        # Pretty print results
        if 'error' in results:
            print(f"ERROR: {results['error']}", file=sys.stderr)
            sys.exit(1)

        print(f"\nFound {results['count']} cases for attorney: {results['attorney_name']}")
        if results['courts_searched'] != 'all':
            print(f"Courts: {results['courts_searched']}")
        print()

        for i, docket in enumerate(results['dockets'], 1):
            print(f"{i}. {docket['case_name']}")
            print(f"   Case No: {docket['case_number']}")
            print(f"   Court: {docket['court']}")
            print(f"   Filed: {docket['date_filed']}")
            print(f"   Status: {docket['status']}", end='')
            if docket['date_terminated']:
                print(f" (Terminated: {docket['date_terminated']})")
            else:
                print()
            if docket['judge']:
                print(f"   Judge: {docket['judge']}")
            if docket.get('nature_of_suit'):
                print(f"   Nature: {docket['nature_of_suit']}")
            print(f"   URL: {docket['url']}")
            print()


if __name__ == '__main__':
    main()
