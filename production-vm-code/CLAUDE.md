# CLAUDE.md - Roscoe Production Deployment Guide

This file provides guidance to Claude when working with code in the production deployment.

## Production Environment

| Setting | Value |
|---------|-------|
| **VM** | `roscoe-paralegal-vm` (Google Cloud Compute Engine) |
| **Zone** | us-central1-a |
| **IP** | 34.63.223.97 |
| **Workspace** | GCS bucket `whaley_law_firm` mounted at `/mnt/workspace` via gcsfuse |
| **Container Orchestration** | Docker Compose (postgres, redis, roscoe, uploads, ui) |

## Project Overview

**Roscoe** is a LangGraph-based paralegal AI agent for personal injury litigation. It uses dynamic skills, automatic case context injection, and workflow-driven task management.

### Key Features

- **Dynamic Skills System**: Skills loaded semantically based on user requests
- **Case Context Injection**: Auto-loads case data when client names mentioned (fuzzy matching)
- **Workflow State Derivation**: Computes workflow progress from existing data
- **Docker Script Execution**: Python scripts run in isolated containers with GCS access
- **Multi-Model Support**: Configurable (Anthropic/OpenAI/Google) with fallback
- **Gmail/Calendar Integration**: Full Google Workspace integration via OAuth

---

## Directory Mapping: Local → Production

The project spans three directories locally that map to production paths:

| Local Path | Production Path | Purpose |
|------------|-----------------|---------|
| `/Volumes/X10 Pro/Roscoe/production-vm-code/` | `/home/aaronwhaley/roscoe/` | Agent source code |
| `/Volumes/X10 Pro/Roscoe/workspace_paralegal/` | `/mnt/workspace/` | GCS-backed workspace |
| `/Volumes/X10 Pro/Roscoe/Roscoe_runtime/` | `/mnt/workspace/` (merged) | Workflow engine |

### This Directory Structure (production-vm-code/)

```
production-vm-code/
├── src/roscoe/
│   ├── agents/paralegal/          # Main paralegal agent
│   │   ├── agent.py               # Agent definition
│   │   ├── models.py              # Model configuration
│   │   ├── prompts.py             # System prompts
│   │   ├── tools.py               # Built-in tools
│   │   ├── gmail_tools.py         # Gmail integration
│   │   ├── calendar_tools.py      # Calendar integration
│   │   ├── script_executor.py     # Docker script execution
│   │   └── sub_agents.py          # Multimodal sub-agent
│   │
│   ├── core/                      # Middleware & state computation
│   │   ├── case_context_middleware.py
│   │   ├── skill_middleware.py
│   │   └── workflow_state_computer.py
│   │
│   └── workflow_engine/           # State machine (production version)
│       ├── orchestrator/
│       │   └── state_machine.py   # 1700+ lines - core logic
│       ├── schemas/               # State schemas
│       └── _adapters/
│           └── case_data.py
│
├── ui/                            # Web UI (Next.js + assistant-ui)
│   ├── app/                       # Next.js app router
│   │   ├── page.tsx               # Main chat interface
│   │   ├── assistant.tsx          # Assistant-UI chat component
│   │   ├── workbench.tsx          # UI layout/workbench
│   │   ├── monaco-frame/          # Code editor integration
│   │   ├── calendar-frame/        # Calendar view integration
│   │   └── api/                   # API routes (LangGraph proxy)
│   ├── components/                # UI components (shadcn/ui)
│   ├── Dockerfile                 # Multi-stage build
│   └── package.json               # Node.js dependencies
│
├── docker-compose.yml             # Container orchestration
├── langgraph.json                 # LangGraph server config
├── pyproject.toml                 # Python dependencies
└── WORKFLOW_ENGINE_INTEGRATION.md # Workflow integration docs
```

### GCS Workspace Structure (/mnt/workspace/)

