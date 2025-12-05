# Roscoe UI Integration - Current Status

**Date:** November 29, 2025  
**Status:** ✅ LOCAL TESTING WORKING

---

## ✅ COMPLETED

### 1. Backend: `generate_ui` Tool (Thesys C1)
**File:** `src/roscoe/agents/paralegal/tools.py`

Added a new tool that calls Thesys C1 API to generate rich interactive UI.

### 2. Backend: Agent Updated
**File:** `src/roscoe/agents/paralegal/agent.py`

Added `generate_ui` to the agent's tools list.

### 3. Backend: CopilotKit Server (AG-UI Protocol)
**File:** `src/roscoe/copilotkit_server.py`

FastAPI server that wraps Roscoe with CopilotKit's AG-UI protocol:
- Sets `LANGGRAPH_DEPLOYMENT=true` before importing agent
- Uses `MemorySaver` checkpointer for local dev
- Recompiles agent graph with checkpointer
- Exposes `/copilotkit/agents/roscoe_paralegal` endpoint
- Exposes `/health` endpoint
- Runs on port 8124

```python
# Key pattern for AG-UI integration:
from langgraph.checkpoint.memory import MemorySaver
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import LangGraphAGUIAgent

memory_checkpointer = MemorySaver()
graph_with_checkpointer = personal_assistant_agent.builder.compile(
    checkpointer=memory_checkpointer
)

add_langgraph_fastapi_endpoint(
    app=app,
    agent=LangGraphAGUIAgent(
        name="roscoe_paralegal",
        description="...",
        graph=graph_with_checkpointer,
    ),
    path="/copilotkit/agents/roscoe_paralegal",
)
```

### 4. Frontend: API Route (AG-UI Protocol)
**File:** `roscoe-ui/src/app/api/chat/route.ts`

Uses `LangGraphHttpAgent` to connect to AG-UI endpoint:

```typescript
import { LangGraphHttpAgent } from "@copilotkit/runtime";

const runtime = new CopilotRuntime({
  agents: {
    'roscoe_paralegal': new LangGraphHttpAgent({
      url: `${REMOTE_ACTION_URL}/agents/roscoe_paralegal`,
    }),
  },
});
```

### 5. Frontend: Simplified Page
**File:** `roscoe-ui/src/app/page.tsx`

Uses CopilotSidebar for chat interface (temporarily removed C1Component due to dependency issues).

### 6. Environment Variables
**Backend (.env):**
- All API keys configured
- `WORKSPACE_DIR` set

**Frontend (.env.local):**
- `ROSCOE_COPILOTKIT_URL=http://localhost:8124`

---

## 🔄 NEXT STEPS

### Option A: Deploy to GCE VM (Recommended)
```bash
# 1. Build Docker image with copilotkit server
langgraph build -t agwhaley/roscoe-agents:copilotkit

# 2. Push to Docker Hub
docker push agwhaley/roscoe-agents:copilotkit

# 3. Update GCE docker-compose.yml to add copilotkit service
# 4. Deploy to GCE
```

### Option B: Use Existing Image
Add CopilotKit service to GCE docker-compose.yml using existing image with different command.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐
│   React UI      │────▶│  /api/chat (Next.js) │
│   (localhost:   │     │  LangGraphHttpAgent   │
│    3000)        │     └──────────┬───────────┘
└─────────────────┘                │
                                   ▼
                    ┌──────────────────────────────┐
                    │  CopilotKit Server (AG-UI)   │
                    │  (localhost:8124)            │
                    │  /copilotkit/agents/         │
                    │    roscoe_paralegal          │
                    └──────────┬───────────────────┘
                               │
                               ▼
                    ┌──────────────────────────────┐
                    │  Roscoe Agent (LangGraph)    │
                    │  with MemorySaver checkpoint │
                    │                              │
                    │  Tools:                      │
                    │  - generate_ui (Thesys C1)   │
                    │  - execute_python_script     │
                    │  - send_slack_message        │
                    │  - etc.                      │
                    └──────────────────────────────┘
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `src/roscoe/copilotkit_server.py` | CopilotKit AG-UI FastAPI server |
| `src/roscoe/agents/paralegal/agent.py` | Agent with checkpointer support |
| `roscoe-ui/src/app/api/chat/route.ts` | Frontend API route with LangGraphHttpAgent |
| `roscoe-ui/src/app/page.tsx` | Frontend with CopilotSidebar |

---

## Running Locally

### Backend
```bash
cd /Volumes/X10\ Pro/Roscoe
source .venv/bin/activate
uvicorn roscoe.copilotkit_server:app --host 0.0.0.0 --port 8124
```

### Frontend
```bash
cd /Volumes/X10\ Pro/Roscoe/roscoe-ui
npm run dev
```

### Test
1. Open http://localhost:3000
2. Chat with Roscoe in the sidebar
3. Backend health check: http://localhost:8124/health

---

## Important Notes

1. **Checkpointer Required**: AG-UI protocol requires a checkpointer. Use `MemorySaver` for local dev, PostgreSQL for production.

2. **LANGGRAPH_DEPLOYMENT**: Must be set to `true` before importing agent so it uses `checkpointer=None` instead of `checkpointer=False`.

3. **URL Pattern**: `LangGraphHttpAgent` prepends `/copilotkit` to URLs, so backend path must include `/copilotkit/agents/...`.

4. **Dependencies**: Frontend needs `@ag-ui/client` and `@ag-ui/langgraph` packages.
