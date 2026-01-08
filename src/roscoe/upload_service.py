"""
File Upload Service for Roscoe

Allows users to upload documents directly to the agent workspace.
The agent can then read, analyze (with vision), and save to appropriate case folders.

Runs on port 8125 in the roscoe-uploads container.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import os
import shutil
from datetime import datetime
from typing import Optional

app = FastAPI(title="Roscoe Upload Service")

# CORS configuration (allow UI to upload files)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your UI domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get workspace roots from environment
# GCS_WORKSPACE: GCS Fuse mount (for binary files like PDFs, images)
# LOCAL_WORKSPACE: Fast local disk (for text files like JSON, markdown)
GCS_WORKSPACE = Path(os.getenv("WORKSPACE_ROOT", "/mnt/workspace"))
LOCAL_WORKSPACE = Path(os.getenv("LOCAL_WORKSPACE", "/home/aaronwhaley/workspace_local"))

UPLOADS_BASE_DIR = os.getenv("UPLOADS_BASE_DIR", "uploads/inbox")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
UPLOAD_TOKEN = os.getenv("UPLOAD_TOKEN", "")  # Optional auth token

# Text file extensions that should be stored locally (faster access)
TEXT_EXTENSIONS = {
    '.md', '.txt', '.json', '.py', '.html', '.css', '.js',
    '.yaml', '.yml', '.csv', '.xml', '.rst', '.ini', '.cfg',
    '.sh', '.bash', '.toml', '.env', '.log'
}

def is_text_file(filename: str) -> bool:
    """Check if file should be stored locally based on extension."""
    ext = Path(filename).suffix.lower()
    return ext in TEXT_EXTENSIONS

def get_workspace_for_file(filename: str) -> Path:
    """Get the appropriate workspace root based on file type."""
    if is_text_file(filename):
        return LOCAL_WORKSPACE
    return GCS_WORKSPACE

# Ensure uploads directories exist in both workspaces
(GCS_WORKSPACE / UPLOADS_BASE_DIR).mkdir(parents=True, exist_ok=True)
(LOCAL_WORKSPACE / UPLOADS_BASE_DIR).mkdir(parents=True, exist_ok=True)

# Default uploads dir (uses GCS for backward compatibility)
UPLOADS_DIR = GCS_WORKSPACE / UPLOADS_BASE_DIR


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "roscoe-uploads"}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    case_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    token: Optional[str] = Form(None),
):
    """
    Upload a file to the workspace inbox for agent processing.

    Args:
        file: The file to upload
        case_name: Optional case folder name to associate with this file
        description: Optional description of the file
        token: Optional authentication token (if UPLOAD_TOKEN is set)

    Returns:
        JSON with upload details including file path
    """
    # Verify token if configured
    if UPLOAD_TOKEN and token != UPLOAD_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid upload token")

    # Check file size
    file_size_mb = 0
    if file.size:
        file_size_mb = file.size / (1024 * 1024)
        if file_size_mb > MAX_UPLOAD_MB:
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {file_size_mb:.1f}MB (max: {MAX_UPLOAD_MB}MB)"
            )

    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = file.filename or "uploaded_file"

    # Sanitize filename (remove dangerous characters)
    safe_filename = "".join(c for c in original_filename if c.isalnum() or c in ".-_ ")
    unique_filename = f"{timestamp}_{safe_filename}"

    # Determine upload path based on file type and case
    # Text files go to local workspace (fast), binary files go to GCS (persistent storage)
    workspace = get_workspace_for_file(safe_filename)
    storage_type = "local" if is_text_file(safe_filename) else "gcs"

    if case_name:
        # Upload to case folder if specified
        upload_path = workspace / "projects" / case_name / "uploads" / unique_filename
        upload_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Upload to general inbox
        upload_path = workspace / UPLOADS_BASE_DIR / unique_filename
        upload_path.parent.mkdir(parents=True, exist_ok=True)

    # Save file
    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Build relative path for agent (relative to the workspace it was saved to)
    relative_path = str(upload_path.relative_to(workspace))

    return JSONResponse({
        "success": True,
        "filename": safe_filename,
        "unique_filename": unique_filename,
        "path": f"/{relative_path}",  # Agent uses workspace-relative paths
        "absolute_path": str(upload_path),
        "size_mb": file_size_mb,
        "case_name": case_name,
        "description": description,
        "uploaded_at": timestamp,
        "storage_type": storage_type,  # "local" for text files, "gcs" for binary
        "message": f"File uploaded successfully ({storage_type}). Agent can access at: /{relative_path}"
    })


@app.get("/uploads")
async def list_uploads(case_name: Optional[str] = None):
    """
    List uploaded files in inbox or for a specific case.
    Checks both local and GCS workspaces.

    Args:
        case_name: Optional case folder name to filter uploads

    Returns:
        JSON with list of uploaded files
    """
    uploads = []

    # Check both local and GCS workspaces
    for workspace, storage_type in [(LOCAL_WORKSPACE, "local"), (GCS_WORKSPACE, "gcs")]:
        if case_name:
            upload_dir = workspace / "projects" / case_name / "uploads"
        else:
            upload_dir = workspace / UPLOADS_BASE_DIR

        if not upload_dir.exists():
            continue

        for file_path in upload_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                relative_path = str(file_path.relative_to(workspace))
                uploads.append({
                    "filename": file_path.name,
                    "path": f"/{relative_path}",
                    "size_mb": stat.st_size / (1024 * 1024),
                    "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "storage_type": storage_type,
                })

    # Sort by upload time (newest first)
    uploads.sort(key=lambda x: x["uploaded_at"], reverse=True)

    return {"uploads": uploads, "count": len(uploads)}


@app.delete("/upload/{filename}")
async def delete_upload(filename: str, case_name: Optional[str] = None, token: Optional[str] = None):
    """
    Delete an uploaded file. Checks both local and GCS workspaces.

    Args:
        filename: Name of file to delete
        case_name: Optional case folder name
        token: Optional authentication token

    Returns:
        Confirmation message
    """
    # Verify token if configured
    if UPLOAD_TOKEN and token != UPLOAD_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid upload token")

    # Check both workspaces for the file
    file_path = None
    for workspace in [LOCAL_WORKSPACE, GCS_WORKSPACE]:
        if case_name:
            candidate_path = workspace / "projects" / case_name / "uploads" / filename
        else:
            candidate_path = workspace / UPLOADS_BASE_DIR / filename

        if candidate_path.exists():
            file_path = candidate_path
            break

    if file_path is None:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_path.unlink()
        return {"success": True, "message": f"File {filename} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8125)