```
/mnt/workspace/                     # GCS bucket root (whaley_law_firm)
├── Database/                       # Centralized JSON database
│   ├── caselist.json              # Master case list
│   ├── case_overview.json         # Case summaries
│   ├── insurance.json             # Insurance claims
│   ├── liens.json                 # Medical liens
│   ├── notes.json                 # Case notes (28MB+)
│   ├── calendar.json              # Deadlines/tasks
│   └── script_execution_logs/     # Audit trail
│
├── Tools/                          # Executable Python scripts (60+)
│   ├── research/                  # Internet search
│   ├── medical_research/          # PubMed, Semantic Scholar
│   ├── legal_research/            # CourtListener (9 scripts)
│   ├── document_processing/       # PDF conversion
│   ├── document_generation/       # DOCX/PDF creation
│   └── [other categories...]
│
├── Skills/                         # Dynamic skill definitions
│   ├── skills_manifest.json       # Skill registry (26+ skills)
│   └── [skill directories...]
│
├── Prompts/                        # Context chunks
├── projects/                       # Case folders (20,000+ files)
├── forms/                          # Document templates
├── workflows/                      # Phase-specific workflows
└── workflow_engine/                # Workflow definitions
```

---

## Core Architecture

### Agent Definition (`src/roscoe/agents/paralegal/agent.py`)

```python
personal_assistant_agent = create_deep_agent(
    system_prompt=minimal_personal_assistant_prompt,
    subagents=[get_multimodal_sub_agent()],  # Gemini for audio/video/images
    model=get_agent_llm(),                    # Lazy-loaded model
    backend=FilesystemBackend(root_dir="/mnt/workspace", virtual_mode=True),
    tools=[
        send_slack_message, upload_file_to_slack,
        execute_python_script, execute_python_script_with_browser,
        render_ui_script, analyze_image,
        search_emails, get_email, send_email, create_draft, save_email_to_case,
        list_events, create_event, update_event, delete_event, find_free_time,
    ],
    middleware=[
        CaseContextMiddleware(...),
        SkillSelectorMiddleware(...),
    ],
).with_config({"recursion_limit": 500})
```

**Production Notes**:
- **No ShellToolMiddleware** (causes pickle errors with checkpointing)
- **Lazy model initialization** (avoids pickle errors with thread locks)
- **Virtual filesystem** (all paths relative to `/mnt/workspace`)

### Model Configuration (`src/roscoe/agents/paralegal/models.py`)

```python
MODEL_PROVIDER = "anthropic"  # Options: "anthropic", "openai", "google"

ENABLE_FALLBACK = True
FALLBACK_MODEL = "gemini-3-pro-preview"
```

| Provider | Model | Use Case |
|----------|-------|----------|
| `anthropic` | Claude Sonnet 4.5 | Default - best for legal reasoning |
| `openai` | GPT-5.1 Thinking | Extended reasoning tasks |
| `google` | Gemini 3 Pro | **Always** used for multimodal (audio/video/images) |

**Lazy Initialization** (required for production):
```python
# ❌ Don't use directly
agent_llm = None

# ✅ Use getter functions
get_agent_llm()        # Main agent
get_sub_agent_llm()    # Sub-agents
get_multimodal_llm()   # Always Gemini 3 Pro
```

### Middleware System

**CaseContextMiddleware** (`src/roscoe/core/case_context_middleware.py`):
1. Detects client names via fuzzy matching (80% threshold with `rapidfuzz`)
2. Loads case data from `/mnt/workspace/Database/`
3. Computes workflow state via `WorkflowStateComputer`
4. Injects formatted context into system prompt

**SkillSelectorMiddleware** (`src/roscoe/core/skill_middleware.py`):
1. Embeds skill descriptions using `sentence-transformers`
2. Computes cosine similarity (0.3 threshold)
3. Loads matching skill into system prompt

**WorkflowStateComputer** (`src/roscoe/core/workflow_state_computer.py`):
- Derives workflow state from data (no manual state tracking)
- Loads derivation rules from `/mnt/workspace/workflow_engine/`
- Returns current phase, progress, blockers, next actions

---

## Docker Script Execution

Scripts run in isolated Docker containers with GCS filesystem access.

### How It Works (`src/roscoe/agents/paralegal/script_executor.py`)

```python
execute_python_script(
    script_path="/Tools/research/internet_search.py",
    case_name="Smith-MVA-01-15-2024",
    script_args=["whiplash symptoms", "--max-results", "20"],
    timeout=300
)
```

**Under the hood**:
1. Spins up `roscoe-python-runner:latest` Docker container
2. Mounts `/mnt/workspace` at `/app/workspace_paralegal` (read-write)
3. Sets environment variables (API keys, case context)
4. Executes with resource limits (2GB RAM, 1 CPU)
5. Logs to `/mnt/workspace/Database/script_execution_logs/`

### Playwright Support

```python
execute_python_script_with_browser(
    script_path="/Tools/web_scraping/kyecourts_docket.py",
    script_args=["23-CI-00123"],
    timeout=600
)
```
Uses `roscoe-python-runner:playwright` image with Chromium.

