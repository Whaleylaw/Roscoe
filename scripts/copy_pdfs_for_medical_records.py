#!/usr/bin/env python3
"""
Copy PDF files to Medical Records folder to match existing MD files.
"""

import os
import sys
import shutil
from pathlib import Path

def copy_pdfs_for_mds(case_dir: str, dry_run: bool = True):
    """
    Find all MD files in Medical Records and copy corresponding PDFs from _pdf_originals.

    Args:
        case_dir: Path to case directory
        dry_run: If True, only show what would be done
    """

    case_path = Path(case_dir)
    medical_records = case_path / "Medical Records"
    pdf_originals = case_path / "_pdf_originals" / "_pdf_originals"

    if not medical_records.exists():
        print(f"❌ Medical Records folder not found: {medical_records}")
        return False

    if not pdf_originals.exists():
        print(f"❌ PDF originals folder not found: {pdf_originals}")
        return False

    print(f"{'🔍 DRY RUN MODE' if dry_run else '✅ LIVE MODE'}\n")

    # Track statistics
    stats = {
        "total_md": 0,
        "pdf_exists": 0,
        "pdf_copied": 0,
        "pdf_not_found": 0,
        "errors": 0
    }

    # Find all MD files in Medical Records
    md_files = list(medical_records.rglob("*.md"))
    stats["total_md"] = len(md_files)

    print(f"Found {len(md_files)} MD files in Medical Records\n")

    for md_file in md_files:
        # Get corresponding PDF name
        pdf_name = md_file.name.replace(".md", ".pdf")
        pdf_target = md_file.parent / pdf_name

        # Check if PDF already exists
        if pdf_target.exists():
            stats["pdf_exists"] += 1
            continue

        # Try to find PDF in originals
        # First try with full provider path structure
        relative_path = md_file.relative_to(medical_records)
        relative_pdf_path = str(relative_path).replace(".md", ".pdf")

        # Try different possible locations in pdf_originals
        possible_paths = [
            pdf_originals / "2_MEDICAL_RECORDS" / pdf_name,  # Flat structure
            pdf_originals / "Medical Records" / relative_pdf_path,  # Mirror structure
            pdf_originals / pdf_name,  # Root level
        ]

        # Also check if filename has provider name pattern
        # e.g., "2022-12-05 - James Kiper - Medical Records - Provider - File.pdf"

        pdf_source = None
        for possible_path in possible_paths:
            if possible_path.exists():
                pdf_source = possible_path
                break

        if pdf_source:
            print(f"\n📄 MD: {relative_path}")
            print(f"📑 PDF: {pdf_name}")
            print(f"   ← {pdf_source.relative_to(pdf_originals)}")

            if not dry_run:
                try:
                    shutil.copy2(str(pdf_source), str(pdf_target))
                    stats["pdf_copied"] += 1
                except Exception as e:
                    print(f"   ❌ Error copying: {e}")
                    stats["errors"] += 1
            else:
                stats["pdf_copied"] += 1
        else:
            # Look for the PDF anywhere in pdf_originals by name
            found_files = list(pdf_originals.rglob(pdf_name))
            if found_files:
                pdf_source = found_files[0]
                print(f"\n📄 MD: {relative_path}")
                print(f"📑 PDF: {pdf_name}")
                print(f"   ← {pdf_source.relative_to(pdf_originals)}")

                if not dry_run:
                    try:
                        shutil.copy2(str(pdf_source), str(pdf_target))
                        stats["pdf_copied"] += 1
                    except Exception as e:
                        print(f"   ❌ Error copying: {e}")
                        stats["errors"] += 1
                else:
                    stats["pdf_copied"] += 1
            else:
                print(f"\n⚠️  No PDF found for: {relative_path}")
                print(f"   Looking for: {pdf_name}")
                stats["pdf_not_found"] += 1

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"📄 Total MD files: {stats['total_md']}")
    print(f"✅ PDFs already exist: {stats['pdf_exists']}")
    print(f"✅ PDFs copied: {stats['pdf_copied']}")
    print(f"⚠️  PDFs not found: {stats['pdf_not_found']}")
    if stats['errors']:
        print(f"❌ Errors: {stats['errors']}")

    return stats['pdf_not_found'] == 0 and stats['errors'] == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python copy_pdfs_for_medical_records.py <case_directory> [--live]")
        print("\nExample:")
        print("  python copy_pdfs_for_medical_records.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022")
        print("  python copy_pdfs_for_medical_records.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022 --live")
        sys.exit(1)

    case_dir = sys.argv[1]
    dry_run = "--live" not in sys.argv

    if not os.path.exists(case_dir):
        print(f"❌ Case directory not found: {case_dir}")
        sys.exit(1)

    success = copy_pdfs_for_mds(case_dir, dry_run=dry_run)

    if dry_run:
        print("\n🔍 This was a dry run. Use --live flag to apply changes.")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
