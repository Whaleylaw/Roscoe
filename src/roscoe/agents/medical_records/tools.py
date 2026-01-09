"""
Tools for Medical Records Analysis Agent.

Progress tracking tools based on "Effective Harnesses for Long-Running Agents":
- update_progress: Update progress.json with completed tasks
- update_job_status: Update job status for paralegal agent polling
- write_report: Save analysis reports to case folder

Prevents premature completion through structured task tracking with passes: true/false.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool


# Workspace paths
GCS_WORKSPACE = Path(os.environ.get("WORKSPACE_ROOT", "/mnt/workspace"))
LOCAL_WORKSPACE = Path(os.environ.get("LOCAL_WORKSPACE", "/app/workspace_local"))
ANALYSIS_JOBS_DIR = LOCAL_WORKSPACE / "analysis_jobs"


@tool
def update_progress(
    job_id: str,
    case_folder: str,
    current_phase: str,
    task_description: str,
    task_status: str = "complete",
    artifacts_created: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Update the progress.json file for the current analysis job.

    This is the primary mechanism for tracking progress across context windows.
    Every significant action should update progress.json so the next session
    can resume from where we left off.

    Args:
        job_id: The analysis job ID
        case_folder: Path to case folder (e.g., "/projects/Wilson-MVA-2024")
        current_phase: Current phase name (setup, fact_investigation, medical_extraction, parallel_analysis, final_synthesis)
        task_description: Description of the task being updated
        task_status: Status of the task (pending, in_progress, complete, failed)
        artifacts_created: List of file paths created by this task

    Returns:
        Updated progress state dict
    """
    # Progress file in case reports folder
    progress_path = LOCAL_WORKSPACE / case_folder.lstrip("/") / "reports" / "analysis_progress.json"
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing or create new
    if progress_path.exists():
        progress = json.loads(progress_path.read_text())
    else:
        progress = {
            "job_id": job_id,
            "case_folder": case_folder,
            "started_at": datetime.now().isoformat(),
            "current_phase": "setup",
            "phases": {
                "setup": {"status": "pending"},
                "fact_investigation": {"status": "pending"},
                "medical_extraction": {"status": "pending"},
                "parallel_analysis": {"status": "pending"},
                "final_synthesis": {"status": "pending"},
            },
            "tasks": [],
            "artifacts_created": [],
            "last_action": None,
            "last_updated": None,
        }

    # Update phase
    progress["current_phase"] = current_phase
    if task_status == "in_progress":
        progress["phases"][current_phase]["status"] = "in_progress"
    elif task_status == "complete":
        # Check if all tasks in phase are complete
        phase_tasks = [t for t in progress["tasks"] if t.get("phase") == current_phase]
        if all(t.get("status") == "complete" for t in phase_tasks):
            progress["phases"][current_phase]["status"] = "complete"
            progress["phases"][current_phase]["completed_at"] = datetime.now().isoformat()

    # Find or add task
    task_found = False
    for task in progress["tasks"]:
        if task["description"] == task_description:
            task["status"] = task_status
            task["updated_at"] = datetime.now().isoformat()
            if task_status == "complete":
                task["passes"] = True
            task_found = True
            break

    if not task_found:
        progress["tasks"].append({
            "description": task_description,
            "phase": current_phase,
            "status": task_status,
            "passes": task_status == "complete",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        })

    # Track artifacts
    if artifacts_created:
        for artifact in artifacts_created:
            if artifact not in progress["artifacts_created"]:
                progress["artifacts_created"].append(artifact)

    # Update metadata
    progress["last_action"] = task_description
    progress["last_updated"] = datetime.now().isoformat()

    # Save
    progress_path.write_text(json.dumps(progress, indent=2))

    return {
        "success": True,
        "progress_file": str(progress_path),
        "current_phase": current_phase,
        "task": task_description,
        "status": task_status,
    }


