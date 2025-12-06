#!/usr/bin/env python3
"""
Document Viewer UI Script

Display documents (PDFs, Markdown, plain text) in the UI.
- PDFs: Generates GCS signed URL for iframe embedding
- Markdown/Text: Returns content directly for frontend rendering

Usage:
    python document_viewer.py --file-path "/projects/Case-Name/Medical Records/report.pdf"
    python document_viewer.py --file-path "/Reports/analysis.md"

Output:
    JSON with component="DocumentViewer" and file data
"""

import argparse
import os
from pathlib import Path
from datetime import timedelta
from typing import Optional

from _utils import (
    get_workspace_path,
    output_result,
    output_error,
)


# GCS bucket name - same as used in main tools
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "whaley_law_firm")


def get_file_type(file_path: Path) -> str:
    """Determine file type from extension."""
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return "pdf"
    elif ext in [".md", ".markdown"]:
        return "markdown"
    elif ext in [".txt", ".text", ".log"]:
        return "text"
    elif ext in [".json"]:
        return "json"
    elif ext in [".html", ".htm"]:
        return "html"
    else:
        # Default to text for unknown types
        return "text"


def generate_signed_url(gcs_path: str, expiration_minutes: int = 60) -> Optional[str]:
    """
    Generate a GCS signed URL for file access.
    
    Args:
        gcs_path: Path relative to the bucket root (e.g., "projects/Case/file.pdf")
        expiration_minutes: URL validity duration
        
    Returns:
        Signed URL string or None if generation fails
    """
    try:
        from google.cloud import storage
        
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(gcs_path)
        
        # Check if blob exists
        if not blob.exists():
            return None
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET",
        )
        return url
    except Exception as e:
        print(f"Warning: Failed to generate signed URL: {e}", file=__import__('sys').stderr)
        return None


def read_file_content(file_path: Path, max_size_mb: int = 5) -> Optional[str]:
    """
    Read file content for text-based files.
    
    Args:
        file_path: Full path to the file
        max_size_mb: Maximum file size in MB to read
        
    Returns:
        File content as string or None if too large/unreadable
    """
    try:
        # Check file size
        file_size = file_path.stat().st_size
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            return None
        
        # Read content
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Failed to read file: {e}", file=__import__('sys').stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Generate document viewer UI data")
    parser.add_argument("--file-path", required=True, help="Workspace-relative file path")
    parser.add_argument("--expiration", type=int, default=60, help="URL expiration in minutes (for PDFs)")
    args = parser.parse_args()
    
    workspace_path = get_workspace_path()
    
    # Normalize file path - handle both absolute and relative paths
    file_path_str = args.file_path.lstrip("/")
    
    # Build full path
    full_path = workspace_path / file_path_str
    
    if not full_path.exists():
        output_error(f"File not found: {args.file_path}")
    
    if not full_path.is_file():
        output_error(f"Path is not a file: {args.file_path}")
    
    # Get file info
    file_type = get_file_type(full_path)
    file_name = full_path.name
    file_size = full_path.stat().st_size
    
    # Prepare response data
    data = {
        "file_path": args.file_path,
        "file_name": file_name,
        "file_type": file_type,
        "file_size": file_size,
        "file_size_formatted": format_file_size(file_size),
        "content": None,
        "url": None,
    }
    
    if file_type == "pdf":
        # Generate signed URL for PDF
        # GCS path is relative to bucket root (same as workspace mount)
        gcs_path = file_path_str
        signed_url = generate_signed_url(gcs_path, args.expiration)
        
        if signed_url:
            data["url"] = signed_url
        else:
            output_error(f"Failed to generate signed URL for: {args.file_path}")
    else:
        # Read content for text-based files
        content = read_file_content(full_path)
        
        if content is not None:
            data["content"] = content
        else:
            # File too large or unreadable - try to generate signed URL as fallback
            gcs_path = file_path_str
            signed_url = generate_signed_url(gcs_path, args.expiration)
            
            if signed_url:
                data["url"] = signed_url
                data["content_note"] = "File too large to display inline. Use URL to download."
            else:
                output_error(f"File too large to display and URL generation failed: {args.file_path}")
    
    output_result({
        "component": "DocumentViewer",
        "data": data,
    })


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


if __name__ == "__main__":
    main()

