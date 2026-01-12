"""
Roscoe Workflow Engine Orchestrator

This module provides graph-based workflow state computation for PI case management.

Usage:
    from roscoe.workflow_engine.orchestrator.graph_state_computer import (
        DerivedWorkflowState,
        compute_workflow_state,
        format_status_for_agent
    )

    # Compute workflow state from graph
    state = await compute_workflow_state("case-123")

    # Format for agent
    message = await format_status_for_agent(state)
"""

from .graph_state_computer import DerivedWorkflowState

__all__ = ['DerivedWorkflowState']
