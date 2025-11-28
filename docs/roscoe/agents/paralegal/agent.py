"""
Roscoe - Dynamic Skills-Based Paralegal AI Agent

This agent uses a dynamic skills architecture:
- Skills are loaded automatically based on semantic matching to user requests
- Specialized sub-agent for multimodal analysis (images/audio/video)
- Unlimited skills can be added to /workspace/Skills/ without code changes

Architecture:
1. SkillSelectorMiddleware: Semantic search to find relevant skills
2. Skills injection: Relevant skills loaded into system prompt
3. Custom sub-agent: multimodal-agent (GPT-5.1 with multimodal capabilities)
4. General-purpose sub-agent: Built-in, inherits main agent model (GPT-5.1 Thinking)

Research and other capabilities are handled through the skills system.
See workspace/Skills/skills_manifest.json for available skills.

NOTE: Switched from Gemini 3 Pro to GPT-5.1 Thinking due to rate limits.
"""

import os
from pathlib import Path
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import ShellToolMiddleware, HostExecutionPolicy

from roscoe.agents.paralegal.models import agent_llm
from roscoe.core.skill_middleware import SkillSelectorMiddleware
from roscoe.agents.paralegal.prompts import minimal_personal_assistant_prompt
from roscoe.agents.paralegal.sub_agents import multimodal_sub_agent
from roscoe.agents.paralegal.tools import send_slack_message, upload_file_to_slack, execute_code

# Get path to skills manifest (in src/, packaged with code)
MANIFEST_PATH = Path(__file__).parent / "skills_manifest.json"

# Get workspace directory - use env variable or default to repo workspace_paralegal
# In deployment, this will be the workspace_paralegal/ directory in the repo
# In local dev, can override with WORKSPACE_DIR env variable
workspace_dir = os.environ.get("WORKSPACE_DIR", "/Volumes/X10 Pro/Roscoe/workspace_paralegal")

# Check if we're in production (LangGraph server with checkpointing)
# Shell tool can't be used with checkpointing due to pickle issues
is_production = os.environ.get("LANGGRAPH_DEPLOYMENT", "false").lower() == "true"

# Create Roscoe with dynamic skills architecture
# Custom sub-agent for specialized tasks:
# - multimodal-agent: GPT-5.1 for images/audio/video analysis
# Research and other capabilities handled through skills system (see workspace/Skills/)
personal_assistant_agent = create_deep_agent(
    system_prompt=minimal_personal_assistant_prompt,
    subagents=[
        multimodal_sub_agent,  # GPT-5.1 with multimodal capabilities
    ],
    model=agent_llm,  # GPT-5.1 Thinking
    backend=FilesystemBackend(root_dir=workspace_dir, virtual_mode=True),
    tools=[
        send_slack_message,
        upload_file_to_slack,
        execute_code,  # Runloop sandbox for code execution (stateless, no pickle issues)
    ],
    middleware=[
        # Skill selector: semantic search + skill injection
        SkillSelectorMiddleware(
            manifest_path=str(MANIFEST_PATH),  # Manifest in src/ (code)
            skills_dir=f"{workspace_dir}/Skills",  # Skills markdown in workspace (runtime)
            max_skills=1,  # Load top 1 matching skill per request
            similarity_threshold=0.3  # Minimum similarity score (0-1)
        ),
    ] + ([] if is_production else [
        # Shell tool: Only in local dev (can't be checkpointed in production)
        ShellToolMiddleware(
            workspace_root=workspace_dir,
            execution_policy=HostExecutionPolicy(),
        ),
    ]),
    checkpointer=False if not is_production else None,  # Let server handle checkpointing in production
).with_config({"recursion_limit": 1000})