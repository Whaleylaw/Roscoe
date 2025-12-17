# CLAUDE.md - Roscoe Production Deployment Guide

This file provides guidance to Claude when working with code in the production deployment.

## Production Environment

| Setting | Value |
|---------|-------|
| **VM** | `roscoe-paralegal-vm` (Google Cloud Compute Engine) |
| **Zone** | us-central1-a |
| **IP** | 34.63.223.97 |
| **Workspace** | GCS bucket `whaley_law_firm` mounted at `/mnt/workspace` via gcsfuse |
| **Container Orchestration** | Docker Compose (postgres, redis, roscoe, copilotkit, uploads, ui) |

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
├── ui/                            # Web UI (Next.js + CopilotKit)
│   ├── app/                       # Next.js app router
│   │   ├── page.tsx               # Main chat interface
│   │   ├── workbench.tsx          # UI layout/workbench
│   │   ├── monaco-frame/          # Code editor integration
│   │   ├── calendar-frame/        # Calendar view integration
│   │   └── api/                   # API routes (CopilotKit proxy)
│   ├── components/                # UI components (shadcn/ui)
│   │   └── artifacts/             # Atomic artifact components
│   ├── lib/                       # Utilities and CopilotKit tools
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
# Start all services (postgres, redis, roscoe, copilotkit, uploads, ui)
docker compose up -d

# View logs
docker compose logs -f roscoe
docker compose logs -f copilotkit
docker compose logs -f ui

# Restart after code changes
docker compose restart roscoe  # Agent code changes
docker compose restart copilotkit  # CopilotKit backend changes
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
| CopilotKit Backend | http://34.63.223.97:8124 |
| Web UI (CopilotKit) | http://34.63.223.97:3001 |
| LangSmith | https://smith.langchain.com/projects/roscoe-local |

---

## CopilotKit UI Architecture

The web interface provides a modern chat-based interaction with Roscoe, built with Next.js and CopilotKit 1.5. **Replaced assistant-ui** (v0.7.12 had LangChain v1 compatibility issues).

### Technology Stack

| Component | Technology |
|-----------|-----------|
| Framework | Next.js 16 (App Router) |
| UI Library | CopilotKit 1.5 (AG-UI protocol) |
| Styling | Tailwind CSS 4 + shadcn/ui |
| Code Editor | Monaco Editor (VS Code) |
| Validation | Zod |
| Runtime | React 19 |
| Container | Node.js 22 Alpine |

### Key Features

- **Modular Artifact System**: Atomic UI components (ContactCard, MedicalProviderCard, InsuranceCard) dynamically generated by agent
- **Build Once, Use Many**: Components registered in central registry, automatically available to agent
- **Artifact Canvas**: Agent generates UI like Claude Artifacts - creates, updates, removes components in real-time
- **Type-Safe**: Zod schemas validate all artifact data at runtime
- **AG-UI Protocol**: Native LangGraph integration via CopilotKit's streaming protocol
- **Workspace Browser**: Read-only access to `/mnt/workspace` for viewing case files
- **Monaco Editor Frame**: Embedded code editor for viewing/editing scripts
- **Calendar Frame**: Integrated calendar view for case deadlines and events
- **Composable**: Agent combines atomic components to build complex interfaces

### Architecture Layers

**See [COPILOTKIT_ARCHITECTURE.md](docs/COPILOTKIT_ARCHITECTURE.md) for detailed documentation.**

1. **Atomic Components** (`ui/components/artifacts/`) - Reusable UI blocks with Zod schemas
2. **Artifact Canvas** (`ui/components/artifacts/artifact-canvas.tsx`) - Rendering system for dynamic UI
3. **CopilotKit Tools** (`ui/lib/copilotkit-artifact-tools.tsx`) - Agent capabilities (create/update/remove artifacts)
4. **Backend Integration** (`src/roscoe/copilotkit_server.py`) - AG-UI protocol endpoint wrapping LangGraph
5. **Workspace Tools** (`ui/lib/copilotkit-workspace-tools.tsx`) - File browsing and document viewing

### Docker Configuration

CopilotKit runs as multiple cooperating services in `docker-compose.yml`:

```yaml
copilotkit:
  # AG-UI backend (port 8124)
  # Wraps LangGraph agent for CopilotKit
  build: .
  container_name: roscoe-copilotkit
  ports:
    - "8124:8124"
  command: python -m roscoe.copilotkit_server
  environment:
    - LANGGRAPH_DEPLOYMENT=true
    - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    # ... other API keys
  volumes:
    - /mnt/workspace:/mnt/workspace:ro

ui:
  # Next.js frontend (port 3001)
  # CopilotKit React components
  build:
    context: ./ui
  ports:
    - 3001:3000
  environment:
    COPILOTKIT_LANGGRAPH_URL: http://copilotkit:8124  # CopilotKit endpoint
    WORKSPACE_ROOT: /mnt/workspace
  volumes:
    - /mnt/workspace:/mnt/workspace:ro
```

