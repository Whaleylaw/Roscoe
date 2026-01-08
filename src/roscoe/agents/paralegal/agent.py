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
6. ShellToolMiddleware: Provides Glob, Grep, and shell access to LOCAL_WORKSPACE

Model Selection (via MODEL_PROVIDER environment variable):
- "anthropic" (default): Claude Sonnet 4.5
- "openai": GPT-5.1 Thinking
- "google": Gemini 3 Pro Preview

Research and other capabilities are handled through the skills system.
See workspace/Skills/skills_manifest.json for available skills.

Workspace Architecture:
- GCS_WORKSPACE (/mnt/workspace): Binary files (PDFs, images, audio, video)
- LOCAL_WORKSPACE (/app/workspace_local): Text files (synced from GCS)
- ShellToolMiddleware operates on LOCAL_WORKSPACE for fast file operations
"""

import os
from pathlib import Path
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import ShellToolMiddleware, HostExecutionPolicy

from roscoe.agents.paralegal.models import get_agent_llm, MODEL_PROVIDER
from roscoe.core.skill_middleware import SkillSelectorMiddleware, set_middleware_instance
from roscoe.core.case_context_middleware import CaseContextMiddleware
from roscoe.core.workflow_middleware import WorkflowMiddleware
from roscoe.core.ui_context_middleware import UIContextMiddleware
from roscoe.agents.paralegal.prompts import minimal_personal_assistant_prompt
from roscoe.agents.paralegal.sub_agents import get_multimodal_sub_agent
from roscoe.agents.paralegal.tools import (
    send_slack_message,
    upload_file_to_slack,
    # NOTE: execute_python_script tools removed - use ShellToolMiddleware instead
    list_skills,  # List all available skills with YAML descriptions
    refresh_skills,  # Rescan skills directory mid-session
    load_skill,  # Load a specific skill by name
    internet_search,  # Tavily web search for general research
    # File operations
    move_file,  # Move/rename files within workspace
    copy_file,  # Copy files within workspace
    display_document,  # Display document/artifact in UI canvas
    # Lob.com physical mail tools
    verify_address,  # Validate/standardize mailing addresses
    send_letter,  # Send letters via USPS
    send_certified_mail,  # Send certified mail with tracking
    send_postcard,  # Send postcards
    check_mail_status,  # Track mail delivery status
    list_sent_mail,  # List sent mail history
    # Knowledge graph tools (Direct Cypher)
    write_entity,  # Create entities and relationships using direct Cypher
    query_case_graph,  # Search episodes/notes with natural language (semantic search)
    get_case_structure,  # Get structured case data (parties, insurance, providers, status)
    graph_query,  # Direct Cypher queries for structural lookups
    get_workflow_resources,  # Query workflow definitions (phases, workflows, steps, skills)
    # Workflow state tools (deterministic graph-based state)
    get_case_workflow_status,  # Get formatted workflow state for a case
    update_landmark,  # Update landmark status (complete/in_progress/incomplete)
    advance_phase,  # Advance case to next phase (checks blockers)
    recalculate_case_phase,  # Analyze phase readiness (completion % + blockers)
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

# Local workspace for fast text file access (synced from GCS)
# ShellToolMiddleware will point here for fast Glob/Grep operations
local_workspace_dir = os.environ.get("LOCAL_WORKSPACE", "/home/aaronwhaley/workspace_local")

# Check if we're in production (LangGraph server with checkpointing)
# NOTE: ShellToolMiddleware is now enabled - it provides Glob, Grep, and shell access
# to LOCAL_WORKSPACE for fast text file operations
is_production = os.environ.get("LANGGRAPH_DEPLOYMENT", "false").lower() == "true"

# Create middleware instances (so tools can access them)
# Case context middleware: detects client mentions, loads case data
case_context_middleware = CaseContextMiddleware(
    workspace_dir=workspace_dir,
    fuzzy_threshold=80,  # Minimum fuzzy match score (0-100)
    max_cases=2,  # Support up to 2 cases mentioned in same query
)

# Workflow middleware: computes workflow state from case data, injects guidance
# Runs AFTER case context to use detected_cases, provides next actions with resource paths
workflow_middleware = WorkflowMiddleware(
    workspace_dir=workspace_dir,  # Uses workspace/workflow_engine/schemas/ for rules
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
        # NOTE: execute_python_script tools removed - ShellToolMiddleware provides shell access
        # File operations
        move_file,  # Move/rename files within workspace
        copy_file,  # Copy files within workspace
        display_document,  # Display document/artifact in UI canvas (right panel)
        # Lob.com physical mail tools
        verify_address,  # Validate/standardize mailing addresses before sending
        send_letter,  # Send letters via USPS (demand letters, notices)
        send_certified_mail,  # Send certified mail with tracking + return receipt
        send_postcard,  # Send postcards (reminders)
        check_mail_status,  # Track mail delivery status
        list_sent_mail,  # List sent mail history by case/type
        # Research tools
        internet_search,  # Tavily web search - use for any web research needs
        # Skills discovery tools
        list_skills,  # List all available skills with YAML descriptions
        refresh_skills,  # Rescan skills directory mid-session
        load_skill,  # Load a specific skill by name
        # Knowledge graph tools (Direct Cypher)
        write_entity,  # Create entities and relationships (universal write tool)
        query_case_graph,  # Search episodes/notes with natural language (semantic search)
        get_case_structure,  # Get structured case data (parties, insurance, providers, status)
        graph_query,  # Direct Cypher queries (cases_by_provider, provider_stats, custom_cypher)
        get_workflow_resources,  # Query workflow structure (phases, workflows, steps, skills, templates)
        # Workflow state tools (deterministic graph-based)
        get_case_workflow_status,  # Get formatted workflow state for a case
        update_landmark,  # Update landmark status (complete/in_progress/incomplete)
        advance_phase,  # Advance case to next phase (checks blockers)
        recalculate_case_phase,  # Analyze phase readiness (completion % + blockers)
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
        # NOTE: create_deep_agent adds its own SummarizationMiddleware internally.
        # It triggers at 85% of model's max_input_tokens (~850k for Gemini).
        # We can't override it without switching to create_agent (bigger change).
        # If hitting rate limits, consider switching models or using create_agent.

        # Case context injection: detects client mentions, loads case data
        case_context_middleware,
        # Workflow orchestration: computes workflow state, injects guidance with resource paths
        workflow_middleware,
        # Skill selector: semantic search + skill injection (scans SKILL.md files)
        skill_selector_middleware,
        # UI context: bridges CopilotKit UI state to agent (open documents, workspace location)
        UIContextMiddleware(),
        # Shell tool: provides Glob, Grep, and shell commands for LOCAL_WORKSPACE
        # Points to local SSD for fast text file operations (synced from GCS)
        ShellToolMiddleware(
            workspace_root=local_workspace_dir,
            execution_policy=HostExecutionPolicy(),
        ),
    ],
    checkpointer=False if not is_production else None,  # Let server handle checkpointing in production
).with_config({"recursion_limit": 500})

# Start Slack Socket-Mode bridge inside the container if configured
ensure_bridge_started()
