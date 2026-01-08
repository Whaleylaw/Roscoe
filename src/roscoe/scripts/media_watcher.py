#!/usr/bin/env python3
"""
Media Watcher Service

Monitors the GCS workspace for media files (images, audio, video) and creates
stub markdown files in the local workspace so the agent can discover them
through file search.

The stubs contain metadata and instructions for using the appropriate
analyze_* tools to access the actual content.

Usage:
    # Run as daemon (for systemd)
    python media_watcher.py

    # Run once (process existing media without stubs)
    python media_watcher.py --once

    # Dry run (show what would be created)
    python media_watcher.py --dry-run
"""

import os
import sys
import time
import json
import logging
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Set, Literal

# Media file extensions
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff', '.svg'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.webm', '.aac', '.flac', '.ogg'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.wmv'}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | AUDIO_EXTENSIONS | VIDEO_EXTENSIONS

# Workspace paths
GCS_WORKSPACE = Path(os.environ.get("WORKSPACE_ROOT", "/mnt/workspace"))
LOCAL_WORKSPACE = Path(os.environ.get("LOCAL_WORKSPACE", "/home/aaronwhaley/workspace_local"))

# Directories to watch for media (relative to GCS_WORKSPACE)
WATCH_DIRECTORIES = [
    "projects",  # Case folders
]

# State tracking
STATE_FILE = LOCAL_WORKSPACE / ".sync_metadata" / "media_stubs.json"
LOG_FILE = LOCAL_WORKSPACE / ".sync_metadata" / "media_watcher.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, mode='a') if LOG_FILE.parent.exists() else logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Polling interval (seconds)
POLL_INTERVAL = 300  # Check every 5 minutes (less frequent than PDF watcher)


def get_file_hash(file_path: Path) -> str:
    """Get MD5 hash of file for change detection (only first 64KB for speed)."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        # Only hash first 64KB for large media files
        chunk = f.read(65536)
        hasher.update(chunk)
    return hasher.hexdigest()


def load_state() -> dict:
    """Load state of previously processed media files."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            return {"processed": {}, "errors": {}}
    return {"processed": {}, "errors": {}}


def save_state(state: dict):
    """Save state to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_media_type(path: Path) -> Literal['image', 'audio', 'video', 'unknown']:
    """Determine media type from file extension."""
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return 'image'
    elif ext in AUDIO_EXTENSIONS:
        return 'audio'
    elif ext in VIDEO_EXTENSIONS:
        return 'video'
    return 'unknown'


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable form."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def get_stub_path(media_path: Path, gcs_workspace: Path, local_workspace: Path) -> Path:
    """
    Get the local stub path for a media file.

    Example:
        /mnt/workspace/projects/Case/photos/accident.jpg
        -> /home/.../workspace_local/projects/Case/photos/accident.jpg.md
    """
    try:
        relative = media_path.relative_to(gcs_workspace)
    except ValueError:
        relative = Path(media_path.name)

    # Add .md extension (e.g., accident.jpg -> accident.jpg.md)
    stub_path = local_workspace / (str(relative) + ".md")
    return stub_path


def create_stub_content(
    media_path: Path,
    gcs_workspace: Path,
    media_type: Literal['image', 'audio', 'video'],
    size_bytes: int
) -> str:
    """Generate stub markdown content for a media file."""
    try:
        rel_path = str(media_path.relative_to(gcs_workspace))
    except ValueError:
        rel_path = media_path.name

    ext = media_path.suffix.lower().lstrip('.')
    size_str = format_size(size_bytes)
    timestamp = datetime.now().isoformat()

    # Build the stub content
    frontmatter = f"""---
source: {media_path.name}
type: {media_type}
format: {ext}
size_bytes: {size_bytes}
gcs_path: {rel_path}
created: {timestamp}
---"""

    if media_type == 'image':
        tool_name = "analyze_image"
        tool_desc = """This will use Google Gemini to analyze the image content and provide:
