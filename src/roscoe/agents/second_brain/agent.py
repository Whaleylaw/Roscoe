"""
Roscoe Second Brain Agent.

A standalone agent for personal memory management:
- Capture tasks, ideas, interactions, people, notes
- Query and search captured memories
- Auto-detect capture opportunities from conversation
- Proactive morning digests at 7 AM

Uses create_deep_agent (same framework as paralegal, no subagents needed).
"""

import os
from deepagents import create_deep_agent

from roscoe.agents.second_brain.models import get_agent_llm
from roscoe.agents.second_brain.prompts import SECOND_BRAIN_SYSTEM_PROMPT
from roscoe.agents.second_brain.tools import get_all_tools

# Import proactive surfacing middleware and slack adapter
from roscoe.second_brain_implementation.core.proactive_surfacing_middleware import (
    ProactiveSurfacingMiddleware,
)
from roscoe.core.slack_adapter import get_slack_client
from roscoe.core.graphiti_client import get_graphiti_client


# Check if we're in production
is_production = os.environ.get("LANGGRAPH_DEPLOYMENT", "false").lower() == "true"


def create_second_brain_agent():
    """
    Create the Second Brain agent.

    Uses:
    - Claude Sonnet (main model)
    - Explicit capture tools
    - ProactiveSurfacingMiddleware for morning digests
    - No subagents needed

    Returns:
        LangGraph agent ready for execution
    """
    # Get tools
    tools = get_all_tools()

    # Initialize middleware
    middleware = []
    try:
        # Get graph client for data queries
        graph_client = get_graphiti_client()
        # Get slack client for delivery
        slack_client = get_slack_client()

        # Add proactive surfacing for morning digests
        proactive_middleware = ProactiveSurfacingMiddleware(
            graph_client=graph_client,
            slack_client=slack_client,
        )
        middleware.append(proactive_middleware)
        print("📬 ProactiveSurfacingMiddleware added to Second Brain", flush=True)
    except Exception as e:
        print(f"⚠️ Could not initialize ProactiveSurfacingMiddleware: {e}", flush=True)

    # Create agent using same framework as paralegal
    agent = create_deep_agent(
        system_prompt=SECOND_BRAIN_SYSTEM_PROMPT,
        subagents=[],  # No subagents needed
        model=get_agent_llm(),  # Claude Sonnet 4.5
        backend=None,  # Default backend
        tools=tools,
        middleware=middleware,
        checkpointer=False if not is_production else None,  # Let server handle
    ).with_config({"recursion_limit": 250})

    print("🧠 SECOND BRAIN AGENT INITIALIZED", flush=True)

    return agent


# Export for langgraph.json
second_brain_agent = create_second_brain_agent()
