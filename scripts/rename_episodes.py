#!/usr/bin/env python3
"""
Episode Renaming Migration Script

Renames all Episode nodes in the knowledge graph with a better naming convention:
    {Client Last Name} | {First 40 chars of content} | {YYYY-MM-DD}

Example: "Sitgraves | Intake documents were sent to client | 2024-07-18"

Usage:
    python rename_episodes.py --dry-run    # Preview changes without applying
    python rename_episodes.py              # Apply changes
    python rename_episodes.py --batch 500  # Process in batches of 500
"""

import argparse
import re
import sys
from datetime import datetime
from typing import Optional

# FalkorDB connection
try:
    from falkordb import FalkorDB
except ImportError:
    print("Error: falkordb package not installed. Run: pip install falkordb")
    sys.exit(1)


def extract_client_last_name(case_name: str) -> str:
    """
    Extract client last name from case_name.

    Examples:
        "Abby-Sitgraves-MVA-7-13-2024" -> "Sitgraves"
        "Estate-of-Betty-Prince-Premise-7-14-2020" -> "Prince"
        "Muhammad-Alif-MVA-12-09-2022" -> "Alif"
    """
    if not case_name:
        return "Unknown"

    # Handle "Estate-of-" prefix
    if case_name.startswith("Estate-of-"):
        case_name = case_name[10:]  # Remove "Estate-of-"

    # Split by hyphen and find the name parts (before case type like MVA, Premise, etc)
    parts = case_name.split("-")

    # Common case type markers
    case_types = {"MVA", "Premise", "WC", "Slip", "Fall", "Dog", "Bite", "Product"}

    # Find where the name ends (first case type marker or date pattern)
    name_parts = []
    for part in parts:
        # Stop if we hit a case type or what looks like a date
        if part in case_types or (part.isdigit() and len(part) <= 2):
            break
        name_parts.append(part)

    # Last name is typically the last name part
    if len(name_parts) >= 2:
        return name_parts[-1]  # Last name
    elif name_parts:
        return name_parts[0]

    return "Unknown"


def clean_content_for_name(content: str, max_length: int = 40) -> str:
    """
    Extract first meaningful sentence/phrase from content for use in name.

    Removes case name references and boilerplate, keeps the action/event.
    """
    if not content:
        return "No content"

    # Remove common boilerplate patterns
    content = re.sub(r'^Case:?\s*[\w-]+\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'^\s*[\w-]+-MVA-[\d-]+\s*', '', content)
    content = re.sub(r'The client is [\w\s]+\.?\s*', '', content)
    content = re.sub(r'[\w\s]+ is the client[^.]*\.?\s*', '', content)

    # Get first sentence or phrase
    content = content.strip()

    # Try to find first complete sentence
    sentence_match = re.match(r'^([^.!?\n]+[.!?])', content)
    if sentence_match:
        first_sentence = sentence_match.group(1).strip()
    else:
        first_sentence = content.split('\n')[0].strip()

    # Truncate if needed
    if len(first_sentence) > max_length:
        # Try to break at word boundary
        truncated = first_sentence[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length - 15:  # Don't cut off too much
            truncated = truncated[:last_space]
        first_sentence = truncated + "..."

    return first_sentence if first_sentence else "Note entry"


def format_date(valid_at: str) -> str:
    """
    Format valid_at timestamp to YYYY-MM-DD.

    Handles various formats:
        "2024-07-18T00:00:00" -> "2024-07-18"
        "2024-07-18" -> "2024-07-18"
    """
    if not valid_at:
        return "Unknown-Date"

    # Already in right format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', valid_at):
        return valid_at

    # ISO format with time
    if 'T' in valid_at:
        return valid_at.split('T')[0]

    return valid_at[:10] if len(valid_at) >= 10 else valid_at


def generate_new_name(case_name: str, content: str, valid_at: str) -> str:
    """
    Generate new episode name using the convention:
    {Client Last Name} | {Content Summary} | {YYYY-MM-DD}
    """
    client_last = extract_client_last_name(case_name)
    content_summary = clean_content_for_name(content)
    date_str = format_date(valid_at)

    return f"{client_last} | {content_summary} | {date_str}"


def rename_episodes(
    host: str = "localhost",
    port: int = 6380,
    graph_name: str = "roscoe_graph",
    dry_run: bool = True,
    batch_size: int = 100,
    limit: Optional[int] = None,
):
    """
    Rename all episodes in the graph.
    """
    print(f"Connecting to FalkorDB at {host}:{port}...")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph(graph_name)

    # Get total count
    result = graph.query("MATCH (e:Episode) RETURN count(e) as total")
    total = result.result_set[0][0]
    print(f"Total episodes: {total}")

    if limit:
        total = min(total, limit)
        print(f"Processing limited to: {limit}")

    # Process in batches
    processed = 0
    renamed = 0
    errors = 0

    while processed < total:
        # Fetch batch
        query = f"""
            MATCH (e:Episode)
            RETURN e.uuid, e.name, e.case_name, e.content, e.valid_at
            SKIP {processed}
            LIMIT {batch_size}
        """
        result = graph.query(query)

        if not result.result_set:
            break

        for row in result.result_set:
            uuid, old_name, case_name, content, valid_at = row

            try:
                new_name = generate_new_name(case_name, content, valid_at)

                if dry_run:
                    if processed < 10 or processed % 1000 == 0:  # Show samples
                        print(f"\n[{processed}] UUID: {uuid[:8]}...")
                        print(f"  Old: {old_name}")
                        print(f"  New: {new_name}")
                else:
                    # Apply the rename
                    update_query = """
                        MATCH (e:Episode {uuid: $uuid})
                        SET e.name = $new_name
                        RETURN e.uuid
                    """
                    graph.query(update_query, params={"uuid": uuid, "new_name": new_name})
                    renamed += 1

                    if renamed % 500 == 0:
                        print(f"  Renamed {renamed} episodes...")

            except Exception as e:
                errors += 1
                print(f"Error processing {uuid}: {e}")

            processed += 1
            if limit and processed >= limit:
                break

        if not dry_run:
            print(f"Processed batch: {processed}/{total}")

    print(f"\n{'='*50}")
    print(f"{'DRY RUN - No changes applied' if dry_run else 'MIGRATION COMPLETE'}")
    print(f"Total processed: {processed}")
    print(f"Renamed: {renamed if not dry_run else 'N/A (dry run)'}")
    print(f"Errors: {errors}")


def main():
    parser = argparse.ArgumentParser(description="Rename Episode nodes in knowledge graph")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--host", default="localhost", help="FalkorDB host")
    parser.add_argument("--port", type=int, default=6380, help="FalkorDB port")
    parser.add_argument("--graph", default="roscoe_graph", help="Graph name")
    parser.add_argument("--batch", type=int, default=100, help="Batch size")
    parser.add_argument("--limit", type=int, help="Limit total episodes to process")

    args = parser.parse_args()

    rename_episodes(
        host=args.host,
        port=args.port,
        graph_name=args.graph,
        dry_run=args.dry_run,
        batch_size=args.batch,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
