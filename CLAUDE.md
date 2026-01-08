# CLAUDE.md

## Project Overview

**Roscoe** - Multi-agent platform on LangGraph for personal injury litigation.

**Agent:** `roscoe_paralegal` - Medical records analysis, legal research, case management, workflow tracking.

## Architecture

```
Browser → Next.js UI (port 3000) → LangGraph API (port 8123) → Agent
                                                              ↓
                                              FalkorDB (graph) + GCS (files)
```

## Deployment

**VM:** `roscoe-paralegal-vm` (GCP us-central1-a)

**Code sync flow:** Local → GitHub → VM
```
/Volumes/X10 Pro/Roscoe/  →  github.com/Whaleylaw/Roscoe  →  /home/aaronwhaley/roscoe/
```

**Deploy changes:**
```bash
# Local: commit and push
git add -A && git commit -m "message" && git push

# VM: pull and restart
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a
cd /home/aaronwhaley/roscoe && git pull
docker restart roscoe-agents                    # Python changes
pkill -f 'next dev' && cd ui && nohup npm run dev > /tmp/ui.log 2>&1 &  # UI changes
```

**Docker containers on VM:**
| Container | Port | Purpose |
|-----------|------|---------|
| roscoe-agents | 8123 | LangGraph API |
| roscoe-graphdb | 6380, 3001 | FalkorDB (graph: `roscoe_graph`) |
| roscoe-postgres | 5432 | LangGraph checkpoints |
| roscoe-redis | 6379 | LangGraph cache |
| roscoe-uploads | 8125 | File upload service |

**UI:** Runs as host process from `/home/aaronwhaley/roscoe/ui/` (symlinked to `roscoe-ui`)

## Key Files

| File | Purpose |
|------|---------|
| `src/roscoe/agents/paralegal/agent.py` | Agent entry point |
| `src/roscoe/agents/paralegal/models.py` | Model config (MODEL_PROVIDER) |
| `src/roscoe/agents/paralegal/tools.py` | Agent tools |
| `src/roscoe/core/graphiti_client.py` | Graph queries |
| `src/roscoe/workflow_engine/orchestrator/graph_state_computer.py` | Workflow state |
| `ui/src/lib/langgraph-client.ts` | SSE streaming |
| `ui/src/components/chat/chat-panel.tsx` | Chat UI |
| `langgraph.json` | LangGraph agent config |
| `docker-compose.yml` | Container orchestration |

## Models

```python
# src/roscoe/agents/paralegal/models.py
MODEL_PROVIDER = "anthropic"  # "anthropic", "openai", "google"
```

**Use getter functions:**
```python
from roscoe.agents.paralegal.models import get_agent_llm
model = get_agent_llm()  # NOT agent_llm
```

## Workspace Paths

```python
# CORRECT - workspace-relative
read_file("/Reports/summary.md")
ls("/projects/Wilson-MVA-2024/")

# WRONG - absolute paths
read_file("/Volumes/X10 Pro/Roscoe/workspace/...")
```

## Directory Structure

```
/mnt/workspace/                    # GCS bucket mounted on VM
├── Database/                      # JSON databases
├── Reports/                       # Analysis outputs
├── Tools/                         # Python scripts
├── Skills/                        # Skill folders with SKILL.md
└── projects/{case}/               # Case folders (8-bucket org)
```

```
src/roscoe/
├── agents/paralegal/              # Main agent
├── core/                          # Middleware, graph client
└── workflow_engine/orchestrator/  # State computation
```

```
ui/src/
├── app/api/chat/                  # LangGraph proxy
├── app/api/threads/               # Thread management
├── components/chat/               # Chat panel
├── lib/                           # langgraph-client.ts
└── stores/                        # Zustand state
```

## Physical Mail (Lob.com)

Tools for sending letters, certified mail, and postcards via USPS:

| Tool | Purpose |
|------|---------|
| `verify_address` | Validate addresses before sending |
| `send_letter` | Send letters (demand letters, notices) |
| `send_certified_mail` | Certified mail with tracking |
| `send_postcard` | Postcards (reminders) |
| `check_mail_status` | Track delivery status |
| `list_sent_mail` | View sent mail history |

**Config:** `LOB_API_KEY_TEST`/`LOB_API_KEY_LIVE` in .env, firm address in `/Database/firm_settings.json`

## Quick Reference

- **Deployment:** See `.claude/deployment.md`
- **Knowledge Graph:** See `.claude/graph.md`
- **Workflow Engine:** See `.claude/workflow.md`
- **Tools & Skills:** See `.claude/tools.md`
- **Troubleshooting:** See `.claude/troubleshooting.md`

## Local Development

```bash
langgraph dev           # Agent server (port 2024)
cd ui && npm run dev    # UI (port 3000)
```
