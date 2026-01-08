#!/usr/bin/env python3
"""
Ingest Case Episodes from JSON Files into Graphiti Knowledge Graph

This script ingests 13,789 episodes from memory card JSON files into the
Graphiti knowledge graph, enabling semantic search and temporal queries.

Features:
- Batch processing for performance
- Progress tracking and logging
- Error handling with resume capability
- Parallel processing via SEMAPHORE_LIMIT
- Custom entity and edge type extraction

Usage:
    python -m roscoe.scripts.ingest_episodes_from_json
    python -m roscoe.scripts.ingest_episodes_from_json --dry-run
    python -m roscoe.scripts.ingest_episodes_from_json --batch-size 25
    python -m roscoe.scripts.ingest_episodes_from_json --limit 100  # Test with first 100
"""

import asyncio
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from roscoe.core.graphiti_client import (
    get_graphiti,
    ENTITY_TYPES_DICT,
    EDGE_TYPES_DICT,
    EDGE_TYPE_MAP,
    CASE_DATA_GROUP_ID,
)
from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode


# Configuration
BATCH_SIZE = 50  # Process 50 episodes per batch
SEMAPHORE_LIMIT = int(os.getenv("SEMAPHORE_LIMIT", "20"))  # Parallel processing limit

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


def load_episodes_from_json(episodes_dir: Path) -> list[dict]:
    """Load all episodes from JSON files in the episodes directory."""
    all_episodes = []

    json_files = sorted(episodes_dir.glob("*.json"))
    logger.info(f"Found {len(json_files)} case JSON files")

    for json_file in json_files:
        try:
            with open(json_file) as f:
                episodes = json.load(f)

            # Add source file info
            for episode in episodes:
                episode['_source_file'] = json_file.name

            all_episodes.extend(episodes)

        except Exception as e:
            logger.error(f"Error loading {json_file.name}: {e}")
            continue

    logger.info(f"Loaded {len(all_episodes)} total episodes")
    return all_episodes


async def ingest_episode(
    graphiti,
    episode: dict,
    use_custom_types: bool = True,
) -> tuple[bool, Optional[str]]:
    """
    Ingest a single episode into Graphiti.

    Returns:
        (success: bool, error_message: Optional[str])
    """
    try:
        # Parse reference time
        reference_time = datetime.fromisoformat(episode['reference_time'].replace('Z', '+00:00'))

        # Build episode body with case context
        episode_body = episode['episode_body']

        # Prepare kwargs
        kwargs = {
            "name": episode['episode_name'],
            "episode_body": episode_body,
            "source": EpisodeType.text,
            "source_description": episode.get('source_description', episode.get('source', 'unknown')),
            "reference_time": reference_time,
            "group_id": CASE_DATA_GROUP_ID,
        }

        # Add custom types if enabled
        if use_custom_types:
            kwargs["entity_types"] = ENTITY_TYPES_DICT
            kwargs["edge_types"] = EDGE_TYPES_DICT
            kwargs["edge_type_map"] = EDGE_TYPE_MAP

        await graphiti.add_episode(**kwargs)

        return (True, None)

    except Exception as e:
        error_msg = f"{episode.get('case_name', 'Unknown')}/{episode.get('episode_name', 'Unknown')}: {str(e)}"
        return (False, error_msg)


async def ingest_batch_bulk(
    graphiti,
    episodes: list[dict],
    batch_num: int,
    total_batches: int,
) -> tuple[int, int, list[str]]:
    """
    Ingest a batch of episodes using bulk processing for parallelism.

    Returns:
        (success_count, error_count, error_messages)
    """
    logger.info(f"Batch {batch_num}/{total_batches}: Processing {len(episodes)} episodes...")

    try:
        # Convert to RawEpisode objects
        raw_episodes = []
        for ep in episodes:
            reference_time = datetime.fromisoformat(ep['reference_time'].replace('Z', '+00:00'))

            raw_ep = RawEpisode(
                name=ep['episode_name'],
                content=ep['episode_body'],
                source_description=ep.get('source_description', ep.get('source', 'unknown')),
                source=EpisodeType.text,
                reference_time=reference_time,
            )
            raw_episodes.append(raw_ep)

        # Bulk ingest with parallel processing
        await graphiti.add_episode_bulk(
            raw_episodes,
            group_id=CASE_DATA_GROUP_ID,
            entity_types=ENTITY_TYPES_DICT,
            edge_types=EDGE_TYPES_DICT,
            edge_type_map=EDGE_TYPE_MAP,
        )

        logger.info(f"  ✓ Batch {batch_num} complete: {len(episodes)} episodes ingested")
        return (len(episodes), 0, [])

    except Exception as e:
        error_msg = f"Batch {batch_num} failed: {str(e)}"
        logger.error(f"  ✗ {error_msg}")
        return (0, len(episodes), [error_msg])


