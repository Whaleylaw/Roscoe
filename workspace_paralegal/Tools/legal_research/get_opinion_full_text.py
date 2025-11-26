#!/usr/bin/env python3
"""
CourtListener Opinion Full Text Retriever

Gets the complete text and metadata for a specific opinion.
Useful for reading the full opinion after finding it via search.

Usage:
    python get_opinion_full_text.py 12345
    python get_opinion_full_text.py 12345 --format html
    python get_opinion_full_text.py 12345 --save /path/to/save.txt
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

API_KEY = os.getenv('COURTLISTENER_API_KEY')
BASE_URL = 'https://www.courtlistener.com/api/rest/v4'


def get_opinion_details(opinion_id):
    """
    Get complete opinion details including metadata.

    Args:
        opinion_id: The opinion ID

    Returns:
        dict: Complete opinion data
    """
    if not API_KEY:
        return {'error': 'COURTLISTENER_API_KEY not found'}

    headers = {'Authorization': f'Token {API_KEY}'}

    try:
        response = requests.get(
            f'{BASE_URL}/opinions/{opinion_id}/',
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}


def get_cluster_details(cluster_id):
    """
    Get cluster (case) details.

    Args:
        cluster_id: The cluster ID

    Returns:
        dict: Cluster data including case name, citations, etc.
    """
    if not API_KEY:
        return {'error': 'COURTLISTENER_API_KEY not found'}

    headers = {'Authorization': f'Token {API_KEY}'}

    try:
        response = requests.get(
            f'{BASE_URL}/clusters/{cluster_id}/',
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}


def get_opinion_full_text(opinion_id, output_format='plain'):
    """
    Get the full text of an opinion with metadata.

    Args:
        opinion_id: Opinion ID
        output_format: 'plain', 'html', or 'json'

    Returns:
        dict: Opinion with full text and metadata
    """
    # Get opinion details
    opinion = get_opinion_details(opinion_id)

    if 'error' in opinion:
        return opinion

    # Get cluster details for case name and citations
    cluster_id = opinion.get('cluster')
    cluster = get_cluster_details(cluster_id) if cluster_id else {}

    # Build comprehensive result
    result = {
        'opinion_id': opinion.get('id'),
        'cluster_id': cluster_id,
        'case_name': cluster.get('case_name', 'Unknown'),
        'citations': cluster.get('citations', []),
        'court': opinion.get('court'),
        'date_filed': cluster.get('date_filed'),
        'precedential_status': cluster.get('precedential_status'),
        'judges': cluster.get('judges', ''),
        'author': opinion.get('author_str'),
        'joined_by': opinion.get('joined_by_str'),
        'type': opinion.get('type'),
        'download_url': opinion.get('download_url'),
        'local_path': opinion.get('local_path'),
        'page_count': opinion.get('page_count'),
        'url': f"https://www.courtlistener.com{opinion.get('absolute_url', '')}",
        'full_text': {
            'plain': opinion.get('plain_text', ''),
            'html': opinion.get('html', ''),
            'html_lawbox': opinion.get('html_lawbox', ''),
            'html_columbia': opinion.get('html_columbia', ''),
            'xml_harvard': opinion.get('xml_harvard', '')
        }
    }

    # Select requested format
    if output_format == 'plain':
        result['text'] = result['full_text']['plain']
    elif output_format == 'html':
        # Try different HTML sources in order of preference
        result['text'] = (result['full_text']['html'] or
                         result['full_text']['html_lawbox'] or
                         result['full_text']['html_columbia'] or
                         result['full_text']['plain'])

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Get full text of a CourtListener opinion'
    )
    parser.add_argument('opinion_id', type=int, help='Opinion ID')
    parser.add_argument('--format', choices=['plain', 'html', 'json'],
                       default='plain', help='Output format (default: plain)')
    parser.add_argument('--save', help='Save full text to file')
    parser.add_argument('--json', action='store_true',
                       help='Output complete metadata as JSON')
    parser.add_argument('--metadata-only', action='store_true',
                       help='Show only metadata, not full text')

    args = parser.parse_args()

    # Get opinion
    result = get_opinion_full_text(args.opinion_id, output_format=args.format)

    if 'error' in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)

    # Output handling
    if args.json:
        print(json.dumps(result, indent=2))
    elif args.metadata_only:
        # Print metadata only
        print(f"\n{'='*80}")
        print(f"CASE: {result['case_name']}")
        print(f"{'='*80}")
        if result['citations']:
            print(f"Citations: {', '.join(result['citations'])}")
        print(f"Court: {result['court']}")
        print(f"Date Filed: {result['date_filed']}")
        print(f"Status: {result['precedential_status']}")
        if result['judges']:
            print(f"Judges: {result['judges']}")
        if result['author']:
            print(f"Author: {result['author']}")
        if result['joined_by']:
            print(f"Joined by: {result['joined_by']}")
        print(f"Type: {result['type']}")
        print(f"Pages: {result['page_count']}")
        print(f"URL: {result['url']}")
        if result['download_url']:
            print(f"Download: {result['download_url']}")
        print(f"{'='*80}\n")
    else:
        # Print metadata + full text
        print(f"\n{'='*80}")
        print(f"CASE: {result['case_name']}")
        print(f"{'='*80}")
        if result['citations']:
            print(f"Citations: {', '.join(result['citations'])}")
        print(f"Court: {result['court']}")
        print(f"Date: {result['date_filed']}")
        print(f"{'='*80}\n")

        text = result.get('text', result['full_text']['plain'])

        if args.save:
            # Save to file
            save_path = Path(args.save)
            save_path.write_text(text)
            print(f"Full text saved to: {args.save}")
        else:
            # Print to stdout
            print(text)

    return 0


if __name__ == '__main__':
    sys.exit(main())
