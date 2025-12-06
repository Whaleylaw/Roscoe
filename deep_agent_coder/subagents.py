"""
Deep Agent Coder - Subagent Configurations

Subagents are defined as simple dictionaries. Deep Agents handles
the spawning and context isolation automatically via the `task` tool.
"""

from .prompts import (
    CODER_SYSTEM_PROMPT,
    TESTER_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
    FIXER_SYSTEM_PROMPT,
)


def get_subagents(model: str = "claude-sonnet-4-5-20250929") -> list[dict]:
    """
    Return subagent configurations for the Initializer agent.
    
    Each subagent is a dict with:
    - name: Unique identifier (used when calling task())
    - description: What the subagent does (helps main agent decide when to use it)
    - system_prompt: Instructions for the subagent
    - tools: Additional tools (empty = inherits filesystem tools)
    - model: Override model (optional, defaults to main agent's model)
    """
    return [
        {
            "name": "coder",
            "description": (
                "Implements one feature at a time. Give it a clear specification "
                "and it will write clean, working code. Use for: creating new files, "
                "implementing functions, adding features, writing tests."
            ),
            "system_prompt": CODER_SYSTEM_PROMPT,
            "tools": [],  # Inherits filesystem tools from main agent
            "model": model,
        },
        {
            "name": "tester",
            "description": (
                "Verifies implementations work correctly. Runs automated tests "
                "and performs manual verification. Use after coder finishes "
                "to ensure the feature works before marking complete."
            ),
            "system_prompt": TESTER_SYSTEM_PROMPT,
            "tools": [],
            "model": model,
        },
        {
            "name": "reviewer",
            "description": (
                "Reviews code for quality, security, and best practices. "
                "Use after tester confirms functionality works. Returns "
                "structured feedback with issues categorized by severity."
            ),
            "system_prompt": REVIEWER_SYSTEM_PROMPT,
            "tools": [],
            "model": model,
        },
        {
            "name": "fixer",
            "description": (
                "Fixes bugs and addresses review feedback. Makes minimal, "
                "targeted changes. Use when tester finds issues or reviewer "
                "requests changes. Do NOT use coder for fixes."
            ),
            "system_prompt": FIXER_SYSTEM_PROMPT,
            "tools": [],
            "model": model,
        },
    ]
