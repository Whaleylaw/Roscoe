# Roscoe UI Architecture Document

## Overview

This document outlines the current Roscoe system architecture and the plan for integrating CopilotKit as the new UI framework.

---

## PART 1: CURRENT ARCHITECTURE

### 1.1 Backend: Roscoe Agent (Python/LangGraph)

**Location:** `/src/roscoe/agents/paralegal/`

**Technology Stack:**
- **Framework:** DeepAgents (custom LangGraph wrapper)
- **LLM:** Claude Sonnet 4.5 (configurable via `MODEL_PROVIDER`)
- **Server:** LangGraph Server (standard `langgraph serve` via uvicorn)
- **Database:** PostgreSQL (checkpointing) + Redis (caching)
- **Storage:** GCS via gcsfuse mount at `/mnt/workspace`

**Key Files:**
| File | Purpose |
|------|---------|
| `agent.py` | Main agent definition with middleware pipeline |
| `tools.py` | Agent tools (Slack, script execution, multimodal analysis) |
| `prompts.py` | System prompt with persona and workspace instructions |
| `models.py` | LLM configuration (anthropic/openai/google) |
| `sub_agents.py` | Multimodal sub-agent definition |
| `script_executor.py` | Docker-based script execution |

**Agent Architecture:**
```
User Input
    │
    ▼
┌──────────────────────────────────────────────┐
│           CaseContextMiddleware              │
│  (Detects client/case mentions, injects     │
│   case context from /Database/caselist.json) │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│          SkillSelectorMiddleware             │
│  (Semantic search finds relevant skills,    │
│   injects skill workflow into prompt)        │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│          personal_assistant_agent            │
│  (DeepAgent with Claude Sonnet 4.5)         │
│                                              │
│  Tools:                                      │
│  - send_slack_message                        │
│  - upload_file_to_slack                      │
│  - execute_python_script (Docker)            │
│  - execute_python_script_with_browser        │
│                                              │
│  Sub-agents:                                 │
│  - multimodal_sub_agent (images/audio/video) │
└──────────────────────────────────────────────┘
    │
    ▼
Response (streamed)
```

**API Endpoints (LangGraph Server - Port 8000/8123):**
- `GET /ok` - Health check
- `GET /graphs` - List available graphs
- `POST /runs/stream` - Stream agent runs
- `POST /runs` - Create agent runs
- `GET /runs/{run_id}` - Get run status

---

### 1.2 Current GCE Deployment

**VM:** `roscoe-paralegal-vm` (us-central1-a)
**External IP:** `34.63.223.97` (dynamic - may change)

**Docker Compose Services:**
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `roscoe-agents` | `agwhaley/roscoe-agents:fixed` | 8123→8000 | LangGraph agent server |
| `roscoe-ui` | `agwhaley/roscoe-ui:latest` | 3000→3000 | Old Next.js UI |
| `postgres` | `postgres:15-alpine` | 5432 | Checkpointing |
| `redis` | `redis:7-alpine` | 6379 | Caching |

**Firewall Rules:**
- `allow-roscoe-agent` - tcp:8123 (0.0.0.0/0)
- `allow-roscoe-ui` - tcp:3000 (0.0.0.0/0)

**GCS Mount:** `/mnt/workspace` → `whaley_law_firm` bucket

---

### 1.3 Current Interfaces

**1. Slack Integration (Primary current interface):**
- Socket Mode via `slack_bot.py`
- Listens on Slack channels
- Messages routed to agent via `[SLACK CONVERSATION]` context
- Responses sent back via `send_slack_message` tool

**2. Old UI (roscoe-ui:latest on port 3000):**
- Basic Next.js chat interface
- Connects directly to LangGraph server
- Limited functionality

**3. LangGraph Studio:**
- Development interface via `langgraph dev`
- Not deployed in production

---

## PART 2: TARGET ARCHITECTURE (CopilotKit Integration)