---

## Production Deployment

### SSH to VM

```bash
gcloud compute ssh roscoe-paralegal-vm --zone us-central1-a
```

### Docker Services

```bash
# Start all services (postgres, redis, roscoe, uploads, ui)
docker compose up -d

# View logs
docker compose logs -f roscoe
docker compose logs -f ui

# Restart after code changes
docker compose restart roscoe  # Agent code changes
docker compose build ui && docker compose restart ui  # UI code changes

# Check status
docker ps
```

### Update Agent Code

```bash
# On VM
cd ~/roscoe
git pull origin main
docker compose restart roscoe
docker compose logs -f roscoe
```

### Update Tool (No Restart Needed)

```bash
# Edit tool directly on GCS mount
nano /mnt/workspace/Tools/category/tool_name.py

# Test
python /mnt/workspace/Tools/category/tool_name.py --help
```

### Update Skill (No Restart Needed)

```bash
# Edit skill
nano /mnt/workspace/Skills/skill-name/skill.md

# Update manifest
nano /mnt/workspace/Skills/skills_manifest.json
```

### Change Model Provider

Edit `src/roscoe/agents/paralegal/models.py`:
```python
MODEL_PROVIDER = "anthropic"  # or "openai" or "google"
```
Then: `docker compose restart roscoe`

---

## Environment Variables

Set in `/home/aaronwhaley/.env` on VM:

```bash
# LLM API Keys
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIza...

# Research APIs
TAVILY_API_KEY=tvly-...

# LangSmith (monitoring)
LANGSMITH_API_KEY=lsv2_pt_...
LANGCHAIN_TRACING_V2=true

# Slack Integration
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_DEFAULT_CHANNEL=#legal-updates

# Database
DATABASE_URI=postgres://postgres:postgres@postgres:5432/postgres
REDIS_URI=redis://redis:6379

# Workspace
WORKSPACE_ROOT=/mnt/workspace
WORKSPACE_DIR=/mnt/workspace

# Deployment flags
LANGGRAPH_DEPLOYMENT=true
LANGGRAPH_RECURSION_LIMIT=500
```

---

## Access URLs

| Service | URL |
|---------|-----|
| LangGraph API | http://34.63.223.97:8123 |
| Web UI (assistant-ui) | http://34.63.223.97:3001 |
| LangSmith | https://smith.langchain.com/projects/roscoe-local |

---

## Web UI (assistant-ui)

