#!/usr/bin/env python3
"""
PDF Watcher Service

Monitors the GCS workspace for new PDF files and automatically converts them
to Markdown, saving the result to the local workspace.

This enables the agent to read PDF content as fast local text files.

Usage:
    # Run as daemon (for systemd)
    python pdf_watcher.py

    # Run once (process existing PDFs without markdown)
    python pdf_watcher.py --once

    # Dry run (show what would be converted)
    python pdf_watcher.py --dry-run
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
from typing import Optional, Set

# PDF processing
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from markitdown import MarkItDown
    HAS_MARKITDOWN = True
except ImportError:
    HAS_MARKITDOWN = False

# Workspace paths
GCS_WORKSPACE = Path(os.environ.get("WORKSPACE_ROOT", "/mnt/workspace"))
LOCAL_WORKSPACE = Path(os.environ.get("LOCAL_WORKSPACE", "/home/aaronwhaley/workspace_local"))

# State tracking
STATE_FILE = LOCAL_WORKSPACE / ".sync_metadata" / "pdf_conversions.json"
LOG_FILE = LOCAL_WORKSPACE / ".sync_metadata" / "pdf_watcher.log"

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
POLL_INTERVAL = 60  # Check every minute


def get_pdf_hash(pdf_path: Path) -> str:
    """Get MD5 hash of PDF file for change detection."""
    hasher = hashlib.md5()
    with open(pdf_path, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_conversion_state() -> dict:
    """Load state of previously converted PDFs."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            return {"converted": {}, "errors": {}}
    return {"converted": {}, "errors": {}}


def save_conversion_state(state: dict):
    """Save conversion state to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def convert_pdf_to_markdown(pdf_path: Path) -> Optional[str]:
    """
    Convert a PDF to markdown text.

    Uses pdfplumber for text extraction. Falls back to markitdown if available.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Markdown content or None if conversion failed
    """
    if HAS_PDFPLUMBER:
        try:
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"## Page {i}\n\n{page_text}")

            if text_parts:
                # Add metadata header
                header = f"""---
source: {pdf_path.name}
converted: {datetime.now().isoformat()}
pages: {len(text_parts)}
---

# {pdf_path.stem}

"""
                return header + "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"pdfplumber failed for {pdf_path}: {e}")

    if HAS_MARKITDOWN:
        try:
            md = MarkItDown()
            result = md.convert(str(pdf_path))
            if result and result.text_content:
                header = f"""---
source: {pdf_path.name}
converted: {datetime.now().isoformat()}
converter: markitdown
---

# {pdf_path.stem}