### 2.1 Architecture Overview (Hybrid: CopilotKit + Thesys C1 as Tool)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          REACT FRONTEND                                   │
│                    (CopilotKit + Thesys C1Component)                     │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  CopilotSidebar                                                  │   │
│   │  ├── Regular text messages (from Roscoe)                        │   │
│   │  └── Rich UI components (from Thesys C1, rendered via           │   │
│   │      C1Component when agent calls generate_ui tool)             │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Main Canvas (Artifacts)                                         │   │
│   │  └── Case cards, documents, visualizations                      │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     CopilotKit Runtime (Next.js API)                     │
│                           /api/chat                                       │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                   CopilotKit Python SDK (FastAPI)                        │
│                         Port 8124 on GCE                                  │
│                                                                          │
│   Endpoints:                                                              │
│   - /copilotkit (CopilotKit protocol)                                   │
│   - /health                                                              │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     ROSCOE AGENT (LangGraph)                             │
│                    personal_assistant_agent                              │
│                                                                          │
│   Middleware Pipeline:                                                    │
│   ├── CaseContextMiddleware (injects case data)                         │
│   └── SkillSelectorMiddleware (loads relevant skills)                   │
│                                                                          │
│   Tools:                                                                  │
│   ├── send_slack_message                                                 │
│   ├── upload_file_to_slack                                               │
│   ├── execute_python_script (Docker)                                    │
│   ├── execute_python_script_with_browser (Playwright)                   │
│   └── generate_ui (NEW - calls Thesys C1) ◄────────────────────────┐    │
│                                                                     │    │
│   Sub-agents:                                                       │    │
│   └── multimodal_sub_agent (images/audio/video)                    │    │
│                                                                     │    │
└─────────────────────────────────────────────────────────────────────│────┘
                                                                      │
                                                                      │
                           When agent decides rich UI is needed:      │
                                                                      ▼
                              ┌───────────────────────────────────────────┐
                              │           THESYS C1 API                   │
                              │     https://api.thesys.dev/v1/embed       │
                              │                                           │
                              │  Input: instruction + data context        │
                              │  Output: Interactive UI component (HTML)  │
                              │                                           │
                              │  Examples:                                │
                              │  - Case summary cards                     │
                              │  - Medical timelines                      │
                              │  - Damage calculators                     │
                              │  - Interactive forms                      │
                              └───────────────────────────────────────────┘
```

**Key Insight:** Roscoe remains the "brain" and decides WHEN to generate rich UI.
Regular responses are plain text. Special visualizations use C1.

### 2.2 What CopilotKit Provides

**CopilotKit is:**
- A React SDK for building AI chat interfaces
- A protocol (AG-UI) for agent-frontend communication
- A Python SDK for wrapping LangGraph agents

**CopilotKit is NOT:**
- A replacement for LangGraph (it wraps LangGraph)
- A replacement for your agent logic
- The LLM itself (it uses your existing agent)

### 2.3 Integration Pattern

**Option Chosen: Remote Endpoint Pattern**

CopilotKit connects to LangGraph via the CopilotKit Python SDK:

```python
# src/roscoe/copilotkit_server.py
from copilotkit import CopilotKitSDK, LangGraphAgent
from copilotkit.integrations.fastapi import add_fastapi_endpoint

sdk = CopilotKitSDK(
    agents=[
        LangGraphAgent(
            name="roscoe_paralegal",
            description="AI Paralegal Assistant",
            graph=personal_assistant_agent,  # Your existing agent!
        ),
    ],
)

add_fastapi_endpoint(app, sdk, "/copilotkit")
```

**Frontend API Route:**
```typescript
// roscoe-ui/src/app/api/chat/route.ts
const runtime = new CopilotRuntime({
  remoteEndpoints: [
    { url: "http://34.63.223.97:8124/copilotkit" },
  ],
});
```

---

## PART 3: IMPLEMENTATION PLAN

### Phase 1: Add Thesys C1 Tool to Roscoe Agent

**New Tool: `generate_ui`**

```python
# src/roscoe/agents/paralegal/tools.py

