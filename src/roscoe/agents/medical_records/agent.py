"""
Medical Records Analysis Agent.

A standalone LangGraph agent for comprehensive medical records analysis
in personal injury cases. Uses:
- create_react_agent for the agent loop
- ShellToolMiddleware for file operations (glob, grep, shell)
- Progress tracking via progress.json
- Task list with passes: true/false to prevent premature completion

This agent is invoked via fire-and-forget pattern from the paralegal DeepAgent.
"""

import os
from pathlib import Path

from langgraph.prebuilt import create_react_agent
from langchain.agents.middleware import ShellToolMiddleware, HostExecutionPolicy

from roscoe.agents.medical_records.models import get_agent_llm
from roscoe.agents.medical_records.prompts import MEDICAL_RECORDS_ANALYSIS_PROMPT
from roscoe.agents.medical_records.tools import get_tools


# Workspace paths
LOCAL_WORKSPACE = os.environ.get("LOCAL_WORKSPACE", "/app/workspace_local")


def create_medical_records_agent():
    """
    Create the medical records analysis agent.

    Uses:
    - Claude Sonnet with Gemini fallback
    - ShellToolMiddleware for file operations
    - Custom progress tracking tools

    Returns:
        LangGraph agent ready for execution
    """
    # Get model (lazily initialized)
    model = get_agent_llm()

    # Get custom tools for progress tracking
    tools = get_tools()

    # Create the agent with react pattern
    # Note: In newer LangGraph versions, use 'prompt' instead of 'state_modifier'
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=MEDICAL_RECORDS_ANALYSIS_PROMPT,
    )

    return agent


# Export for langgraph.json
# The agent is created lazily when the module is loaded
medical_records_agent = create_medical_records_agent()
