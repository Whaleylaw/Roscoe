#!/usr/bin/env python3
"""
Parallel Case-Based Episode Ingestion for Graphiti

Processes episodes in parallel by case using worker pool:
- 6 concurrent workers
- Each worker processes 1 case at a time  
- Episodes within a case are batched (25 per batch)
- Automatic retry on errors

Usage:
    python -m roscoe.scripts.ingest_episodes_parallel
    python -m roscoe.scripts.ingest_episodes_parallel --workers 4
    python -m roscoe.scripts.ingest_episodes_parallel --limit 100
"""

import asyncio
import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from collections import defaultdict

from roscoe.core.graphiti_client import (
    get_graphiti,
    ENTITY_TYPES_DICT,
    EDGE_TYPES_DICT,
    EDGE_TYPE_MAP,
    CASE_DATA_GROUP_ID,
)
from graphiti_core.nodes import EpisodeType

# Configuration
NUM_WORKERS = 5  # Reduced for stability
EPISODES_PER_BATCH = 10  # Smaller batches to reduce FalkorDB load

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


def get_ingested_episode_names() -> set[str]:
    """Get set of episode names that are already in the graph."""
    from falkordb import FalkorDB

    try:
        db = FalkorDB(host=os.getenv("FALKORDB_HOST", "roscoe-graphdb"), port=int(os.getenv("FALKORDB_PORT", "6379")))
        graph = db.select_graph("roscoe_graph")

        # Get all Episodic node names
        query = """
        MATCH (e:Episodic)
        RETURN e.name
        """
        result = graph.query(query)

        ingested_episodes = set()
        if result.result_set:
            for row in result.result_set:
                episode_name = row[0]
                if episode_name:
                    ingested_episodes.add(episode_name)

        logger.info(f"Found {len(ingested_episodes)} episodes already in graph")
        return ingested_episodes
    except Exception as e:
        logger.warning(f"Could not check ingested episodes: {e}")
        return set()


def load_episodes_by_case(episodes_dir: Path, skip_completed: bool = True) -> dict[str, list[dict]]:
    """Load episodes grouped by case name, filtering out already-ingested episodes."""
    episodes_by_case = defaultdict(list)

    json_files = sorted(episodes_dir.glob("*.json"))
    logger.info(f"Found {len(json_files)} case JSON files")

    # Get episode names already in graph (for episode-level deduplication)
    ingested_episode_names = get_ingested_episode_names() if skip_completed else set()

    total_loaded = 0
    total_skipped = 0

    for json_file in json_files:
        try:
            case_name = json_file.stem

            with open(json_file) as f:
                all_episodes = json.load(f)

            # Filter out episodes that are already ingested
            new_episodes = []
            for ep in all_episodes:
                if ep['episode_name'] in ingested_episode_names:
                    total_skipped += 1
                else:
                    new_episodes.append(ep)

            if new_episodes:
                episodes_by_case[case_name].extend(new_episodes)
                total_loaded += len(new_episodes)
                if len(new_episodes) < len(all_episodes):
                    logger.info(f"{case_name}: {len(new_episodes)}/{len(all_episodes)} episodes (skipped {len(all_episodes) - len(new_episodes)} already ingested)")

        except Exception as e:
            logger.error(f"Error loading {json_file.name}: {e}")
            continue

    logger.info(f"Loaded {total_loaded} new episodes across {len(episodes_by_case)} cases")
    logger.info(f"Skipped {total_skipped} episodes already in graph")

    return dict(episodes_by_case)


async def ingest_episode(graphiti, episode: dict) -> tuple[bool, Optional[str]]:
    """Ingest a single episode."""
    try:
        reference_time = datetime.fromisoformat(episode['reference_time'].replace('Z', '+00:00'))

        await graphiti.add_episode(
            name=episode['episode_name'],
            episode_body=episode['episode_body'],
            source=EpisodeType.text,
            source_description=episode.get('source_description', episode.get('source', 'unknown')),
            reference_time=reference_time,
            group_id=CASE_DATA_GROUP_ID,
            entity_types=ENTITY_TYPES_DICT,
            edge_types=EDGE_TYPES_DICT,
            edge_type_map=EDGE_TYPE_MAP,
        )

        return (True, None)

    except Exception as e:
        error_msg = f"{episode.get('episode_name', 'Unknown')}: {str(e)[:100]}"
        return (False, error_msg)