def generate_ui(
    instruction: str,
    data: dict,
    component_type: str = "auto",
) -> str:
    """
    Generate rich interactive UI using Thesys C1.
    
    Use this when you need to display:
    - Case summary cards with expandable sections
    - Medical timelines or chronologies
    - Interactive damage calculators
    - Document comparison views
    - Forms to collect user input
    - Progress trackers
    - Charts or visualizations
    
    Args:
        instruction: What UI to generate (e.g., "Create an interactive case summary card")
        data: The data to visualize (case info, medical records, etc.)
        component_type: Hint for UI type: "card", "timeline", "form", "chart", "auto"
    
    Returns:
        C1 response that frontend will render as interactive UI
    """
    # Call Thesys C1 API
    response = thesys_client.generate(
        instruction=instruction,
        context=data,
        model="c1/anthropic/claude-sonnet-4"
    )
    return response
```

**Files to Modify:**
1. `src/roscoe/agents/paralegal/tools.py` - Add `generate_ui` tool
2. `src/roscoe/agents/paralegal/agent.py` - Register tool
3. `pyproject.toml` - Add `thesys` or use `openai` client

### Phase 2: Backend Integration (CopilotKit Python SDK)

**Files to Create/Modify:**

1. **`src/roscoe/copilotkit_server.py`** (CREATED)
   - FastAPI app wrapping Roscoe with CopilotKit SDK
   - Exposes `/copilotkit` endpoint for CopilotKit frontend

2. **`pyproject.toml`** (MODIFIED)
   - Added: `copilotkit`, `fastapi`, `uvicorn`

### Phase 3: Frontend - Render C1 Responses

**Update page.tsx to handle C1 responses:**

```typescript
// When agent calls generate_ui tool, the response contains C1 markup
// Use useCopilotAction to render C1 responses

useCopilotAction({
  name: "generate_ui",
  render: ({ args, result }) => {
    if (result) {
      return (
        <C1Component
          c1Response={result}
          isStreaming={false}
          onAction={(action) => {
            // Handle user interactions with the generated UI
            appendMessage(new TextMessage({
              role: MessageRole.User,
              content: JSON.stringify(action),
            }));
          }}
        />
      );
    }
    return <div>Generating visualization...</div>;
  },
});
```

### Phase 4: Deployment

**Steps Required:**

1. **Create Dockerfile** with both servers:
   ```dockerfile
   # Run LangGraph on 8000, CopilotKit on 8124
   ```

2. **Update docker-compose.yml on GCE:**
   ```yaml
   roscoe:
     image: agwhaley/roscoe-agents:copilotkit
     ports:
       - 8123:8000  # LangGraph server (Slack, etc.)
       - 8124:8124  # CopilotKit server (React UI)
     environment:
       - THESYS_API_KEY=${THESYS_API_KEY}
   ```

3. **Open Firewall Port:**
   ```bash
   gcloud compute firewall-rules create allow-roscoe-copilotkit \
     --allow tcp:8124 --source-ranges 0.0.0.0/0
   ```

4. **Deploy New UI** to Vercel or as Docker service

---

## PART 4: KEY DECISIONS

### 4.1 Why CopilotKit + Remote Endpoint?

| Option | Pros | Cons |
|--------|------|------|
| **Copilot Cloud** | Managed, easy setup | Monthly cost, tunnels needed |
| **langGraphPlatformEndpoint** | Direct LangGraph | For LangGraph Platform only |
| **Remote Endpoint (CHOSEN)** | Self-hosted, flexible | Need Python SDK wrapper |

### 4.2 Why Keep Both Servers?

- **Port 8123 (LangGraph):** Slack integration, existing clients
- **Port 8124 (CopilotKit):** New React UI

Both use the SAME agent code - just different API formats.

### 4.3 Thesys Integration: C1 as a Tool

Per [Thesys Integration Patterns](https://docs.thesys.dev/guides/integration-patterns#c1-as-a-tool), we can use **C1 as a Tool** pattern:

**How it works:**
```
User asks: "Show me a summary of the Wilson case"
    │
    ▼
