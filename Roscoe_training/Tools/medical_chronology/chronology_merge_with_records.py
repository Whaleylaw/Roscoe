#!/usr/bin/env python3
"""
Merge generated chronology PDF with source medical records PDF.

Usage:
    python chronology_merge_with_records.py --chronology PATH --records PATH --output PATH

Example:
    python chronology_merge_with_records.py \
        --chronology /Reports/Chronology.pdf \
        --records /Records/all_records.pdf \
        --output /Reports/Chronology_and_Records.pdf
"""

import argparse
import json
import sys
import os

# Add the Skills directory to path for imports
SKILLS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Skills', 'medical-records')
sys.path.insert(0, SKILLS_DIR)

from chronology_tools import merge_chronology_with_records


def main():
    parser = argparse.ArgumentParser(
        description='Merge chronology PDF with source medical records'
    )
    parser.add_argument('--chronology', required=True, help='Path to chronology PDF')
    parser.add_argument('--records', required=True, help='Path to source records PDF')
    parser.add_argument('--output', required=True, help='Output path for combined PDF')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    # Validate input files exist
    if not os.path.exists(args.chronology):
        result = {
            "success": False,
            "error": f"Chronology file not found: {args.chronology}"
        }
        print(json.dumps(result), file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(args.records):
        result = {
            "success": False,
            "error": f"Records file not found: {args.records}"
        }
        print(json.dumps(result), file=sys.stderr)
        sys.exit(1)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        output_path = merge_chronology_with_records(
            chronology_pdf=args.chronology,
            records_pdf=args.records,
            output_path=args.output
        )
        
        result = {
            "success": True,
            "message": "PDFs merged successfully",
            "output_path": output_path
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

