#!/usr/bin/env python3
"""
Rename scrambled MD files to descriptive names and copy corresponding PDFs.
Uses the scrambled_md_map from pdf_md_mapping.json.
"""

import os
import sys
import shutil
from pathlib import Path
import json

def rename_and_copy_files(case_dir: str, folder_filter: str = None, dry_run: bool = True):
    """
    Rename scrambled MD files to descriptive names and copy matching PDFs.

    Args:
        case_dir: Path to case directory
        folder_filter: Only process files in this folder (e.g., "Medical Records")
        dry_run: If True, only show what would be done
    """

    case_path = Path(case_dir)
    mapping_file = case_path / "pdf_md_mapping.json"
    pdf_originals = case_path / "_pdf_originals" / "_pdf_originals"

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
    print(f"Found {len(scrambled_map)} file mappings\n")

    # Track statistics
    stats = {
        "renamed_md": 0,
        "copied_pdf": 0,
        "md_not_found": 0,
        "pdf_not_found": 0,
        "skipped_filter": 0
    }

    # Process each mapping
    for descriptive_name, scrambled_name in scrambled_map.items():
        # Apply folder filter if specified
        if folder_filter and not descriptive_name.startswith(folder_filter):
            stats["skipped_filter"] += 1
            continue

        # Paths
        scrambled_md_path = case_path / scrambled_name
        descriptive_md_path = case_path / descriptive_name

        # Get PDF path (replace .md with .pdf in descriptive name)
        descriptive_pdf_name = descriptive_name.replace(".md", ".pdf")
        pdf_original_path = pdf_originals / descriptive_pdf_name
        descriptive_pdf_path = case_path / descriptive_pdf_name

        # Check if scrambled MD exists
        if not scrambled_md_path.exists():
            print(f"⚠️  MD not found: {scrambled_name}")
            stats["md_not_found"] += 1
            continue

        # Rename MD file
        print(f"\n📄 MD: {scrambled_name}")
        print(f"   → {descriptive_name}")

        if not dry_run:
            # Create parent directory if needed
            descriptive_md_path.parent.mkdir(parents=True, exist_ok=True)

            # Rename (move) the file
            shutil.move(str(scrambled_md_path), str(descriptive_md_path))
            stats["renamed_md"] += 1
        else:
            stats["renamed_md"] += 1

        # Copy corresponding PDF
        if pdf_original_path.exists():
            print(f"📑 PDF: {descriptive_pdf_name}")
            print(f"   ← {pdf_original_path.name}")

            if not dry_run:
                # Create parent directory if needed
                descriptive_pdf_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy PDF to same location as MD
                shutil.copy2(str(pdf_original_path), str(descriptive_pdf_path))
                stats["copied_pdf"] += 1
            else:
                stats["copied_pdf"] += 1
        else:
            print(f"⚠️  PDF not found: {pdf_original_path}")
            stats["pdf_not_found"] += 1

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"✅ MD files renamed: {stats['renamed_md']}")
    print(f"✅ PDF files copied: {stats['copied_pdf']}")
    print(f"⚠️  MD files not found: {stats['md_not_found']}")
    print(f"⚠️  PDF files not found: {stats['pdf_not_found']}")
    if folder_filter:
        print(f"ℹ️  Files skipped (not in '{folder_filter}'): {stats['skipped_filter']}")

    return stats["md_not_found"] == 0 and stats["pdf_not_found"] == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python rename_files_from_mapping.py <case_directory> [--folder FOLDER] [--live]")
        print("\nExample:")
        print("  python rename_files_from_mapping.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022")
        print("  python rename_files_from_mapping.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022 --folder '2_MEDICAL_RECORDS'")
        print("  python rename_files_from_mapping.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022 --live")
        sys.exit(1)

    case_dir = sys.argv[1]
    dry_run = "--live" not in sys.argv

    # Check for folder filter
    folder_filter = None
    if "--folder" in sys.argv:
        folder_idx = sys.argv.index("--folder")
        if folder_idx + 1 < len(sys.argv):
            folder_filter = sys.argv[folder_idx + 1]
            print(f"ℹ️  Filtering to folder: {folder_filter}\n")

    if not os.path.exists(case_dir):
        print(f"❌ Case directory not found: {case_dir}")
        sys.exit(1)

    success = rename_and_copy_files(case_dir, folder_filter=folder_filter, dry_run=dry_run)

    if dry_run:
        print("\n🔍 This was a dry run. Use --live flag to apply changes.")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
