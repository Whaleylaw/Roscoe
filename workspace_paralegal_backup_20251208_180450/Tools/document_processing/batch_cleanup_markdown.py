#!/usr/bin/env python3
"""
Batch clean up markdown files from PDF conversion artifacts.

Finds all .md files in a directory (recursively) and cleans them using cleanup_markdown.py.

Usage:
    python batch_cleanup_markdown.py <directory> [--dry-run] [--backup]
"""

import argparse
import sys
from pathlib import Path

# Import the cleanup function from cleanup_markdown.py
# We'll use subprocess to call it to keep it modular
import subprocess


def find_markdown_files(directory: Path, recursive: bool = True) -> list[Path]:
    """
    Find all markdown files in directory.
    
    Args:
        directory: Root directory to search
        recursive: Whether to search subdirectories
        
    Returns:
        List of Path objects for .md files
    """
    if recursive:
        return list(directory.rglob("*.md"))
    else:
        return list(directory.glob("*.md"))


def main():
    parser = argparse.ArgumentParser(
        description='Batch clean up markdown files from PDF conversion artifacts'
    )
    parser.add_argument(
        'directory',
        help='Directory containing markdown files to clean'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be cleaned without actually cleaning'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create .bak backup files (default: no backup)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Explicitly disable backups (overrides --backup)'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        help='Patterns to exclude (e.g., --exclude "*.bak.md" "backup/*")'
    )
    
    args = parser.parse_args()
    
    # Resolve directory path
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory not found: {directory}", file=sys.stderr)
        sys.exit(1)
    
    if not directory.is_dir():
        print(f"Error: Not a directory: {directory}", file=sys.stderr)
        sys.exit(1)
    
    # Find all markdown files
    md_files = find_markdown_files(directory, recursive=True)
    
    # Filter out backups and excluded patterns
    filtered_files = []
    for md_file in md_files:
        # Skip backup files
        if md_file.name.endswith('.bak.md') or '.bak' in md_file.name:
            continue
        
        # Skip excluded patterns
        if args.exclude:
            skip = False
            for pattern in args.exclude:
                if pattern in str(md_file):
                    skip = True
                    break
            if skip:
                continue
        
        filtered_files.append(md_file)
    
    if not filtered_files:
        print(f"No markdown files found in {directory}", file=sys.stderr)
        sys.exit(0)
    
    print(f"Found {len(filtered_files)} markdown file(s) to clean", file=sys.stderr)
    
    if args.dry_run:
        print("\nDRY RUN - Files that would be cleaned:", file=sys.stderr)
        for md_file in filtered_files:
            print(f"  {md_file}", file=sys.stderr)
        sys.exit(0)
    
    # Determine backup flag
    create_backup = args.backup and not args.no_backup
    
    # Get path to cleanup_markdown.py script
    script_dir = Path(__file__).parent
    cleanup_script = script_dir / "cleanup_markdown.py"
    
    if not cleanup_script.exists():
        print(f"Error: cleanup_markdown.py not found at {cleanup_script}", file=sys.stderr)
        sys.exit(1)
    
    # Process each file
    cleaned_count = 0
    error_count = 0
    total_reduction = 0
    total_original_size = 0
    
    for md_file in filtered_files:
        try:
            print(f"Cleaning: {md_file}", file=sys.stderr)
            
            # Build command
            cmd = [
                sys.executable,
                str(cleanup_script),
                str(md_file),
                "--in-place"
            ]
            
            if create_backup:
                cmd.append("--backup")
            
            # Run cleanup script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(script_dir.parent.parent)  # Set working directory
            )
            
            if result.returncode == 0:
                cleaned_count += 1
                # Parse reduction from stderr output
                # Format: "Original: X chars | Cleaned: Y chars | Reduced: Z chars (P%)"
                for line in result.stderr.split('\n'):
                    if 'Original:' in line and 'Reduced:' in line:
                        # Extract reduction percentage
                        try:
                            parts = line.split('|')
                            original_part = parts[0].split(':')[1].strip().replace(',', '')
                            reduction_part = parts[2].split('(')[1].split('%')[0]
                            original_size = int(original_part.split()[0])
                            reduction_pct = float(reduction_part)
                            total_original_size += original_size
                            total_reduction += original_size * (reduction_pct / 100)
                        except (ValueError, IndexError):
                            pass
                        break
            else:
                error_count += 1
                print(f"  Error cleaning {md_file}: {result.stderr}", file=sys.stderr)
        
        except Exception as e:
            error_count += 1
            print(f"  Exception cleaning {md_file}: {e}", file=sys.stderr)
    
    # Print summary
    print("\n" + "="*60, file=sys.stderr)
    print(f"Batch cleanup complete:", file=sys.stderr)
    print(f"  Files cleaned: {cleaned_count}/{len(filtered_files)}", file=sys.stderr)
    if error_count > 0:
        print(f"  Errors: {error_count}", file=sys.stderr)
    if total_original_size > 0:
        avg_reduction_pct = (total_reduction / total_original_size) * 100
        print(
            f"  Average reduction: {avg_reduction_pct:.1f}% "
            f"({total_reduction:,.0f} chars removed from {total_original_size:,.0f} total)",
            file=sys.stderr
        )
    print("="*60, file=sys.stderr)


if __name__ == '__main__':
    main()

