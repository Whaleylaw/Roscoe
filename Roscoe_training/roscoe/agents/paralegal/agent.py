"""
Roscoe - Dynamic Skills-Based Paralegal AI Agent

This agent uses a dynamic skills architecture:
- Skills are loaded automatically based on semantic matching to user requests
- Case context is automatically injected when client names are mentioned
- Phase-driven workflow management with proactive suggestions
- Specialized sub-agent for multimodal analysis (images/audio/video)
- Unlimited skills can be added to /workspace/Skills/ without code changes

Architecture:
1. SummarizationMiddleware: Compress conversation history when approaching token limits
2. CaseContextMiddleware: Detects client/case mentions, injects case context
3. WorkflowMiddleware: Injects workflow status, suggests next actions based on phase
4. SkillSelectorMiddleware: Semantic search to find relevant skills
5. Custom sub-agent: multimodal-agent (inherits model from MODEL_PROVIDER)
6. General-purpose sub-agent: Built-in, inherits main agent model

Workflow Engine:
- Phases: Intake → Treatment → Demand → Negotiation → Settlement/Litigation
- Workflows: Operational procedures tied to each phase
- Skills: Atomic capabilities used by workflows
- Agent asks: "Where are we? What needs to be done? What's next?"

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
from langchain.agents.middleware import ShellToolMiddleware, HostExecutionPolicy, SummarizationMiddleware

from roscoe.agents.paralegal.models import get_agent_llm, get_summarization_llm, MODEL_PROVIDER
from roscoe.core.skill_middleware import SkillSelectorMiddleware
from roscoe.core.case_context_middleware import CaseContextMiddleware
from roscoe.core.workflow_middleware import WorkflowMiddleware
from roscoe.agents.paralegal.prompts import minimal_personal_assistant_prompt
from roscoe.agents.paralegal.sub_agents import multimodal_sub_agent
from roscoe.agents.paralegal.tools import (
    send_slack_message,
    upload_file_to_slack,
    execute_python_script,  # Docker-based script execution with GCS access
    execute_python_script_with_browser,  # Playwright browser automation
    render_ui_script,  # Universal UI script executor for case dashboards, etc.
    # NOTE: generate_ui, generate_artifact (Thesys C1) removed - use render_ui_script
    # NOTE: internet_search, analyze_image, analyze_audio, analyze_video
    # are now Python scripts in Tools/ executed via execute_python_script
)
from roscoe.slack_launcher import ensure_bridge_started

# Get path to skills manifest (in src/, packaged with code)
MANIFEST_PATH = Path(__file__).parent / "skills_manifest.json"

# Get paths for workflow engine manifests
PHASES_MANIFEST_PATH = Path(__file__).parent / "phases_manifest.json"
WORKFLOWS_MANIFEST_PATH = Path(__file__).parent / "workflows_manifest.json"

# Get workspace directory - use env variable or default to GCS mount
# In production (GCE VM): /mnt/workspace (gcsfuse mount of whaley_law_firm bucket)
# In local dev: Override with WORKSPACE_DIR env variable
workspace_dir = os.environ.get("WORKSPACE_DIR", "/mnt/workspace")

# ============================================================================
# SUMMARIZATION PROMPT FOR LEGAL/PARALEGAL WORK
# Custom prompt to ensure summaries preserve legally relevant information
# ============================================================================
LEGAL_SUMMARY_PROMPT = """You are summarizing a conversation between an attorney/paralegal and an AI legal assistant.

Create a concise summary that preserves:
1. **Case Information**: Client names, case numbers, opposing parties, key dates
2. **Medical Details**: Injuries, treatments, providers, diagnoses, prognosis
3. **Financial Data**: Damages, medical bills, liens, settlement amounts, insurance limits
4. **Legal Strategy**: Case theories, arguments, deadlines, next steps
5. **Document References**: Specific files, reports, or evidence discussed
6. **Action Items**: Tasks assigned, deadlines set, follow-ups needed
7. **Key Findings**: Important discoveries, red flags, inconsistencies identified

IMPORTANT: Do NOT summarize tool calls and their raw outputs - focus on the substantive conversation content and conclusions reached. Preserve exact figures, dates, and names - do not generalize these.

Conversation to summarize:
{messages}

Summary:"""

# Check if we're in production (LangGraph server with checkpointing)
# Shell tool can't be used with checkpointing due to pickle issues
is_production = os.environ.get("LANGGRAPH_DEPLOYMENT", "false").lower() == "true"

# Create Roscoe with dynamic skills architecture
# Model determined by MODEL_PROVIDER env var (default: anthropic = Claude Sonnet 4.5)
# Custom sub-agent for specialized tasks:
# - multimodal-agent: Uses same model provider for images/audio/video analysis
# Research and other capabilities handled through skills system (see workspace/Skills/)
personal_assistant_agent = create_deep_agent(
    system_prompt=minimal_personal_assistant_prompt,
    subagents=[
        multimodal_sub_agent,  # Multimodal analysis (model from MODEL_PROVIDER)
    ],
    model=get_agent_llm(),  # Model determined by MODEL_PROVIDER (see models.py) - lazily initialized
    backend=FilesystemBackend(root_dir=workspace_dir, virtual_mode=True),
    tools=[
        send_slack_message,
        upload_file_to_slack,
        execute_python_script,  # Docker-based script execution with GCS filesystem access
        execute_python_script_with_browser,  # Playwright browser automation for web scraping
        render_ui_script,  # Universal UI script executor (case dashboards, insurance, liens, etc.)
    ],
    middleware=[
        # Summarization: Compress conversation history when approaching token limits
        # Triggers at 170k tokens to stay safely under Claude's 200k context limit
        # Uses Claude Haiku for fast, cost-effective summarization
        SummarizationMiddleware(
            model=get_summarization_llm(),  # Claude Haiku 4.5 - fast and cheap
            trigger=("tokens", 170000),  # Trigger at 170k tokens (30k buffer before 200k limit)
            keep=("messages", 20),  # Keep the 20 most recent messages intact
            summary_prompt=LEGAL_SUMMARY_PROMPT,  # Custom legal-focused summary prompt
            trim_tokens_to_summarize=50000,  # Max tokens to include when generating summary
        ),
        # Case context injection: detects client mentions, loads case data
        CaseContextMiddleware(
            workspace_dir=workspace_dir,
            fuzzy_threshold=80,  # Minimum fuzzy match score (0-100)
            max_cases=2,  # Support up to 2 cases mentioned in same query
        ),
        # Workflow orchestration: injects workflow status and suggestions
        # Runs after CaseContextMiddleware (depends on detected_cases in state)
        WorkflowMiddleware(
            workspace_dir=workspace_dir,
            phases_manifest_path=str(PHASES_MANIFEST_PATH),
            workflows_manifest_path=str(WORKFLOWS_MANIFEST_PATH),
        ),
        # Skill selector: semantic search + skill injection
        SkillSelectorMiddleware(
            manifest_path=str(MANIFEST_PATH),  # Manifest in src/ (code)
            skills_dir=f"{workspace_dir}/Skills",  # Skills markdown in workspace (runtime)
            max_skills=1,  # Load top 1 matching skill per request
            similarity_threshold=0.3  # Minimum similarity score (0-1)
        ),
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