- Visual description
- Relevant legal observations
- Key details for case documentation"""
    elif media_type == 'audio':
        tool_name = "analyze_audio"
        tool_desc = """This will transcribe the audio using OpenAI Whisper and provide:
- Full transcription with timestamps
- Speaker identification (if multiple)
- Key statements for case documentation"""
    else:  # video
        tool_name = "analyze_video"
        tool_desc = """This will analyze the video using Google Gemini and provide:
- Timeline of events
- Audio transcription
- Visual observations
- Key moments for case documentation"""

    content = f"""{frontmatter}

# {media_type.title()}: {media_path.name}

**Location:** `{rel_path}`
**Type:** {ext.upper()} {media_type}
**Size:** {size_str}

## How to Analyze

Use the `{tool_name}()` tool:
```
{tool_name}("{rel_path}")
```

{tool_desc}
"""
    return content


def find_new_media(
    gcs_workspace: Path,
    local_workspace: Path,
    state: dict,
    watch_dirs: list[str] = None
) -> tuple[list[tuple[Path, str, str]], int]:
    """
    Find media files that need stub creation.

    Returns tuple of:
    - List of (media_path, hash, media_type) tuples for files needing stubs
    - Count of files skipped because stub already exists
    """
    new_media = []
    skipped_existing = 0

    dirs_to_watch = watch_dirs or WATCH_DIRECTORIES

    for watch_dir in dirs_to_watch:
        watch_path = gcs_workspace / watch_dir
        if not watch_path.exists():
            logger.debug(f"Watch directory does not exist: {watch_path}")
            continue

        logger.debug(f"Scanning: {watch_path}")

        for media_path in watch_path.rglob("*"):
            # Skip directories
            if media_path.is_dir():
                continue

            # Check if it's a media file
            ext = media_path.suffix.lower()
            if ext not in MEDIA_EXTENSIONS:
                continue

            # Skip hidden directories
            if any(part.startswith('.') for part in media_path.parts):
                continue

            # Get relative path for state tracking
            try:
                rel_path = str(media_path.relative_to(gcs_workspace))
            except ValueError:
                rel_path = media_path.name

            media_type = get_media_type(media_path)

            # Check if already in state file
            if rel_path in state.get("processed", {}):
                try:
                    file_hash = get_file_hash(media_path)
                except Exception as e:
                    logger.warning(f"Could not hash {rel_path}: {e}")
                    continue
                if state["processed"][rel_path].get("hash") == file_hash:
                    continue

            # Check if stub already exists locally
            stub_path = get_stub_path(media_path, gcs_workspace, local_workspace)

            if stub_path.exists():
                # Stub already exists - add to state for tracking
                try:
                    file_hash = get_file_hash(media_path)
                except Exception as e:
                    logger.warning(f"Could not hash {rel_path}: {e}")
                    continue

                logger.debug(f"Stub exists (skipping): {stub_path.name}")
                state.setdefault("processed", {})[rel_path] = {
                    "hash": file_hash,
                    "stub_path": str(stub_path.relative_to(local_workspace)),
                    "media_type": media_type,
                    "timestamp": datetime.now().isoformat(),
                    "source": "existing_sync"
                }
                skipped_existing += 1
                continue

            # Media file needs stub creation
            try:
                file_hash = get_file_hash(media_path)
            except Exception as e:
                logger.warning(f"Could not hash {rel_path}: {e}")
                continue

            new_media.append((media_path, file_hash, media_type))

    return new_media, skipped_existing


def process_media_file(
    media_path: Path,
    file_hash: str,
    media_type: str,
    gcs_workspace: Path,
    local_workspace: Path,
    state: dict,
    dry_run: bool = False
) -> bool:
    """
    Process a single media file: create stub markdown.

    Returns True if successful, False otherwise.
    """
    stub_path = get_stub_path(media_path, gcs_workspace, local_workspace)
    rel_path = str(media_path.relative_to(gcs_workspace))

    if dry_run:
        logger.info(f"[DRY RUN] Would create stub: {rel_path} -> {stub_path}")
        return True

    logger.info(f"Creating stub: {rel_path}")

    try:
        # Get file size
        size_bytes = media_path.stat().st_size

        # Generate stub content
        stub_content = create_stub_content(
            media_path, gcs_workspace, media_type, size_bytes
        )

        # Save stub
        stub_path.parent.mkdir(parents=True, exist_ok=True)
        stub_path.write_text(stub_content)

        # Update state
        state.setdefault("processed", {})[rel_path] = {
            "hash": file_hash,
            "stub_path": str(stub_path.relative_to(local_workspace)),
            "media_type": media_type,
            "timestamp": datetime.now().isoformat(),
            "size_bytes": size_bytes
        }

        logger.info(f"Saved: {stub_path.relative_to(local_workspace)}")
        return True

    except Exception as e:
        logger.error(f"Failed to create stub for {rel_path}: {e}")
        state.setdefault("errors", {})[rel_path] = {
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
        return False


def run_once(dry_run: bool = False) -> dict:
    """
    Run a single pass: find and create stubs for all new media files.

    Returns stats dict.
    """
    stats = {
        "scanned": 0,
        "created": 0,
        "failed": 0,
        "skipped": 0,
        "by_type": {"image": 0, "audio": 0, "video": 0}
    }

    state = load_state()
    new_media, skipped_existing = find_new_media(GCS_WORKSPACE, LOCAL_WORKSPACE, state)

    # Save state immediately to persist "existing_sync" entries
    if not dry_run and skipped_existing > 0:
        save_state(state)
        logger.info(f"Registered {skipped_existing} existing stubs in state")

    stats["scanned"] = len(new_media) + skipped_existing
    stats["skipped"] = skipped_existing

    for media_path, file_hash, media_type in new_media:
        if process_media_file(media_path, file_hash, media_type, GCS_WORKSPACE, LOCAL_WORKSPACE, state, dry_run):
            stats["created"] += 1
            stats["by_type"][media_type] += 1
        else:
            stats["failed"] += 1

    if not dry_run:
        save_state(state)

    return stats


def run_daemon():
    """
    Run as daemon: continuously poll for new media files.
    """
    logger.info("Starting media watcher daemon")
    logger.info(f"  GCS workspace: {GCS_WORKSPACE}")
    logger.info(f"  Local workspace: {LOCAL_WORKSPACE}")
    logger.info(f"  Watch directories: {WATCH_DIRECTORIES}")
    logger.info(f"  Poll interval: {POLL_INTERVAL}s")

    while True:
        try:
            stats = run_once()
            if stats["created"] > 0 or stats["failed"] > 0:
                logger.info(f"Cycle complete: {stats['created']} created, {stats['failed']} failed")
        except Exception as e:
            logger.error(f"Error in watch cycle: {e}")

        time.sleep(POLL_INTERVAL)


def main():
    parser = argparse.ArgumentParser(
        description="Watch for new media files in GCS and create stub markdown files"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (don't run as daemon)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without doing it"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Ensure directories exist
    LOCAL_WORKSPACE.mkdir(parents=True, exist_ok=True)
    (LOCAL_WORKSPACE / ".sync_metadata").mkdir(parents=True, exist_ok=True)

    if args.once or args.dry_run:
        stats = run_once(dry_run=args.dry_run)
        print(f"\nMedia Watcher Summary:")
        print(f"  Scanned: {stats['scanned']}")
        print(f"  Skipped (existing stubs): {stats['skipped']}")
        print(f"  Created: {stats['created']}")
        print(f"    Images: {stats['by_type']['image']}")
        print(f"    Audio: {stats['by_type']['audio']}")
        print(f"    Video: {stats['by_type']['video']}")
        print(f"  Failed: {stats['failed']}")
        return 0 if stats["failed"] == 0 else 1
    else:
        run_daemon()
        return 0


if __name__ == "__main__":
    sys.exit(main())
