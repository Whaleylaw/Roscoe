"""
Patched FilesystemBackend with timeout and result limits for glob operations.

The original deepagents FilesystemBackend.glob_info has no timeout, which causes
the agent to hang indefinitely on large directory trees with recursive patterns.

This module patches the glob_info method to:
1. Add a configurable timeout (default: 30 seconds)
2. Add a result limit (default: 1000 files)
3. Use a signal-based timeout for safety
"""

import logging
import signal
from datetime import datetime
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

# Configuration
GLOB_TIMEOUT_SECONDS = 30  # Maximum time for glob operation
GLOB_MAX_RESULTS = 1000    # Maximum number of results to return


class GlobTimeoutError(Exception):
    """Raised when glob operation times out."""
    pass


def _timeout_handler(signum, frame):
    """Signal handler for glob timeout."""
    raise GlobTimeoutError("Glob operation timed out")


def patched_glob_info(self, pattern: str, path: str = "/") -> list[dict[str, Any]]:
    """
    Patched glob_info with timeout and result limit.

    This replaces the original FilesystemBackend.glob_info to prevent
    the agent from hanging on large directory trees.
    """
    if pattern.startswith("/"):
        pattern = pattern.lstrip("/")

    search_path = self.cwd if path == "/" else self._resolve_path(path)
    if not search_path.exists() or not search_path.is_dir():
        return []

    results: list[dict[str, Any]] = []
    timed_out = False
    hit_limit = False

    # Set up timeout using signal (Unix only)
    old_handler = None
    try:
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(GLOB_TIMEOUT_SECONDS)
    except (ValueError, AttributeError):
        # signal.alarm not available (Windows or non-main thread)
        LOGGER.warning("Glob timeout not available (non-Unix or non-main thread)")
        old_handler = None

    try:
        # Use recursive globbing to match files in subdirectories
        for matched_path in search_path.rglob(pattern):
            # Check result limit
            if len(results) >= GLOB_MAX_RESULTS:
                hit_limit = True
                LOGGER.warning(f"Glob hit result limit ({GLOB_MAX_RESULTS}), stopping early")
                break

            try:
                is_file = matched_path.is_file()
            except OSError:
                continue
            if not is_file:
                continue

            abs_path = str(matched_path)
            if not self.virtual_mode:
                try:
                    st = matched_path.stat()
                    results.append(
                        {
                            "path": abs_path,
                            "is_dir": False,
                            "size": int(st.st_size),
                            "modified_at": datetime.fromtimestamp(st.st_mtime).isoformat(),
                        }
                    )
                except OSError:
                    results.append({"path": abs_path, "is_dir": False})
            else:
                cwd_str = str(self.cwd)
                if not cwd_str.endswith("/"):
                    cwd_str += "/"
                if abs_path.startswith(cwd_str):
                    relative_path = abs_path[len(cwd_str):]
                elif abs_path.startswith(str(self.cwd)):
                    relative_path = abs_path[len(str(self.cwd)):].lstrip("/")
                else:
                    relative_path = abs_path
                virt = "/" + relative_path
                try:
                    st = matched_path.stat()
                    results.append(
                        {
                            "path": virt,
                            "is_dir": False,
                            "size": int(st.st_size),
                            "modified_at": datetime.fromtimestamp(st.st_mtime).isoformat(),
                        }
                    )
                except OSError:
                    results.append({"path": virt, "is_dir": False})

    except GlobTimeoutError:
        timed_out = True
        LOGGER.error(f"Glob timed out after {GLOB_TIMEOUT_SECONDS}s for pattern: {pattern}")
    except (OSError, ValueError) as e:
        LOGGER.error(f"Glob error: {e}")
    finally:
        # Cancel the alarm and restore old handler
        if old_handler is not None:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    results.sort(key=lambda x: x.get("path", ""))

    # Log summary
    if timed_out or hit_limit:
        LOGGER.warning(
            f"Glob returned {len(results)} results (timed_out={timed_out}, hit_limit={hit_limit}) "
            f"for pattern: {pattern}"
        )
    else:
        LOGGER.info(f"Glob returned {len(results)} results for pattern: {pattern}")

    return results


def patch_filesystem_backend():
    """
    Monkey-patch FilesystemBackend.glob_info with our timeout version.

    Call this at agent startup before any glob operations.
    """
    try:
        from deepagents.backends.filesystem import FilesystemBackend

        # Save original for reference
        FilesystemBackend._original_glob_info = FilesystemBackend.glob_info

        # Apply patch
        FilesystemBackend.glob_info = patched_glob_info

        LOGGER.info(
            f"Patched FilesystemBackend.glob_info with timeout={GLOB_TIMEOUT_SECONDS}s, "
            f"max_results={GLOB_MAX_RESULTS}"
        )
        print(f"🔧 Patched FilesystemBackend.glob_info (timeout={GLOB_TIMEOUT_SECONDS}s, max={GLOB_MAX_RESULTS})")
        return True

    except ImportError as e:
        LOGGER.error(f"Could not patch FilesystemBackend: {e}")
        return False


# Auto-patch on import
_patched = patch_filesystem_backend()
