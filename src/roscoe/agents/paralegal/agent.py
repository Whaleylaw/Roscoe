"""
Roscoe - Dynamic Skills-Based Paralegal AI Agent

This agent uses a dynamic skills architecture:
- Skills are loaded automatically based on semantic matching to user requests
- Case context is automatically injected when client names are mentioned
- Specialized sub-agent for multimodal analysis (images/audio/video)
- Unlimited skills can be added to /workspace/Skills/ without code changes

Architecture:
1. CaseContextMiddleware: Detects client/case mentions, injects case context
2. SkillSelectorMiddleware: Semantic search to find relevant skills
3. Skills injection: Relevant skills loaded into system prompt
4. Custom sub-agent: multimodal-agent (inherits model from MODEL_PROVIDER)
5. General-purpose sub-agent: Built-in, inherits main agent model

Model Selection (via MODEL_PROVIDER environment variable):
- "anthropic" (default): Claude Sonnet 4.5
- "openai": GPT-5.1 Thinking
- "google": Gemini 3 Pro Preview

Research and other capabilities are handled through the skills system.
See workspace/Skills/skills_manifest.json for available skills.

Script Execution:
- Docker-based script execution with direct GCS filesystem access
- Scripts in /Tools/ run in isolated containers with read-write access
- Playwright browser automation available for web scraping
"""

import os
from pathlib import Path
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import ShellToolMiddleware, HostExecutionPolicy

from roscoe.agents.paralegal.models import get_agent_llm, MODEL_PROVIDER
from roscoe.core.skill_middleware import SkillSelectorMiddleware, set_middleware_instance
from roscoe.core.case_context_middleware import CaseContextMiddleware
from roscoe.agents.paralegal.prompts import minimal_personal_assistant_prompt
from roscoe.agents.paralegal.sub_agents import get_multimodal_sub_agent
from roscoe.agents.paralegal.tools import (
    send_slack_message,
    upload_file_to_slack,
    execute_python_script,  # Docker-based script execution with GCS access
    execute_python_script_with_browser,  # Playwright browser automation
    render_ui_script,  # Universal UI script executor for case dashboards, etc.
    list_skills,  # List all available skills with YAML descriptions
    refresh_skills,  # Rescan skills directory mid-session
    load_skill,  # Load a specific skill by name
    # NOTE: generate_ui, generate_artifact (Thesys C1) removed - use render_ui_script
    # NOTE: internet_search, analyze_image, analyze_audio, analyze_video
    # are now Python scripts in Tools/ executed via execute_python_script
)
# Gmail tools for email management (requires Google OAuth credentials)
from roscoe.agents.paralegal.gmail_tools import (
    search_emails,
    get_email,
    send_email,
    create_draft,
    get_thread,
    list_labels,
    save_email_to_case,
    save_emails_batch,
)
# Google Calendar tools for scheduling (requires Google OAuth credentials)
from roscoe.agents.paralegal.calendar_tools import (
    list_events,
    create_event,
    update_event,
    delete_event,
    find_free_time,
    get_event,
)
from roscoe.slack_launcher import ensure_bridge_started

# Get path to skills manifest (in src/, packaged with code)
MANIFEST_PATH = Path(__file__).parent / "skills_manifest.json"

# Get workspace directory - use env variable or default to GCS mount
# In production (GCE VM): /mnt/workspace (gcsfuse mount of whaley_law_firm bucket)
# In local dev: Override with WORKSPACE_DIR env variable
workspace_dir = os.environ.get("WORKSPACE_DIR", "/mnt/workspace")

# Check if we're in production (LangGraph server with checkpointing)
# Shell tool can't be used with checkpointing due to pickle issues
is_production = os.environ.get("LANGGRAPH_DEPLOYMENT", "false").lower() == "true"

# Create middleware instances (so tools can access them)
# Case context middleware: detects client mentions, loads case data
case_context_middleware = CaseContextMiddleware(
    workspace_dir=workspace_dir,
    fuzzy_threshold=80,  # Minimum fuzzy match score (0-100)
    max_cases=2,  # Support up to 2 cases mentioned in same query
)

# Skill selector middleware: scans SKILL.md files, semantic search + skill injection
# Now reads from YAML frontmatter in SKILL.md files (per Anthropic Agent Skills Spec)
skill_selector_middleware = SkillSelectorMiddleware(
    skills_dir=f"{workspace_dir}/Skills",  # Skills in workspace (runtime)
    max_skills=1,  # Load top 1 matching skill per request
    similarity_threshold=0.3  # Minimum similarity score (0-1)
)

# Set the middleware instance globally so tools (list_skills, load_skill) can access it
set_middleware_instance(skill_selector_middleware)

# Create Roscoe with dynamic skills architecture
# Model determined by MODEL_PROVIDER env var (default: anthropic = Claude Sonnet 4.5)
# Custom sub-agent for specialized tasks:
# - multimodal-agent: Uses same model provider for images/audio/video analysis
# Research and other capabilities handled through skills system (see workspace/Skills/)
personal_assistant_agent = create_deep_agent(
    system_prompt=minimal_personal_assistant_prompt,
    subagents=[
        get_multimodal_sub_agent(),  # Multimodal analysis (model from MODEL_PROVIDER)
    ],
    model=get_agent_llm(),  # Model determined by MODEL_PROVIDER (see models.py) - lazily initialized
    backend=FilesystemBackend(root_dir=workspace_dir, virtual_mode=True),
    tools=[
        send_slack_message,
        upload_file_to_slack,
        execute_python_script,  # Docker-based script execution with GCS filesystem access
        execute_python_script_with_browser,  # Playwright browser automation for web scraping
        render_ui_script,  # Universal UI script executor (case dashboards, insurance, liens, etc.)
        # Skills discovery tools
        list_skills,  # List all available skills with YAML descriptions
        refresh_skills,  # Rescan skills directory mid-session
        load_skill,  # Load a specific skill by name
        # Gmail tools (requires GOOGLE_CREDENTIALS_FILE env var)
        search_emails,
        get_email,
        send_email,
        create_draft,
        get_thread,
        list_labels,
        save_email_to_case,  # Save complete .eml + attachments to case folder
        save_emails_batch,   # Batch save multiple emails to case folder
        # Google Calendar tools (requires GOOGLE_CREDENTIALS_FILE env var)
        list_events,
        create_event,
        update_event,
        delete_event,
        find_free_time,
        get_event,
    ],
    middleware=[
        # NOTE: Do NOT add SummarizationMiddleware here - create_deep_agent already adds one!
        # Adding another causes "duplicate middleware instances" error.
        # The framework's default SummarizationMiddleware is configured appropriately.
        
        # Case context injection: detects client mentions, loads case data
        case_context_middleware,
        # Skill selector: semantic search + skill injection (scans SKILL.md files)
        skill_selector_middleware,
    ],
    # DISABLED: ShellToolMiddleware causes pickle errors with LangGraph checkpointing
    # The middleware below was causing TypeError: cannot pickle '_thread.lock' object
    # because LANGGRAPH_DEPLOYMENT env var was not set, making is_production=False
    # Uncomment for local dev testing only:
    # + ([] if is_production else [
    #     ShellToolMiddleware(
    #         workspace_root=workspace_dir,
    #         execution_policy=HostExecutionPolicy(),
    #     ),
    # ]),
    checkpointer=False if not is_production else None,  # Let server handle checkpointing in production
).with_config({"recursion_limit": 500})

# Start Slack Socket-Mode bridge inside the container if configured
ensure_bridge_started()
