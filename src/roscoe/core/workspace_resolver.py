"""
Workspace Resolver Module

Routes file operations between local disk (fast, for text files) and GCS Fuse (for binary files).

This module provides:
- Path resolution based on file type
- Automatic sync from local to GCS after writes
- Conflict detection and backup

Architecture:
    Agent Tools → resolve_path() → Local Disk (text files) or GCS Mount (binary files)

    After writes to local disk, sync_file_to_gcs() copies to GCS mount for backup.
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Literal, Optional, Tuple

logger = logging.getLogger(__name__)

# File extensions that should be stored locally (text-based, small)
TEXT_EXTENSIONS = {
    '.md', '.txt', '.json', '.py', '.html', '.css', '.js',
    '.yaml', '.yml', '.csv', '.xml', '.rst', '.ini', '.cfg',
    '.sh', '.bash', '.toml', '.env', '.log'
}

# File extensions that must stay on GCS (binary, large)
BINARY_EXTENSIONS = {
    '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff', '.svg',
    '.mp3', '.mp4', '.wav', '.mov', '.avi', '.mkv', '.webm', '.m4a',
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.exe', '.dll', '.so', '.dylib'
}

# Workspace paths from environment
LOCAL_WORKSPACE = Path(os.environ.get("LOCAL_WORKSPACE", "/home/aaronwhaley/workspace_local"))
GCS_WORKSPACE = Path(os.environ.get("WORKSPACE_ROOT", "/mnt/workspace"))

# Sync metadata directory for conflict tracking
SYNC_METADATA_DIR = LOCAL_WORKSPACE / ".sync_metadata"
CONFLICTS_DIR = SYNC_METADATA_DIR / "conflicts"


def is_text_file(path: str) -> bool:
    """
    Check if a file should be stored locally based on its extension.

    Args:
        path: Workspace-relative or absolute path to check

    Returns:
        True if the file is a text file that should be stored locally
    """
    ext = Path(path).suffix.lower()

    # Explicit text extensions
    if ext in TEXT_EXTENSIONS:
        return True

    # Explicit binary extensions
    if ext in BINARY_EXTENSIONS:
        return False

    # Default: treat unknown extensions as binary (safer for large files)
    return False


def resolve_path(
    workspace_relative_path: str,
    operation: Literal['read', 'write'] = 'read'
) -> Path:
    """
    Resolve workspace-relative path to actual filesystem path.

    Routes text files to local disk, binary files to GCS mount.
    Maintains backward compatibility with existing code.

    Args:
        workspace_relative_path: Path relative to workspace root (e.g., "/Reports/summary.md")
        operation: 'read' or 'write' - affects path resolution for writes

    Returns:
        Absolute Path to the file

    Examples:
        >>> resolve_path("/Reports/summary.md", "read")
        Path('/home/aaronwhaley/workspace_local/Reports/summary.md')

        >>> resolve_path("/projects/case/docs/invoice.pdf", "read")
        Path('/mnt/workspace/projects/case/docs/invoice.pdf')
    """
    # Normalize path - remove leading slash
    clean_path = workspace_relative_path.lstrip('/')

    # Determine file type and base path
    if is_text_file(clean_path):
        base = LOCAL_WORKSPACE
    else:
        base = GCS_WORKSPACE

    resolved = base / clean_path

    # For read operations, fall back to GCS if local doesn't exist
    if operation == 'read' and is_text_file(clean_path):
        if not resolved.exists():
            gcs_fallback = GCS_WORKSPACE / clean_path
            if gcs_fallback.exists():
                logger.debug(f"Local file not found, falling back to GCS: {clean_path}")
                return gcs_fallback

    return resolved


def get_both_paths(workspace_relative_path: str) -> Tuple[Path, Path]:
    """
    Get both local and GCS paths for a workspace-relative path.

    Useful for sync operations or when you need to check both locations.

    Args:
        workspace_relative_path: Path relative to workspace root

    Returns:
        Tuple of (local_path, gcs_path)
    """
    clean_path = workspace_relative_path.lstrip('/')
    return LOCAL_WORKSPACE / clean_path, GCS_WORKSPACE / clean_path


def sync_file_to_gcs(workspace_relative_path: str) -> bool:
    """
    Sync a file from local workspace to GCS mount.

    Called after write operations to ensure GCS has the latest version.
    Creates parent directories if needed.

    Args:
        workspace_relative_path: Path relative to workspace root

    Returns:
        True if sync succeeded, False otherwise
    """
    clean_path = workspace_relative_path.lstrip('/')
    local_path = LOCAL_WORKSPACE / clean_path
    gcs_path = GCS_WORKSPACE / clean_path

    if not local_path.exists():
        logger.warning(f"Cannot sync: local file does not exist: {local_path}")
        return False

    try:
        # Create parent directories on GCS if needed
        gcs_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file (preserves metadata)
        shutil.copy2(local_path, gcs_path)
        logger.info(f"Synced to GCS: {clean_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to sync {clean_path} to GCS: {e}")
        return False


def sync_file_from_gcs(workspace_relative_path: str, overwrite: bool = False) -> bool:
    """
    Sync a file from GCS mount to local workspace.

    Args:
        workspace_relative_path: Path relative to workspace root
        overwrite: If True, overwrite existing local file; if False, skip if exists

    Returns:
        True if sync succeeded or file already exists, False on error
    """
    clean_path = workspace_relative_path.lstrip('/')
    local_path = LOCAL_WORKSPACE / clean_path
    gcs_path = GCS_WORKSPACE / clean_path

    if not gcs_path.exists():
        logger.warning(f"Cannot sync: GCS file does not exist: {gcs_path}")
        return False

    if local_path.exists() and not overwrite:
        logger.debug(f"Local file already exists, skipping: {clean_path}")
        return True

    try:
        # Backup existing local file if it differs (conflict detection)
        if local_path.exists() and overwrite:
            _backup_conflict(local_path, clean_path)

        # Create parent directories locally if needed
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file from GCS
        shutil.copy2(gcs_path, local_path)
        logger.info(f"Synced from GCS: {clean_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to sync {clean_path} from GCS: {e}")
        return False


def _backup_conflict(local_path: Path, workspace_relative_path: str) -> Optional[Path]:
    """
    Backup a local file before overwriting (conflict resolution).

    Args:
        local_path: Absolute path to local file
        workspace_relative_path: Workspace-relative path for naming

    Returns:
        Path to backup file, or None if backup failed
    """
    if not local_path.exists():
        return None

    try:
        CONFLICTS_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{timestamp}_{local_path.name}"
        backup_path = CONFLICTS_DIR / backup_name

        shutil.copy2(local_path, backup_path)
        logger.info(f"Backed up conflict: {workspace_relative_path} -> {backup_path}")
        return backup_path

    except Exception as e:
        logger.error(f"Failed to backup conflict for {workspace_relative_path}: {e}")
        return None


def ensure_local_workspace_structure():
    """
    Ensure the local workspace has the required directory structure.

    Creates directories if they don't exist:
    - /Database
    - /Reports
    - /Tools
    - /Skills
    - /projects
    - /uploads/inbox
    - /.sync_metadata/conflicts
    """
    directories = [
        LOCAL_WORKSPACE / "Database",
        LOCAL_WORKSPACE / "Reports",
        LOCAL_WORKSPACE / "Tools",
        LOCAL_WORKSPACE / "Skills",
        LOCAL_WORKSPACE / "projects",
        LOCAL_WORKSPACE / "uploads" / "inbox",
        CONFLICTS_DIR,
    ]

    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {dir_path}")


def list_conflicts() -> list[dict]:
    """
    List all conflict backups for review.

    Returns:
        List of dicts with conflict info: filename, timestamp, size
    """
    if not CONFLICTS_DIR.exists():
        return []

    conflicts = []
    for f in CONFLICTS_DIR.iterdir():
        if f.is_file():
            conflicts.append({
                "filename": f.name,
                "path": str(f),
                "size_bytes": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            })

    return sorted(conflicts, key=lambda x: x["modified"], reverse=True)


def clear_conflicts(older_than_days: int = 7) -> int:
    """
    Clear old conflict backups.

    Args:
        older_than_days: Delete conflicts older than this many days

    Returns:
        Number of files deleted
    """
    if not CONFLICTS_DIR.exists():
        return 0

    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=older_than_days)
    deleted = 0

    for f in CONFLICTS_DIR.iterdir():
        if f.is_file():
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                f.unlink()
                deleted += 1
                logger.info(f"Deleted old conflict backup: {f.name}")

    return deleted
