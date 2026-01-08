#!/usr/bin/env python3
"""
Match NEW entities from review documents against directory.json

Finds all entities marked "? NEW" and checks if they match existing
entries in the master directory.
"""

import re
from pathlib import Path
from collections import defaultdict
from rapidfuzz import fuzz


def load_directory_names(directory_file: Path) -> list[str]:
    """Extract all full_name entries from directory.json."""
    names = []

    with open(directory_file) as f:
        content = f.read()
        # Extract all "full_name": "..." patterns
        matches = re.findall(r'"full_name":\s*"([^"]+)"', content)
        names = [m.strip() for m in matches if m.strip()]

    return sorted(set(names))


def load_new_entities_from_reviews(reviews_dir: Path) -> dict:
    """
    Load all entities marked "? NEW" from review documents.

    Returns: dict of {entity_type: {entity_name: [case_names]}}
    """
    new_entities = defaultdict(lambda: defaultdict(list))

    review_files = list(reviews_dir.glob("review_*.md"))
    print(f"  - Found {len(review_files)} review files")

    for review_file in review_files:
        case_name = review_file.stem.replace('review_', '')

        with open(review_file) as f:
            content = f.read()

        # Extract entity sections (### EntityType)
        sections = re.split(r'\n### ([A-Za-z]+) \(\d+ consolidated\)', content)

        for i in range(1, len(sections), 2):
            entity_type = sections[i]
            section_content = sections[i+1]

            # Find all "? NEW" entities in this section
            # Pattern: - [ ] Name — *? NEW* or - [ ] **Name** — *? NEW*
            # Match both: simple names and bold names
            new_pattern = r'- \[ \] (?:\*\*)?([^*—]+?)(?:\*\*)? — \*\? NEW\*'
            matches = re.findall(new_pattern, section_content)

            for entity_name in matches:
                entity_name = entity_name.strip()
                new_entities[entity_type][entity_name].append(case_name)

    return new_entities


def fuzzy_match_name(proposed: str, directory_names: list[str], threshold: int = 85) -> tuple[bool, str, int]:
    """
    Check if proposed name matches any directory entry.

    Returns: (matched: bool, matched_name: str, score: int)
    """
    proposed_lower = proposed.lower().strip()

    best_match = None
    best_score = 0

    for dir_name in directory_names:
        dir_lower = dir_name.lower().strip()

        # Exact match
        if proposed_lower == dir_lower:
            return True, dir_name, 100

        # Fuzzy match
        score = fuzz.ratio(proposed_lower, dir_lower)
        if score > best_score:
            best_score = score
            best_match = dir_name

        # Substring match (one contains the other)
        if len(proposed_lower) > 5 and len(dir_lower) > 5:
            if proposed_lower in dir_lower or dir_lower in proposed_lower:
                if score >= threshold - 10:  # Slightly lower threshold for substrings
                    return True, dir_name, score

    if best_score >= threshold:
        return True, best_match, best_score

    return False, "", best_score


def main():
    reviews_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/reviews")
    directory_file = Path("/Volumes/X10 Pro/Roscoe/json-files/directory.json")

    print("=" * 80)
    print("MATCHING NEW ENTITIES AGAINST DIRECTORY")
    print("=" * 80)
    print()

    # Load directory names
    print("Loading directory names...")
    directory_names = load_directory_names(directory_file)
    print(f"  - {len(directory_names)} unique names in directory")
    print()

    # Load new entities from reviews
    print("Loading entities marked '? NEW' from review documents...")
    new_entities = load_new_entities_from_reviews(reviews_dir)

    total_new = sum(len(entities) for entities in new_entities.values())
    print(f"  - {total_new} unique NEW entities across all reviews")
    print()

    # Match against directory
    print("Matching against directory...")
    print()

    matches_found = defaultdict(list)
    no_match = defaultdict(list)

    for entity_type, entities in sorted(new_entities.items()):
        print(f"### {entity_type} ({len(entities)} NEW)")

        for entity_name, case_names in sorted(entities.items()):
            matched, dir_name, score = fuzzy_match_name(entity_name, directory_names)

            if matched:
                matches_found[entity_type].append({
                    'proposed': entity_name,
                    'directory': dir_name,
                    'score': score,
                    'cases': case_names
                })
                print(f"  ✓ {entity_name}")
                print(f"      → MATCHES: {dir_name} (score: {score})")
                print(f"      → Found in {len(case_names)} cases")
            else:
                no_match[entity_type].append({
                    'proposed': entity_name,
                    'best_score': score,
                    'cases': case_names
                })

        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    total_matched = sum(len(matches) for matches in matches_found.values())
    total_unmatched = sum(len(entities) for entities in no_match.values())

    print(f"Total NEW entities: {total_new}")
    print(f"  - Matched in directory: {total_matched}")
    print(f"  - Not in directory: {total_unmatched}")
    print()

    if matches_found:
        print("MATCHES BY ENTITY TYPE:")
        for entity_type, matches in sorted(matches_found.items()):
            print(f"  {entity_type}: {len(matches)} matches")
        print()

    # Save detailed results
    output_file = reviews_dir / "directory_matches.txt"
    with open(output_file, 'w') as f:
        f.write("DIRECTORY MATCHES FOR NEW ENTITIES\n")
        f.write("=" * 80 + "\n\n")

        for entity_type, matches in sorted(matches_found.items()):
            f.write(f"\n{entity_type} ({len(matches)} matches)\n")
            f.write("-" * 80 + "\n")
            for m in matches:
                f.write(f"\nProposed: {m['proposed']}\n")
                f.write(f"Directory: {m['directory']} (score: {m['score']})\n")
                f.write(f"Cases: {', '.join(m['cases'][:5])}")
                if len(m['cases']) > 5:
                    f.write(f" +{len(m['cases'])-5} more")
                f.write("\n")

    print(f"✅ Detailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