@tool
def update_job_status(
    job_id: str,
    status: str,
    phase: Optional[str] = None,
    message: Optional[str] = None,
    result_path: Optional[str] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update the job status file for paralegal agent polling.

    The paralegal agent uses get_medical_analysis_status(job_id) to check
    this file and report progress to the user.

    Args:
        job_id: The analysis job ID
        status: Job status (queued, running, completed, failed)
        phase: Current phase name (optional)
        message: Status message for display (optional)
        result_path: Path to final result file when complete (optional)
        error: Error message if failed (optional)

    Returns:
        Updated status dict
    """
    # Job status in analysis_jobs directory
    job_dir = ANALYSIS_JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    status_path = job_dir / "status.json"

    # Load existing or create new
    if status_path.exists():
        job_status = json.loads(status_path.read_text())
    else:
        job_status = {
            "job_id": job_id,
            "created_at": datetime.now().isoformat(),
            "status": "queued",
        }

    # Update status
    job_status["status"] = status
    job_status["updated_at"] = datetime.now().isoformat()

    if phase:
        job_status["current_phase"] = phase
    if message:
        job_status["message"] = message
    if result_path:
        job_status["result_path"] = result_path
    if error:
        job_status["error"] = error

    # Track phase history
    if "phase_history" not in job_status:
        job_status["phase_history"] = []
    if phase and (not job_status["phase_history"] or job_status["phase_history"][-1]["phase"] != phase):
        job_status["phase_history"].append({
            "phase": phase,
            "started_at": datetime.now().isoformat(),
        })

    # Save
    status_path.write_text(json.dumps(job_status, indent=2))

    return {
        "success": True,
        "job_id": job_id,
        "status": status,
        "phase": phase,
        "status_file": str(status_path),
    }


@tool
def write_report(
    case_folder: str,
    report_name: str,
    content: str,
    subfolder: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Write an analysis report to the case reports folder.

    Args:
        case_folder: Path to case folder (e.g., "/projects/Wilson-MVA-2024")
        report_name: Report filename (e.g., "chronology.md", "causation.md")
        content: Report content (markdown)
        subfolder: Optional subfolder within reports (e.g., "extractions")

    Returns:
        Result dict with file path
    """
    # Build path
    reports_dir = LOCAL_WORKSPACE / case_folder.lstrip("/") / "reports"
    if subfolder:
        reports_dir = reports_dir / subfolder
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_path = reports_dir / report_name

    # Write report
    report_path.write_text(content)

    return {
        "success": True,
        "report_path": str(report_path),
        "size_bytes": len(content),
        "workspace_path": f"/reports/{subfolder + '/' if subfolder else ''}{report_name}",
    }


@tool
def read_progress(job_id: str, case_folder: str) -> Dict[str, Any]:
    """
    Read the current progress state for resuming analysis.

    Called at the start of each session to understand what work
    has been done and what remains.

    Args:
        job_id: The analysis job ID
        case_folder: Path to case folder

    Returns:
        Progress state dict or empty dict if not found
    """
    progress_path = LOCAL_WORKSPACE / case_folder.lstrip("/") / "reports" / "analysis_progress.json"

    if not progress_path.exists():
        return {
            "found": False,
            "message": "No progress file found - this is a new analysis",
        }

    progress = json.loads(progress_path.read_text())

    # Calculate summary
    total_tasks = len(progress.get("tasks", []))
    completed_tasks = len([t for t in progress.get("tasks", []) if t.get("passes", False)])

    phases = progress.get("phases", {})
    completed_phases = len([p for p, v in phases.items() if v.get("status") == "complete"])

    return {
        "found": True,
        "job_id": progress.get("job_id"),
        "current_phase": progress.get("current_phase"),
        "last_action": progress.get("last_action"),
        "last_updated": progress.get("last_updated"),
        "tasks_completed": f"{completed_tasks}/{total_tasks}",
        "phases_completed": f"{completed_phases}/5",
        "artifacts_created": progress.get("artifacts_created", []),
        "next_incomplete_task": next(
            (t["description"] for t in progress.get("tasks", []) if not t.get("passes", False)),
            None
        ),
        "full_progress": progress,
    }


def get_tools():
    """Get all tools for the medical records analysis agent."""
    return [
        update_progress,
        update_job_status,
        write_report,
        read_progress,
    ]
