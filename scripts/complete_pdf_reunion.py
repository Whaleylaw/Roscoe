#!/usr/bin/env python3
"""
Complete the PDF reunion process for the Case File Organization skill.
Uses pdf_md_mapping.json to find and copy PDFs to match their MD companions.
"""

import os
import sys
import shutil
import json
import re
from pathlib import Path
from typing import Dict, Optional

def extract_date_from_filename(filename: str) -> Optional[str]:
    """Extract YYYY-MM-DD date from filename."""
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        return match.group(0)
    return None

def extract_provider_keywords(path: str) -> set:
    """Extract potential provider keywords from path."""
    # Remove dates and common words
    text = re.sub(r'\d{4}-\d{2}-\d{2}', '', path)
    text = re.sub(r'James Kiper|Medical Records?|Medical Bills?|Medical Requests?', '', text, flags=re.IGNORECASE)

    # Extract meaningful words (3+ chars)
    words = set()
    for word in re.findall(r'\b[A-Za-z]{3,}\b', text):
        words.add(word.lower())

    return words

def find_best_match(md_file: Path, mapped_paths: list, case_path: Path) -> Optional[str]:
    """
    Find best matching mapped path for an MD file based on date and provider.

    Args:
        md_file: Current MD file path
        mapped_paths: List of descriptive paths from mapping
        case_path: Case directory path

    Returns:
        Best matching descriptive path or None
    """
    md_date = extract_date_from_filename(md_file.name)
    if not md_date:
        return None

    # Get provider folder and keywords from current location
    try:
        relative_path = md_file.relative_to(case_path / "Medical Records")
        provider_folder = str(relative_path.parts[0]) if relative_path.parts else ""
        md_keywords = extract_provider_keywords(str(relative_path))
    except ValueError:
        return None

    # Find candidates with same date
    candidates = []
    for mapped_path in mapped_paths:
        mapped_date = extract_date_from_filename(mapped_path)
        if mapped_date == md_date:
            candidates.append(mapped_path)

    if not candidates:
        return None

    if len(candidates) == 1:
        return candidates[0]

    # Score candidates by provider keyword overlap
    best_match = None
    best_score = 0

    for candidate in candidates:
        candidate_keywords = extract_provider_keywords(candidate)
        overlap = len(md_keywords & candidate_keywords)

        # Bonus for provider folder name match
        if provider_folder.lower() in candidate.lower():
            overlap += 5

        if overlap > best_score:
            best_score = overlap
            best_match = candidate

    return best_match if best_score > 0 else candidates[0]  # Fall back to first if no clear winner

def complete_pdf_reunion(case_dir: str, dry_run: bool = True):
    """
    Complete the PDF reunion for Medical Records.

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
        print("❌ No scrambled_md_map found")
        return False

    print(f"{'🔍 DRY RUN MODE' if dry_run else '✅ LIVE MODE'}\n")
    print(f"Found {len(scrambled_map)} file mappings\n")

    # Build reverse index: descriptive_path -> pdf_location
    medical_mapped_paths = {}
    for descriptive_path in scrambled_map.keys():
        if descriptive_path.startswith("2_MEDICAL_RECORDS"):
            # Get PDF location
            pdf_path = descriptive_path.replace(".md", ".pdf")
            pdf_full_path = pdf_originals / pdf_path
            if pdf_full_path.exists():
                medical_mapped_paths[descriptive_path] = pdf_full_path

    print(f"📋 Found {len(medical_mapped_paths)} Medical Records PDFs in originals\n")

    # Track statistics
    stats = {
        "total_md": 0,
        "matched": 0,
        "copied": 0,
        "pdf_exists": 0,
        "no_match": 0,
        "errors": 0
    }

    # Process each MD file in Medical Records
    md_files = list(medical_records.rglob("*.md"))
    stats["total_md"] = len(md_files)

    for md_file in md_files:
        # Check if PDF already exists
        pdf_target = md_file.parent / md_file.name.replace(".md", ".pdf")

        if pdf_target.exists():
            stats["pdf_exists"] += 1
            continue

        # Find best matching mapped path
        best_match = find_best_match(md_file, list(medical_mapped_paths.keys()), case_path)

        if not best_match:
            relative_md = md_file.relative_to(medical_records)
            print(f"\n⚠️  No match found for: Medical Records/{relative_md}")
            stats["no_match"] += 1
            continue

        # Get PDF source
        pdf_source = medical_mapped_paths[best_match]

        relative_md = md_file.relative_to(medical_records)
        relative_source = pdf_source.relative_to(pdf_originals)

        print(f"\n📄 MD: Medical Records/{relative_md}")
        print(f"📑 PDF: {pdf_target.name}")
        print(f"   ← {relative_source}")
        print(f"   Match: {best_match}")

        stats["matched"] += 1

        if not dry_run:
            try:
                shutil.copy2(str(pdf_source), str(pdf_target))
                stats["copied"] += 1
                print(f"   ✅ Copied")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                stats["errors"] += 1
        else:
            stats["copied"] += 1

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"📄 Total MD files: {stats['total_md']}")
    print(f"✅ PDFs already exist: {stats['pdf_exists']}")
    print(f"🔍 Matches found: {stats['matched']}")
    print(f"✅ PDFs copied: {stats['copied']}")
    print(f"⚠️  No match found: {stats['no_match']}")
    if stats['errors']:
        print(f"❌ Errors: {stats['errors']}")

    return stats['errors'] == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python complete_pdf_reunion.py <case_directory> [--live]")
        print("\nExample:")
        print("  python complete_pdf_reunion.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022")
        print("  python complete_pdf_reunion.py /mnt/workspace/projects/James-Kiper-MVA-12-5-2022 --live")
        sys.exit(1)

    case_dir = sys.argv[1]
    dry_run = "--live" not in sys.argv

    if not os.path.exists(case_dir):
        print(f"❌ Case directory not found: {case_dir}")
        sys.exit(1)

    success = complete_pdf_reunion(case_dir, dry_run=dry_run)

    if dry_run:
        print("\n🔍 This was a dry run. Use --live flag to apply changes.")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
