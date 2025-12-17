# CLAUDE.md - Roscoe Project Guide

This file provides guidance to Claude when working with code in the Roscoe project.

## Project Overview

**Roscoe** is a LangGraph-based paralegal AI agent for personal injury litigation. It uses dynamic skills, automatic case context injection, and workflow-driven task management.

## Directory Structure

The project spans **three main directories**:

```
/Volumes/X10 Pro/Roscoe/
├── local-dev-code/          # This directory - LOCAL DEVELOPMENT SOURCE CODE
├── production-vm-code/      # Production-ready code (synced to GCP VM)
├── Roscoe_runtime/          # Workflow engine definitions & state machine
└── workspace_paralegal/     # Live workspace data (syncs to GCS bucket)
```

---

## 1. local-dev-code/ (This Directory)

**Purpose**: Local development and testing of the Roscoe agent.

```
local-dev-code/
├── src/roscoe/
│   ├── agents/paralegal/     # Main paralegal agent
│   │   ├── agent.py          # Agent definition (create_deep_agent)
│   │   ├── models.py         # Model configuration (Claude/GPT/Gemini)
│   │   ├── prompts.py        # System prompts
│   │   ├── tools.py          # Built-in tools (Slack, script execution)
│   │   ├── gmail_tools.py    # Gmail integration
│   │   ├── calendar_tools.py # Google Calendar integration
│   │   ├── script_executor.py # Docker script execution
│   │   └── sub_agents.py     # Multimodal sub-agent
│   │
│   └── core/                 # Middleware & state computation
│       ├── case_context_middleware.py  # Auto-loads case data
│       ├── skill_middleware.py         # Semantic skill selection
│       └── workflow_state_computer.py  # Derives workflow state
│
├── langgraph.json           # LangGraph server config
├── pyproject.toml           # Python dependencies
├── docker/                  # Docker images for script execution
└── deploy-to-vm.sh          # Deployment script
```

**Run locally**:
```bash
cd "/Volumes/X10 Pro/Roscoe/local-dev-code"
langgraph dev  # Runs on http://localhost:2024
```

---

## 2. production-vm-code/

**Purpose**: Production-ready code deployed to Google Cloud VM.

**Deployment**: `roscoe-paralegal-vm` on GCP (us-central1-a, IP: 34.63.223.97)

Structure is identical to `local-dev-code/` with additional:
- `docker-compose.yml` - Container orchestration
- Production-specific configurations
- Additional workflow engine components

**Deploy changes**:
```bash
# From local-dev-code
./deploy-to-vm.sh

# Or manually SSH to VM
gcloud compute ssh roscoe-paralegal-vm --zone us-central1-a
cd ~/roscoe && git pull
docker compose restart roscoe
```

---

## 3. Roscoe_runtime/

**Purpose**: Workflow engine definitions, phase workflows, and runtime state.

```
Roscoe_runtime/
├── workflow_engine/
│   ├── orchestrator/
│   │   └── state_machine.py       # Core state machine logic
│   ├── schemas/
│   │   ├── case_state.schema.json # Master case state schema
│   │   ├── phase_definitions.json # Phase entry/exit criteria
│   │   ├── workflow_definitions.json # Workflow step definitions
│   │   └── derivation_rules.json  # How to compute state from data
│   ├── templates/
│   │   ├── new_case_state.json    # Template for new cases
│   │   └── response_templates.md  # Agent response patterns
│   └── _adapters/
│       └── case_data.py           # Data access adapter
│
├── workflows/                      # Phase-specific workflows
│   ├── phase_0_onboarding/
│   ├── phase_1_file_setup/
│   ├── phase_2_treatment/
│   ├── phase_3_demand/
│   ├── phase_4_negotiation/
│   ├── phase_5_settlement/
│   ├── phase_6_lien/
│   ├── phase_7_litigation/        # 174 files - discovery, depositions, trial
│   ├── phase_8_closed/
│   ├── skills/                    # Phase-specific skills (149 .md files)
│   ├── templates/                 # Document templates (68 .md files)
│   └── tools/                     # Workflow-specific tools
│
├── Tools/
│   └── document_generation/       # PDF/DOCX generation
│
└── Database/                      # Runtime state files (903 .state files)
```

