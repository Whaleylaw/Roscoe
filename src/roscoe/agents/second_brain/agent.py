"""
Roscoe Second Brain Agent.

A standalone agent for personal memory management:
- Capture tasks, ideas, interactions, people, notes
- Query and search captured memories
- Auto-detect capture opportunities from conversation
- Morning digest on request (use get_morning_brief tool)

Uses create_deep_agent (same framework as paralegal, no subagents needed).
"""

import os
from deepagents import create_deep_agent

from roscoe.agents.second_brain.models import get_agent_llm
from roscoe.agents.second_brain.prompts import SECOND_BRAIN_SYSTEM_PROMPT
from roscoe.agents.second_brain.tools import get_all_tools


# Check if we're in production
is_production = os.environ.get("LANGGRAPH_DEPLOYMENT", "false").lower() == "true"


def create_second_brain_agent():
    """
    Create the Second Brain agent.

    Uses:
    - Claude Sonnet (main model)
    - Explicit capture tools
    - get_morning_brief tool for on-demand digests
    - No subagents needed

    Returns:
        LangGraph agent ready for execution
    """
    # Get tools
    tools = get_all_tools()

    # Create agent using same framework as paralegal
    # Note: Proactive digest middleware not enabled yet - use get_morning_brief tool instead
    agent = create_deep_agent(
        system_prompt=SECOND_BRAIN_SYSTEM_PROMPT,
        subagents=[],  # No subagents needed
        model=get_agent_llm(),  # Claude Sonnet 4.5
        backend=None,  # Default backend
        tools=tools,
        middleware=[],
        checkpointer=False if not is_production else None,  # Let server handle
    ).with_config({"recursion_limit": 250})

    print("🧠 SECOND BRAIN AGENT INITIALIZED", flush=True)

    return agent


# Export for langgraph.json
second_brain_agent = create_second_brain_agent()