**Key Points**:
- **Two services**: `copilotkit` (Python backend) and `ui` (Next.js frontend)
- UI proxies CopilotKit API through `/api/copilotkit` to avoid CORS
- Both have **read-only** access to workspace for security
- Uses **service DNS** (`http://copilotkit:8124`) for internal communication

### Network Flow

```
User Browser → UI (port 3001) → /api/copilotkit proxy → CopilotKit (port 8124) → LangGraph Agent → Response
```

### Adding New Artifact Components

**No backend changes needed!** Just create component and deploy:

1. Create `ui/components/artifacts/my-component.tsx` with Zod schema
2. Register in `artifactRegistry.register()`
3. Import in `ui/app/workbench.tsx`
4. Deploy: `docker compose build ui && docker compose restart ui`

Agent can now use it via `create_artifact` tool.

**Example:**

```typescript
// 1. Define schema + component
export const myComponentSchema = z.object({
  title: z.string().min(1),
  description: z.string().optional(),
});

export function MyComponent({ data }: ArtifactProps) {
  const validated = myComponentSchema.parse(data);
  return <Card><CardTitle>{validated.title}</CardTitle></Card>;
}

// 2. Register
artifactRegistry.register({
  id: "my-component",
  name: "My Component",
  description: "Description for agent",
  component: MyComponent,
  schema: myComponentSchema,
  category: "ui",
});
```

### Updating UI

```bash
# On VM - UI changes only
cd ~/roscoe
git pull origin main
docker compose build ui
docker compose restart ui
docker compose logs -f ui

# On VM - Backend + UI changes
cd ~/roscoe
git pull origin main
docker compose build ui copilotkit
docker compose up -d
docker compose logs -f ui copilotkit
```

### Workbench Layout

```
┌─────────────────────────────────────────────────────────────┐
│  File Browser  │  Center Panel (4 views)  │  CopilotKit    │
│  (Workspace)   │                           │  Sidebar       │
│                │  • Viewer (docs/PDFs)     │                │
│  Database/     │  • Monaco (code editor)   │  Chat with     │
│  Tools/        │  • Calendar (deadlines)   │  Roscoe        │
│  Skills/       │  • Artifacts (UI canvas)  │                │
│  projects/     │                           │                │
└─────────────────────────────────────────────────────────────┘
```

### Available Artifact Components

| Component | ID | Purpose | Category |
|-----------|-----|---------|----------|
| ContactCard | `contact-card` | Display contact info (attorney, client, witness) | contact |
| MedicalProviderCard | `medical-provider-card` | Healthcare provider with treatments | medical |
| InsuranceCard | `insurance-card` | Insurance carrier, policy, adjuster | insurance |

### File Browser API

The UI includes workspace browsing capabilities via Next.js API routes:

```typescript
// List directory contents
GET /api/workspace/list?path=/Database

// Read file contents
GET /api/workspace/file?path=/Database/caselist.json
```

These routes are protected by the container's read-only mount and only serve files from `/mnt/workspace`.

### Troubleshooting

```bash
# Check services
docker ps | grep roscoe-ui
docker ps | grep roscoe-copilotkit

# Check logs
docker compose logs ui | tail -50
docker compose logs copilotkit | tail -50

# Test endpoints
curl http://localhost:3001/api/copilotkit
# Expected: {"status":"ok","service":"copilotkit-proxy"}

curl http://localhost:8124/health
# Expected: {"status":"ok","service":"roscoe-copilotkit"}

# Rebuild from scratch
docker compose down
docker compose build --no-cache ui copilotkit
docker compose up -d
```

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
| View CopilotKit logs | `docker compose logs -f copilotkit` |
| Restart agent | `docker compose restart roscoe` |
| Restart UI | `docker compose build ui && docker compose restart ui` |
| Restart CopilotKit | `docker compose restart copilotkit` |
| Access Web UI | http://34.63.223.97:3001 |
| Edit agent code | `/home/aaronwhaley/roscoe/src/roscoe/agents/paralegal/` |
| Edit UI code | `/home/aaronwhaley/roscoe/ui/` |
| Edit artifact components | `/home/aaronwhaley/roscoe/ui/components/artifacts/` |
| Edit tools | `/mnt/workspace/Tools/` |
| Edit skills | `/mnt/workspace/Skills/` |
| View case data | `/mnt/workspace/Database/` |
| Check script logs | `/mnt/workspace/Database/script_execution_logs/` |
