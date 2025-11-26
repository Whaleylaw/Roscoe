#!/usr/bin/env python3
"""
CourtListener Docket Details Retriever

Gets complete docket information including all filings, parties, and dates.
Useful for getting the full docket sheet for a case.

Usage:
    python get_docket_details.py 12345
    python get_docket_details.py 12345 --filings-only
    python get_docket_details.py 12345 --save /path/to/docket.json
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

API_KEY = os.getenv('COURTLISTENER_API_KEY')
BASE_URL = 'https://www.courtlistener.com/api/rest/v4'


def get_docket_full_details(docket_id):
    """
    Get complete docket details including all entries.

    Args:
        docket_id: The docket ID

    Returns:
        dict: Complete docket information
    """
    if not API_KEY:
        return {'error': 'COURTLISTENER_API_KEY not found'}

    headers = {'Authorization': f'Token {API_KEY}'}

    try:
        response = requests.get(
            f'{BASE_URL}/dockets/{docket_id}/',
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}


def get_docket_entries(docket_id, limit=500):
    """
    Get all docket entries (filings) for a docket.

    Args:
        docket_id: The docket ID
        limit: Maximum entries to retrieve

    Returns:
        list: Docket entries sorted by date
    """
    if not API_KEY:
        return {'error': 'COURTLISTENER_API_KEY not found'}

    headers = {'Authorization': f'Token {API_KEY}'}
    params = {
        'docket': docket_id,
        'order_by': 'entry_number',
        'page_size': limit
    }

    try:
        response = requests.get(
            f'{BASE_URL}/docket-entries/',
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        entries = []
        for entry in data.get('results', []):
            entries.append({
                'entry_number': entry.get('entry_number'),
                'date_filed': entry.get('date_filed'),
                'description': entry.get('description'),
                'pacer_doc_id': entry.get('pacer_doc_id'),
                'pacer_seq_no': entry.get('pacer_seq_no'),
                'recap_documents': entry.get('recap_documents', [])
            })

        return entries

    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}


def format_docket_summary(docket, include_entries=True):
    """
    Format docket data into a readable summary.

    Args:
        docket: Docket data from API
        include_entries: Whether to include docket entries

    Returns:
        dict: Formatted docket summary
    """
    summary = {
        'docket_id': docket.get('id'),
        'case_name': docket.get('case_name'),
        'case_number': docket.get('docket_number'),
        'court': docket.get('court'),
        'court_name': docket.get('court_name'),
        'dates': {
            'filed': docket.get('date_filed'),
            'terminated': docket.get('date_terminated'),
            'last_filing': docket.get('date_last_filing'),
            'last_modified': docket.get('date_modified')
        },
        'status': 'Closed' if docket.get('date_terminated') else 'Open',
        'judge': {
            'assigned_to': docket.get('assigned_to_str'),
            'referred_to': docket.get('referred_to_str')
        },
        'case_details': {
            'nature_of_suit': docket.get('nature_of_suit'),
            'cause': docket.get('cause'),
            'jurisdiction_type': docket.get('jurisdiction_type'),
            'jury_demand': docket.get('jury_demand')
        },
        'parties': docket.get('parties', []),
        'url': f"https://www.courtlistener.com{docket.get('absolute_url', '')}",
        'pacer_case_id': docket.get('pacer_case_id')
    }

    if include_entries:
        entries = get_docket_entries(docket.get('id'))
        if isinstance(entries, list):
            summary['entries'] = entries
            summary['entry_count'] = len(entries)

    return summary


def get_upcoming_events(docket):
    """
    Extract upcoming court dates and deadlines from docket.

    Args:
        docket: Docket data

    Returns:
        list: Upcoming events/dates
    """
    events = []
    today = datetime.now().date()

    # Check for trial date
    if docket.get('date_trial'):
        trial_date = datetime.fromisoformat(docket['date_trial']).date()
        if trial_date >= today:
            events.append({
                'type': 'Trial Date',
                'date': docket['date_trial'],
                'description': 'Scheduled trial date'
            })

    # Check for scheduled hearings in docket entries
    entries = get_docket_entries(docket.get('id'))
    if isinstance(entries, list):
        for entry in entries:
            desc = entry.get('description', '').lower()
            date_filed = entry.get('date_filed')

            if date_filed:
                entry_date = datetime.fromisoformat(date_filed).date()
                if entry_date >= today:
                    # Look for hearing-related keywords
                    if any(word in desc for word in ['hearing', 'motion hearing', 'status conference',
                                                      'pretrial conference', 'oral argument']):
                        events.append({
                            'type': 'Hearing',
                            'date': date_filed,
                            'description': entry.get('description')
                        })

    # Sort by date
    events.sort(key=lambda x: x['date'])
    return events


def main():
    parser = argparse.ArgumentParser(
        description='Get detailed docket information from CourtListener'
    )
    parser.add_argument('docket_id', type=int, help='Docket ID')
    parser.add_argument('--filings-only', action='store_true',
                       help='Show only docket entries (filings)')
    parser.add_argument('--upcoming', action='store_true',
                       help='Show only upcoming court dates')
    parser.add_argument('--save', help='Save complete data to JSON file')
    parser.add_argument('--json', action='store_true',
                       help='Output raw JSON')

    args = parser.parse_args()

    # Get docket details
    docket = get_docket_full_details(args.docket_id)

    if 'error' in docket:
        print(f"ERROR: {docket['error']}", file=sys.stderr)
        sys.exit(1)

    # Format summary
    summary = format_docket_summary(docket, include_entries=not args.upcoming)

    # Save to file if requested
    if args.save:
        save_path = Path(args.save)
        save_path.write_text(json.dumps(summary, indent=2))
        print(f"Docket details saved to: {args.save}")
        return 0

    # Output handling
    if args.json:
        print(json.dumps(summary, indent=2))
    elif args.upcoming:
        # Show only upcoming events
        events = get_upcoming_events(docket)

        print(f"\n{'='*80}")
        print(f"UPCOMING EVENTS: {summary['case_name']}")
        print(f"Case No: {summary['case_number']}")
        print(f"{'='*80}\n")

        if events:
            for event in events:
                print(f"{event['type']}: {event['date']}")
                print(f"  {event['description']}")
                print()
        else:
            print("No upcoming events found.")
    elif args.filings_only:
        # Show only docket entries
        print(f"\n{'='*80}")
        print(f"DOCKET ENTRIES: {summary['case_name']}")
        print(f"Case No: {summary['case_number']}")
        print(f"{'='*80}\n")

        for entry in summary.get('entries', []):
            print(f"Entry #{entry['entry_number']} | {entry['date_filed']}")
            print(f"  {entry['description']}")
            if entry.get('recap_documents'):
                print(f"  Documents: {len(entry['recap_documents'])}")
            print()
    else:
        # Full summary
        print(f"\n{'='*80}")
        print(f"CASE: {summary['case_name']}")
        print(f"{'='*80}")
        print(f"Case Number: {summary['case_number']}")
        print(f"Court: {summary['court_name']}")
        print(f"Status: {summary['status']}")
        print()
        print(f"Date Filed: {summary['dates']['filed']}")
        if summary['dates']['terminated']:
            print(f"Date Terminated: {summary['dates']['terminated']}")
        print(f"Last Filing: {summary['dates']['last_filing']}")
        print()
        if summary['judge']['assigned_to']:
            print(f"Assigned Judge: {summary['judge']['assigned_to']}")
        if summary['judge']['referred_to']:
            print(f"Referred Judge: {summary['judge']['referred_to']}")
        print()
        if summary['case_details']['nature_of_suit']:
            print(f"Nature of Suit: {summary['case_details']['nature_of_suit']}")
        if summary['case_details']['cause']:
            print(f"Cause: {summary['case_details']['cause']}")
        print()
        print(f"URL: {summary['url']}")
        print(f"{'='*80}\n")

        if summary.get('entry_count'):
            print(f"DOCKET ENTRIES ({summary['entry_count']} total):\n")
            for entry in summary.get('entries', [])[:20]:  # Show first 20
                print(f"#{entry['entry_number']} | {entry['date_filed']}")
                print(f"  {entry['description']}")
                print()

            if summary['entry_count'] > 20:
                print(f"... and {summary['entry_count'] - 20} more entries")

    return 0


if __name__ == '__main__':
    sys.exit(main())