"""
                return header + result.text_content
        except Exception as e:
            logger.error(f"markitdown failed for {pdf_path}: {e}")

    return None


def get_markdown_path(pdf_path: Path, gcs_workspace: Path, local_workspace: Path) -> Path:
    """
    Get the local markdown path for a PDF.

    Maintains the same directory structure but with .md extension.

    Example:
        /mnt/workspace/projects/Case/docs/file.pdf
        -> /home/.../workspace_local/projects/Case/docs/file.pdf.md
    """
    try:
        relative = pdf_path.relative_to(gcs_workspace)
    except ValueError:
        relative = Path(pdf_path.name)

    # Add .md extension (keep .pdf in name for traceability)
    md_path = local_workspace / relative.with_suffix('.pdf.md')
    return md_path


def find_new_pdfs(gcs_workspace: Path, state: dict) -> list[tuple[Path, str]]:
    """
    Find PDFs that need conversion.

    Returns list of (pdf_path, hash) tuples for PDFs that:
    - Have no corresponding markdown file
    - Have changed since last conversion (different hash)
    """
    new_pdfs = []

    for pdf_path in gcs_workspace.rglob("*.pdf"):
        # Skip hidden directories
        if any(part.startswith('.') for part in pdf_path.parts):
            continue

        # Get relative path for state tracking
        try:
            rel_path = str(pdf_path.relative_to(gcs_workspace))
        except ValueError:
            rel_path = pdf_path.name

        # Check if already converted
        pdf_hash = get_pdf_hash(pdf_path)

        if rel_path in state.get("converted", {}):
            if state["converted"][rel_path].get("hash") == pdf_hash:
                # Already converted with same hash
                continue

        new_pdfs.append((pdf_path, pdf_hash))

    return new_pdfs


def process_pdf(
    pdf_path: Path,
    pdf_hash: str,
    gcs_workspace: Path,
    local_workspace: Path,
    state: dict,
    dry_run: bool = False
) -> bool:
    """
    Process a single PDF: convert to markdown and save.

    Returns True if successful, False otherwise.
    """
    md_path = get_markdown_path(pdf_path, gcs_workspace, local_workspace)
    rel_path = str(pdf_path.relative_to(gcs_workspace))

    if dry_run:
        logger.info(f"[DRY RUN] Would convert: {rel_path} -> {md_path}")
        return True

    logger.info(f"Converting: {rel_path}")

    # Convert PDF
    markdown = convert_pdf_to_markdown(pdf_path)

    if markdown is None:
        logger.error(f"Failed to convert: {rel_path}")
        state.setdefault("errors", {})[rel_path] = {
            "timestamp": datetime.now().isoformat(),
            "error": "Conversion returned None"
        }
        return False

    # Save markdown
    try:
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(markdown)

        # Update state
        state.setdefault("converted", {})[rel_path] = {
            "hash": pdf_hash,
            "markdown_path": str(md_path.relative_to(local_workspace)),
            "timestamp": datetime.now().isoformat(),
            "size_bytes": len(markdown)
        }

        logger.info(f"Saved: {md_path.relative_to(local_workspace)}")
        return True

    except Exception as e:
        logger.error(f"Failed to save markdown for {rel_path}: {e}")
        state.setdefault("errors", {})[rel_path] = {
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
        return False


def run_once(dry_run: bool = False) -> dict:
    """
    Run a single pass: find and convert all new PDFs.

    Returns stats dict.
    """
    stats = {
        "scanned": 0,
        "converted": 0,
        "failed": 0,
        "skipped": 0,
    }

    state = load_conversion_state()
    new_pdfs = find_new_pdfs(GCS_WORKSPACE, state)

    stats["scanned"] = len(new_pdfs)

    for pdf_path, pdf_hash in new_pdfs:
        if process_pdf(pdf_path, pdf_hash, GCS_WORKSPACE, LOCAL_WORKSPACE, state, dry_run):
            stats["converted"] += 1
        else:
            stats["failed"] += 1

    if not dry_run:
        save_conversion_state(state)

    return stats


def run_daemon():
    """
    Run as daemon: continuously poll for new PDFs.
    """
    logger.info("Starting PDF watcher daemon")
    logger.info(f"  GCS workspace: {GCS_WORKSPACE}")
    logger.info(f"  Local workspace: {LOCAL_WORKSPACE}")
    logger.info(f"  Poll interval: {POLL_INTERVAL}s")

    while True:
        try:
            stats = run_once()
            if stats["converted"] > 0 or stats["failed"] > 0:
                logger.info(f"Cycle complete: {stats['converted']} converted, {stats['failed']} failed")
        except Exception as e:
            logger.error(f"Error in watch cycle: {e}")

        time.sleep(POLL_INTERVAL)


def main():
    parser = argparse.ArgumentParser(
        description="Watch for new PDFs in GCS and convert to Markdown"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (don't run as daemon)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be converted without doing it"
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

    if not HAS_PDFPLUMBER and not HAS_MARKITDOWN:
        logger.error("Neither pdfplumber nor markitdown available. Install one to enable PDF conversion.")
        return 1

    if args.once or args.dry_run:
        stats = run_once(dry_run=args.dry_run)
        print(f"\nPDF Watcher Summary:")
        print(f"  Scanned: {stats['scanned']}")
        print(f"  Converted: {stats['converted']}")
        print(f"  Failed: {stats['failed']}")
        return 0 if stats["failed"] == 0 else 1
    else:
        run_daemon()
        return 0


if __name__ == "__main__":
    sys.exit(main())
