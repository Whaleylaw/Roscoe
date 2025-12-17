"""
Case State Store

Handles loading and saving case_state.json files for workflow state tracking.
Operates in STRICT mode - raises errors if state files are missing (assumes migration has run).

Usage:
    from roscoe.core.case_state_store import CaseStateStore
    
    store = CaseStateStore()
    
    # Load state (raises FileNotFoundError if missing)
    case_state = store.load(project_name)
    
    # Save state
    store.save(project_name, case_state)
    
    # Get path to state file
    path = store.get_state_path(project_name)
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CaseStateNotFoundError(FileNotFoundError):
    """Raised when case_state.json is not found for a project."""
    
    def __init__(self, project_name: str, expected_path: Path):
        self.project_name = project_name
        self.expected_path = expected_path
        super().__init__(
            f"case_state.json not found for '{project_name}'. "
            f"Expected at: {expected_path}. "
            f"Run the migration script to create state files for existing cases."
        )


class CaseStateStore:
    """
    Manages case_state.json files for workflow state persistence.
    
    Storage Location:
        ${WORKSPACE_DIR}/projects/{project_name}/Case Information/case_state.json
    
    Strict Mode:
        This store operates in strict mode - it will NOT create state files automatically.
        If a state file is missing, it raises CaseStateNotFoundError.
        Use the migration script to create state files for existing cases.
    """
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        """
        Initialize the store.
        
        Args:
            workspace_dir: Optional workspace directory override.
                          If not provided, uses WORKSPACE_DIR or WORKSPACE_ROOT env vars.
        """
        if workspace_dir:
            self.workspace_dir = Path(workspace_dir)
        else:
            self.workspace_dir = self._resolve_workspace_dir()
    
    def _resolve_workspace_dir(self) -> Path:
        """Resolve workspace directory from environment."""
        # Try environment variables in order of preference
        for env_var in ["WORKSPACE_DIR", "WORKSPACE_ROOT", "ROSCOE_ROOT"]:
            env_val = os.environ.get(env_var)
            if env_val:
                path = Path(env_val)
                if path.exists():
                    return path
        
        # Fallback paths
        fallbacks = [
            Path("/mnt/workspace"),  # GCS mount on VM
            Path("/app/workspace_paralegal"),  # Docker container
            Path("/Volumes/X10 Pro/Roscoe/Roscoe_runtime"),  # Local dev
            Path("/Volumes/X10 Pro/Roscoe/workspace_paralegal"),  # Legacy local
        ]
        
        for path in fallbacks:
            if path.exists():
                return path
        
        # Last resort
        logger.warning("Could not resolve workspace directory, using current directory")
        return Path(".")
    
    def get_state_path(self, project_name: str) -> Path:
        """
        Get the path to case_state.json for a project.
        
        Args:
            project_name: Case/project name (e.g., "Smith-MVA-01-15-2024")
        
        Returns:
            Path to the case_state.json file
        """
        return self.workspace_dir / "projects" / project_name / "Case Information" / "case_state.json"
    
    def exists(self, project_name: str) -> bool:
        """
        Check if case_state.json exists for a project.
        
        Args:
            project_name: Case/project name
        
        Returns:
            True if file exists, False otherwise
        """
        return self.get_state_path(project_name).exists()
    
    def load(self, project_name: str) -> Dict[str, Any]:
        """
        Load case_state.json for a project.
        
        STRICT MODE: Raises CaseStateNotFoundError if file doesn't exist.
        
        Args:
            project_name: Case/project name
        
        Returns:
            Case state dictionary
        
        Raises:
            CaseStateNotFoundError: If state file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        state_path = self.get_state_path(project_name)
        
        if not state_path.exists():
            logger.error(
                f"case_state.json not found for project '{project_name}'. "
                f"Expected at: {state_path}"
            )
            raise CaseStateNotFoundError(project_name, state_path)
        
        try:
            with open(state_path, 'r', encoding='utf-8') as f:
                case_state = json.load(f)
            
            logger.debug(f"Loaded case state for '{project_name}' from {state_path}")
            return case_state
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in case_state.json for '{project_name}': {e}")
            raise
    
    def save(self, project_name: str, case_state: Dict[str, Any]) -> Path:
        """
        Save case_state.json for a project.
        
        Creates parent directories if they don't exist.
        Updates the 'updated_at' timestamp.
        
        Args:
            project_name: Case/project name
            case_state: Case state dictionary to save
        
        Returns:
            Path where file was saved
        """
        state_path = self.get_state_path(project_name)
        
        # Ensure directory exists
        state_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Update timestamp
        case_state["updated_at"] = datetime.now().isoformat()
        
        # Write file
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(case_state, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Saved case state for '{project_name}' to {state_path}")
        return state_path
    
    def load_or_none(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Load case_state.json, returning None if not found.
        
        This is a convenience method for cases where you want to handle
        missing state files gracefully (e.g., logging only).
        
        Args:
            project_name: Case/project name
        
        Returns:
            Case state dictionary or None if not found
        """
        try:
            return self.load(project_name)
        except CaseStateNotFoundError:
            return None
    
    def list_all_projects(self) -> list[str]:
        """
        List all projects that have case_state.json files.
        
        Returns:
            List of project names
        """
        projects_dir = self.workspace_dir / "projects"
        if not projects_dir.exists():
            return []
        
        projects = []
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                state_file = project_dir / "Case Information" / "case_state.json"
                if state_file.exists():
                    projects.append(project_dir.name)
        
        return sorted(projects)


# Module-level convenience functions
_default_store: Optional[CaseStateStore] = None


def get_default_store() -> CaseStateStore:
    """Get the default case state store instance."""
    global _default_store
    if _default_store is None:
        _default_store = CaseStateStore()
    return _default_store


def load_case_state(project_name: str) -> Dict[str, Any]:
    """
    Load case state for a project using the default store.
    
    Args:
        project_name: Case/project name
    
    Returns:
        Case state dictionary
    
    Raises:
        CaseStateNotFoundError: If state file doesn't exist
    """
    return get_default_store().load(project_name)


def save_case_state(project_name: str, case_state: Dict[str, Any]) -> Path:
    """
    Save case state for a project using the default store.
    
    Args:
        project_name: Case/project name
        case_state: Case state dictionary
    
    Returns:
        Path where file was saved
    """
    return get_default_store().save(project_name, case_state)


def case_state_exists(project_name: str) -> bool:
    """
    Check if case state exists for a project.
    
    Args:
        project_name: Case/project name
    
    Returns:
        True if state file exists
    """
    return get_default_store().exists(project_name)
