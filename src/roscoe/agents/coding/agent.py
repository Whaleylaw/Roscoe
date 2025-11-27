"""
Roscoe Coding Agent - Software Development AI Assistant

This agent specializes in:
- Code analysis and review
- Bug fixing and debugging
- Feature implementation
- Refactoring and optimization
- Testing and documentation
- Architecture design

Uses Claude Sonnet 4.5 for superior code generation capabilities.
"""

import os
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import ShellToolMiddleware, HostExecutionPolicy

from roscoe.agents.coding.models import agent_llm
from roscoe.agents.coding.prompts import coding_agent_prompt
from roscoe.slack_launcher import ensure_bridge_started

# Get workspace directory - use env variable or default to repo workspace_coding
# In deployment, this will be the workspace_coding/ directory in the repo
# In local dev, can override with WORKSPACE_CODING_DIR env variable
workspace_dir = os.environ.get(
    "WORKSPACE_CODING_DIR",
    "/Volumes/X10 Pro/projects"
)

# Create Coding Agent
# Uses Claude Sonnet 4.5 for excellent code generation capabilities
# FilesystemBackend provides sandboxed file operations
coding_agent = create_deep_agent(
    system_prompt=coding_agent_prompt,
    subagents=[],  # No specialized sub-agents yet - can add later
    model=agent_llm,  # Claude Sonnet 4.5
    backend=FilesystemBackend(root_dir=workspace_dir, virtual_mode=True),
    tools=[],  # No additional tools - shell provided via middleware
    middleware=[
        ShellToolMiddleware(
            workspace_root=workspace_dir,
            execution_policy=HostExecutionPolicy(),
        ),
    ],
    checkpointer=False,  # Disable checkpointing - shell sessions can't be pickled
).with_config({"recursion_limit": 1000})

# Ensure Slack bridge also runs when only the coding agent is loaded
ensure_bridge_started()
