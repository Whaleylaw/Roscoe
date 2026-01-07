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

# Get workspace root from environment
WORKSPACE_ROOT = Path(os.getenv("WORKSPACE_ROOT", "/mnt/workspace"))
UPLOADS_BASE_DIR = os.getenv("UPLOADS_BASE_DIR", "uploads/inbox")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
UPLOAD_TOKEN = os.getenv("UPLOAD_TOKEN", "")  # Optional auth token

# Ensure uploads directory exists
UPLOADS_DIR = WORKSPACE_ROOT / UPLOADS_BASE_DIR
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


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

    # Determine upload path
    if case_name:
        # Upload to case folder if specified
        upload_path = WORKSPACE_ROOT / "projects" / case_name / "uploads" / unique_filename
        upload_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Upload to general inbox
        upload_path = UPLOADS_DIR / unique_filename

    # Save file
    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Build relative path for agent
    relative_path = str(upload_path.relative_to(WORKSPACE_ROOT))

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
        "message": f"File uploaded successfully. Agent can access at: {relative_path}"
    })


@app.get("/uploads")
async def list_uploads(case_name: Optional[str] = None):
    """
    List uploaded files in inbox or for a specific case.

    Args:
        case_name: Optional case folder name to filter uploads

    Returns:
        JSON with list of uploaded files
    """
    if case_name:
        upload_dir = WORKSPACE_ROOT / "projects" / case_name / "uploads"
    else:
        upload_dir = UPLOADS_DIR

    if not upload_dir.exists():
        return {"uploads": [], "count": 0}

    uploads = []
    for file_path in upload_dir.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            relative_path = str(file_path.relative_to(WORKSPACE_ROOT))
            uploads.append({
                "filename": file_path.name,
                "path": f"/{relative_path}",
                "size_mb": stat.st_size / (1024 * 1024),
                "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

    # Sort by upload time (newest first)
    uploads.sort(key=lambda x: x["uploaded_at"], reverse=True)

    return {"uploads": uploads, "count": len(uploads)}


@app.delete("/upload/{filename}")
async def delete_upload(filename: str, case_name: Optional[str] = None, token: Optional[str] = None):
    """
    Delete an uploaded file.

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

    if case_name:
        file_path = WORKSPACE_ROOT / "projects" / case_name / "uploads" / filename
    else:
        file_path = UPLOADS_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_path.unlink()
        return {"success": True, "message": f"File {filename} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8125)
