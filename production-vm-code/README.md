# Production VM Code Snapshot

**Created**: December 8, 2024
**Source**: GCE VM `roscoe-paralegal-vm` (34.63.223.97, us-central1-a)

This is a **snapshot of the actual production code** running on the Google Cloud VM. This represents what's deployed and serving requests, not development code.

## What's Included

### Core Python Code (`src/`)
- ✅ **25 Python files** (complete source code)
- ✅ **Agent implementations** (paralegal + coding agents)
- ✅ **Middleware** (case context injection, skill selection, workflow state)
- ✅ **Tool definitions** (Gmail, Calendar, Slack, script execution)
- ✅ **Model configurations** (lazy initialization, multi-provider support)

### Configuration Files
- ✅ `pyproject.toml` - Python dependencies and package config
- ✅ `langgraph.json` - LangGraph deployment config (graphs, store)
- ✅ `docker-compose.yml` - Production container orchestration
- ✅ `CLAUDE.md` - Comprehensive production documentation

## File Structure

```
production-vm-code/
├── CLAUDE.md                          # Production documentation (27KB)
├── docker-compose.yml                 # Container orchestration
├── langgraph.json                     # LangGraph config
├── pyproject.toml                     # Python package config
├── README.md                          # This file
└── src/
    └── roscoe/
        ├── __init__.py
        ├── Deprecated/
        │   ├── copilotkit_server.py   # [DEPRECATED] CopilotKit integration (moved to Deprecated)
        │   └── Persistence.md          # [DEPRECATED] CopilotKit persistence docs
        ├── slack_launcher.py          # Slack Socket Mode bridge
        ├── Persistence.md             # Persistence documentation
        │
        ├── core/                      # Shared infrastructure
        │   ├── __init__.py
        │   ├── case_context_middleware.py   # Auto case context injection
        │   ├── skill_middleware.py          # Semantic skill selection
        │   ├── workflow_state_computer.py   # Workflow state derivation
        │   └── google_auth.py               # Google OAuth helpers
        │
        └── agents/
            ├── paralegal/             # Paralegal agent (production)
            │   ├── agent.py           # Main agent definition
            │   ├── models.py          # Model config (anthropic/openai/google)
            │   ├── tools.py           # Tool definitions
            │   ├── prompts.py         # System prompts
            │   ├── sub_agents.py      # Sub-agent definitions
            │   ├── script_executor.py # Docker script execution
            │   ├── gmail_tools.py     # Gmail integration (OAuth)
            │   ├── calendar_tools.py  # Calendar integration (OAuth)
            │   └── skills_manifest.json  # Skills registry (in code)
            │
            └── coding/                # Coding agent (planned)
                ├── agent.py
                ├── models.py
                ├── tools.py
                ├── prompts.py
                └── sub_agents.py
```

## Key Differences from Local Repo

### Production-Specific Features

1. **Lazy Model Initialization** (`models.py`)
   - Models created on first access to avoid pickle errors
   - Getter functions: `get_agent_llm()`, `get_sub_agent_llm()`, `get_multimodal_llm()`

2. **Docker Script Execution** (`script_executor.py`)
   - Scripts run in isolated containers with GCS filesystem access
   - Resource limits (2GB RAM, 1 CPU core)
   - Audit logging to `/mnt/workspace/Database/script_execution_logs/`

3. **Case Context Middleware** (`case_context_middleware.py`)
   - Fuzzy matching for client name detection (80% threshold)
   - Loads from centralized `/mnt/workspace/Database/` JSON files
   - Workflow state computation via `WorkflowStateComputer`
   - Message sanitization (fixes orphaned tool_use/tool_result)

4. ~~**CopilotKit Server**~~ [DEPRECATED - Using DeepAgents UI instead]
   - ~~FastAPI server for UI integration (port 8124)~~
   - ~~Connects Next.js frontend to LangGraph backend~~
   - **Replaced by**: DeepAgents UI (port 3000, connects directly to LangGraph API)

5. **Gmail/Calendar Tools** (`gmail_tools.py`, `calendar_tools.py`)
   - Full Google Workspace OAuth integration
   - Email search, send, save to case folders
   - Calendar event management, free time finding

6. **Multi-Provider Model Support** (`models.py`)
   - `MODEL_PROVIDER = "anthropic"` (or "openai" or "google")
   - Automatic fallback on rate limits
   - 1M context window for Claude Sonnet 4.5

### Production Environment

**Deployment**: Docker Compose on GCE VM
- Port 8123: LangGraph API (DeepAgents UI)
- ~~Port 8124: CopilotKit server~~ [DEPRECATED]
- Port 3000: DeepAgents UI (replaces Next.js/CopilotKit)
- Port 5432: PostgreSQL (checkpointing)
- Port 6379: Redis (caching)

**Workspace**: GCS bucket (`whaley_law_firm`) mounted at `/mnt/workspace`
- Tools: `/mnt/workspace/Tools/` (65KB manifest, 20+ categories)
- Skills: `/mnt/workspace/Skills/` (17KB manifest, 20+ skills)
- Database: `/mnt/workspace/Database/` (centralized JSON files)
- Workflow Engine: `/mnt/workspace/workflow_engine/` (checklists, templates, schemas)

## What's NOT Included

This snapshot contains **only the Python source code** from the VM's `~/roscoe/` directory. It does NOT include:

- ❌ GCS workspace files (`/mnt/workspace/`)
  - Tools (Python scripts)
  - Skills (markdown files)
  - Database (JSON files)
  - Workflow engine (checklists, templates)
  - Case files (`projects/`)
- ❌ Environment variables (`.env` file)
- ❌ OAuth credentials (`credentials.json`, `token.json`)
- ❌ Docker images
- ❌ PostgreSQL/Redis data

**Why?** The workspace is 68GB+ and contains sensitive case files. The source code here shows the **agent logic**, while the workspace contains the **data and runtime scripts**.

## How to Use This Snapshot

### Compare with Local Development Code

```bash
# Compare agent implementation
diff production-vm-code/src/roscoe/agents/paralegal/agent.py src/roscoe/agents/paralegal/agent.py

# Compare model config
diff production-vm-code/src/roscoe/agents/paralegal/models.py src/roscoe/agents/paralegal/models.py
```

### Reference Production Configuration

This snapshot shows **exactly what's running in production**:
- Model provider settings
- Middleware configuration
- Tool definitions
- Docker integration
- OAuth setup

### Sync Changes to Production

If you make changes locally and want to deploy:

```bash
# 1. Test locally first
cd "/Volumes/X10 Pro/Roscoe"
langgraph dev

# 2. Copy to VM
gcloud compute scp --recurse --zone us-central1-a \
  src/roscoe/agents/paralegal/ \
  roscoe-paralegal-vm:~/roscoe/src/roscoe/agents/paralegal/

# 3. Restart on VM
gcloud compute ssh roscoe-paralegal-vm --zone us-central1-a \
  --command "cd ~ && docker compose restart roscoe"
```

## Version Info

**Python**: 3.11
**LangGraph**: Latest (from pyproject.toml)
**DeepAgents**: >=0.2.0
**Docker Images**:
- `roscoe-agents:local` (main agent container)
- `roscoe-python-runner:latest` (script execution)
- `roscoe-python-runner:playwright` (browser automation)

## Support

- **CLAUDE.md**: Complete production documentation (27KB, included)
- **VM Access**: `gcloud compute ssh roscoe-paralegal-vm --zone us-central1-a`
- **Logs**: `docker compose logs -f roscoe`
- **LangSmith**: https://smith.langchain.com/projects/roscoe-local
