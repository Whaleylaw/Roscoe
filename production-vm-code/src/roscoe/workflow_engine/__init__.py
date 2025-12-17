"""
Roscoe Workflow Engine

Provides state machine-based workflow tracking for personal injury cases.
Vendored from Roscoe_runtime/workflow_engine for deterministic deployments.
"""

from .orchestrator.state_machine import StateMachine, get_case_status_message

__all__ = ["StateMachine", "get_case_status_message"]
