"""
Roscoe Second Brain Agent.

A standalone agent for personal memory management:
- Capture tasks, ideas, interactions, people, notes
- Query and search captured memories
- Auto-detect capture opportunities
- Morning digests via ProactiveSurfacingMiddleware
- TELOS context loading via TELOSMiddleware

Uses create_agent (simpler than DeepAgents - no subagents needed).
"""

import os
from langchain.agents import create_agent

from roscoe.agents.second_brain.models import get_agent_llm
from roscoe.agents.second_brain.prompts import SECOND_BRAIN_SYSTEM_PROMPT
from roscoe.agents.second_brain.tools import get_all_tools

# Middleware imports
from roscoe.second_brain_implementation.core.telos_middleware import TELOSMiddleware
from roscoe.second_brain_implementation.core.proactive_surfacing_middleware import ProactiveSurfacingMiddleware
from roscoe.core.graph_adapter import graph_client
from roscoe.core.slack_adapter import get_slack_client


# Workspace directory
workspace_dir = os.environ.get("WORKSPACE_DIR", "/mnt/workspace")

# Check if we're in production
is_production = os.environ.get("LANGGRAPH_DEPLOYMENT", "false").lower() == "true"


def create_second_brain_agent():
    """
    Create the Second Brain agent.

    Uses:
    - Claude Sonnet (main model)
    - TELOSMiddleware (context loading)
    - ProactiveSurfacingMiddleware (morning digests)
    - Explicit capture tools

    Returns:
        LangGraph agent ready for execution
    """
    # Create middleware instances
    telos_middleware = TELOSMiddleware(workspace_dir=workspace_dir)
    proactive_middleware = ProactiveSurfacingMiddleware(
        graph_client=graph_client,
        slack_client=get_slack_client()
    )

    # Get tools
    tools = get_all_tools()

    # Create agent
    agent = create_agent(
        model=get_agent_llm(),
        tools=tools,
        system_prompt=SECOND_BRAIN_SYSTEM_PROMPT,
        middleware=[
            telos_middleware,
            proactive_middleware,
        ],
    )

    print("🧠 SECOND BRAIN AGENT INITIALIZED", flush=True)

    return agent


# Export for langgraph.json
second_brain_agent = create_second_brain_agent()