async def process_case(
    case_name: str,
    episodes: list[dict],
    worker_id: int,
    progress_counter: dict,
) -> tuple[int, int]:
    """Process all episodes for a case in batches."""
    graphiti = await get_graphiti()

    success = 0
    errors = 0
    total_eps = len(episodes)

    logger.info(f"[Worker {worker_id}] Starting {case_name}: {total_eps} episodes")

    for i in range(0, total_eps, EPISODES_PER_BATCH):
        batch = episodes[i:i + EPISODES_PER_BATCH]

        for episode in batch:
            ok, err = await ingest_episode(graphiti, episode)
            if ok:
                success += 1
                progress_counter['total'] += 1
            else:
                errors += 1

        # Progress log every batch
        if (i // EPISODES_PER_BATCH + 1) % 5 == 0:
            logger.info(f"[Worker {worker_id}] {case_name}: {success}/{total_eps} episodes")

    logger.info(f"[Worker {worker_id}] ✓ {case_name}: {success} success, {errors} errors")
    return (success, errors)


async def worker(
    worker_id: int,
    case_queue: asyncio.Queue,
    progress_counter: dict,
    results: list,
):
    """Worker that processes cases from queue."""
    while True:
        try:
            case_name, episodes = await asyncio.wait_for(case_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            break

        try:
            success, errors = await process_case(case_name, episodes, worker_id, progress_counter)
            results.append({
                'case': case_name,
                'worker': worker_id,
                'success': success,
                'errors': errors,
            })
        except Exception as e:
            logger.error(f"[Worker {worker_id}] Failed {case_name}: {e}")
            results.append({
                'case': case_name,
                'worker': worker_id,
                'success': 0,
                'errors': len(episodes),
            })
        finally:
            case_queue.task_done()


async def main(workers: int = NUM_WORKERS, limit: Optional[int] = None, episodes_dir: Optional[str] = None):
    """Main parallel ingestion."""
    print("=" * 70)
    print("PARALLEL CASE-BASED EPISODE INGESTION")
    print("=" * 70)
    print(f"Workers: {workers}")
    print(f"Episodes per batch: {EPISODES_PER_BATCH}")
    if limit:
        print(f"Limit: {limit} episodes")
    print()

    # Determine directory
    if episodes_dir:
        episodes_path = Path(episodes_dir)
    else:
        workspace_dir = os.getenv("WORKSPACE_DIR", "/mnt/workspace")
        episodes_path = Path(workspace_dir) / "temp_json_import" / "episodes" / "by_case"

        if not episodes_path.exists():
            episodes_path = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/by_case")

    if not episodes_path.exists():
        print(f"❌ Directory not found: {episodes_path}")
        return

    logger.info(f"Directory: {episodes_path}")

    # Load episodes by case (skip completed cases for resume)
    episodes_by_case = load_episodes_by_case(episodes_path, skip_completed=True)

    if limit:
        total = 0
        limited = {}
        for case_name, eps in episodes_by_case.items():
            if total >= limit:
                break
            remaining = limit - total
            limited[case_name] = eps[:remaining]
            total += len(limited[case_name])
        episodes_by_case = limited
        logger.info(f"Limited to {total} episodes")

    total_cases = len(episodes_by_case)
    total_episodes = sum(len(eps) for eps in episodes_by_case.values())

    logger.info(f"Processing {total_episodes} episodes across {total_cases} cases")
    logger.info(f"Using GPT-5 Mini for entity extraction")
    print()

    # Create queue
    case_queue = asyncio.Queue()
    for case_name, eps in episodes_by_case.items():
        await case_queue.put((case_name, eps))

    progress_counter = {'total': 0}
    results = []

    logger.info(f"Starting {workers} workers...")
    start_time = datetime.now()

    worker_tasks = [
        asyncio.create_task(worker(i + 1, case_queue, progress_counter, results))
        for i in range(workers)
    ]

    await asyncio.gather(*worker_tasks)

    elapsed = (datetime.now() - start_time).total_seconds()

    total_success = sum(r['success'] for r in results)
    total_errors = sum(r['errors'] for r in results)

    print()
    print("=" * 70)
    print("✅ PARALLEL INGESTION COMPLETE")
    print("=" * 70)
    print(f"Total episodes: {total_episodes}")
    print(f"Successfully ingested: {total_success}")
    print(f"Errors: {total_errors}")
    print(f"Time: {elapsed:.1f}s ({total_success / elapsed:.1f} eps/sec)")
    print(f"Cases: {len(results)}")
    print()


def run():
    parser = argparse.ArgumentParser(description='Parallel case-based episode ingestion')
    parser.add_argument('--workers', type=int, default=NUM_WORKERS,
                       help=f'Parallel workers (default: {NUM_WORKERS})')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit episodes (testing)')
    parser.add_argument('--episodes-dir', type=str, default=None,
                       help='Path to episodes/by_case')
    args = parser.parse_args()

    asyncio.run(main(workers=args.workers, limit=args.limit, episodes_dir=args.episodes_dir))


if __name__ == "__main__":
    run()
