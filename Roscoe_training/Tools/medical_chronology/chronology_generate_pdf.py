#!/usr/bin/env python3
"""
Generate a professional medical chronology PDF from structured entry data.

Usage:
    python chronology_generate_pdf.py --client-name NAME --dob DATE --injury-date DATE \
        --entries-json PATH --output PATH [--firm-name NAME] [--source-records PATH]

Example:
    python chronology_generate_pdf.py \
        --client-name "Mills, Amy" \
        --dob "12/28/1983" \
        --injury-date "04/26/2019" \
        --entries-json /case/chronology_entries.json \
        --output /Reports/
"""

import argparse
import json
import sys
import os

# Add the Skills directory to path for imports
SKILLS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Skills', 'medical-records')
sys.path.insert(0, SKILLS_DIR)

from chronology_tools import create_medical_chronology, DEFAULT_CACHE_PATH


def main():
    parser = argparse.ArgumentParser(
        description='Generate a professional medical chronology PDF'
    )
    parser.add_argument('--client-name', required=True, help='Client name (e.g., "Mills, Amy")')
    parser.add_argument('--dob', required=True, help='Date of birth (MM/DD/YYYY)')
    parser.add_argument('--injury-date', required=True, help='Date of injury (MM/DD/YYYY)')
    parser.add_argument('--entries-json', required=True, help='Path to JSON file with chronology entries')
    parser.add_argument('--output', required=True, help='Output directory for generated files')
    parser.add_argument('--firm-name', default='Law Firm', help='Firm name for disclaimer')
    parser.add_argument('--source-records', help='Optional path to source records PDF for merging')
    parser.add_argument(
        '--cache-path',
        default=None,
        help='Path to medical research cache'
    )
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    # Load entries
    with open(args.entries_json, 'r') as f:
        entries_data = json.load(f)
    
    # Handle both raw entries list and wrapped format
    if isinstance(entries_data, list):
        entries = entries_data
    else:
        entries = entries_data.get('entries', [])
    
    # Build client info
    client_info = {
        'name': args.client_name,
        'dob': args.dob,
        'date_of_injury': args.injury_date
    }
    
    # Determine cache path
    cache_path = args.cache_path
    if not cache_path:
        workspace = os.environ.get('WORKSPACE_DIR', '/workspace')
        cache_path = os.path.join(workspace, 'Resources', 'medical_research_cache.json')
    
    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)
    
    try:
        result = create_medical_chronology(
            client_info=client_info,
            entries=entries,
            output_dir=args.output,
            firm_name=args.firm_name,
            source_records_pdf=args.source_records,
            cache_path=cache_path
        )
        
        output = {
            "success": True,
            "message": "Medical chronology generated successfully",
            "files": {
                "pdf": result.get('pdf'),
                "json": result.get('json'),
                "combined": result.get('combined')
            },
            "entry_count": len(entries),
            "treatment_gaps": result.get('treatment_gaps', [])
        }
        
        if result.get('terms_needing_research'):
            output['warning'] = result.get('warning')
            output['terms_needing_research'] = result.get('terms_needing_research')
        
        if args.pretty:
            print(json.dumps(output, indent=2))
        else:
            print(json.dumps(output))
            
    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(result), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

