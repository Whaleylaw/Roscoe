#!/usr/bin/env python3
"""
Split a PDF file into multiple documents by page ranges.

Usage:
    python split_pdf.py <input_pdf> <output_prefix> --pages <range1> [--pages <range2> ...]
    python split_pdf.py input.pdf output --pages 1-63 --pages 64-end
    python split_pdf.py input.pdf output --pages 1-10 --pages 11-20 --pages 21-end
"""

import argparse
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
    except ImportError:
        print("Error: pypdf or PyPDF2 required. Install with: pip install pypdf", file=sys.stderr)
        sys.exit(1)


def parse_page_range(page_range: str, total_pages: int) -> tuple[int, int]:
    """
    Parse a page range string like "1-63", "64-end", or "10".
    
    Args:
        page_range: Range string (e.g., "1-63", "64-end", "10")
        total_pages: Total number of pages in PDF
        
    Returns:
        Tuple of (start_page, end_page) (0-indexed, inclusive)
    """
    page_range = page_range.strip().lower()
    
    if '-' in page_range:
        start_str, end_str = page_range.split('-', 1)
        start = int(start_str.strip()) - 1  # Convert to 0-indexed
        if end_str.strip() == 'end':
            end = total_pages - 1  # Last page (0-indexed)
        else:
            end = int(end_str.strip()) - 1  # Convert to 0-indexed
    else:
        # Single page
        page_num = int(page_range)
        start = page_num - 1  # Convert to 0-indexed
        end = start
    
    # Validate range
    if start < 0:
        start = 0
    if end >= total_pages:
        end = total_pages - 1
    if start > end:
        raise ValueError(f"Invalid range: start ({start+1}) > end ({end+1})")
    
    return start, end


def split_pdf(input_path: Path, output_prefix: str, page_ranges: list[str]) -> None:
    """
    Split a PDF into multiple files based on page ranges.
    
    Args:
        input_path: Path to input PDF
        output_prefix: Prefix for output files (e.g., "output" → "output_part1.pdf", "output_part2.pdf")
        page_ranges: List of page range strings (e.g., ["1-63", "64-end"])
    """
    # Read input PDF
    print(f"Reading PDF: {input_path}", file=sys.stderr)
    reader = PdfReader(str(input_path))
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}", file=sys.stderr)
    
    # Parse page ranges
    parsed_ranges = []
    for range_str in page_ranges:
        start, end = parse_page_range(range_str, total_pages)
        parsed_ranges.append((start, end))
        print(f"  Range: {range_str} → pages {start+1} to {end+1} (0-indexed: {start} to {end})", file=sys.stderr)
    
    # Create output files
    for i, (start, end) in enumerate(parsed_ranges, 1):
        output_path = Path(f"{output_prefix}_part{i}.pdf")
        
        print(f"\nCreating {output_path} (pages {start+1} to {end+1})...", file=sys.stderr)
        
        writer = PdfWriter()
        
        # Add pages in range (end is inclusive)
        for page_num in range(start, end + 1):
            writer.add_page(reader.pages[page_num])
        
        # Write output file
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        print(f"  ✓ Created {output_path} ({end - start + 1} pages)", file=sys.stderr)
    
    print(f"\n✓ Split complete: {len(parsed_ranges)} file(s) created", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Split a PDF file into multiple documents by page ranges',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Split into two parts: pages 1-63 and 64-end
  python split_pdf.py input.pdf output --pages 1-63 --pages 64-end
  
  # Split into three parts
  python split_pdf.py input.pdf output --pages 1-100 --pages 101-500 --pages 501-end
  
  # Single page range
  python split_pdf.py input.pdf output --pages 1-63
        """
    )
    parser.add_argument('input_pdf', help='Input PDF file to split')
    parser.add_argument('output_prefix', help='Output file prefix (e.g., "output" → "output_part1.pdf")')
    parser.add_argument(
        '--pages',
        action='append',
        required=True,
        help='Page range (e.g., "1-63", "64-end", "10"). Can specify multiple times.'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input_pdf)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    if not input_path.suffix.lower() == '.pdf':
        print(f"Error: File is not a PDF: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Split the PDF
    try:
        split_pdf(input_path, args.output_prefix, args.pages)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()



