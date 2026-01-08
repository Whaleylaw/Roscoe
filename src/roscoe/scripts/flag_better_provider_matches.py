#!/usr/bin/env python3
"""
Flag better medical provider matches in review files.

With 2,159 providers (1,386 new), many generic matches like "Norton Hospital"
can now be matched to specific locations like "Norton Hospital Downtown".

Adds flags WITHOUT changing existing matches.
"""

import json
import re
from pathlib import Path
from rapidfuzz import fuzz


def find_better_matches(entity_name: str, current_match: str, all_providers: list) -> list:
    """
    Find more specific provider matches.

    Example:
    - Current: "Norton Hospital"
    - Better: ["Norton Hospital Downtown", "Norton Hospital - Emergency"]

    Returns: List of better match names
    """
    better_matches = []

    # Parse current match name (may include extra info)
    current_clean = current_match.split('(')[0].strip()

    for provider in all_providers:
        provider_name = provider['name']

        # Skip if it's the current match
        if provider_name == current_clean:
            continue

        # Check if this is MORE SPECIFIC than current
        # More specific = contains current name + additional detail
        if current_clean.lower() in provider_name.lower():
            # This provider name contains the current match
            # Check if it's actually more detailed
            if len(provider_name) > len(current_clean):
                # More specific - has additional location/detail
                score = fuzz.ratio(entity_name.lower(), provider_name.lower())
                if score >= 80:  # Good match to original entity name
                    better_matches.append(provider_name)

    # Also check if entity_name itself is more specific
    entity_clean = entity_name.split('(')[0].strip()
    if entity_clean != current_clean:
        for provider in all_providers:
            provider_name = provider['name']
            score = fuzz.ratio(entity_clean.lower(), provider_name.lower())
            if score >= 90 and provider_name != current_clean:
                if provider_name not in better_matches:
                    better_matches.append(provider_name)

    return better_matches[:3]  # Max 3 suggestions


def scan_review_files():
    """Scan review files and flag better medical provider matches."""
    reviews_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/reviews")
    entities_dir = reviews_dir.parent.parent / "entities"

    # Load approved reviews to skip
    approved_file = reviews_dir / "APPROVED_REVIEWS.txt"
    approved = set()
    if approved_file.exists():
        with open(approved_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    approved.add(line)

    # Load all medical providers
    with open(entities_dir / "medical_providers.json") as f:
        all_providers = json.load(f)

    print("=" * 80)
    print("FLAGGING BETTER MEDICAL PROVIDER MATCHES")
    print("=" * 80)
    print(f"Providers in database: {len(all_providers)}")
    print(f"Approved reviews (skipped): {len(approved)}")
    print()

    # Scan review files
    review_files = sorted(reviews_dir.glob("review_*.md"))
    total_flags = 0
    files_with_flags = []

    for review_file in review_files:
        if review_file.name in approved:
            continue

        with open(review_file) as f:
            content = f.read()

        # Find MedicalProvider section
        # Pattern: ### MedicalProvider (N consolidated) followed by entity lines
        med_provider_section = re.search(
            r'### MedicalProvider \(\d+ consolidated\)(.*?)(?=###|---|\Z)',
            content,
            re.DOTALL
        )

        if not med_provider_section:
            continue

        section_content = med_provider_section.group(1)
        updated_section = section_content
        flags_in_file = 0

        # Find all entity lines in section
        # Pattern: - [ ] Name — *✓ MATCHES: Match Name*
        lines = section_content.split('\n')
        new_lines = []

        for line in lines:
            new_lines.append(line)

            match = re.match(r'- \[ \] (?:\*\*)?([^*—]+?)(?:\*\*)? — \*✓ MATCHES: ([^*]+)\*', line)
            if match:
                entity_name = match.group(1).strip()
                current_match = match.group(2).strip()

                # Check for better matches
                better = find_better_matches(entity_name, current_match, all_providers)

                if better:
                    # Add flag
                    flag_line = f"      💡 NOTE: More specific match(es) available:"
                    new_lines.append(flag_line)
                    for better_match in better:
                        new_lines.append(f"         - {better_match}")
                    flags_in_file += 1

        if flags_in_file > 0:
            # Rebuild section
            updated_section = '\n'.join(new_lines)
            content = content.replace(section_content, updated_section)

            # Save
            with open(review_file, 'w') as f:
                f.write(content)

            total_flags += flags_in_file
            files_with_flags.append(review_file.name)
            print(f"✓ {review_file.name}: {flags_in_file} flags added")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files flagged: {len(files_with_flags)}")
    print(f"Total flags added: {total_flags}")
    print()

    if files_with_flags:
        print("Review these files for better matches:")
        for filename in files_with_flags[:20]:
            print(f"  - {filename}")
        if len(files_with_flags) > 20:
            print(f"  ... and {len(files_with_flags) - 20} more")


if __name__ == "__main__":
    scan_review_files()
