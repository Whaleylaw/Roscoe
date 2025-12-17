#!/usr/bin/env python3
"""
Clean up markdown files from PDF conversion artifacts.

Removes:
- (cid:XX) character encoding artifacts
- Repeated "dddd" strings
- Broken encoding sequences
- Excessive whitespace
- Other PDF-to-markdown conversion noise

Usage:
    python cleanup_markdown.py <input_file> [--output <output_file>] [--in-place]
"""

import argparse
import re
import sys
from pathlib import Path


def cleanup_markdown(content: str) -> str:
    """
    Clean up markdown content from PDF conversion artifacts.
    
    Args:
        content: Raw markdown content
        
    Returns:
        Cleaned markdown content
    """
    # Remove (cid:XX) sequences - these are PDF character encoding artifacts
    # Pattern: (cid: followed by 1-3 digits, then )
    content = re.sub(r'\(cid:\d{1,3}\)', '', content)
    
    # Remove standalone "dddd" lines (common PDF artifact)
    # Match lines that are just "dddd" with optional whitespace
    content = re.sub(r'^dddd\s*$', '', content, flags=re.MULTILINE)
    
    # Remove "dddd" anywhere in text (it's always noise)
    content = re.sub(r'\bdddd\b', '', content)
    
    # Remove lines that are mostly single repeated characters (e.g., "CCCC", "=====")
    content = re.sub(r'^([^\w\s])\1{10,}\s*$', '', content, flags=re.MULTILINE)
    
    # Remove broken Unicode sequences and encoding artifacts
    # Pattern: sequences like ^(cid:19)(cid:18) etc.
    content = re.sub(r'\^\(cid:\d{1,3}\)[^(]*', '', content)
    
    # Remove lines that are mostly special characters and encoding artifacts
    # If a line is >80% non-alphanumeric (excluding spaces), it's likely noise
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip lines that are mostly encoding artifacts
        if len(line.strip()) > 0:
            # Count alphanumeric characters
            alnum_count = sum(1 for c in line if c.isalnum())
            total_chars = len(line.replace(' ', ''))
            if total_chars > 0:
                alnum_ratio = alnum_count / total_chars
                # Keep lines with at least 30% alphanumeric content
                if alnum_ratio >= 0.3:
                    cleaned_lines.append(line)
            else:
                # Empty or whitespace-only lines - keep minimal spacing
                if len(cleaned_lines) == 0 or cleaned_lines[-1].strip():
                    cleaned_lines.append('')
    
    content = '\n'.join(cleaned_lines)
    
    # Remove excessive blank lines (more than 2 consecutive)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Clean up excessive whitespace within lines (keep single spaces)
    content = re.sub(r'[ \t]{2,}', ' ', content)
    
    # Remove trailing whitespace from lines
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Remove lines that are just special characters and symbols
    # Pattern: lines with mostly symbols, brackets, etc.
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            # Preserve intentional blank lines
            if len(cleaned_lines) == 0 or cleaned_lines[-1].strip():
                cleaned_lines.append('')
        else:
            # Count meaningful characters (letters, numbers, common punctuation)
            meaningful = sum(1 for c in stripped if c.isalnum() or c in '.,;:!?()-$%')
            if meaningful >= len(stripped) * 0.4:  # At least 40% meaningful
                cleaned_lines.append(line)
            # Skip lines that are mostly noise
    
    content = '\n'.join(cleaned_lines)
    
    # Final cleanup: remove any remaining (cid: patterns that might have been missed
    content = re.sub(r'\(cid:[^)]+\)', '', content)
    
    # Remove excessive blank lines one more time
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip() + '\n' if content.strip() else content


def main():
    parser = argparse.ArgumentParser(
        description='Clean up markdown files from PDF conversion artifacts'
    )
    parser.add_argument('input_file', help='Input markdown file to clean')
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: overwrite input if --in-place, else stdout)'
    )
    parser.add_argument(
        '--in-place', '-i',
        action='store_true',
        help='Modify file in place (overwrites original)'
    )
    parser.add_argument(
        '--backup', '-b',
        action='store_true',
        help='Create backup file (.bak) when using --in-place'
    )
    
    args = parser.parse_args()
    
    # Read input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        content = input_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # Try with error handling
        content = input_path.read_text(encoding='utf-8', errors='replace')
    
    # Clean the content
    cleaned = cleanup_markdown(content)
    
    # Determine output
    if args.in_place:
        if args.backup:
            backup_path = input_path.with_suffix(input_path.suffix + '.bak')
            backup_path.write_text(content, encoding='utf-8')
            print(f"Backup created: {backup_path}", file=sys.stderr)
        
        input_path.write_text(cleaned, encoding='utf-8')
        print(f"Cleaned: {input_path}", file=sys.stderr)
    elif args.output:
        output_path = Path(args.output)
        output_path.write_text(cleaned, encoding='utf-8')
        print(f"Cleaned file written to: {output_path}", file=sys.stderr)
    else:
        # Write to stdout
        print(cleaned, end='')
    
    # Print statistics
    original_size = len(content)
    cleaned_size = len(cleaned)
    reduction = original_size - cleaned_size
    reduction_pct = (reduction / original_size * 100) if original_size > 0 else 0
    
    print(
        f"Original: {original_size:,} chars | "
        f"Cleaned: {cleaned_size:,} chars | "
        f"Reduced: {reduction:,} chars ({reduction_pct:.1f}%)",
        file=sys.stderr
    )


if __name__ == '__main__':
    main()

