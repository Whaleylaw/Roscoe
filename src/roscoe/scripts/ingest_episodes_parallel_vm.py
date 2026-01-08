#!/usr/bin/env python3
"""
Parallel Episode Ingestion (VM Version)

Runs entirely inside the roscoe-agents Docker container on the VM.
Uses multiprocessing to ingest multiple cases simultaneously.

Usage (inside roscoe-agents container):
    # Ingest all cases with 5 workers
    python -m roscoe.scripts.ingest_episodes_parallel_vm --workers 5

    # Ingest specific cases
    python -m roscoe.scripts.ingest_episodes_parallel_vm --cases "Case1,Case2" --workers 3

    # Run with nohup to survive disconnections
    nohup python -m roscoe.scripts.ingest_episodes_parallel_vm --workers 5 > /tmp/ingestion.log 2>&1 &
"""

import asyncio
import json
from pathlib import Path
import argparse
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List


def ingest_single_case(case_name: str, episodes_dir: str) -> Dict:
    """
    Ingest a single case (runs in separate process).

    Note: This function must be at module level for multiprocessing to pickle it.
    """
    import asyncio
    from roscoe.scripts.ingest_episodes_to_graphiti import ingest_all_or_one

    start_time = time.time()

    try:
        # Run the async ingestion function
        asyncio.run(ingest_all_or_one(
            case_name=case_name,
            batch_size=25,
            episodes_dir=episodes_dir
        ))

        elapsed = time.time() - start_time
        return {
            "case": case_name,
            "success": True,
            "elapsed": elapsed,
            "error": None
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "case": case_name,
            "success": False,
            "elapsed": elapsed,
            "error": str(e)[:200]
        }


def main():
    parser = argparse.ArgumentParser(description='Parallel episode ingestion (VM version)')
    parser.add_argument('--workers', type=int, default=5,
                       help='Number of parallel workers (default: 5)')
    parser.add_argument('--cases', type=str,
                       help='Comma-separated case names (or omit for all)')
    parser.add_argument('--episodes-dir', type=str,
                       default='/mnt/workspace/episodes/by_case',
                       help='Directory with episode JSON files')
    args = parser.parse_args()

    episodes_dir = Path(args.episodes_dir)

    print("=" * 70)
    print("PARALLEL EPISODE INGESTION (VM VERSION)")
    print("=" * 70)
    print(f"Workers: {args.workers}")
    print(f"Episodes directory: {episodes_dir}")
    print(f"Running inside Docker container: roscoe-agents")
    print()

    # Get case files to process
    if args.cases:
        case_names = [c.strip() for c in args.cases.split(',')]
        case_files = [episodes_dir / f"{name}.json" for name in case_names]
        # Verify they exist
        case_files = [f for f in case_files if f.exists()]
        if len(case_files) < len(case_names):
            missing = set(case_names) - {f.stem for f in case_files}
            print(f"⚠️  Warning: Could not find files for: {', '.join(missing)}")
    else:
        # Get all non-excluded case files
        case_files = sorted([f for f in episodes_dir.glob("*.json")
                           if f.is_file() and not f.name.startswith('_')])

    if not case_files:
        print("❌ No case files found to process!")
        return

    print(f"Found {len(case_files)} case files to process")
    print()

    # Extract case names (without .json)
    case_names = [f.stem for f in case_files]

    # Process in parallel
    print(f"🚀 Starting {args.workers} parallel workers...")
    print(f"   Each worker will ingest one case at a time")
    print()

    start_time = time.time()
    completed_cases = []
    failed_cases = []
    results = []

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        # Submit all cases
        futures = {
            executor.submit(ingest_single_case, case_name, str(episodes_dir)): case_name
            for case_name in case_names
        }

        # Process as they complete
        for i, future in enumerate(as_completed(futures), 1):
            case_name = futures[future]

            try:
                result = future.result()
                results.append(result)

                if result["success"]:
                    completed_cases.append(result["case"])
                    print(f"[{i}/{len(case_names)}] ✅ {result['case']}: "
                          f"completed in {result['elapsed']:.0f}s")
                else:
                    failed_cases.append(result["case"])
                    print(f"[{i}/{len(case_names)}] ❌ {result['case']}: FAILED")
                    if result["error"]:
                        print(f"   Error: {result['error']}")

            except Exception as e:
                failed_cases.append(case_name)
                print(f"[{i}/{len(case_names)}] ❌ {case_name}: "
                      f"exception - {str(e)[:100]}")

    total_elapsed = time.time() - start_time

    print()
    print("=" * 70)
    print("✅ PARALLEL INGESTION COMPLETE")
    print("=" * 70)
    print(f"Total cases: {len(case_names)}")
    print(f"Completed: {len(completed_cases)}")
    print(f"Failed: {len(failed_cases)}")
    print(f"Total time: {total_elapsed/60:.1f} minutes")
    print(f"Average time per case: {total_elapsed/len(case_names):.1f} seconds")
    print()

    if failed_cases:
        print(f"Failed cases ({len(failed_cases)}):")
        for case in failed_cases[:20]:
            print(f"  - {case}")
        if len(failed_cases) > 20:
            print(f"  ... and {len(failed_cases) - 20} more")
        print()

    print("=" * 70)


if __name__ == "__main__":
    main()
