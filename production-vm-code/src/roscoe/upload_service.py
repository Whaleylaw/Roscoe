"""
Upload sidecar service for Roscoe (production).

Purpose
-------
Provide a simple HTTP endpoint for uploading files (images, PDFs, etc.) into the
GCS-backed workspace mount (/mnt/workspace via gcsfuse). This enables UIs (e.g.
LangSmith Studio, DeepAgents UI, custom tools) to upload a file, get back a
workspace path, and then ask the agent to analyze/move/rename it.

Design
------
- Runs as a separate service (sidecar) alongside the LangGraph API container.
- Accepts multipart/form-data uploads.
- Writes files into /mnt/workspace/uploads/inbox/<case_name|unassigned>/...
- Returns:
  - workspace_path (e.g. "/uploads/inbox/unassigned/20251215T010203Z_photo.jpg")
  - paste (a ready-to-paste snippet for the chat)

Security
--------
Optionally require a shared secret via header `X-Upload-Token`, configured by env
var `UPLOAD_TOKEN`. If UPLOAD_TOKEN is unset, uploads are unauthenticated.

Env vars
--------
- WORKSPACE_ROOT: default "/mnt/workspace"
- UPLOADS_BASE_DIR: default "uploads/inbox"
- MAX_UPLOAD_MB: default "50"
- UPLOAD_TOKEN: optional shared secret
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except Exception:
        return default


WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", "/mnt/workspace")).resolve()
UPLOADS_BASE_DIR = os.environ.get("UPLOADS_BASE_DIR", "uploads/inbox").strip().strip("/")
MAX_UPLOAD_MB = _env_int("MAX_UPLOAD_MB", 50)
UPLOAD_TOKEN = os.environ.get("UPLOAD_TOKEN")


app = FastAPI(
    title="Roscoe Upload Service",
    version="1.0.0",
)

# CORS: keep permissive by default; lock down at reverse-proxy if needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_filename(name: str) -> str:
    name = (name or "upload").strip()
    name = name.replace("\\", "_").replace("/", "_")
    name = _SAFE_NAME_RE.sub("_", name)
    name = re.sub(r"_+", "_", name).strip("._-")
    return name or "upload"


def _safe_case_segment(case_name: Optional[str]) -> str:
    if not case_name:
        return "unassigned"
    return _sanitize_filename(case_name)[:120]


def _workspace_rel(path: Path) -> str:
    # Convert absolute /mnt/workspace/... to workspace-relative "/..."
    try:
        rel = path.resolve().relative_to(WORKSPACE_ROOT)
    except Exception:
        # Fall back (should not happen if we write under workspace root)
        rel = path.name
    return "/" + str(rel).replace("\\", "/")


@app.get("/health")
async def health() -> dict:
    return {
        "ok": True,
        "workspace_root": str(WORKSPACE_ROOT),
        "uploads_base_dir": UPLOADS_BASE_DIR,
        "max_upload_mb": MAX_UPLOAD_MB,
        "auth_required": bool(UPLOAD_TOKEN),
    }


@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    case_name: Optional[str] = Form(default=None),
    desired_name: Optional[str] = Form(default=None),
    x_upload_token: Optional[str] = Header(default=None, alias="X-Upload-Token"),
) -> dict:
    # Optional shared-secret auth
    if UPLOAD_TOKEN:
        if not x_upload_token or x_upload_token != UPLOAD_TOKEN:
            raise HTTPException(status_code=401, detail="Unauthorized")

    if not file.filename and not desired_name:
        raise HTTPException(status_code=400, detail="Missing filename")

    # Ensure workspace root exists/mounted
    if not WORKSPACE_ROOT.exists():
        raise HTTPException(status_code=500, detail=f"Workspace root not found: {WORKSPACE_ROOT}")

    case_seg = _safe_case_segment(case_name)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    original = _sanitize_filename(desired_name or file.filename or "upload")
    out_dir = (WORKSPACE_ROOT / UPLOADS_BASE_DIR / case_seg).resolve()

    # Guard: must remain under workspace root
    try:
        out_dir.relative_to(WORKSPACE_ROOT)
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid upload directory resolution")

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{ts}_{original}"

    # Stream to disk with size cap
    max_bytes = MAX_UPLOAD_MB * 1024 * 1024
    written = 0
    try:
        with open(out_path, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB
                if not chunk:
                    break
                written += len(chunk)
                if written > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Max is {MAX_UPLOAD_MB}MB.",
                    )
                f.write(chunk)
    except HTTPException:
        # Clean up partial file
        try:
            if out_path.exists():
                out_path.unlink()
        except Exception:
            pass
        raise
    except Exception as e:
        try:
            if out_path.exists():
                out_path.unlink()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to write upload: {e}")

    ws_path = _workspace_rel(out_path)

    paste = (
        f"Uploaded to `{ws_path}`.\n\n"
        f"Next:\n"
        f"- If it's an image: `analyze_image(\"{ws_path}\")`\n"
        f"- If it's a PDF scan: convert pages to images, then analyze selected pages."
    )

    return {
        "ok": True,
        "workspace_path": ws_path,
        "bytes_written": written,
        "case_name": case_name,
        "paste": paste,
    }

