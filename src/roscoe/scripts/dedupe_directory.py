#!/usr/bin/env python3
"""
Directory Deduplication Script

Analyzes directory.json to find potential duplicate entries using fuzzy matching.
Generates a deduplication report for human review and a merge map for subsequent loading.

Usage:
    python -m roscoe.scripts.dedupe_directory --input /path/to/directory.json --output /path/to/output/
    
Output Files:
    - directory_deduplication_report.json: Full report with duplicate groups
    - directory_merge_map.json: Simple UUID mapping for loading scripts
    - directory_deduplicated.json: Cleaned directory with duplicates merged
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

try:
    from rapidfuzz import fuzz, process
except ImportError:
    print("ERROR: rapidfuzz not installed. Run: pip install rapidfuzz")
    sys.exit(1)


# Similarity thresholds
AUTO_MERGE_THRESHOLD = 95  # High confidence - auto-merge
REVIEW_THRESHOLD = 90      # Medium confidence - flag for review (high to reduce false positives)
PHONE_MATCH_BONUS = 15     # Bonus for matching phone numbers
# Below REVIEW_THRESHOLD = skip (probably different entities)


def load_directory(path: Path) -> list[dict]:
    """Load directory.json and extract entries from jsonb_agg wrapper."""
    with open(path) as f:
        content = f.read().strip()
    
    # Handle malformed export with trailing bracket
    # Some exports have extra ']' at the end
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Try removing trailing characters until we get valid JSON
        for trim in range(1, 10):
            try:
                data = json.loads(content[:-trim].rstrip())
                print(f"Note: Trimmed {trim} characters from malformed JSON")
                break
            except json.JSONDecodeError:
                continue
        else:
            raise ValueError("Could not parse directory.json - malformed JSON")
    
    # Handle various PostgreSQL export formats
    if isinstance(data, dict) and "jsonb_agg" in data:
        entries = data["jsonb_agg"]
    elif isinstance(data, list):
        # Check if it's a list with one dict containing jsonb_agg
        if len(data) >= 1 and isinstance(data[0], dict) and "jsonb_agg" in data[0]:
            entries = data[0]["jsonb_agg"]
        else:
            entries = data
    else:
        raise ValueError(f"Unexpected directory.json format: {type(data)}")
    
    print(f"Loaded {len(entries)} directory entries")
    return entries


def normalize_name(name: str) -> str:
    """Normalize name for better matching."""
    if not name:
        return ""
    # Lowercase, strip whitespace
    normalized = name.lower().strip()
    # Remove common suffixes that don't affect identity
    for suffix in [", llc", " llc", ", inc", " inc", ", pc", " pc", 
                   " insurance company", " insurance co", " ins co",
                   " insurance", " ins"]:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]
    return normalized


def phones_match(entry1: dict, entry2: dict) -> bool:
    """Check if two entries have matching phone numbers."""
    phone1 = entry1.get("phone_normalized")
    phone2 = entry2.get("phone_normalized")
    if phone1 and phone2:
        return phone1 == phone2
    return False


def is_person_name(name: str) -> bool:
    """Check if a name looks like a person (vs organization)."""
    # Person names typically have 2-3 words, no keywords like hospital, insurance, etc.
    org_keywords = [
        "hospital", "medical", "health", "insurance", "chiropractic",
        "center", "clinic", "therapy", "services", "inc", "llc", "pc",
        "auto", "towing", "pharmacy", "urgent", "care", "rehabilitation",
        "imaging", "radiology", "orthopedic", "associates", "group",
        "physical", "transport", "ambulance", "emergency", "baptist",
        "jewish", "norton", "university", "regional", "memorial"
    ]
    lower_name = name.lower()
    if any(kw in lower_name for kw in org_keywords):
        return False
    # Person names usually have 2-4 words
    words = name.split()
    return 2 <= len(words) <= 4


def find_duplicate_groups(entries: list[dict], 
                          similarity_threshold: int = REVIEW_THRESHOLD) -> list[dict]:
    """
    Find groups of potentially duplicate entries using fuzzy matching.
    
    Uses a conservative approach:
    1. Only match names with high similarity (default 90%+)
    2. Use simple ratio to avoid false positives from shared words
    3. Boost confidence when phone numbers match
    
    Returns list of duplicate groups, each with:
    - canonical: the entry to keep (most complete data)
    - duplicates: list of entries to merge into canonical
    - confidence: similarity score
    - action: "merge" or "review"
    """
    # Build lookup by UUID
    by_uuid = {e["uuid"]: e for e in entries}
    
    # Extract names for fuzzy matching
    names = [(e["uuid"], e.get("full_name", "")) for e in entries if e.get("full_name")]
    
    processed = set()
    duplicate_groups = []
    
    # Sort by name for consistent processing
    sorted_names = sorted(names, key=lambda x: x[1].lower())
    
    for uuid, name in sorted_names:
        if uuid in processed:
            continue
        
        entry = by_uuid[uuid]
        normalized = normalize_name(name)
        
        # Find candidates (not yet processed)
        candidates = {u: n for u, n in sorted_names if u not in processed and u != uuid}
        
        if not candidates:
            processed.add(uuid)
            continue
        
        # Use simple ratio - more conservative than token-based scorers
        # This requires the strings to be actually similar, not just share words
        matches = process.extract(
            name,
            candidates,
            scorer=fuzz.ratio,
            score_cutoff=similarity_threshold,
            limit=5  # Limit matches - true duplicates should be few
        )
        
        if not matches:
            processed.add(uuid)
            continue
        
        # Validate matches and adjust confidence
        validated = []
        for match_name, score, match_uuid in matches:
            match_entry = by_uuid[match_uuid]
            
            # Boost confidence if phone numbers match
            if phones_match(entry, match_entry):
                score = min(100, score + PHONE_MATCH_BONUS)
            
            # For organizations, be extra careful about partial name matches
            if not is_person_name(name):
                # Check if names are too different in length
                len_ratio = min(len(name), len(match_name)) / max(len(name), len(match_name))
                if len_ratio < 0.5:  # One name is less than half the other
                    continue
            
            validated.append((match_name, score, match_uuid))
        
        if not validated:
            processed.add(uuid)
            continue
        
        # Build the duplicate group (include the original entry)
        group_uuids = [uuid] + [m[2] for m in validated]
        group_entries = [by_uuid[u] for u in group_uuids]
        
        # Determine canonical entry (most complete data)
        canonical = select_canonical(group_entries)
        duplicates = [e for e in group_entries if e["uuid"] != canonical["uuid"]]
        
        if duplicates:
            # Calculate average confidence from validated matches
            avg_confidence = sum(m[1] for m in validated) / len(validated)
            
            duplicate_groups.append({
                "canonical": canonical,
                "duplicates": duplicates,
                "confidence": round(avg_confidence, 1),
                "action": "merge" if avg_confidence >= AUTO_MERGE_THRESHOLD else "review",
                "matched_names": [e.get("full_name", "") for e in group_entries]
            })
        
        # Mark all as processed
        processed.update(group_uuids)
    
    return duplicate_groups


def select_canonical(entries: list[dict]) -> dict:
    """
    Select the canonical entry from a group of duplicates.
    Prefer the entry with the most complete data.
    """
    def completeness_score(entry: dict) -> int:
        score = 0
        if entry.get("phone"):
            score += 2
        if entry.get("email"):
            score += 2
        if entry.get("address"):
            score += 2
        if entry.get("full_name"):
            # Prefer longer names (more specific)
            score += len(entry.get("full_name", "")) / 50
        return score
    
    # Sort by completeness, then by UUID (for consistency)
    sorted_entries = sorted(entries, key=lambda e: (-completeness_score(e), e["uuid"]))
    return sorted_entries[0]


def merge_entries(canonical: dict, duplicates: list[dict]) -> dict:
    """
    Merge duplicate entries into canonical, filling in missing data.
    """
    merged = dict(canonical)
    
    for dup in duplicates:
        # Fill in missing fields from duplicates
        if not merged.get("phone") and dup.get("phone"):
            merged["phone"] = dup["phone"]
            merged["phone_normalized"] = dup.get("phone_normalized")
        if not merged.get("email") and dup.get("email"):
            merged["email"] = dup["email"]
        if not merged.get("address") and dup.get("address"):
            merged["address"] = dup["address"]
    
    # Track merged UUIDs
    merged["_merged_from"] = [d["uuid"] for d in duplicates]
    
    return merged


def generate_report(entries: list[dict], duplicate_groups: list[dict], output_dir: Path):
    """Generate deduplication report and merge map."""
    
    # Build merge map: duplicate UUID -> canonical UUID
    merge_map = {}
    for group in duplicate_groups:
        canonical_uuid = group["canonical"]["uuid"]
        for dup in group["duplicates"]:
            merge_map[str(dup["uuid"])] = canonical_uuid
    
    # Separate auto-merge and review groups
    auto_merge = [g for g in duplicate_groups if g["action"] == "merge"]
    needs_review = [g for g in duplicate_groups if g["action"] == "review"]
    
    # Statistics
    stats = {
        "total_entries": len(entries),
        "duplicate_groups_found": len(duplicate_groups),
        "auto_merge_groups": len(auto_merge),
        "needs_review_groups": len(needs_review),
        "entries_to_merge": len(merge_map),
        "entries_after_dedup": len(entries) - len(merge_map),
    }
    
    # Full report
    report = {
        "statistics": stats,
        "auto_merge_groups": auto_merge,
        "needs_review_groups": needs_review,
        "merge_map": merge_map,
    }
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write full report
    report_path = output_dir / "directory_deduplication_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Written: {report_path}")
    
    # Write merge map (for loading scripts)
    merge_map_path = output_dir / "directory_merge_map.json"
    with open(merge_map_path, "w") as f:
        json.dump(merge_map, f, indent=2)
    print(f"Written: {merge_map_path}")
    
    # Create deduplicated directory
    by_uuid = {e["uuid"]: e for e in entries}
    deduplicated = []
    
    for entry in entries:
        uuid = entry["uuid"]
        if str(uuid) in merge_map:
            # This is a duplicate, skip it
            continue
        
        # Check if this is a canonical entry with duplicates
        canonical_for = [g for g in duplicate_groups if g["canonical"]["uuid"] == uuid]
        if canonical_for:
            # Merge data from duplicates
            merged = merge_entries(entry, canonical_for[0]["duplicates"])
            deduplicated.append(merged)
        else:
            # No duplicates, keep as-is
            deduplicated.append(entry)
    
    dedup_path = output_dir / "directory_deduplicated.json"
    with open(dedup_path, "w") as f:
        json.dump(deduplicated, f, indent=2)
    print(f"Written: {dedup_path}")
    
    return stats, report


def print_summary(stats: dict, duplicate_groups: list[dict]):
    """Print a human-readable summary."""
    print("\n" + "=" * 60)
    print("DIRECTORY DEDUPLICATION SUMMARY")
    print("=" * 60)
    print(f"Total entries:           {stats['total_entries']}")
    print(f"Duplicate groups found:  {stats['duplicate_groups_found']}")
    print(f"  - Auto-merge (>92%):   {stats['auto_merge_groups']}")
    print(f"  - Needs review:        {stats['needs_review_groups']}")
    print(f"Entries to merge:        {stats['entries_to_merge']}")
    print(f"Entries after dedup:     {stats['entries_after_dedup']}")
    print("=" * 60)
    
    # Show sample of duplicates found
    if duplicate_groups:
        print("\nSAMPLE DUPLICATE GROUPS:")
        print("-" * 60)
        for group in duplicate_groups[:10]:
            action = "✓ AUTO-MERGE" if group["action"] == "merge" else "⚠ REVIEW"
            print(f"\n[{action}] Confidence: {group['confidence']}%")
            print(f"  Canonical: {group['canonical'].get('full_name', 'N/A')}")
            for dup in group["duplicates"]:
                print(f"  Duplicate: {dup.get('full_name', 'N/A')}")
        
        if len(duplicate_groups) > 10:
            print(f"\n... and {len(duplicate_groups) - 10} more groups")


def main():
    parser = argparse.ArgumentParser(
        description="Deduplicate directory.json entries using fuzzy matching"
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Path to directory.json"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output directory for reports"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=int,
        default=REVIEW_THRESHOLD,
        help=f"Similarity threshold for matching (default: {REVIEW_THRESHOLD})"
    )
    parser.add_argument(
        "--auto-merge-threshold",
        type=int,
        default=AUTO_MERGE_THRESHOLD,
        help=f"Threshold for auto-merge (default: {AUTO_MERGE_THRESHOLD})"
    )
    
    args = parser.parse_args()
    
    # Load directory
    entries = load_directory(args.input)
    
    # Find duplicates
    print(f"Finding duplicates with threshold={args.threshold}...")
    duplicate_groups = find_duplicate_groups(entries, args.threshold)
    
    # Update action based on auto-merge threshold
    for group in duplicate_groups:
        group["action"] = "merge" if group["confidence"] >= args.auto_merge_threshold else "review"
    
    # Generate reports
    stats, report = generate_report(entries, duplicate_groups, args.output)
    
    # Print summary
    print_summary(stats, duplicate_groups)
    
    print(f"\nReview the report at: {args.output / 'directory_deduplication_report.json'}")
    print("Edit 'action' fields from 'review' to 'merge' or 'skip' as needed.")


if __name__ == "__main__":
    main()
