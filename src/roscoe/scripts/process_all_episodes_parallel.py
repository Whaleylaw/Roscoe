#!/usr/bin/env python3
"""
Process All Case Episodes in Parallel with Resume Capability

Distributes cases among 5 workers for parallel processing.
Logs completed cases to enable resume.
Outputs proposed relationships only - NO graph writes.

Usage:
    python -m roscoe.scripts.process_all_episodes_parallel
    python -m roscoe.scripts.process_all_episodes_parallel --workers 3
    python -m roscoe.scripts.process_all_episodes_parallel --resume
"""

import json
import asyncio
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime


# Import the single-case processor
from roscoe.scripts.process_episodes_for_case import process_case_episodes


COMPLETED_LOG = "/mnt/workspace/json-files/memory-cards/episodes/completed_cases.log"


def get_all_case_names(cleaned_episodes_path: Path) -> list[str]:
    """Get unique case names from cleaned episodes."""
    with open(cleaned_episodes_path) as f:
        episodes = json.load(f)

    case_names = set()
    for ep in episodes:
        case_name = ep.get('case_name')
        if case_name:
            case_names.add(case_name)

    return sorted(list(case_names))


def get_completed_cases() -> set[str]:
    """Read log of completed cases for resume capability."""
    completed = set()

    log_paths = [
        Path("/mnt/workspace/json-files/memory-cards/episodes/completed_cases.log"),
        Path("/home/aaronwhaley/json-files/memory-cards/episodes/completed_cases.log"),
        Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/completed_cases.log"),
    ]

    for log_path in log_paths:
        if log_path.exists():
            with open(log_path) as f:
                for line in f:
                    case_name = line.strip()
                    if case_name:
                        completed.add(case_name)
            break

    return completed


def log_completed_case(case_name: str):
    """Append completed case to log file."""
    log_paths = [
        Path("/mnt/workspace/json-files/memory-cards/episodes/completed_cases.log"),
        Path("/home/aaronwhaley/json-files/memory-cards/episodes/completed_cases.log"),
        Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/completed_cases.log"),
    ]

    for log_path in log_paths:
        if log_path.parent.exists():
            with open(log_path, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"{case_name}\t{timestamp}\n")
            break


async def process_case_worker(
    worker_id: int,
    case_queue: asyncio.Queue,
    progress_counter: dict,
):
    """Worker that processes cases from the queue."""
    while True:
        try:
            case_name = await asyncio.wait_for(case_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            # Queue is empty
            break

        try:
            print(f"\n[Worker {worker_id}] Starting {case_name}")

            # Process the case (outputs JSON with proposed relationships)
            await process_case_episodes(case_name, limit=None, dry_run=False)

            # Log completion
            log_completed_case(case_name)
            progress_counter['completed'] += 1

            print(f"[Worker {worker_id}] ✓ Completed {case_name} ({progress_counter['completed']} total)")

        except Exception as e:
            print(f"[Worker {worker_id}] ✗ Error processing {case_name}: {str(e)[:200]}")
            progress_counter['errors'] += 1

        finally:
            case_queue.task_done()


async def main(workers: int = 5, resume: bool = True):
    """Main parallel processing function."""
    print("=" * 70)
    print("PARALLEL EPISODE PROCESSING - ALL CASES")
    print("=" * 70)
    print(f"Workers: {workers}")
    print(f"Resume mode: {resume}")
    print()

    # Load case names
    cleaned_paths = [
        Path("/mnt/workspace/json-files/memory-cards/episodes/cleaned_episodes.json"),
        Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/cleaned_episodes.json"),
    ]

    cleaned_path = None
    for p in cleaned_paths:
        if p.exists():
            cleaned_path = p
            break

    if not cleaned_path:
        print("❌ cleaned_episodes.json not found")
        return

    print(f"Loading cases from: {cleaned_path}")

    all_cases = get_all_case_names(cleaned_path)
    print(f"Found {len(all_cases)} cases")

    # Check for completed cases
    completed = get_completed_cases() if resume else set()

    if completed:
        print(f"Resuming: {len(completed)} cases already completed")

    # Filter out completed
    remaining = [c for c in all_cases if c not in completed]

    if not remaining:
        print("\n✅ All cases already processed!")
        return

    print(f"Processing {len(remaining)} remaining cases")
    print()

    # Create queue
    case_queue = asyncio.Queue()
    for case_name in remaining:
        await case_queue.put(case_name)

    # Progress tracking
    progress_counter = {'completed': 0, 'errors': 0}

    # Start workers
    print(f"Starting {workers} workers...")
    start_time = datetime.now()

    worker_tasks = [
        asyncio.create_task(process_case_worker(i + 1, case_queue, progress_counter))
        for i in range(workers)
    ]

    # Wait for all workers
    await asyncio.gather(*worker_tasks)

    elapsed = (datetime.now() - start_time).total_seconds()

    print()
    print("=" * 70)
    print("✅ PROCESSING COMPLETE")
    print("=" * 70)
    print(f"Cases processed: {progress_counter['completed']}")
    print(f"Errors: {progress_counter['errors']}")
    print(f"Time: {elapsed/60:.1f} minutes")
    print()
    print("Review proposed relationships in:")
    print("  /mnt/workspace/json-files/memory-cards/episodes/processed_*.json")


def run():
    parser = argparse.ArgumentParser(description='Process all case episodes in parallel')
    parser.add_argument('--workers', type=int, default=5,
                       help='Number of parallel workers (default: 5)')
    parser.add_argument('--no-resume', action='store_true',
                       help='Process all cases (ignore completed log)')
    args = parser.parse_args()

    asyncio.run(main(workers=args.workers, resume=not args.no_resume))


if __name__ == "__main__":
    run()
