#!/usr/bin/env python3
"""
Ingest Episodes into Graphiti

Reads episode JSON files and ingests them into the knowledge graph.

Usage:
    python ingest_episodes_to_graphiti.py --case "Abigail-Whaley-MVA-10-24-2024"
    python ingest_episodes_to_graphiti.py --all
    python ingest_episodes_to_graphiti.py --case "Case-Name" --batch-size 10
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
import argparse


async def ingest_case_episodes(case_file: Path, batch_size: int = 25) -> dict:
    """
    Ingest episodes from a case file into Graphiti.

    Returns dict with stats
    """
    from roscoe.core.graphiti_client import get_graphiti, CASE_DATA_GROUP_ID
    from graphiti_core.nodes import EpisodeType

    print(f"📂 Processing: {case_file.name}")

    # Load episodes
    with open(case_file, 'r') as f:
        episodes = json.load(f)

    stats = {
        "total": len(episodes),
        "ingested": 0,
        "skipped": 0,
        "errors": 0
    }

    # Get Graphiti client
    graphiti = await get_graphiti()

    # Process episodes
    for i, episode in enumerate(episodes, 1):
        # Skip if marked
        if episode.get("skip"):
            stats["skipped"] += 1
            continue

        # Extract fields
        case_name = episode.get("case_name")
        episode_name = episode.get("episode_name", f"Episode {i}")
        episode_body = episode.get("episode_body", "")
        reference_time_str = episode.get("reference_time")
        source_desc = episode.get("source_description", "staff")

        if not episode_body or len(episode_body.strip()) < 10:
            stats["skipped"] += 1
            continue

        # Parse reference time
        try:
            reference_time = datetime.fromisoformat(reference_time_str) if reference_time_str else datetime.now()
        except:
            reference_time = datetime.now()

        try:
            # Add episode to Graphiti
            await graphiti.add_episode(
                name=episode_name,
                episode_body=episode_body,
                source=EpisodeType.text,
                source_description=source_desc,
                reference_time=reference_time,
                group_id=CASE_DATA_GROUP_ID
            )

            stats["ingested"] += 1

            # Progress indicator
            if stats["ingested"] % 5 == 0:
                print(f"   Progress: {stats['ingested']}/{len(episodes) - stats['skipped']} ingested...")

        except Exception as e:
            print(f"   ❌ Error ingesting episode {i}: {str(e)[:100]}")
            stats["errors"] += 1

    return stats


async def ingest_all_or_one(case_name: str = None, batch_size: int = 25, episodes_dir: str = None):
    """Main ingestion function."""
    if episodes_dir:
        by_case_dir = Path(episodes_dir)
    else:
        by_case_dir = Path("/mnt/workspace/episodes/by_case")

    print("=" * 70)
    print("INGESTING EPISODES INTO GRAPHITI")
    print("=" * 70)
    print()

    # Get files to process
    if case_name:
        case_files = [by_case_dir / f"{case_name}.json"]
        if not case_files[0].exists():
            print(f"❌ Case file not found: {case_files[0]}")
            return
        print(f"Mode: Single case ({case_name})")
    else:
        case_files = sorted([f for f in by_case_dir.glob("*.json") if f.is_file()])
        print(f"Mode: All cases ({len(case_files)} files)")

    print(f"Batch size: {batch_size} episodes per progress update")
    print()

    # Process files
    total_stats = {
        "total": 0,
        "ingested": 0,
        "skipped": 0,
        "errors": 0
    }

    import time
    start_time = time.time()

    for case_file in case_files:
        stats = await ingest_case_episodes(case_file, batch_size)

        # Aggregate
        for key in total_stats:
            total_stats[key] += stats[key]

        print(f"   ✅ {case_file.stem}: {stats['ingested']} ingested, {stats['skipped']} skipped, {stats['errors']} errors")
        print()

    elapsed = time.time() - start_time

    print("=" * 70)
    print("✅ INGESTION COMPLETE")
    print("=" * 70)
    print(f"Total episodes: {total_stats['total']}")
    print(f"Successfully ingested: {total_stats['ingested']}")
    print(f"Skipped: {total_stats['skipped']}")
    print(f"Errors: {total_stats['errors']}")
    print(f"Time: {elapsed:.1f} seconds")
    print(f"Rate: {total_stats['ingested'] / elapsed:.1f} episodes/second" if elapsed > 0 else "")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Ingest episodes into Graphiti')
    parser.add_argument('--case', type=str, help='Case name to ingest (without .json)')
    parser.add_argument('--all', action='store_true', help='Ingest all case files')
    parser.add_argument('--batch-size', type=int, default=25, help='Progress update frequency')
    parser.add_argument('--episodes-dir', type=str, help='Directory containing episode files')
    args = parser.parse_args()

    if not args.case and not args.all:
        print("❌ Error: Specify --case NAME or --all")
        parser.print_help()
        return

    case_name = args.case if args.case else None

    asyncio.run(ingest_all_or_one(case_name, args.batch_size, args.episodes_dir))


if __name__ == "__main__":
    main()
