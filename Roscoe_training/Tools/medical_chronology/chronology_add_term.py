#!/usr/bin/env python3
"""
Add a researched medical term to the cache with proper citation.

Usage:
    python chronology_add_term.py --term TERM --definition DEF --source SOURCE --url URL [--category CAT]

Example:
    python chronology_add_term.py \
        --term "Cervical Radiculopathy" \
        --definition "A condition where a nerve in the neck is compressed..." \
        --source "Mayo Clinic" \
        --url "https://mayoclinic.org/..." \
        --category terms
"""

import argparse
import json
import sys
import os

# Add the Skills directory to path for imports
SKILLS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Skills', 'medical-records')
sys.path.insert(0, SKILLS_DIR)

from chronology_tools import add_researched_term, DEFAULT_CACHE_PATH


def main():
    parser = argparse.ArgumentParser(
        description='Add a researched medical term to the cache with citation'
    )
    parser.add_argument('--term', required=True, help='The medical term')
    parser.add_argument('--definition', required=True, help='The researched definition')
    parser.add_argument('--source', required=True, help='Source name (e.g., "Mayo Clinic")')
    parser.add_argument('--url', required=True, help='Source URL')
    parser.add_argument(
        '--category', 
        default='terms',
        choices=['terms', 'medications', 'procedures', 'anatomy'],
        help='Category for the term (default: terms)'
    )
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
    
    # Ensure cache directory exists
    cache_dir = os.path.dirname(cache_path)
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
    
    try:
        entry = add_researched_term(
            term=args.term,
            definition=args.definition,
            source_name=args.source,
            source_url=args.url,
            category=args.category,
            cache_path=cache_path
        )
        
        result = {
            "success": True,
            "message": f"Added term '{args.term}' to cache",
            "entry": entry,
            "cache_path": cache_path
        }
        
        if args.pretty:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result))
            
    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(result), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

