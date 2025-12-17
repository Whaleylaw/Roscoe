#!/usr/bin/env python3
"""
Workflow State Computer

Thin adapter between case_context_middleware and the StateMachine.
Loads case_state.json (strict mode) and returns formatted status for agent injection.

This module:
1. Loads case_state.json via CaseStateStore (raises if missing)
2. Runs StateMachine.get_case_status() to compute status with data sync
3. Formats output via StateMachine.format_status_for_agent()
4. Returns a compatible object for the middleware

Usage:
    from roscoe.core.workflow_state_computer import compute_workflow_state
    
    state = compute_workflow_state("Smith-MVA-01-15-2024")
    print(state.formatted_status)  # Markdown for agent prompt
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

from .case_state_store import (
    CaseStateStore, 
    CaseStateNotFoundError,
    load_case_state,
    save_case_state,
    case_state_exists
)

logger = logging.getLogger(__name__)

# Lazy-loaded StateMachine instance
_state_machine = None


def _get_state_machine():
    """Get or create the StateMachine instance (lazy loading)."""
    global _state_machine
    if _state_machine is None:
        from roscoe.workflow_engine import StateMachine
        
        # Determine schemas directory
        schemas_dir = Path(__file__).parent.parent / "workflow_engine" / "schemas"
        
        _state_machine = StateMachine(schemas_dir=schemas_dir)
        logger.debug(f"Initialized StateMachine with schemas from {schemas_dir}")
    
    return _state_machine


@dataclass
class WorkflowStateResult:
    """
    Result object returned by compute_workflow_state().
    
    Maintains compatibility with the existing middleware interface.
    """
    project_name: str
    client_name: str
    current_phase: str
    phase_progress: float
    formatted_status: str
    sol_status: Dict = None
    completed_workflows: List[str] = None
    in_progress_workflows: List[str] = None
    blockers: List[Dict] = None
    next_actions: List[Dict] = None
    data_corrections: List[Dict] = None
    pending_phase_change: Dict = None
    raw_status: Dict = None
    
    def __post_init__(self):
        # Initialize lists if None
        if self.completed_workflows is None:
            self.completed_workflows = []
        if self.in_progress_workflows is None:
            self.in_progress_workflows = []
        if self.blockers is None:
            self.blockers = []
        if self.next_actions is None:
            self.next_actions = []
        if self.data_corrections is None:
            self.data_corrections = []


def compute_workflow_state(project_name: str) -> WorkflowStateResult:
    """
    Main entry point: Compute workflow state for a case.
    
    STRICT MODE: Raises CaseStateNotFoundError if case_state.json is missing.
    Run the migration script to create state files for existing cases.
    
    Args:
        project_name: The case/project name (e.g., "Smith-MVA-01-15-2024")
    
    Returns:
        WorkflowStateResult object with formatted_status and other state info
    
    Raises:
        CaseStateNotFoundError: If case_state.json doesn't exist for this project
    """
    # Load case state (strict - raises if missing)
    case_state = load_case_state(project_name)
    
    # Get StateMachine
    sm = _get_state_machine()
    
    # Compute comprehensive status (triggers data sync + validation)
    status = sm.get_case_status(case_state)
    
    # Save updated state if corrections were made
    if status.get("data_corrections"):
        save_case_state(project_name, case_state)
        logger.info(
            f"Auto-corrected {len(status['data_corrections'])} workflow(s) for '{project_name}'"
        )
    
    # Format for agent injection
    formatted_status = sm.format_status_for_agent(status)
    
    # Extract workflow lists for compatibility
    completed_workflows = [
        item.get("name", "") 
        for item in status.get("completed_items", []) 
        if item.get("type") == "workflow"
    ]
    
    # Build blocking items list
    blockers = []
    for item in status.get("blocking_items", []):
        blockers.append({
            "id": item.get("id", ""),
            "message": item.get("description", ""),
            "owner": item.get("owner", "external"),
            "blocking": True
        })
    
    # Build next actions list (convert NextAction dataclass to dict)
    next_actions = []
    for action in status.get("next_actions", []):
        if hasattr(action, 'description'):
            # It's a NextAction dataclass
            next_actions.append({
                "description": action.description,
                "owner": action.owner,
                "workflow": action.workflow,
                "step": action.step,
                "can_automate": action.can_automate,
                "tool_available": action.tool_available,
                "manual_fallback": action.manual_fallback
            })
        else:
            # It's already a dict
            next_actions.append(action)
    
    return WorkflowStateResult(
        project_name=project_name,
        client_name=status.get("client_name", project_name),
        current_phase=status.get("current_phase", "unknown"),
        phase_progress=float(status.get("phase_progress", 0)),
        formatted_status=formatted_status,
        sol_status=None,  # SOL is included in alerts
        completed_workflows=completed_workflows,
        in_progress_workflows=[],  # Not directly exposed by new API
        blockers=blockers,
        next_actions=next_actions,
        data_corrections=status.get("data_corrections", []),
        pending_phase_change=status.get("pending_phase_change"),
        raw_status=status
    )


def compute_workflow_state_safe(project_name: str) -> Optional[WorkflowStateResult]:
    """
    Compute workflow state, returning None if state file is missing.
    
    Use this for graceful degradation when missing state should not be fatal.
    Logs a warning when state is missing.
    
    Args:
        project_name: The case/project name
    
    Returns:
        WorkflowStateResult or None if state file is missing
    """
    try:
        return compute_workflow_state(project_name)
    except CaseStateNotFoundError as e:
        logger.warning(
            f"Workflow state not available for '{project_name}': {e}. "
            f"Run migration script to create case_state.json."
        )
        return None
    except Exception as e:
        logger.error(f"Error computing workflow state for '{project_name}': {e}")
        return None


def get_formatted_status(project_name: str) -> str:
    """
    Get just the formatted status string for a case.
    
    Convenience function for simple status retrieval.
    Returns empty string if state is missing.
    
    Args:
        project_name: The case/project name
    
    Returns:
        Formatted markdown status string, or empty string on error
    """
    result = compute_workflow_state_safe(project_name)
    return result.formatted_status if result else ""


# CLI for testing
def main():
    """CLI for testing workflow state computation."""
    import argparse
    import json
    import sys
    
    parser = argparse.ArgumentParser(description="Compute workflow state for a case")
    parser.add_argument("--case", "-c", required=True, help="Case/project name")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty print")
    parser.add_argument("--check", action="store_true", help="Check if state exists (exit 0/1)")
    
    args = parser.parse_args()
    
    if args.check:
        exists = case_state_exists(args.case)
        print(f"case_state.json exists: {exists}")
        sys.exit(0 if exists else 1)
    
    try:
        state = compute_workflow_state(args.case)
        
        if args.json:
            output = {
                "project_name": state.project_name,
                "client_name": state.client_name,
                "current_phase": state.current_phase,
                "phase_progress": state.phase_progress,
                "completed_workflows": state.completed_workflows,
                "blockers": state.blockers,
                "next_actions": state.next_actions,
                "data_corrections": state.data_corrections,
                "pending_phase_change": state.pending_phase_change
            }
            print(json.dumps(output, indent=2 if args.pretty else None))
        else:
            print(state.formatted_status)
    
    except CaseStateNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nTo create state files for existing cases, run:", file=sys.stderr)
        print("  python -m roscoe.workflow_engine.scripts.migrate_case_states", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
