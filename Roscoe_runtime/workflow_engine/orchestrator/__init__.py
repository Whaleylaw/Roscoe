"""
Roscoe Workflow Engine Orchestrator

This module provides state machine orchestration for PI case management.

Usage:
    from orchestrator import StateMachine, get_case_status_message
    
    # Create state machine
    sm = StateMachine()
    
    # Create new case
    case = sm.create_new_case("2024-0001", "John Smith", "2024-01-15", "mva")
    
    # Get status
    status = sm.get_case_status(case)
    message = sm.format_status_for_agent(status)
    
    # Complete a step
    case = sm.complete_step(case, "intake", "collect_client_info", {
        "client.phone": "502-555-1234",
        "client.email": "john@example.com"
    })
    
    # Add pending item
    case = sm.add_pending_item(
        case,
        description="Waiting for signed retainer",
        owner="client",
        workflow="send_documents_for_signature",
        blocking=True
    )
"""

from .state_machine import StateMachine, get_case_status_message

__all__ = ['StateMachine', 'get_case_status_message']