**Key Concept**: The workflow engine tracks case progression through 9 phases with clear entry/exit criteria. State is **derived from data**, not manually tracked.

---

## 4. workspace_paralegal/

**Purpose**: Live workspace data - case files, tools, skills, forms. Syncs to GCS bucket (`whaley_law_firm`) in production.

```
workspace_paralegal/
├── Database/                       # Centralized JSON database
│   ├── caselist.json              # Master case list (fuzzy search index)
│   ├── case_overview.json         # Case summaries
│   ├── insurance.json             # Insurance claims data
│   ├── liens.json                 # Medical liens
│   ├── medical_providers.json     # Provider info
│   ├── notes.json                 # Case notes (28MB+)
│   ├── calendar.json              # Deadlines/tasks
│   └── script_execution_logs/     # Audit trail
│
├── Tools/                          # Executable Python scripts (60+)
│   ├── research/                  # Internet search (Tavily)
│   ├── medical_research/          # PubMed, Semantic Scholar
│   ├── legal_research/            # CourtListener (9 scripts)
│   ├── document_processing/       # PDF conversion, OCR
│   ├── document_generation/       # DOCX/PDF creation
│   ├── calendar/                  # Google Calendar tools
│   ├── insurance/                 # PIP waterfall analysis
│   ├── settlement/                # Settlement calculations
│   ├── UI/                        # Dashboard generators
│   ├── web_scraping/              # Court docket scrapers
│   └── _adapters/                 # Data adapters (CaseData)
│
├── Skills/                         # Dynamic skill definitions
│   ├── skills_manifest.json       # Skill registry (26+ skills)
│   ├── medical-records-analysis/  # 5-phase medical workflow
│   ├── police-report-analysis/    # KY police reports
│   ├── courtlistener-legal-research/
│   ├── case-file-organization/    # 8-bucket system
│   ├── document-docx/             # Word document handling
│   ├── document-pdf/              # PDF processing
│   ├── demand-letter-generation/  # Settlement demands
│   ├── litigation-discovery/      # Discovery skills (11 files)
│   ├── litigation-depositions/    # Deposition skills (10 files)
│   └── sub-agents/                # Sub-skill definitions
│
├── Prompts/                        # Context chunks (loaded semantically)
│   ├── chunks_manifest.json
│   ├── calendar_management.md
│   ├── notes_recording.md
│   └── slack_communication.md
│
├── projects/                       # Case folders (20,000+ files)
│   └── [ClientName-Type-Date]/
│       ├── Case_Information/
│       ├── Client/
│       ├── Investigation/
│       ├── Medical_Records/
│       ├── Medical_Bills/
│       ├── Insurance/
│       ├── Lien/
│       ├── Expenses/
│       ├── Negotiation_Settlement/
│       └── Litigation/
│
├── forms/                          # Document templates
│   ├── complaints/                # 33 complaint templates
│   ├── discovery/                 # 57 discovery templates
│   ├── motions/                   # 28 motion templates
│   └── liens/                     # Lien forms
│
├── workflows/                      # Same as Roscoe_runtime/workflows
└── workflow_engine/                # Same as Roscoe_runtime/workflow_engine
```

---

## Core Architecture

### Agent Structure

```python
personal_assistant_agent = create_deep_agent(
    system_prompt=minimal_personal_assistant_prompt,
    subagents=[get_multimodal_sub_agent()],  # Gemini for audio/video/images
    model=get_agent_llm(),                    # Lazy-loaded (Claude/GPT/Gemini)
    backend=FilesystemBackend(root_dir=WORKSPACE_ROOT, virtual_mode=True),
    tools=[
        send_slack_message, upload_file_to_slack,
        execute_python_script, execute_python_script_with_browser,
        render_ui_script, analyze_image,
        # Gmail tools
        search_emails, get_email, send_email, create_draft, save_email_to_case,
        # Calendar tools
        list_events, create_event, update_event, delete_event, find_free_time,
    ],
    middleware=[
        CaseContextMiddleware(...),    # Auto-loads case data when names mentioned
        SkillSelectorMiddleware(...),  # Semantic skill selection
    ],
).with_config({"recursion_limit": 500})
```