Roscoe Agent (Claude Sonnet 4.5)
    │
    ├── Retrieves case data from workspace
    │
    ├── Decides: "This needs rich UI visualization"
    │
    └── Calls Thesys C1 Tool with context:
        {
          "instruction": "Generate an interactive case summary card",
          "data": { case_name, status, damages, timeline, ... }
        }
            │
            ▼
        Thesys C1 generates interactive UI component
            │
            ▼
        UI streams directly to frontend
```

**Benefits:**
- ✅ Roscoe remains the "brain" (controls logic, retrieves data)
- ✅ C1 generates beautiful, interactive UI on demand
- ✅ Works with any LLM as the gateway
- ✅ Agent decides WHEN to show rich UI vs plain text

**Use Cases:**
- Case summary cards with expandable sections
- Medical timeline visualizations
- Interactive damage calculators
- Document comparison views
- Progress trackers for long-running tasks
- Forms for collecting user input

**Implementation:**
Add a `generate_ui` tool to Roscoe that calls Thesys C1 API

---

## PART 5: CURRENT STATUS

| Component | Status | Location |
|-----------|--------|----------|
| Roscoe Agent | ✅ Running | GCE:8123 |
| PostgreSQL | ✅ Running | GCE:5432 |
| Redis | ✅ Running | GCE:6379 |
| Slack Integration | ✅ Working | Via agent |
| Old UI (roscoe-ui) | ✅ Running | GCE:3000 |
| New UI (CopilotKit) | 🟡 Local only | localhost:3001 |
| CopilotKit Server | ✅ Code ready | `src/roscoe/copilotkit_server.py` |
| Thesys C1 Tool | ✅ Implemented | `src/roscoe/agents/paralegal/tools.py` |
| Frontend Renderer | ✅ Implemented | `roscoe-ui/src/app/page.tsx` |
| Deployment Script | ✅ Created | `deploy-copilotkit.sh` |
| Firewall 8124 | ❌ Not created | Needed |

---

## PART 6: IMPLEMENTATION ORDER

### Step 1: Add `generate_ui` Tool (Backend)
- Create Thesys C1 client in tools.py
- Add tool to agent
- Test locally with `langgraph dev`

### Step 2: Update Frontend to Render C1
- Add `useCopilotAction` for `generate_ui` tool
- Import and configure `C1Component` from `@thesysai/genui-sdk`
- Test with local Roscoe

### Step 3: Create CopilotKit Server Wrapper
- Finalize `copilotkit_server.py`
- Test locally with FastAPI

### Step 4: Create Multi-Server Dockerfile
- Single image running both LangGraph (8000) and CopilotKit (8124)
- Or: Supervisor process to manage both

### Step 5: Deploy to GCE
- Build and push Docker image
- Create firewall rule for 8124
- Update docker-compose.yml
- Restart services

### Step 6: Deploy UI
- Option A: Deploy to Vercel (recommended for speed)
- Option B: Build Docker image and add to compose

---

## SUMMARY: The Hybrid Approach

**Why this architecture is better:**

| Approach | Pros | Cons |
|----------|------|------|
| Thesys-only | Beautiful auto-generated UI | Loses Roscoe's intelligence |
| CopilotKit-only | Works with Roscoe | No generative UI |
| **Hybrid (chosen)** | Best of both | Slightly more complexity |

**The key insight:** Roscoe is the "brain" that decides:
1. When to respond with plain text (most interactions)
2. When to call `generate_ui` for rich visualizations (case cards, timelines, forms)

This preserves Roscoe's legal expertise while adding beautiful, interactive UI when needed.

