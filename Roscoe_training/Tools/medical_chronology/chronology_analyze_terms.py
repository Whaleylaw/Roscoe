#!/usr/bin/env python3
"""
Analyze medical text to identify terms that need definition.

Usage:
    python chronology_analyze_terms.py --text TEXT [--cache-path PATH]
    python chronology_analyze_terms.py --text-file PATH [--cache-path PATH]

Example:
    python chronology_analyze_terms.py --text "Patient diagnosed with cervical radiculopathy"
"""

import argparse
import json
import sys
import os

# Add the Skills directory to path for imports
SKILLS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Skills', 'medical-records')
sys.path.insert(0, SKILLS_DIR)

from chronology_tools import suggest_definitions, DEFAULT_CACHE_PATH


def main():
    parser = argparse.ArgumentParser(
        description='Analyze medical text to identify terms needing definition'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', help='Medical text to analyze')
    group.add_argument('--text-file', help='Path to file containing medical text')
    parser.add_argument(
        '--cache-path',
        default=None,
        help='Path to cache file (default: Resources/medical_research_cache.json)'
    )
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    # Get text to analyze
    if args.text:
        text = args.text
    else:
        with open(args.text_file, 'r') as f:
            text = f.read()
    
    # Determine cache path
    cache_path = args.cache_path
    if not cache_path:
        workspace = os.environ.get('WORKSPACE_DIR', '/workspace')
        cache_path = os.path.join(workspace, 'Resources', 'medical_research_cache.json')
    
    # Analyze the text
    analysis = suggest_definitions(text, cache_path=cache_path)
    
    # Format results
    cached_formatted = []
    for term, info in analysis.get('cached', []):
        cached_formatted.append({
            "term": term,
            "definition": info.get("definition"),
            "source": info.get("source"),
            "url": info.get("url")
        })
    
    abbreviations_formatted = []
    for abbrev, expansion in analysis.get('abbreviations', []):
        abbreviations_formatted.append({
            "abbreviation": abbrev,
            "expansion": expansion
        })
    
    result = {
        "text_length": len(text),
        "cached_terms": cached_formatted,
        "cached_count": len(cached_formatted),
        "needs_research": analysis.get('needs_research', []),
        "needs_research_count": len(analysis.get('needs_research', [])),
        "abbreviations": abbreviations_formatted,
        "abbreviations_count": len(abbreviations_formatted)
    }
    
    # Add research suggestions
    if result['needs_research']:
        result['research_suggestions'] = [
            f'python /Tools/research/internet_search.py "{term} definition site:mayoclinic.org" --include-content'
            for term in result['needs_research'][:5]
        ]
    
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))


if __name__ == '__main__':
    main()

