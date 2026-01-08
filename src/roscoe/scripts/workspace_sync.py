#!/usr/bin/env python3
"""
Workspace Sync Script

Bidirectional sync between GCS bucket and local workspace.
- GCS → Local: Text files only (periodic batch sync)
- Local → GCS: Called after individual writes (immediate)

Usage:
    # Full sync from GCS to local (initial setup or manual refresh)
    python workspace_sync.py --full

    # Incremental sync (default, used by systemd timer)
    python workspace_sync.py

    # Sync specific directory
    python workspace_sync.py --path=/Database

    # Dry run (show what would be synced)
    python workspace_sync.py --dry-run

    # Force overwrite local files
    python workspace_sync.py --force
"""

import os
import sys
import argparse
import logging
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from roscoe.core.workspace_resolver import (
    TEXT_EXTENSIONS,
    LOCAL_WORKSPACE,
    GCS_WORKSPACE,
    SYNC_METADATA_DIR,
    is_text_file,
    sync_file_from_gcs,
    ensure_local_workspace_structure,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(SYNC_METADATA_DIR / "sync.log", mode='a')
    ]
)
logger = logging.getLogger(__name__)

# GCS bucket name
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "whaley_law_firm")

# Sync state file
SYNC_STATE_FILE = SYNC_METADATA_DIR / "sync_state.json"


def get_exclude_pattern() -> str:
    """
    Build gsutil rsync exclude pattern for binary files.

    Returns:
        Regex pattern to exclude binary files from sync
    """
    # Escape dots in extensions and join with |
    extensions = [ext.lstrip('.') for ext in [
        '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
        '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff', '.svg',
        '.mp3', '.mp4', '.wav', '.mov', '.avi', '.mkv', '.webm', '.m4a',
        '.zip', '.tar', '.gz', '.rar', '.7z',
        '.exe', '.dll', '.so', '.dylib'
    ]]

    # Build regex: .*\.(pdf|docx|doc|...)$
    pattern = r'.*\.(' + '|'.join(extensions) + r')$'
    return pattern


