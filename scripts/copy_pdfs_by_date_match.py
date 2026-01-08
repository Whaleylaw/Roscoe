#!/usr/bin/env python3
"""
Copy PDF files to Medical Records by matching date patterns.
Uses pdf_md_mapping.json to find PDF originals, matches to MD files by date.
"""

import os
import sys
import shutil
import re
from pathlib import Path
import json

def extract_date(filename: str) -> str:
    """Extract YYYY-MM-DD date pattern from filename."""
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        return match.group(0)
    # Try YYYYMMDD format
    match = re.search(r'(\d{8})', filename)
    if match:
        date_str = match.group(0)
        return f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
    return None

def copy_pdfs_by_date(case_dir: str, dry_run: bool = True):
    """
    Copy PDFs to Medical Records by matching dates between mapping and actual files.

    Args:
        case_dir: Path to case directory
        dry_run: If True, only show what would be done
    """

    case_path = Path(case_dir)
    mapping_file = case_path / "pdf_md_mapping.json"
    pdf_originals = case_path / "_pdf_originals" / "_pdf_originals"
    medical_records = case_path / "Medical Records"

    if not mapping_file.exists():
        print(f"❌ Mapping file not found: {mapping_file}")
        return False

    if not pdf_originals.exists():
        print(f"❌ PDF originals folder not found: {pdf_originals}")
        return False

    # Load mapping
    with open(mapping_file) as f:
        data = json.load(f)

    scrambled_map = data.get("scrambled_md_map", {})

    if not scrambled_map:
        print("❌ No scrambled_md_map found in mapping file")
        return False

    print(f"{'🔍 DRY RUN MODE' if dry_run else '✅ LIVE MODE'}\n")

    # Build index of Medical Records MD files by date
    print("📋 Indexing Medical Records MD files by date...")
    md_by_date = {}
    for md_file in medical_records.rglob("*.md"):
        date = extract_date(md_file.name)
        if date:
            if date not in md_by_date:
                md_by_date[date] = []
            md_by_date[date].append(md_file)

    print(f"   Found {len(md_by_date)} unique dates in Medical Records\n")

    # Track statistics
    stats = {
        "total_medical_mappings": 0,
        "pdf_exists": 0,
        "pdf_copied": 0,
        "pdf_not_found": 0,
        "md_not_found": 0,
        "errors": 0,
        "skipped_no_date": 0
    }

    # Process each mapping entry for Medical Records
    for descriptive_md_path, scrambled_md_path in scrambled_map.items():
        # Check if this is a Medical Records file
        if not descriptive_md_path.startswith("2_MEDICAL_RECORDS"):
            continue

        stats["total_medical_mappings"] += 1

        # Extract date from mapped path
        date = extract_date(descriptive_md_path)
        if not date:
            stats["skipped_no_date"] += 1
            continue

        # Find matching MD files in Medical Records
        if date not in md_by_date:
            stats["md_not_found"] += 1
            continue

        # Get PDF source path
        descriptive_pdf_path = descriptive_md_path.replace(".md", ".pdf")
        pdf_source = pdf_originals / descriptive_pdf_path

        if not pdf_source.exists():
            print(f"\n⚠️  PDF not found: {descriptive_pdf_path}")
            stats["pdf_not_found"] += 1
            continue

        # Copy PDF to each matching MD location
        for md_file in md_by_date[date]:
            # Determine PDF target name
            # Use the MD filename but with .pdf extension
            pdf_target = md_file.parent / md_file.name.replace(".md", ".pdf")

            if pdf_target.exists():
                stats["pdf_exists"] += 1
                continue

            relative_md = md_file.relative_to(medical_records)
            relative_pdf_source = pdf_source.relative_to(pdf_originals)

            print(f"\n📄 MD: Medical Records/{relative_md}")
            print(f"📑 PDF Target: {md_file.name.replace('.md', '.pdf')}")
            print(f"   ← {relative_pdf_source}")

            if not dry_run:
                try:
                    shutil.copy2(str(pdf_source), str(pdf_target))
                    stats["pdf_copied"] += 1
                    print(f"   ✅ Copied")
                except Exception as e:
                    print(f"   ❌ Error copying: {e}")
                    stats["errors"] += 1
            else:
                stats["pdf_copied"] += 1

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"📋 Medical Records mappings: {stats['total_medical_mappings']}")
    print(f"✅ PDFs already exist: {stats['pdf_exists']}")
    print(f"✅ PDFs copied: {stats['pdf_copied']}")
    print(f"⚠️  PDFs not found in originals: {stats['pdf_not_found']}")
    print(f"⚠️  MD files not found (by date): {stats['md_not_found']}")
    if stats['skipped_no_date']:
        print(f"ℹ️  Skipped (no date in filename): {stats['skipped_no_date']}")
    if stats['errors']:
        print(f"❌ Errors: {stats['errors']}")

    return stats['pdf_not_found'] == 0 and stats['errors'] == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python copy_pdfs_by_date_match.py <case_directory> [--live]")
        print("\nExample:")
        print("  python copy_pdfs_by_date_match.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022")
        print("  python copy_pdfs_by_date_match.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022 --live")
        sys.exit(1)

    case_dir = sys.argv[1]
    dry_run = "--live" not in sys.argv

    if not os.path.exists(case_dir):
        print(f"❌ Case directory not found: {case_dir}")
        sys.exit(1)

    success = copy_pdfs_by_date(case_dir, dry_run=dry_run)

    if dry_run:
        print("\n🔍 This was a dry run. Use --live flag to apply changes.")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