### Model Configuration (`models.py`)

```python
MODEL_PROVIDER = "anthropic"  # Options: "anthropic", "openai", "google"

# Use getter functions (lazy initialization for pickle compatibility)
get_agent_llm()        # Main agent model
get_sub_agent_llm()    # Sub-agents
get_multimodal_llm()   # Always Gemini 3 Pro for audio/video/images
```

### Middleware System

1. **CaseContextMiddleware** (`core/case_context_middleware.py`)
   - Detects client names via fuzzy matching (80% threshold)
   - Loads case data from `Database/*.json`
   - Computes workflow state via `WorkflowStateComputer`
   - Injects context into system prompt

2. **SkillSelectorMiddleware** (`core/skill_middleware.py`)
   - Embeds skill descriptions using `sentence-transformers`
   - Computes cosine similarity (0.3 threshold)
   - Loads matching skill into system prompt

3. **WorkflowStateComputer** (`core/workflow_state_computer.py`)
   - Derives workflow state from existing data (no manual tracking)
   - Identifies blockers (external waits, user actions)
   - Suggests next actions with linked skills/tools

---

## Tools Architecture

**Key innovation**: Tools are NOT loaded into agent context. They're discovered dynamically and executed via Docker.

### Tool Execution Flow

```
1. Agent reads /Tools/tools_manifest.json
2. Agent calls: execute_python_script("/Tools/research/internet_search.py", ["query"])
3. Script runs in Docker container with workspace access
4. Results output to stdout (JSON)
5. Execution logged to /Database/script_execution_logs/
```

### Tool Template

```python
#!/usr/bin/env python3
"""Tool Name - One-line description"""
import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Tool description")
    parser.add_argument("query", help="Query string")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    
    result = do_work(args.query)
    print(json.dumps(result, indent=2 if args.pretty else None))
    sys.exit(0 if result.get("success") else 1)

if __name__ == "__main__":
    main()
```

---

## Skills System

Skills are loaded semantically based on user requests. Add new skills without code changes.

### Skill Manifest Entry

```json
{
  "name": "skill-name",
  "description": "Use when [trigger scenarios]",
  "file": "skill-name/skill.md",
  "triggers": ["keyword1", "keyword2"],
  "model_required": "sonnet",
  "canonical_phase": "file_setup",
  "tools_required": ["/Tools/tool.py"],
  "output_location": "/Reports/output.md"
}
```

### Key Skills

| Skill | Triggers | Purpose |
|-------|----------|---------|
| `medical-records-analysis` | "medical records", "case review" | 5-phase medical workflow |
| `police-report-analysis` | "police report", "crash report" | KY report extraction |
| `courtlistener-legal-research` | "case law", "precedent" | Legal research via CourtListener |
| `case-file-organization` | "organize files" | 8-bucket filing system |
| `document-docx` | "word document", "tracked changes" | DOCX creation/editing |
| `demand-letter-generation` | "demand letter", "settlement demand" | Complete demand package |

---

## Workflow Engine

### Phases (in order)

1. **File Setup** - Initial case setup, documents, insurance claims
2. **Treatment** - Monitoring medical care, gathering records
3. **Demand in Progress** - Assembling and sending demand
4. **Negotiation** - Back and forth with insurance
5. **Settlement** - Finalizing settlement, distribution
6. **Lien Phase** - Resolving outstanding liens
7. **Litigation** - Filing suit through trial
8. **Closed** - Case complete

### State Derivation

State is **computed from data**, not manually tracked:

