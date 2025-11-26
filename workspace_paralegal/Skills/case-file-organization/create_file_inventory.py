#!/usr/bin/env python3
"""
File Inventory Generator for Case File Organization (Content-Only Mode)

Eliminates filename bias by:
1. Moving all PDFs to _pdf_originals/ temporary folder
2. Scrambling .md filenames with random sequential names
3. Creating mapping file to reunite PDFs and .md files at execution time
4. Sub-agents work ONLY with scrambled .md files (pure content analysis)

Used in Phase 1 of the case-file-organization skill.

Usage:
    python create_file_inventory.py "/path/to/case/directory"

Output:
    - /Reports/file_inventory_{case_name}.md (listing scrambled .md files)
    - /Reports/pdf_md_mapping_{case_name}.json (scrambled → original mapping)
    - /_pdf_originals/ (PDFs moved here temporarily)
"""

import sys
import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime


def scramble_and_isolate_pdfs(case_dir: Path):
    """
    Move all PDFs to _pdf_originals/ and scramble .md filenames.

    Returns:
        dict: Mapping of scrambled_md_name → {original_pdf, original_md}
    """

    pdf_originals_dir = case_dir / "_pdf_originals"
    pdf_originals_dir.mkdir(exist_ok=True)

    mapping = {}
    counter = 1

    # Find all PDF + .md pairs
    for pdf_file in case_dir.rglob('*.pdf'):
        # Skip if already in _pdf_originals or Reports
        if '_pdf_originals' in pdf_file.parts or 'Reports' in pdf_file.parts:
            continue

        md_file = pdf_file.with_suffix('.md')

        if not md_file.exists():
            # PDF without .md companion - skip (needs .md extraction first)
            continue

        # Generate scrambled name
        scrambled_name = f"doc_{counter:04d}.md"
        counter += 1

        # Get relative paths from case directory
        original_pdf_rel = pdf_file.relative_to(case_dir)
        original_md_rel = md_file.relative_to(case_dir)

        # Move PDF to _pdf_originals (preserve structure)
        pdf_dest = pdf_originals_dir / original_pdf_rel
        pdf_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(pdf_file), str(pdf_dest))

        # Rename .md to scrambled name (flat structure in root)
        scrambled_md_path = case_dir / scrambled_name
        shutil.move(str(md_file), str(scrambled_md_path))

        # Store mapping
        mapping[scrambled_name] = {
            "original_pdf": str(original_pdf_rel),
            "original_md": str(original_md_rel),
            "pdf_location": str(pdf_dest.relative_to(case_dir))
        }

    return mapping


