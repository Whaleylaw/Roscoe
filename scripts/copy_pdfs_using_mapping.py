#!/usr/bin/env python3
"""
Copy PDF files using the pdf_md_mapping.json to find correct PDF names.
"""

import os
import sys
import shutil
from pathlib import Path
import json

def copy_pdfs_using_mapping(case_dir: str, dry_run: bool = True):
    """
    Copy PDFs to match MD files using the mapping file.

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

    # Track statistics
    stats = {
        "total_mapped": len(scrambled_map),
        "in_medical_records": 0,
        "pdf_exists": 0,
        "pdf_copied": 0,
        "pdf_not_found": 0,
        "errors": 0
    }

    # Process each mapping entry
    for descriptive_md_path, scrambled_md_path in scrambled_map.items():
        # Check if this is a Medical Records file
        if not descriptive_md_path.startswith("2_MEDICAL_RECORDS"):
            continue

        stats["in_medical_records"] += 1

        # Convert numbered path to actual Medical Records path
        # e.g., "2_MEDICAL_RECORDS/file.md" -> "Medical Records/provider/category/file.md"

        # For now, let's check if any MD file in Medical Records has this base name
        base_name = Path(descriptive_md_path).name

        # Find matching MD file in Medical Records
        matching_mds = list(medical_records.rglob(base_name))

        if not matching_mds:
            # MD file doesn't exist in Medical Records yet
            continue

        for md_file in matching_mds:
            # Check if PDF already exists
            pdf_target = md_file.parent / base_name.replace(".md", ".pdf")

            if pdf_target.exists():
                stats["pdf_exists"] += 1
                continue

            # Find PDF in originals using the descriptive path
            descriptive_pdf_path = descriptive_md_path.replace(".md", ".pdf")
            pdf_source = pdf_originals / descriptive_pdf_path

            if pdf_source.exists():
                relative_md = md_file.relative_to(medical_records)
                print(f"\n📄 MD: Medical Records/{relative_md}")
                print(f"📑 PDF: {base_name.replace('.md', '.pdf')}")
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
                print(f"\n⚠️  PDF not found for: {base_name}")
                print(f"   Expected at: {pdf_source.relative_to(case_path)}")
                stats["pdf_not_found"] += 1
                break  # Only report once per base name

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"📋 Total mappings: {stats['total_mapped']}")
    print(f"📁 Medical Records mappings: {stats['in_medical_records']}")
    print(f"✅ PDFs already exist: {stats['pdf_exists']}")
    print(f"✅ PDFs copied: {stats['pdf_copied']}")
    print(f"⚠️  PDFs not found: {stats['pdf_not_found']}")
    if stats['errors']:
        print(f"❌ Errors: {stats['errors']}")

    return stats['pdf_not_found'] == 0 and stats['errors'] == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python copy_pdfs_using_mapping.py <case_directory> [--live]")
        print("\nExample:")
        print("  python copy_pdfs_using_mapping.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022")
        print("  python copy_pdfs_using_mapping.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022 --live")
        sys.exit(1)

    case_dir = sys.argv[1]
    dry_run = "--live" not in sys.argv

    if not os.path.exists(case_dir):
        print(f"❌ Case directory not found: {case_dir}")
        sys.exit(1)

    success = copy_pdfs_using_mapping(case_dir, dry_run=dry_run)

    if dry_run:
        print("\n🔍 This was a dry run. Use --live flag to apply changes.")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
