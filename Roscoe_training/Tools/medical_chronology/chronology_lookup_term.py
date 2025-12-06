#!/usr/bin/env python3
"""
Look up a medical term in the research cache.

Usage:
    python chronology_lookup_term.py --term TERM [--cache-path PATH]

Example:
    python chronology_lookup_term.py --term "radiculopathy"
"""

import argparse
import json
import sys
import os

# Add the Skills directory to path for imports
SKILLS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Skills', 'medical-records')
sys.path.insert(0, SKILLS_DIR)

from chronology_tools import get_cached_definition, STANDARD_ABBREVIATIONS, DEFAULT_CACHE_PATH


def main():
    parser = argparse.ArgumentParser(
        description='Look up a medical term in the research cache'
    )
    parser.add_argument('--term', required=True, help='The medical term to look up')
    parser.add_argument(
        '--cache-path',
        default=None,
        help='Path to cache file (default: Resources/medical_research_cache.json)'
    )
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    # Determine cache path
    cache_path = args.cache_path
    if not cache_path:
        workspace = os.environ.get('WORKSPACE_DIR', '/workspace')
        cache_path = os.path.join(workspace, 'Resources', 'medical_research_cache.json')
    
    term = args.term
    
    # Check standard abbreviations first
    if term.upper() in STANDARD_ABBREVIATIONS:
        result = {
            "found": True,
            "term": term,
            "type": "standard_abbreviation",
            "definition": STANDARD_ABBREVIATIONS[term.upper()],
            "needs_research": False,
            "citation_required": False
        }
    else:
        # Check research cache
        cached = get_cached_definition(term, cache_path=cache_path)
        
        if cached:
            result = {
                "found": True,
                "term": term,
                "type": "cached_research",
                "definition": cached.get("definition"),
                "source": cached.get("source"),
                "url": cached.get("url"),
                "researched_date": cached.get("researched_date"),
                "needs_research": False,
                "citation_required": True
            }
        else:
            result = {
                "found": False,
                "term": term,
                "needs_research": True,
                "message": f"Term '{term}' not found. Use internet_search to research, then add to cache.",
                "suggested_search": f'python /Tools/research/internet_search.py "{term} definition site:mayoclinic.org OR site:clevelandclinic.org" --include-content'
            }
    
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))


if __name__ == '__main__':
    main()