def sync_gcs_to_local_gsutil(
    path: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False
) -> Dict:
    """
    Sync text files from GCS to local using gsutil rsync.

    This is faster for bulk sync but requires gsutil CLI.

    Args:
        path: Optional subdirectory to sync (e.g., "/Database")
        dry_run: If True, show what would be synced without doing it
        force: If True, overwrite existing local files

    Returns:
        Dict with sync stats
    """
    stats = {
        "synced": 0,
        "skipped": 0,
        "errors": 0,
        "started": datetime.now().isoformat(),
    }

    # Determine source and destination
    if path:
        clean_path = path.lstrip('/')
        gcs_source = f"gs://{GCS_BUCKET_NAME}/{clean_path}/"
        local_dest = str(LOCAL_WORKSPACE / clean_path) + "/"
    else:
        gcs_source = f"gs://{GCS_BUCKET_NAME}/"
        local_dest = str(LOCAL_WORKSPACE) + "/"

    # Build gsutil rsync command
    exclude_pattern = get_exclude_pattern()
    cmd = [
        "gsutil", "-m", "rsync", "-r",
        "-x", exclude_pattern,  # Exclude binary files
    ]

    if dry_run:
        cmd.append("-n")  # Dry run

    cmd.extend([gcs_source, local_dest])

    logger.info(f"Running gsutil rsync: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            # Parse output to count synced files
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Copying' in line or 'Skipping' in line:
                    if 'Copying' in line:
                        stats["synced"] += 1
                    else:
                        stats["skipped"] += 1

            logger.info(f"gsutil rsync completed: {stats['synced']} synced, {stats['skipped']} skipped")
        else:
            logger.error(f"gsutil rsync failed: {result.stderr}")
            stats["errors"] += 1

    except subprocess.TimeoutExpired:
        logger.error("gsutil rsync timed out after 10 minutes")
        stats["errors"] += 1
    except FileNotFoundError:
        logger.error("gsutil not found - falling back to Python-based sync")
        return sync_gcs_to_local_python(path, dry_run, force)

    stats["completed"] = datetime.now().isoformat()
    return stats


def sync_gcs_to_local_python(
    path: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False
) -> Dict:
    """
    Sync text files from GCS to local using Python (fallback if gsutil unavailable).

    Walks the GCS mount directory and copies text files to local.

    Args:
        path: Optional subdirectory to sync
        dry_run: If True, show what would be synced
        force: If True, overwrite existing local files

    Returns:
        Dict with sync stats
    """
    stats = {
        "synced": 0,
        "skipped": 0,
        "errors": 0,
        "started": datetime.now().isoformat(),
    }

    # Determine source directory
    if path:
        clean_path = path.lstrip('/')
        gcs_root = GCS_WORKSPACE / clean_path
    else:
        gcs_root = GCS_WORKSPACE

    if not gcs_root.exists():
        logger.error(f"GCS workspace not found: {gcs_root}")
        stats["errors"] += 1
        return stats

    logger.info(f"Scanning GCS workspace: {gcs_root}")

    # Walk GCS directory and sync text files
    for gcs_path in gcs_root.rglob("*"):
        if not gcs_path.is_file():
            continue

        # Skip non-text files
        if not is_text_file(str(gcs_path)):
            continue

        # Skip hidden files and sync metadata
        if any(part.startswith('.') for part in gcs_path.parts):
            continue

        # Get workspace-relative path
        try:
            relative_path = gcs_path.relative_to(GCS_WORKSPACE)
        except ValueError:
            continue

        local_path = LOCAL_WORKSPACE / relative_path

        # Skip if local exists and not forcing
        if local_path.exists() and not force:
            stats["skipped"] += 1
            continue

        if dry_run:
            logger.info(f"[DRY RUN] Would sync: {relative_path}")
            stats["synced"] += 1
            continue

        # Sync the file
        try:
            if sync_file_from_gcs(str(relative_path), overwrite=force):
                stats["synced"] += 1
            else:
                stats["errors"] += 1
        except Exception as e:
            logger.error(f"Error syncing {relative_path}: {e}")
            stats["errors"] += 1

    stats["completed"] = datetime.now().isoformat()
    logger.info(f"Python sync completed: {stats['synced']} synced, {stats['skipped']} skipped, {stats['errors']} errors")
    return stats


def save_sync_state(stats: Dict):
    """Save sync state to file for tracking."""
    SYNC_METADATA_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing state
    state = {"syncs": []}
    if SYNC_STATE_FILE.exists():
        try:
            state = json.loads(SYNC_STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass

    # Append new sync and keep last 100
    state["syncs"].append(stats)
    state["syncs"] = state["syncs"][-100:]
    state["last_sync"] = stats.get("completed", datetime.now().isoformat())

    SYNC_STATE_FILE.write_text(json.dumps(state, indent=2))


def get_last_sync() -> Optional[str]:
    """Get timestamp of last successful sync."""
    if not SYNC_STATE_FILE.exists():
        return None

    try:
        state = json.loads(SYNC_STATE_FILE.read_text())
        return state.get("last_sync")
    except (json.JSONDecodeError, KeyError):
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Sync workspace between GCS and local disk"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full sync (scan all files, not just recent changes)"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="Sync specific subdirectory (e.g., /Database)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synced without doing it"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing local files"
    )
    parser.add_argument(
        "--use-python",
        action="store_true",
        help="Use Python-based sync instead of gsutil"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Ensure local workspace structure exists
    ensure_local_workspace_structure()

    logger.info("=" * 60)
    logger.info(f"Workspace Sync Started: {datetime.now().isoformat()}")
    logger.info(f"  GCS: gs://{GCS_BUCKET_NAME}/")
    logger.info(f"  Local: {LOCAL_WORKSPACE}/")
    logger.info(f"  Mode: {'full' if args.full else 'incremental'}")
    if args.path:
        logger.info(f"  Path: {args.path}")
    if args.dry_run:
        logger.info("  [DRY RUN MODE]")
    logger.info("=" * 60)

    # Run sync
    if args.use_python:
        stats = sync_gcs_to_local_python(args.path, args.dry_run, args.force)
    else:
        stats = sync_gcs_to_local_gsutil(args.path, args.dry_run, args.force)

    # Save state (unless dry run)
    if not args.dry_run:
        save_sync_state(stats)

    # Print summary
    print(f"\nSync Summary:")
    print(f"  Files synced: {stats['synced']}")
    print(f"  Files skipped: {stats['skipped']}")
    print(f"  Errors: {stats['errors']}")

    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
