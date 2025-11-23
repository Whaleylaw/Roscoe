"""
Roscoe - Dynamic Skills-Based Paralegal AI Agent

This agent uses a dynamic skills architecture:
- Skills are loaded automatically based on semantic matching to user requests
- Models are switched dynamically based on skill requirements
- Only uses the built-in general-purpose sub-agent (no hardcoded sub-agents)
- Unlimited skills can be added to /workspace/Skills/ without code changes

Architecture:
1. SkillSelectorMiddleware: Semantic search to find relevant skills
2. model_selector_middleware: Dynamic model switching (Gemini/Sonnet/Haiku)
3. Skills injection: Relevant skills loaded into system prompt
4. General-purpose sub-agent: Inherits current model, executes sub-tasks

See workspace/Skills/skills_manifest.json for available skills.
"""

import os
from pathlib import Path
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from models import agent_llm
from prompts import minimal_personal_assistant_prompt
from middleware import shell_tool
from skill_middleware import SkillSelectorMiddleware, model_selector_middleware

# Get workspace directory - use env variable or default to repo workspace
# In deployment, this will be the workspace/ directory in the repo
# In local dev, can override with WORKSPACE_DIR env variable
workspace_dir = os.environ.get("WORKSPACE_DIR", str(Path(__file__).parent / "workspace"))

# Create Roscoe with dynamic skills architecture
# No hardcoded sub-agents - uses only built-in general-purpose sub-agent
# Skills are loaded dynamically via middleware based on user requests
# Models switch automatically based on skill requirements
personal_assistant_agent = create_deep_agent(
    system_prompt=minimal_personal_assistant_prompt,
    subagents=[],  # EMPTY - relies on built-in general-purpose sub-agent
    model=agent_llm,  # Default: Claude Sonnet 4.5 (switches per skill)
    backend=FilesystemBackend(root_dir=workspace_dir, virtual_mode=True),
    tools=[shell_tool],
    middleware=[
        # Skill selector runs first: semantic search + skill injection
        SkillSelectorMiddleware(
            skills_dir=f"{workspace_dir}/Skills",  # Uppercase to match actual directory
            max_skills=1,  # Load top 1 matching skill per request
            similarity_threshold=0.3  # Minimum similarity score (0-1)
        ),
        # Model selector runs second: reads skill metadata, switches model
        model_selector_middleware,
    ]
).with_config({"recursion_limit": 1000})