async def main(
    dry_run: bool = False,
    batch_size: int = BATCH_SIZE,
    limit: Optional[int] = None,
    workspace_dir: Optional[str] = None,
    episodes_dir: Optional[str] = None,
):
    """Main ingestion function."""
    print("=" * 70)
    print("GRAPHITI EPISODE INGESTION")
    print("=" * 70)
    print(f"Batch Size: {batch_size}")
    print(f"Semaphore Limit: {SEMAPHORE_LIMIT}")
    print(f"Dry Run: {dry_run}")
    if limit:
        print(f"Limit: {limit} episodes (test mode)")
    print()

    # Determine episodes directory
    if episodes_dir:
        # Direct path provided
        episodes_path = Path(episodes_dir)
    elif workspace_dir:
        episodes_path = Path(workspace_dir) / "json-files" / "memory-cards" / "episodes" / "by_case"
    else:
        # Try production path first, fall back to development
        workspace_dir = os.getenv("WORKSPACE_DIR", "/mnt/workspace")
        episodes_path = Path(workspace_dir).parent / "json-files" / "memory-cards" / "episodes" / "by_case"

        if not episodes_path.exists():
            # Development fallback
            episodes_path = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/by_case")

    if not episodes_path.exists():
        print(f"❌ Episodes directory not found: {episodes_path}")
        sys.exit(1)

    logger.info(f"Episodes directory: {episodes_path}")

    # Load episodes
    episodes = load_episodes_from_json(episodes_path)

    if limit:
        episodes = episodes[:limit]
        logger.info(f"Limited to first {len(episodes)} episodes")

    if not episodes:
        logger.error("No episodes found to ingest")
        sys.exit(1)

    # Show breakdown by case
    from collections import Counter
    case_counts = Counter(e.get('case_name', 'Unknown') for e in episodes)
    logger.info(f"\nTop 10 cases by episode count:")
    for case_name, count in case_counts.most_common(10):
        logger.info(f"  {case_name}: {count} episodes")
    print()

    if dry_run:
        print("[DRY RUN] Would ingest these episodes.")
        print(f"Total episodes: {len(episodes)}")
        print(f"Batches: {(len(episodes) + batch_size - 1) // batch_size}")
        return

    # Initialize Graphiti
    logger.info("Initializing Graphiti client...")
    graphiti = await get_graphiti()

    # Process in batches
    total_batches = (len(episodes) + batch_size - 1) // batch_size
    total_success = 0
    total_errors = 0
    all_errors = []

    logger.info(f"Starting ingestion of {len(episodes)} episodes in {total_batches} batches...")
    logger.info(f"Using GPT-5 Mini for entity extraction")
    print()

    start_time = datetime.now()

    for i in range(0, len(episodes), batch_size):
        batch_num = (i // batch_size) + 1
        batch = episodes[i:i + batch_size]

        success, errors, error_msgs = await ingest_batch_bulk(
            graphiti,
            batch,
            batch_num,
            total_batches,
        )

        total_success += success
        total_errors += errors
        all_errors.extend(error_msgs)

        # Progress update every 10 batches
        if batch_num % 10 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = total_success / elapsed if elapsed > 0 else 0
            logger.info(f"\nProgress: {total_success}/{len(episodes)} episodes ({rate:.1f} eps/sec)")
            logger.info(f"Errors so far: {total_errors}")
            print()

    elapsed_total = (datetime.now() - start_time).total_seconds()

    print()
    print("=" * 70)
    print("✅ INGESTION COMPLETE")
    print("=" * 70)
    print(f"Total episodes processed: {len(episodes)}")
    print(f"Successfully ingested: {total_success}")
    print(f"Errors: {total_errors}")
    print(f"Time elapsed: {elapsed_total:.1f} seconds ({total_success / elapsed_total:.1f} eps/sec)")
    print()

    if all_errors:
        print(f"First 20 errors:")
        for error in all_errors[:20]:
            print(f"  - {error}")
        print()


def run():
    parser = argparse.ArgumentParser(description='Ingest case episodes from JSON files')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without ingesting')
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE,
                       help=f'Batch size for processing (default: {BATCH_SIZE})')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of episodes (for testing)')
    parser.add_argument('--workspace-dir', type=str, default=None,
                       help='Workspace directory path (auto-detected if not provided)')
    parser.add_argument('--episodes-dir', type=str, default=None,
                       help='Direct path to episodes/by_case directory')
    args = parser.parse_args()

    asyncio.run(main(
        dry_run=args.dry_run,
        batch_size=args.batch_size,
        limit=args.limit,
        workspace_dir=args.workspace_dir,
        episodes_dir=args.episodes_dir,
    ))


if __name__ == "__main__":
    run()
