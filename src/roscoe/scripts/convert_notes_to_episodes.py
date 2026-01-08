#!/usr/bin/env python3
"""
Convert notes_cleaned.json to Graphiti Episode Format

Reads: /json-files/memory-cards/notes_cleaned.json (17,101 notes)
Writes: /json-files/memory-cards/episodes/notes_as_episodes.json

Converts each note to proper Graphiti episode structure:
- episode_name: "{author} - {date}"
- episode_body: "Case: {case}\nClient: {client}\n\n{note_content}"
- reference_time: ISO timestamp
- source: staff author or system
- case_name: For linking to Case entity

Usage:
    python convert_notes_to_episodes.py
    python convert_notes_to_episodes.py --input /path/to/notes.json --output /path/to/episodes.json
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import argparse


async def get_client_names_from_graph() -> Dict[str, str]:
    """
    Get client names for all cases from the graph.

    Returns dict: {case_name: client_name}
    """
    from roscoe.core.graphiti_client import run_cypher_query

    query = """
    MATCH (c:Entity {entity_type: 'Case'})-[:HAS_CLIENT]->(client:Entity {entity_type: 'Client'})
    RETURN c.name as case_name, client.name as client_name
    """

    results = await run_cypher_query(query, {})

    client_map = {}
    for r in results:
        case = r.get("case_name")
        client = r.get("client_name")
        if case and client:
            client_map[case] = client

    return client_map


def extract_client_from_case_name(case_name: str) -> str:
    """
    Extract client name from case folder name.

    Example: "Abby-Sitgraves-MVA-7-13-2024" → "Abby Sitgraves"
    """
    parts = case_name.split("-")

    # Find the accident type indicator
    for i, part in enumerate(parts):
        if part.upper() in ["MVA", "WC", "SLIP", "FALL", "PREMISE", "SF", "DB", "DUAL"]:
            # Name is everything before the accident type
            name_parts = parts[:i]
            return " ".join(name_parts).replace("-", " ")

    # Fallback: take first 2-3 parts
    if len(parts) >= 2:
        return " ".join(parts[:2]).replace("-", " ")

    return case_name


async def convert_notes_to_episodes(
    notes_file: Path,
    output_file: Path,
    use_graph_for_clients: bool = True
) -> int:
    """
    Convert all notes to Graphiti episode format.

    Args:
        notes_file: Path to notes_cleaned.json
        output_file: Where to write converted episodes
        use_graph_for_clients: Get client names from graph (recommended)

    Returns:
        Number of episodes created
    """
    print("=" * 70)
    print("CONVERTING NOTES TO GRAPHITI EPISODE FORMAT")
    print("=" * 70)
    print(f"Input: {notes_file}")
    print(f"Output: {output_file}")
    print()

    # Load notes
    print("📖 Loading notes...")
    with open(notes_file, 'r') as f:
        notes = json.load(f)

    print(f"   Found {len(notes)} notes")
    print()

    # Get client names from graph
    client_map = {}
    if use_graph_for_clients:
        print("🔍 Getting client names from graph...")
        client_map = await get_client_names_from_graph()
        print(f"   Found {len(client_map)} case→client mappings")
        print()

    # Convert each note to episode
    print("🔄 Converting notes to episodes...")
    episodes = []
    stats = {
        "total": len(notes),
        "converted": 0,
        "skipped_no_case": 0,
        "skipped_no_note": 0,
        "by_case": {}
    }

    for i, note_data in enumerate(notes, 1):
        case_name = note_data.get("project_name")
        note_text = note_data.get("note", "")
        author = note_data.get("author_name", "Unknown")
        author_type = note_data.get("author_type", "system")
        date_str = note_data.get("last_activity", "")
        note_id = note_data.get("id")

        # Skip if missing essential fields
        if not case_name:
            stats["skipped_no_case"] += 1
            continue

        if not note_text or len(note_text.strip()) < 5:
            stats["skipped_no_note"] += 1
            continue

        # Get client name
        if case_name in client_map:
            client_name = client_map[case_name]
        else:
            # Extract from case name
            client_name = extract_client_from_case_name(case_name)

        # Parse date (handle various formats)
        reference_time = None
        if date_str:
            try:
                # Try parsing YYYY-MM-DD
                reference_time = datetime.strptime(date_str, "%Y-%m-%d").isoformat()
            except:
                try:
                    # Try other formats
                    reference_time = datetime.fromisoformat(date_str).isoformat()
                except:
                    reference_time = None

        if not reference_time:
            reference_time = datetime.now().isoformat()

        # Create episode name
        episode_name = f"{author} - {date_str}" if date_str else author

        # Create episode body (Graphiti format)
        episode_body = f"""Case: {case_name}
Client: {client_name}

{note_text}"""

        # Build episode object
        episode = {
            "case_name": case_name,
            "client_name": client_name,
            "episode_name": episode_name,
            "episode_body": episode_body,
            "reference_time": reference_time,
            "source": author_type,
            "source_description": f"{author_type}: {author}",
            "original_note_id": note_id,
            "author": author,
            "date": date_str
        }

        episodes.append(episode)
        stats["converted"] += 1
        stats["by_case"][case_name] = stats["by_case"].get(case_name, 0) + 1

        # Progress indicator
        if i % 1000 == 0:
            print(f"   Progress: {i}/{len(notes)} notes processed...")

    print(f"   ✅ Converted {stats['converted']} notes to episodes")
    print(f"   ⚠️  Skipped {stats['skipped_no_case']} (no case name)")
    print(f"   ⚠️  Skipped {stats['skipped_no_note']} (empty/short notes)")
    print()

    # Write to file
    print(f"💾 Writing episodes to {output_file}...")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(episodes, f, indent=2)

    print(f"   ✅ Wrote {len(episodes)} episodes")
    print()

    # Summary stats
    print("=" * 70)
    print("CONVERSION COMPLETE")
    print("=" * 70)
    print(f"Total notes: {stats['total']}")
    print(f"Episodes created: {stats['converted']}")
    print(f"Skipped: {stats['skipped_no_case'] + stats['skipped_no_note']}")
    print()
    print(f"Top 5 cases by note count:")
    top_cases = sorted(stats["by_case"].items(), key=lambda x: x[1], reverse=True)[:5]
    for case, count in top_cases:
        print(f"  - {case}: {count} notes")
    print()
    print(f"Output file: {output_file}")
    print(f"Ready for review before ingestion!")
    print("=" * 70)

    return len(episodes)


def main():
    parser = argparse.ArgumentParser(description='Convert notes to Graphiti episodes')
    parser.add_argument('--input', type=str,
                       default='/Volumes/X10 Pro/Roscoe/json-files/memory-cards/notes_cleaned.json',
                       help='Input notes file')
    parser.add_argument('--output', type=str,
                       default='/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/notes_as_episodes.json',
                       help='Output episodes file')
    parser.add_argument('--no-graph', action='store_true',
                       help='Don\'t query graph for client names (faster but less accurate)')
    args = parser.parse_args()

    notes_file = Path(args.input)
    output_file = Path(args.output)

    if not notes_file.exists():
        print(f"❌ Input file not found: {notes_file}")
        return

    use_graph = not args.no_graph

    asyncio.run(convert_notes_to_episodes(notes_file, output_file, use_graph))


if __name__ == "__main__":
    main()
