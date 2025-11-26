#!/usr/bin/env python3
"""
CourtListener Upcoming Dates Monitor

Monitors upcoming court dates, hearings, and deadlines across multiple cases.
Useful for calendar management and deadline tracking.

Usage:
    python monitor_upcoming_dates.py --attorney "John Smith"
    python monitor_upcoming_dates.py --dockets 12345,67890,11223
    python monitor_upcoming_dates.py --attorney "John Smith" --days 30
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
from collections import defaultdict

# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

API_KEY = os.getenv('COURTLISTENER_API_KEY')
BASE_URL = 'https://www.courtlistener.com/api/rest/v4'


def get_docket_details(docket_id):
    """Get docket details."""
    if not API_KEY:
        return None

    headers = {'Authorization': f'Token {API_KEY}'}

    try:
        response = requests.get(
            f'{BASE_URL}/dockets/{docket_id}/',
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except:
        return None


def get_docket_entries(docket_id):
    """Get docket entries for a docket."""
    if not API_KEY:
        return []

    headers = {'Authorization': f'Token {API_KEY}'}
    params = {
        'docket': docket_id,
        'order_by': 'entry_number',
        'page_size': 500
    }

    try:
        response = requests.get(
            f'{BASE_URL}/docket-entries/',
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json().get('results', [])
    except:
        return []


def find_attorney_dockets(attorney_name, courts=None, limit=100):
    """Find all dockets for an attorney."""
    if not API_KEY:
        return []

    headers = {'Authorization': f'Token {API_KEY}'}
    params = {
        'q': f'attorney:"{attorney_name}"',
        'type': 'r',
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
        results = response.json().get('results', [])

        docket_ids = []
        for result in results:
            docket_id = result.get('docket_id')
            # Only include open cases
            if docket_id and not result.get('dateTerminated'):
                docket_ids.append(docket_id)

        return docket_ids
    except:
        return []


def extract_upcoming_events(docket, days_ahead=90):
    """
    Extract upcoming events from a docket.

    Args:
        docket: Docket data
        days_ahead: Look ahead this many days

    Returns:
        list: Upcoming events
    """
    events = []
    today = datetime.now().date()
    cutoff = today + timedelta(days=days_ahead)

    # Trial date
    if docket.get('date_trial'):
        try:
            trial_date = datetime.fromisoformat(docket['date_trial']).date()
            if today <= trial_date <= cutoff:
                events.append({
                    'type': 'Trial',
                    'date': docket['date_trial'],
                    'date_obj': trial_date,
                    'description': 'Trial Date',
                    'case_name': docket.get('case_name'),
                    'case_number': docket.get('docket_number'),
                    'docket_id': docket.get('id'),
                    'court': docket.get('court')
                })
        except:
            pass

    # Scan docket entries for hearings
    entries = get_docket_entries(docket.get('id'))

    hearing_keywords = [
        'hearing', 'motion hearing', 'status conference', 'pretrial conference',
        'oral argument', 'telephonic conference', 'zoom hearing', 'video conference',
        'settlement conference', 'scheduling conference', 'case management conference'
    ]

    deadline_keywords = [
        'deadline', 'due date', 'response due', 'filing deadline',
        'discovery deadline', 'dispositive motions', 'expert disclosure'
    ]

    for entry in entries:
        desc = entry.get('description', '').lower()
        date_filed = entry.get('date_filed')

        if not date_filed:
            continue

        try:
            entry_date = datetime.fromisoformat(date_filed).date()

            # Only include future dates within cutoff
            if today <= entry_date <= cutoff:
                # Check for hearings
                if any(keyword in desc for keyword in hearing_keywords):
                    events.append({
                        'type': 'Hearing',
                        'date': date_filed,
                        'date_obj': entry_date,
                        'description': entry.get('description'),
                        'case_name': docket.get('case_name'),
                        'case_number': docket.get('docket_number'),
                        'docket_id': docket.get('id'),
                        'court': docket.get('court'),
                        'entry_number': entry.get('entry_number')
                    })
                # Check for deadlines
                elif any(keyword in desc for keyword in deadline_keywords):
                    events.append({
                        'type': 'Deadline',
                        'date': date_filed,
                        'date_obj': entry_date,
                        'description': entry.get('description'),
                        'case_name': docket.get('case_name'),
                        'case_number': docket.get('docket_number'),
                        'docket_id': docket.get('id'),
                        'court': docket.get('court'),
                        'entry_number': entry.get('entry_number')
                    })
        except:
            continue

    return events


def monitor_upcoming_dates(docket_ids=None, attorney_name=None, courts=None, days_ahead=90):
    """
    Monitor upcoming dates across multiple dockets.

    Args:
        docket_ids: List of specific docket IDs to monitor
        attorney_name: Attorney name to find all their cases
        courts: Court filters
        days_ahead: Look ahead this many days

    Returns:
        dict: Organized upcoming events
    """
    if not API_KEY:
        return {'error': 'COURTLISTENER_API_KEY not found'}

    # Collect docket IDs
    if attorney_name:
        print(f"Finding cases for attorney: {attorney_name}...", file=sys.stderr)
        docket_ids = find_attorney_dockets(attorney_name, courts=courts)
        print(f"Found {len(docket_ids)} open cases", file=sys.stderr)

    if not docket_ids:
        return {'error': 'No dockets specified or found'}

    # Collect all events
    all_events = []

    for i, docket_id in enumerate(docket_ids, 1):
        print(f"Processing docket {i}/{len(docket_ids)}...", file=sys.stderr)
        docket = get_docket_details(docket_id)

        if docket:
            events = extract_upcoming_events(docket, days_ahead=days_ahead)
            all_events.extend(events)

    # Sort by date
    all_events.sort(key=lambda x: x['date_obj'])

    # Group by date
    by_date = defaultdict(list)
    for event in all_events:
        by_date[event['date']].append(event)

    # Group by type
    by_type = defaultdict(list)
    for event in all_events:
        by_type[event['type']].append(event)

    return {
        'total_events': len(all_events),
        'days_ahead': days_ahead,
        'events': all_events,
        'by_date': dict(by_date),
        'by_type': dict(by_type),
        'summary': {
            'trials': len(by_type.get('Trial', [])),
            'hearings': len(by_type.get('Hearing', [])),
            'deadlines': len(by_type.get('Deadline', []))
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Monitor upcoming court dates and deadlines'
    )
    parser.add_argument('--dockets', help='Comma-separated docket IDs')
    parser.add_argument('--attorney', help='Attorney name to find all their cases')
    parser.add_argument('--courts', help='Comma-separated court IDs to filter')
    parser.add_argument('--days', type=int, default=90,
                       help='Look ahead this many days (default: 90)')
    parser.add_argument('--json', action='store_true',
                       help='Output raw JSON')
    parser.add_argument('--calendar', action='store_true',
                       help='Output in calendar format')

    args = parser.parse_args()

    # Parse inputs
    docket_ids = None
    if args.dockets:
        docket_ids = [int(d.strip()) for d in args.dockets.split(',')]

    courts = None
    if args.courts:
        courts = args.courts.split(',')

    if not docket_ids and not args.attorney:
        parser.print_help()
        print("\nERROR: Must specify either --dockets or --attorney", file=sys.stderr)
        sys.exit(1)

    # Monitor dates
    results = monitor_upcoming_dates(
        docket_ids=docket_ids,
        attorney_name=args.attorney,
        courts=courts,
        days_ahead=args.days
    )

    if 'error' in results:
        print(f"ERROR: {results['error']}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.json:
        # Remove date_obj for JSON serialization
        for event in results['events']:
            event.pop('date_obj', None)
        print(json.dumps(results, indent=2))
    elif args.calendar:
        # Calendar format
        print(f"\n{'='*80}")
        print(f"UPCOMING COURT CALENDAR ({results['days_ahead']} days)")
        print(f"{'='*80}")
        print(f"Total Events: {results['total_events']} "
              f"(Trials: {results['summary']['trials']}, "
              f"Hearings: {results['summary']['hearings']}, "
              f"Deadlines: {results['summary']['deadlines']})")
        print(f"{'='*80}\n")

        for date in sorted(results['by_date'].keys()):
            events = results['by_date'][date]
            print(f"📅 {date}")
            print("-" * 80)
            for event in events:
                print(f"  [{event['type']}] {event['case_name']}")
                print(f"    Case No: {event['case_number']}")
                print(f"    Court: {event['court']}")
                print(f"    {event['description']}")
                print()
    else:
        # Standard format
        print(f"\n{'='*80}")
        print(f"UPCOMING EVENTS ({results['days_ahead']} days ahead)")
        print(f"{'='*80}")
        print(f"Total: {results['total_events']} events")
        print(f"  Trials: {results['summary']['trials']}")
        print(f"  Hearings: {results['summary']['hearings']}")
        print(f"  Deadlines: {results['summary']['deadlines']}")
        print(f"{'='*80}\n")

        for event in results['events']:
            print(f"[{event['type'].upper()}] {event['date']}")
            print(f"  Case: {event['case_name']}")
            print(f"  Case No: {event['case_number']}")
            print(f"  Court: {event['court']}")
            print(f"  {event['description']}")
            print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