def generate_inventory(case_dir: Path, output_dir: Path, mapping: dict):
    """Generate file inventory listing scrambled .md files and other non-PDF files."""

    case_name = case_dir.name
    output_file = output_dir / f"file_inventory_{case_name}.md"

    # Collect all files (excluding _pdf_originals and Reports)
    all_files = []
    for file_path in sorted(case_dir.rglob('*')):
        if file_path.is_file():
            # Skip hidden files, system files, and excluded directories
            if file_path.name.startswith('.'):
                continue
            if '_pdf_originals' in file_path.parts or 'Reports' in file_path.parts:
                continue

            # Get relative path from case directory
            rel_path = file_path.relative_to(case_dir)

            # Determine file type
            suffix = file_path.suffix.lower()
            if suffix == '.pdf':
                # Should not happen - all PDFs should be moved
                file_type = 'PDF'
            elif suffix == '.eml':
                file_type = 'EML'
            elif suffix == '.md':
                file_type = 'MD'
            elif suffix in ['.jpg', '.jpeg', '.png', '.gif']:
                file_type = 'IMAGE'
            elif suffix in ['.doc', '.docx']:
                file_type = 'DOC'
            elif suffix in ['.xls', '.xlsx']:
                file_type = 'EXCEL'
            elif suffix in ['.mp4', '.mov', '.avi']:
                file_type = 'VIDEO'
            elif suffix in ['.mp3', '.wav', '.m4a']:
                file_type = 'AUDIO'
            else:
                file_type = suffix[1:].upper() if suffix else 'OTHER'

            # For scrambled .md files, note they have PDF companions (in mapping)
            has_md = 'N/A'
            if file_type == 'MD' and file_path.name in mapping:
                has_md = 'PDF_COMPANION'  # Indicates this .md came from a PDF pair

            all_files.append({
                'path': str(rel_path),
                'type': file_type,
                'has_md': has_md,
                'size': file_path.stat().st_size
            })

    # Generate markdown report
    lines = []
    lines.append(f"# File Inventory: {case_name}\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Case Directory:** `{case_dir}`")
    lines.append(f"**Total Files:** {len(all_files)}")
    lines.append(f"**Mode:** Content-Only (filenames scrambled, PDFs isolated)\n")

    # Summary by type
    type_counts = {}
    for f in all_files:
        type_counts[f['type']] = type_counts.get(f['type'], 0) + 1

    lines.append("## File Type Summary\n")
    for ftype in sorted(type_counts.keys()):
        lines.append(f"- **{ftype}:** {type_counts[ftype]} files")
    lines.append("")

    # Scrambled files note
    pdf_companion_count = sum(1 for f in all_files if f['has_md'] == 'PDF_COMPANION')
    if pdf_companion_count > 0:
        lines.append("## Important Notes\n")
        lines.append(f"- **{pdf_companion_count} .md files** are scrambled versions of PDF companions")
        lines.append(f"- Original PDFs moved to `_pdf_originals/` directory")
        lines.append(f"- Mapping file: `Reports/pdf_md_mapping_{case_name}.json`")
        lines.append(f"- **Analyze ONLY file content** - filenames are randomized")
        lines.append("")

    # Detailed file list
    lines.append("## Complete File List\n")
    lines.append("| Path | Type | Notes |")
    lines.append("|------|------|-------|")

    for f in all_files:
        path = f['path']
        # Escape pipe characters in filenames
        path = path.replace('|', '\\|')

        notes = ""
        if f['has_md'] == 'PDF_COMPANION':
            notes = "PDF companion (scrambled name)"

        lines.append(f"| {path} | {f['type']} | {notes} |")

    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text('\n'.join(lines))

    print(f"Inventory generated: {output_file}")
    print(f"Total files: {len(all_files)}")
    print(f"Scrambled .md files: {pdf_companion_count}")
    print(f"File types: {', '.join([f'{k}: {v}' for k, v in sorted(type_counts.items())])}")

    return output_file, len(all_files)


def save_mapping(mapping: dict, case_dir: Path):
    """Save scrambled → original mapping to JSON file."""

    case_name = case_dir.name
    reports_dir = case_dir / "Reports"
    reports_dir.mkdir(exist_ok=True)

    mapping_file = reports_dir / f"pdf_md_mapping_{case_name}.json"

    with open(mapping_file, 'w') as f:
        json.dump(mapping, f, indent=2)

    print(f"Mapping file created: {mapping_file}")
    print(f"Mapped {len(mapping)} PDF+MD pairs")

    return mapping_file


def main():
    parser = argparse.ArgumentParser(
        description="Generate file inventory with content-only mode (scrambled filenames)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "case_dir",
        help="Path to case directory"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for inventory file (default: case_dir/Reports/)",
        default=None
    )

    args = parser.parse_args()

    case_dir = Path(args.case_dir)

    if not case_dir.exists():
        print(f"ERROR: Case directory not found: {case_dir}", file=sys.stderr)
        sys.exit(1)

    if not case_dir.is_dir():
        print(f"ERROR: Not a directory: {case_dir}", file=sys.stderr)
        sys.exit(1)

    # Default output to case_dir/Reports/
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = case_dir / "Reports"

    try:
        print("Phase 1: Scrambling filenames and isolating PDFs...")
        print("-" * 60)

        # Step 1: Scramble .md files and move PDFs to _pdf_originals/
        mapping = scramble_and_isolate_pdfs(case_dir)

        # Step 2: Save mapping file
        mapping_file = save_mapping(mapping, case_dir)

        print("-" * 60)
        print("Phase 2: Generating inventory...")
        print("-" * 60)

        # Step 3: Generate inventory (only scrambled .md files visible)
        output_file, file_count = generate_inventory(case_dir, output_dir, mapping)

        print("-" * 60)
        print("SUCCESS: Content-only mode activated")
        print(f"Sub-agents will analyze {len(mapping)} scrambled .md files")
        print("Filename bias eliminated - naming will be based purely on content")

        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