```python
# WorkflowStateComputer reads:
# - Database/*.json files
# - Case folder contents
# - workflow_engine/schemas/*.json

# Returns:
{
  "current_phase": "treatment",
  "phase_progress": 0.6,
  "completed": ["intake", "accident_report", "bi_claim_opened"],
  "waiting_on": [
    {"item": "medical records", "provider": "Baptist Health", "requested": "2024-01-15"}
  ],
  "blockers": ["Cannot proceed to demand until treatment complete"],
  "next_actions": ["Follow up on medical records request"]
}
```

---

## Common Development Tasks

### Add/Update a Tool

```bash
# 1. Create script
workspace_paralegal/Tools/category/tool_name.py

# 2. Update manifest (optional - agent discovers tools)
workspace_paralegal/Tools/_adapters/tools_manifest.json

# 3. Test locally
python workspace_paralegal/Tools/category/tool_name.py --help
python workspace_paralegal/Tools/category/tool_name.py "test" --pretty

# No deployment needed - changes are immediate
```

### Add/Update a Skill

```bash
# 1. Create skill file
workspace_paralegal/Skills/skill-name/skill.md

# 2. Update manifest
workspace_paralegal/Skills/skills_manifest.json

# No code changes or deployment needed
```

### Add/Update a Workflow

```bash
# 1. Edit workflow definition
Roscoe_runtime/workflows/phase_N_name/workflow.md

# 2. Update schema if needed
Roscoe_runtime/workflow_engine/schemas/workflow_definitions.json

# No deployment needed for workflow content changes
```

### Update Agent Code

```bash
# 1. Edit code locally
local-dev-code/src/roscoe/agents/paralegal/agent.py

# 2. Test locally
cd local-dev-code && langgraph dev

# 3. Deploy to production
./deploy-to-vm.sh
# OR copy to production-vm-code and push to VM
```

---

## Environment Variables

Create `.env` from `.env.example`:

```bash
# LLM API Keys
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIza...

# Research APIs
TAVILY_API_KEY=tvly-...

# Slack Integration
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# LangSmith (monitoring)
LANGSMITH_API_KEY=lsv2_pt_...
LANGCHAIN_TRACING_V2=true

# Workspace paths
WORKSPACE_ROOT=/Volumes/X10 Pro/Roscoe/workspace_paralegal
```

---

## Key Design Principles

1. **Zero-Code Extensibility**: Add tools/skills by editing files, no deployment
2. **State Derivation**: Workflow state computed from data, not manually tracked
3. **Context Efficiency**: Only load relevant skills/case data per conversation
4. **Docker Isolation**: Scripts run in containers with resource limits
5. **Multi-Model Flexibility**: Switch models via config, fallback on rate limits
6. **Audit Trail**: All script executions logged for compliance

---

## Quick Reference

| Task | Location |
|------|----------|
| Edit agent logic | `local-dev-code/src/roscoe/agents/paralegal/` |
| Edit middleware | `local-dev-code/src/roscoe/core/` |
| Add/edit tools | `workspace_paralegal/Tools/` |
| Add/edit skills | `workspace_paralegal/Skills/` |
| Edit workflows | `Roscoe_runtime/workflows/` |
| Edit workflow schemas | `Roscoe_runtime/workflow_engine/schemas/` |
| View case data | `workspace_paralegal/Database/` |
| View form templates | `workspace_paralegal/forms/` |

---

## Debugging

### Agent not responding
```bash
docker compose logs roscoe | tail -50
docker compose restart roscoe
```

### Script execution failing
```bash
# Check logs
cat workspace_paralegal/Database/script_execution_logs/LATEST.json

# Test manually
python workspace_paralegal/Tools/category/script.py --help
```

### Skill not activating
```bash
# Check triggers in manifest (threshold is 0.3 cosine similarity)
cat workspace_paralegal/Skills/skills_manifest.json | jq '.skills[] | select(.name == "skill-name")'
```

### Case context not loading
```bash
# Verify caselist (threshold is 80% fuzzy match)
cat workspace_paralegal/Database/caselist.json | jq '.[] | select(.client_name | test("Smith"; "i"))'
```