The web interface provides a modern chat-based interaction with Roscoe, built with Next.js and the [assistant-ui](https://github.com/Yonom/assistant-ui) library.

### Technology Stack

| Component | Technology |
|-----------|-----------|
| Framework | Next.js 16 (App Router) |
| UI Library | assistant-ui (LangGraph integration) |
| Styling | Tailwind CSS 4 + shadcn/ui |
| Code Editor | Monaco Editor (VS Code) |
| Runtime | React 19 |
| Container | Node.js 22 Alpine |

### Key Features

- **LangGraph Integration**: Direct connection to Roscoe via `@assistant-ui/react-langgraph`
- **Workspace Browser**: Read-only access to `/mnt/workspace` for viewing case files
- **Monaco Editor Frame**: Embedded code editor for viewing/editing scripts
- **Calendar Frame**: Integrated calendar view for case deadlines and events
- **Markdown Rendering**: Full support for rich text responses with code highlighting
- **Streaming Responses**: Real-time message streaming from LangGraph

### Docker Configuration

The UI runs as a containerized service in `docker-compose.yml`:

```yaml
ui:
  build:
    context: ./ui
    args:
      NEXT_PUBLIC_LANGGRAPH_API_URL: /api
      NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID: roscoe_paralegal
  ports:
    - 3001:3000
  environment:
    LANGGRAPH_API_URL: http://roscoe:8000
    WORKSPACE_ROOT: /mnt/workspace
  volumes:
    - /mnt/workspace:/mnt/workspace:ro
```

**Key Points**:
- Runs on port **3001** (container port 3000 mapped to host 3001)
- Uses **service DNS** (`http://roscoe:8000`) to communicate with LangGraph API
- Has **read-only** access to workspace for security
- Proxies LangGraph API through Next.js `/api` route to avoid CORS

### Development vs Production

| Environment | LangGraph URL | Port |
|-------------|---------------|------|
| **Production (VM)** | `http://roscoe:8000` (Docker network) | 3001 |
| **Local Development** | `http://localhost:8123` | 3000 |

### Updating UI

```bash
# On VM - rebuild and restart
cd ~/roscoe
docker compose build ui
docker compose restart ui
docker compose logs -f ui

# View build logs
docker compose logs ui | grep -A 20 "Building"
```

### File Browser API

The UI includes workspace browsing capabilities via Next.js API routes:

```typescript
// List directory contents
GET /api/workspace/list?path=/Database

// Read file contents
GET /api/workspace/file?path=/Database/caselist.json
```

These routes are protected by the container's read-only mount and only serve files from `/mnt/workspace`.

---

## Integrations

### Slack

- @mention in channels
- Direct messages
- Slash commands (`/roscoe`)
- File uploads
- Socket Mode Bridge runs inside `roscoe-agents` container

```python
send_slack_message("Analysis complete", "#case-updates", urgency="high")
upload_file_to_slack("/Reports/summary.md", "#case-updates")
```

### Gmail/Calendar

OAuth credentials: `/home/aaronwhaley/roscoe/credentials.json` + `token.json`

```python
# Email
search_emails("from:adjuster@insurance.com subject:settlement")
send_email("to@example.com", "Subject", "Body")

# Calendar
list_events(max_results=10)
create_event("SOL Deadline", "2025-12-31", all_day=True)
```

---

## Debugging

### Agent Not Responding

```bash
docker ps                          # Check container status
docker compose restart roscoe      # Restart
docker compose logs roscoe | tail -50  # Check logs
```

### Script Execution Failing

```bash
# Check logs
cat /mnt/workspace/Database/script_execution_logs/LATEST.json

# Test manually
docker run --rm \
  -v /mnt/workspace:/app/workspace_paralegal \
  -e TAVILY_API_KEY=$TAVILY_API_KEY \
  roscoe-python-runner:latest \
  python /app/workspace_paralegal/Tools/category/script.py --help
```

### Case Context Not Loading

```bash
# Verify caselist (80% fuzzy match threshold)
cat /mnt/workspace/Database/caselist.json | jq '.[] | select(.client_name | test("Smith"; "i"))'
```

### Skill Not Activating

```bash
# Check triggers (0.3 cosine similarity threshold)
cat /mnt/workspace/Skills/skills_manifest.json | jq '.skills[] | select(.name == "skill-name")'
```

### Database Access

```bash
# PostgreSQL (checkpointing)
docker exec -it roscoe-postgres psql -U postgres
SELECT * FROM threads;

# Redis (caching)
docker exec -it roscoe-redis redis-cli
```

### UI Not Loading

```bash
# Check container status
docker ps | grep roscoe-ui

# Check UI logs
docker compose logs ui | tail -50

# Rebuild and restart
docker compose build ui
docker compose restart ui

# Verify environment variables
docker exec roscoe-ui env | grep LANGGRAPH

# Test API proxy
curl http://localhost:3001/api/assistants
```

---

## Key Design Principles

1. **Zero-Code Extensibility**: Add tools/skills by editing files on GCS, no restart needed
2. **State Derivation**: Workflow state computed from data, not manually tracked
3. **Context Efficiency**: Only load relevant skills/case data per conversation
4. **Docker Isolation**: Scripts run in containers with resource limits
5. **GCS Persistence**: All workspace changes sync to cloud storage automatically
6. **Multi-Model Flexibility**: Switch models via config, automatic fallback on rate limits
7. **Audit Trail**: All script executions logged for compliance

---

## Quick Reference

| Task | Command/Location |
|------|------------------|
| SSH to VM | `gcloud compute ssh roscoe-paralegal-vm --zone us-central1-a` |
| View agent logs | `docker compose logs -f roscoe` |
| View UI logs | `docker compose logs -f ui` |
| Restart agent | `docker compose restart roscoe` |
| Restart UI | `docker compose build ui && docker compose restart ui` |
| Access Web UI | http://34.63.223.97:3001 |
| Edit agent code | `/home/aaronwhaley/roscoe/src/roscoe/agents/paralegal/` |
| Edit UI code | `/home/aaronwhaley/roscoe/ui/` |
| Edit tools | `/mnt/workspace/Tools/` |
| Edit skills | `/mnt/workspace/Skills/` |
| View case data | `/mnt/workspace/Database/` |
| Check script logs | `/mnt/workspace/Database/script_execution_logs/` |
