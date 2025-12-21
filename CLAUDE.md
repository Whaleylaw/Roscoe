# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Context for Claude Code

**Training Data Cutoff:** January 2025
**Current Date:** December 2025

Significant changes have occurred in the LangChain/LangGraph ecosystem since the training cutoff. When working with LangChain or LangGraph code, **always reference the "langchain-docs" MCP server** for the most current documentation links and implementation patterns.

---

## Project Overview

**Roscoe** is a multi-agent platform built on LangGraph with a custom lean UI (direct LangGraph integration via SSE). The platform uses a dynamic skills architecture for unlimited capability expansion without code changes.

**Current Agents:**
1. **Paralegal Agent** (`roscoe_paralegal`) - Personal injury litigation specialist
   - Medical records analysis with 5-phase workflow
   - Legal research via CourtListener API
   - Case management with automatic context injection
   - Document processing and file organization
   - Multimodal evidence analysis (images, audio, video)

2. **Coding Agent** (`roscoe_coding`) - Agent development and maintenance (planned)

**Key Innovations:**
- **Dynamic Skills System**: Skills loaded via semantic search, not hardcoded
- **Case Context Middleware**: Auto-detects client mentions and injects case data
- **Workflow Engine**: Graph-based state machine with deterministic phase tracking
- **Knowledge Graph**: Graphiti integration for semantic case memory
- **Native Script Execution**: Python scripts run directly on VM (Docker optional)
- **Custom Lean UI**: Direct LangGraph SSE integration with real-time streaming

---

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Frontend (ui/)                                  │
│  Next.js 16 + Custom Lean UI (Direct LangGraph SSE)                         │
│  ├─ ChatPanel: Streaming chat via LangGraph protocol                        │
│  ├─ Workbench: File browser, document viewer, artifacts                     │
│  └─ lib/langgraph-client.ts: Direct SSE connection to LangGraph             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ Server-Sent Events (SSE)
                                      │ http://localhost:8123
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LangGraph API Server (roscoe-agents)                    │
│  Container running langgraph_api.server:app - Port 8000 (host: 8123)        │
│  ├─ Loads agent from mounted source: /deps/Roscoe/src/roscoe                │
│  ├─ Thread management and checkpointing via Postgres                        │
│  └─ Streams agent responses via LangGraph protocol                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LangGraph Agent (DeepAgents)                        │
│  src/roscoe/agents/paralegal/agent.py                                       │
│  ├─ Middleware Pipeline:                                                    │
│  │   1. CaseContextMiddleware: Detects clients, injects case data           │
│  │   2. WorkflowMiddleware: Computes workflow state, injects guidance       │
│  │   3. SkillSelectorMiddleware: Semantic skill matching + injection        │
│  │   4. UIContextMiddleware: Bridges UI state to agent                      │
│  ├─ Sub-Agents:                                                             │
│  │   └─ multimodal-agent: Image/audio/video analysis                        │
│  └─ Tools:                                                                  │
│       ├─ Knowledge Graph: update_case_data, query_case_graph, graph_query   │
│       ├─ Workflow: get_case_workflow_status, update_landmark, advance_phase │
│       ├─ Gmail: search_emails, save_email_to_case, save_emails_batch        │
│       ├─ Calendar: list_events, create_event, find_free_time                │
│       ├─ Slack: send_slack_message, upload_file_to_slack                    │
│       ├─ Scripts: execute_python_script (native subprocess)                 │
│       └─ Skills: list_skills, load_skill, refresh_skills                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
┌───────────────────────────────┐     ┌───────────────────────────────────────┐
│   GCS Filesystem (/mnt/workspace)   │     │      Script Execution                 │
│   ├─ /projects/{case-name}/   │     │      Native Python subprocess on VM    │
│   ├─ /Database/               │     │      ├─ Scripts in /mnt/workspace/Tools│
│   ├─ /Reports/                │     │      ├─ Full access to workspace       │
│   ├─ /Tools/                  │     │      └─ Env vars from agent process    │
│   └─ /Skills/                 │     │                                         │
└───────────────────────────────┘     └───────────────────────────────────────┘
```

### Core Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Agent Framework | LangGraph + DeepAgents | Agent orchestration with sub-agents |
| Primary Model | Claude Sonnet 4.5 | Main agent, complex reasoning |
| Alternative Models | GPT-5.1 Thinking, Gemini 3 Pro | Configurable via MODEL_PROVIDER |
| API Server | LangGraph API (langgraph_api.server) | Serves agent via standard protocol |
| Frontend | Next.js 16 + React 19 | Web interface |
| Chat UI | Custom Lean UI | Direct LangGraph SSE integration (no CopilotKit) |
| State Management | Zustand | Client-side state |
| File System | FilesystemBackend | Sandboxed workspace operations |
| Script Execution | Native Python subprocess | Scripts run directly on VM (Docker optional) |
| Storage | Google Cloud Storage (gcsfuse) | Persistent workspace mount at /mnt/workspace |
| Checkpointing | PostgreSQL | Thread state persistence |
| Knowledge Graph | Graphiti + FalkorDB | Semantic case memory with episodes |
| Workflow Engine | Graph-based state machine | Deterministic phase/landmark tracking |
| Search | Tavily | Internet search |
| Legal Research | CourtListener API | Case law, citations, dockets |
| Email/Calendar | Gmail/Google Calendar API | OAuth2 integration for email and scheduling |
| Embeddings | sentence-transformers | Local semantic skill matching |
| Notifications | Slack SDK | Real-time alerts |

---

## Model Configuration

Models are configured in `src/roscoe/agents/paralegal/models.py`:

```python
# Change MODEL_PROVIDER to switch all models:
MODEL_PROVIDER = "anthropic"  # Options: "anthropic", "openai", "google"
```

| Provider | Model | Best For |
|----------|-------|----------|
| `anthropic` | Claude Sonnet 4.5 | Legal reasoning, document analysis, nuanced work |
| `openai` | GPT-5.1 Thinking | Extended reasoning, step-by-step analysis |
| `google` | Gemini 3 Pro Preview | Large context windows, multimodal native |

All three models have multimodal capabilities. The multimodal sub-agent uses the same provider as the main agent.

### Lazy Model Initialization (IMPORTANT)

Models are lazily initialized to avoid pickle errors with LangGraph checkpointing. **Always use getter functions**, not module-level variables:

```python
# ✅ CORRECT - Use getter functions
from roscoe.agents.paralegal.models import get_agent_llm, get_multimodal_llm
model = get_agent_llm()
multimodal = get_multimodal_llm()

# ❌ WRONG - Module-level variables are None
from roscoe.agents.paralegal.models import agent_llm, multimodal_llm
# These are None! Will cause "'NoneType' object has no attribute 'bind_tools'" errors
```

Available getter functions:
- `get_agent_llm()` - Main agent model
- `get_sub_agent_llm()` - Sub-agent model  
- `get_multimodal_llm()` - Multimodal analysis model
- `get_summarization_llm()` - Claude Haiku for summarization

---

## Middleware Architecture

### 1. CaseContextMiddleware (`src/roscoe/core/case_context_middleware.py`)

**Purpose:** Automatically detects client/case mentions in user messages and injects comprehensive case context into the system prompt.

**Detection Methods:**
- Exact name match: "Caryn McCay"
- Partial match: "McCay case", "Caryn's case"
- Fuzzy match: "Carmen McCay" → "Caryn McCay" (handles typos)
- Project name patterns: "Wilson MVA", "Caryn-McCay-MVA-7-30-2023"

**Injected Context:**
- `overview.json`: Case summary, status, phase, financials
- `contacts.json`: Attorneys, adjusters, providers
- `insurance.json`: Policies, coverage details
- `liens.json`: Medical liens
- `medical_providers.json`: Treating providers

**Configuration:**
```python
CaseContextMiddleware(
    workspace_dir=workspace_dir,
    fuzzy_threshold=80,  # Minimum fuzzy match score (0-100)
    max_cases=2,         # Support up to 2 cases in same query
)
```

### 2. SkillSelectorMiddleware (`src/roscoe/core/skill_middleware.py`)

**Purpose:** Semantically matches user requests to relevant skills and injects skill content into the system prompt.

**How It Works:**
1. Scans `/Skills/` folders at startup for `SKILL.md` or `skill.md` files
2. Parses YAML frontmatter to extract `name` and `description`
3. Embeds all skill descriptions using `sentence-transformers` (all-MiniLM-L6-v2)
4. On each request, computes cosine similarity between user query and skills
5. Loads top-matching skill content into system prompt
6. Sets skill metadata in request state

**Auto-Generated Manifest:**
The middleware builds an in-memory manifest from SKILL.md files at startup - no separate manifest file needed.

**Configuration:**
```python
SkillSelectorMiddleware(
    skills_dir=f"{workspace_dir}/Skills",  # Skill folders with SKILL.md
    max_skills=1,                          # Load top 1 matching skill
    similarity_threshold=0.3               # Minimum similarity (0-1)
)
```

**Runtime Methods:**
- `refresh_skills()` - Rescan skills directory for new additions mid-session
- `get_all_skills()` - Return list of all skill metadata for `list_skills()` tool

### 3. WorkflowMiddleware (`src/roscoe/core/workflow_middleware.py`)

**Purpose:** Computes deterministic workflow state from case data and injects phase-specific guidance with resource paths.

**How It Works:**
1. Runs AFTER CaseContextMiddleware to access detected cases
2. Loads workflow schemas from `/workspace/workflow_engine/schemas/`
3. Computes current phase and landmark completion status
4. Injects guidance with next actions and resource paths to skills/templates
5. Maintains deterministic state via graph-based rules (no hallucinations)

**Key Features:**
- Phase-aware guidance (Intake, Pre-Litigation, Litigation, etc.)
- Landmark tracking with completion status
- Blocker detection (e.g., can't advance without signed retainer)
- Resource path injection (skills, checklists, templates)

### 4. UIContextMiddleware (`src/roscoe/core/ui_context_middleware.py`)

**Purpose:** Bridges CopilotKit UI state to the agent, providing awareness of user's workspace context.

**Injected Context:**
- Currently open documents in workbench
- Active workspace location/path
- UI component state (file browser selection, etc.)

---

## Skills System

### Skills Architecture (Anthropic Agent Skills Spec)

Skills follow the Anthropic Agent Skills Specification. The system uses **YAML frontmatter in SKILL.md files** as the single source of truth.

**Skill Discovery Methods:**
1. **Automatic (Middleware)**: Semantic match on user message against skill descriptions
2. **Manual (Agent Tool)**: Agent calls `list_skills()` to browse and select skills

### Skill Folder Structure

Each skill is a **self-contained folder** with everything needed:

```
skill-name/                    # Folder name MUST match YAML name
├── SKILL.md                   # REQUIRED: YAML frontmatter + instructions
├── scripts/                   # Python/JS scripts referenced by skill
├── docs/                      # Additional documentation
└── templates/                 # Document templates if needed
```

### SKILL.md Format

```yaml
---
name: skill-name
description: When to use this skill - used for semantic matching
license: Optional license info
---

# Skill Instructions
Markdown content with instructions, workflows, examples...
```

### Available Skills

| Skill | Purpose | Type |
|-------|---------|------|
| **Legal Analysis** |||
| `medical-records-analysis` | 5-phase medical analysis pipeline | Native |
| `courtlistener-legal-research` | Case law, citations, dockets | Native |
| `legal-research` | Internet research with Tavily | Native |
| **Document Creation (Claude Skills)** |||
| `pdf` | PDF manipulation, forms, text/table extraction | Claude |
| `docx` | Word document creation/editing with tracked changes | Claude |
| `xlsx` | Spreadsheet creation with formulas and formatting | Claude |
| `pptx` | Presentation creation and editing | Claude |
| **Visual Design (Claude Skills)** |||
| `canvas-design` | Visual art creation in PNG/PDF | Claude |
| `theme-factory` | Apply styling themes to artifacts | Claude |
| **Case Management** |||
| `case-file-organization` | 8-bucket file organization system | Native |
| `import-case-documents` | Batch PDF-to-markdown conversion | Native |
| `calendar-scheduling` | Google Calendar integration | Native |
| `email-management` | Gmail integration | Native |
| `multimedia-evidence-analysis` | Audio/video with case context | Native |
| **Utility** |||
| `script-execution` | Python script execution | Native |
| `document-processing` | OCR and PDF processing | Native |

**Type Legend:**
- **Native**: Original Roscoe skills for legal workflows
- **Claude**: Integrated from Anthropic Claude Skills (document manipulation, design)

### Adding New Skills

1. **Create skill folder** in `/workspace_paralegal/Skills/skill-name/`
2. **Create SKILL.md** with YAML frontmatter (`name`, `description`)
3. **Add scripts** in `skill-name/scripts/` folder (if needed)
4. **No code changes needed** - Middleware auto-discovers at startup

### Agent Tools for Skills

```python
# List all available skills with descriptions
list_skills()

# Refresh skills mid-session after adding new ones
refresh_skills()
```

### Dependencies for Document Skills

See `/workspace_paralegal/Skills/DEPENDENCIES.md` for full package list. Key requirements:

```bash
# Python
pip install pypdf pdfplumber reportlab openpyxl pillow defusedxml pyyaml

# Node.js
npm install -g docx pptxgenjs playwright sharp

# System
apt-get install pandoc libreoffice poppler-utils
```

---

## Tools Architecture

### Philosophy: Standalone Scripts, Not Context-Loaded Tools

**Why standalone scripts instead of traditional tools:**
- ✅ **Zero context bloat** - Tools not loaded until needed
- ✅ **Terminal output processing** - Agent can grep/filter large results
- ✅ **Dynamic discovery** - Add tools without redeploying agent
- ✅ **Token efficiency** - Saves 500-1300 tokens per tool per message
- ✅ **Composable** - Tools work with Unix pipes

### Tools Directory Structure

```
/workspace_paralegal/Tools/
├── tools_manifest.json       # Master registry
├── README.md                 # Documentation
│
├── research/                 # General research (FREE)
│   ├── internet_search.py    # Tavily web search
│   └── expert_witness_lookup.py
│
├── medical_research/         # Medical/academic (FREE)
│   ├── pubmed_search.py      # 39M+ citations
│   └── semantic_scholar_search.py
│
├── legal_research/           # CourtListener API (FREE)
│   ├── search_case_law.py
│   ├── explore_citations.py
│   ├── get_opinion_full_text.py
│   ├── find_my_cases.py
│   ├── get_docket_details.py
│   └── monitor_upcoming_dates.py
│
├── document_processing/      # PDF extraction
│   ├── read_pdf.py
│   ├── import_documents.py
│   └── batch_import_all.py
│
├── reporting/                # Case reports
│   ├── active_negotiations_report.py
│   └── outstanding_medical_bills_report.py
│
├── _generated/               # Agent-generated scripts (temporary)
└── _archive/                 # Deprecated tools
```

### Tool Pattern

All tools follow this standardized pattern:

```python
#!/usr/bin/env python3
"""Tool description with usage examples."""

import argparse
import json
import sys

def tool_function(query: str, **kwargs) -> dict:
    """Core function."""
    try:
        results = do_something(query)
        return {"success": True, "query": query, "results": results}
    except Exception as e:
        return {"error": f"Tool failed: {str(e)}", "query": query}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Query string")
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    
    result = tool_function(args.query, max_results=args.max_results)
    print(json.dumps(result, indent=2 if args.pretty else None))
    sys.exit(0 if "success" in result else 1)

if __name__ == "__main__":
    main()
```

---

## Script Execution

### Overview

Scripts from `/Tools/` can be executed in two modes:
1. **Native Mode** (default on VM): Scripts run directly via Python subprocess
2. **Docker Mode**: Scripts run in isolated containers (requires Docker images)

The execution mode is controlled by `SCRIPT_EXECUTION_MODE` environment variable:
- `auto` (default): Try Docker first, fall back to native if unavailable
- `native`: Always use native Python subprocess
- `docker`: Always use Docker (fails if unavailable)

### Native Execution (Current Production Setup)

Scripts run directly on the VM with the host Python interpreter:
- ✅ No Docker required
- ✅ Full access to workspace at `/mnt/workspace`
- ✅ Environment variables passed from agent process
- ✅ Works immediately without image builds

### Docker Execution (Optional)

For isolated execution, build Docker images via `docker/roscoe-python-runner/build.sh`:

| Image | Base | Purpose |
|-------|------|---------|
| `roscoe-python-runner:latest` | Python 3.11-slim | Standard script execution |
| `roscoe-python-runner:playwright` | Extends latest | Browser automation with Chromium |

### Agent Tools

```python
# Standard execution (auto-detects Docker vs native)
execute_python_script(
    script_path="/Tools/create_file_inventory.py",
    case_name="Wilson-MVA-2024",
    script_args=["--output", "Reports/result.json"],
    timeout=300
)

# Browser automation (requires Docker + Playwright image)
execute_python_script_with_browser(
    script_path="/Tools/web_scraping/courtlistener_search.py",
    script_args=["personal injury", "Kentucky"],
    timeout=600
)

# Check current execution mode
check_script_execution_mode()  # Returns diagnostic info
```

### Execution Flow

1. Agent calls `execute_python_script` tool
2. Script path validated against workspace
3. Mode determined: Docker (if available) or native subprocess
4. API keys passed via environment variables
5. Output captured (stdout/stderr) with mode indicator (🐳 Docker / 🐍 native)
6. Execution logged to `/Database/script_execution_logs/`

---

## Knowledge Graph (Graphiti)

### Overview

Roscoe uses **Graphiti** for semantic case memory, replacing direct JSON file writes with a knowledge graph backend.

**Backend:** FalkorDB (graph database)
**Embedding Model:** sentence-transformers (all-MiniLM-L6-v2)
**Purpose:** Track case entities, relationships, and temporal state changes

### Architecture

```
Agent → update_case_data() → Graphiti Client → FalkorDB
                                              ↓
                                    Episodes + Entities + Facts
                                              ↓
Agent ← query_case_graph() ← Semantic Search ← Graph
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Episodes** | Timestamped events (e.g., "Dr. Smith performed surgery on 2024-03-15") |
| **Entities** | People, organizations, documents (e.g., "Dr. John Smith", "UK Hospital") |
| **Facts** | Relationships and attributes (e.g., "Wilson treated by Dr. Smith") |
| **Temporal State** | Time-aware queries for case history |

### Agent Tools

```python
# Record case updates to knowledge graph (creates episodes)
update_case_data(
    case_name="Wilson-MVA-2024",
    data={"provider": "Dr. Smith", "diagnosis": "L4-L5 herniation"},
    source_type="medical_record",
    source_id="spine_mri_2024_03_15.pdf"
)

# Search knowledge graph with natural language
query_case_graph(
    case_name="Wilson-MVA-2024",
    query="What medical providers treated the patient?"
)

# Direct Cypher queries for structural lookups
graph_query(
    query_name="cases_by_provider",  # Pre-defined in workflow_state_computer.py
    params={"provider_name": "Dr. Smith"}
)

# Link documents to entities
associate_document(
    case_name="Wilson-MVA-2024",
    document_path="/Medical Records/spine_mri.pdf",
    entity_ids=["dr_smith", "uk_hospital"]
)
```

### Migration from JSON Files

**Before (JSON):**
```python
# Agent directly writes to notes.json
write_file("/projects/Wilson-MVA-2024/notes.json", updated_notes)
write_file("/Database/master_lists/notes.json", master_notes)
```

**After (Knowledge Graph):**
```python
# Agent records to graph, system syncs to JSON if needed
update_case_data(
    case_name="Wilson-MVA-2024",
    data=note_data,
    source_type="user_note"
)
```

**Benefits:**
- ✅ Semantic search across all case data
- ✅ Temporal queries ("What changed since last week?")
- ✅ Automatic entity extraction and linking
- ✅ No duplicate data in multiple JSON files
- ✅ Relationship inference (e.g., provider networks)

---

## Hybrid Graph Architecture

### Two-Layer Design

Roscoe uses a **hybrid approach** for graph management:

**Layer 1: Structured Core (Direct Cypher - 65%)**
- Entities: Case, Client, Claim, Provider, Lien
- Workflow State: Phase, Landmark status, progress
- Deterministic relationships
- Module: `src/roscoe/core/graph_manager.py`

**Layer 2: Unstructured Layer (Graphiti - 35%)**
- Entities: Note, Episode
- Operations: Semantic search, community summaries
- Module: `src/roscoe/core/graphiti_client.py`

### When to Use Each

| Operation | Module | Reason |
|-----------|--------|--------|
| Create Case | graph_manager | Structured form data |
| Create Claim | graph_manager | Structured insurance data |
| Update Phase | graph_manager | State machine logic |
| Update Landmark | graph_manager | Deterministic verification |
| Add Note | graphiti_client | Unstructured communication |
| Search Notes | graphiti_client | Semantic search |
| Case Summary | graphiti_client | LLM aggregation |

### Example Usage

```python
# Structured: Use Direct Cypher
from roscoe.core.graph_manager import create_case, create_biclaim

case_name = await create_case("Elizabeth Lindsey", "2024-12-01", "MVA")
await create_biclaim(case_name, "12345", "Progressive", "Jennifer Howard")

# Unstructured: Use Graphiti
from roscoe.core.graphiti_client import add_case_episode

await add_case_episode(
    case_name=case_name,
    episode_name="Adjuster Call",
    episode_body="Spoke with adjuster - PIP exhausted, $10k paid total"
)
```

---

## Workflow Engine

### Overview

The workflow engine provides **deterministic, graph-based workflow state** for personal injury cases, replacing hallucinated guidance with structured phase/landmark tracking.

**Location:** `workspace/workflow_engine/schemas/`
**State Computer:** `src/roscoe/core/workflow_state_computer.py`
**Middleware:** `src/roscoe/core/workflow_middleware.py`

### Architecture

```
Phases (Intake → Pre-Lit → Litigation → Settlement → Closed)
   ↓
Workflows (per phase: Medical Analysis, Demand Package, Discovery)
   ↓
Landmarks (checkpoints: Retainer Signed, MMI Reached, Complaint Filed)
   ↓
Skills + Templates (resources for completing landmarks)
```

### Workflow State Computation

**Input:** Case data from JSON files (overview.json, notes.json, etc.)
**Process:** Graph traversal with rule-based state computation
**Output:** Current phase, completed landmarks, next actions, blockers

```python
# Agent tool: Get formatted workflow status
get_case_workflow_status(case_name="Wilson-MVA-2024")
# Returns: Current phase, progress %, next actions, blockers

# Agent tool: Update landmark status
update_landmark(
    case_name="Wilson-MVA-2024",
    workflow_name="intake",
    landmark_name="retainer_signed",
    status="complete"
)

# Agent tool: Advance to next phase
advance_phase(case_name="Wilson-MVA-2024")
# Checks blockers, advances if criteria met
```

### Deterministic Rules

| Phase | Entry Criteria | Blockers |
|-------|---------------|----------|
| Intake | Case created | Missing retainer signature |
| Pre-Litigation | Retainer signed, liability clear | MMI not reached |
| Litigation | Demand rejected OR statute approaching | Complaint not filed |
| Settlement | Negotiation active | Authorization not received |
| Closed | Settlement paid OR case dismissed | N/A |

### Resource Injection

WorkflowMiddleware injects phase-specific resources into the system prompt:

```
Current Phase: Pre-Litigation
Next Actions:
  1. Complete medical records analysis (use skill: medical-records-analysis)
  2. Draft demand letter (template: /Templates/demand_letter.docx)
  3. Calculate damages (use skill: damages-calculator)

Blockers:
  - Waiting on final medical bill from UK Hospital
```

---

## Frontend (roscoe-ui)

### Technology Stack

- **Next.js 16** with App Router (Turbopack dev server)
- **React 19** with custom hooks
- **Tailwind CSS 4** for styling
- **Radix UI** primitives
- **Zustand** for state management
- **TipTap** for rich text editing
- **react-pdf** for PDF viewing

### Architecture

```
roscoe-ui/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Main workbench UI
│   │   └── globals.css         # Tailwind + CSS variables
│   ├── components/
│   │   ├── chat/               # Chat panel components
│   │   ├── workbench/          # File browser, document viewer
│   │   └── ui/                 # Radix-based UI primitives
│   ├── hooks/
│   │   ├── use-artifact-listener.ts  # SSE artifact streaming
│   │   └── use-langgraph-client.ts   # Direct LangGraph integration
│   ├── lib/
│   │   └── langgraph-client.ts # SSE connection to LangGraph API
│   └── stores/
│       └── workbench-store.ts  # Zustand state (files, artifacts)
└── package.json
```

### Custom Lean UI (No CopilotKit)

The UI connects **directly to the LangGraph API** via Server-Sent Events (SSE), without CopilotKit:

**LangGraph Client** (`lib/langgraph-client.ts`):
```typescript
export class LangGraphClient {
  streamThread(threadId: string, input: any): EventSource {
    const url = `${LANGGRAPH_API_URL}/threads/${threadId}/runs/stream`;
    return new EventSource(url);
  }
}
```

**Chat Integration** (`hooks/use-langgraph-client.ts`):
```typescript
// Direct SSE connection to LangGraph
const eventSource = langgraphClient.streamThread(threadId, userMessage);
eventSource.onmessage = (event) => {
  const parsed = JSON.parse(event.data);
  // Handle agent messages, tool calls, artifacts
};
```

**Benefits:**
- ✅ Zero dependency on CopilotKit SDK
- ✅ Full control over streaming protocol
- ✅ Custom artifact rendering
- ✅ Lightweight and fast

### Generative UI

The agent can generate UI artifacts via streaming. The `render_ui_script` tool executes Python scripts that output UI component data:

```python
# Agent calls render_ui_script with a UI script path
render_ui_script(
    script_path="UI/case_dashboard.py",
    script_args=["--case-name", "Wilson-MVA-2024"]
)
```

UI scripts output JSON with component name and data:

```python
# Example UI script output
output_result({
    "component": "CaseDashboard",
    "data": {
        "case_name": "Wilson",
        "status": "Active",
        "damages": {...}
    }
})
```

Frontend renders via artifact listener:
```typescript
// hooks/use-artifact-listener.ts
useEffect(() => {
  eventSource.onmessage = (event) => {
    if (event.data.type === "artifact") {
      const artifact = JSON.parse(event.data.content);
      workbenchStore.addArtifact(artifact);
    }
  };
}, [eventSource]);
```

Available UI components:
- File browser with workspace navigation
- PDF viewer with page controls
- Markdown renderer with syntax highlighting
- Rich text editor (TipTap) for note-taking
- Custom artifact rendering (charts, tables, dashboards)

---

## Workspace Structure

### Production Layout (`/mnt/workspace`)

```
/mnt/workspace/                     # GCS mount (whaley_law_firm bucket)
├── Database/                       # JSON databases
│   ├── caselist.json              # Master case list
│   ├── clients.json               # Client information
│   ├── directory.json             # Master contact list
│   ├── overview.json              # Case overviews
│   ├── master_lists/              # Aggregated data
│   │   ├── notes.json
│   │   ├── expenses.json
│   │   ├── insurance.json
│   │   ├── liens.json
│   │   ├── medical_providers.json
│   │   ├── pleadings.json
│   │   └── project_contacts.json
│   └── script_execution_logs/     # Audit logs
│
├── Reports/                        # Centralized analysis outputs
│   ├── extractions/               # Individual document extractions
│   ├── frames/                    # Video frame extracts
│   └── *.md                       # Analysis reports
│
├── Tools/                          # Executable Python scripts
│   ├── research/
│   ├── medical_research/
│   ├── legal_research/
│   ├── document_processing/
│   ├── reporting/
│   └── tools_manifest.json
│
├── Skills/                         # Self-contained skill folders
│   ├── DEPENDENCIES.md            # Package requirements for all skills
│   ├── medical-records-analysis/  # Native: Medical analysis pipeline
│   ├── legal-research/            # Native: Tavily search
│   ├── pdf/                       # Claude: PDF manipulation
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── *.md docs
│   ├── docx/                      # Claude: Word documents
│   ├── xlsx/                      # Claude: Spreadsheets
│   ├── pptx/                      # Claude: Presentations
│   ├── canvas-design/             # Claude: Visual design
│   └── theme-factory/             # Claude: Theme styling
│
├── Memories/                       # User preferences and workflows
│
└── projects/                       # Individual case folders
    └── {Case-Name}/               # 8-bucket organization
        ├── case_information/      # Generated summaries (read-only)
        ├── Client/                # Intake docs, contracts
        ├── Investigation/         # Photos, reports, evidence
        ├── Medical Records/       # Clinical notes
        ├── Insurance/             # Dec pages, EOBs
        ├── Lien/                  # Lien notices
        ├── Expenses/              # Case costs
        ├── Negotiation Settlement/
        ├── Litigation/            # Court filings
        └── *.json                 # Project-specific databases
```

### Path Conventions

```python
# ✅ CORRECT - Use workspace-relative paths
read_file("/Reports/case_facts.md")
ls("/projects/Wilson-MVA-2024/Medical Records/")
write_file("/Reports/summary.md", content)

# ❌ WRONG - Never use absolute system paths
read_file("/Volumes/X10 Pro/Roscoe/workspace_paralegal/Reports/case_facts.md")
```

---

## Deployment

### Production Architecture (Google Cloud VM)

The production deployment runs on a Google Cloud VM (`roscoe-paralegal-vm`) with:
- **Agent**: Docker container with mounted source code (no rebuild needed)
- **UI**: Dev server running directly on VM (instant hot-reload)

```
VM: roscoe-paralegal-vm (us-central1-a)
├── /home/aaronwhaley/
│   ├── roscoe/                    # Agent source code (synced from local)
│   │   └── src/roscoe/            # Mounted into agent container
│   ├── roscoe-ui/                 # UI source (runs via npm run dev)
│   │   ├── .env.local             # ROSCOE_LANGGRAPH_URL=http://localhost:8123
│   │   └── node_modules/          # npm dependencies
│   ├── docker-compose.yml         # Container orchestration (agent, postgres, redis)
│   └── .env                       # Environment variables (API keys)
└── /mnt/workspace/                # GCS bucket mount (whaley_law_firm)
```

### Request Flow

```
┌──────────────────┐     /api/chat     ┌─────────────────────────┐
│   Browser        │ ─────────────────▶│  roscoe-ui (Next.js)    │
│   (User)         │                   │  Dev server, port 3000  │
└──────────────────┘                   │  (npm run dev on VM)    │
                                       └────────────┬────────────┘
                                                    │
                                                    │ CopilotKit LangGraphAgent
                                                    │ → http://localhost:8123
                                                    ▼
                                       ┌─────────────────────────┐
                                       │  roscoe-agents          │
                                       │  LangGraph API Server   │
                                       │  Docker, port 8000      │
                                       │  (host: 8123)           │
                                       └────────────┬────────────┘
                                                    │
                              ┌─────────────────────┼─────────────────────┐
                              ▼                     ▼                     ▼
                    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
                    │  roscoe-postgres │  │  roscoe-redis    │  │  /mnt/workspace  │
                    │  Checkpointing   │  │  Caching         │  │  GCS mount       │
                    └──────────────────┘  └──────────────────┘  └──────────────────┘
```

**Important:**
- The UI runs in **dev mode directly on the VM** (not Docker) for instant hot-reload
- The UI connects via **direct SSE** to `http://localhost:8123` (LangGraph API)
- **No CopilotKit** - custom lean UI with direct LangGraph protocol integration
- The `roscoe-copilotkit` container may exist but is **deprecated and unused**

### Docker Containers

| Container | Image | Port (host→container) | Purpose |
|-----------|-------|----------------------|---------|
| roscoe-agents | agwhaley/roscoe-agents:latest | 8123→8000 | LangGraph API server (primary) |
| roscoe-postgres | postgres:15-alpine | 5432→5432 | LangGraph checkpointing |
| roscoe-redis | redis:7-alpine | 6379→6379 | Caching |
| roscoe-falkordb | falkordb/falkordb:latest | 6380→6379 | Knowledge graph backend (Graphiti) |

### UI Dev Mode (Production)

The UI runs in **dev mode directly on the VM** (not in Docker), enabling instant hot-reload on file changes:

```
VM: roscoe-paralegal-vm
├── /home/aaronwhaley/roscoe-ui/     # UI source code
│   ├── .env.local                   # NEXT_PUBLIC_LANGGRAPH_API_URL=http://localhost:8123
│   └── node_modules/                # npm dependencies installed
└── npm run dev                      # Running via nohup, port 3000
```

**Benefits:**
- ✅ No Docker rebuild for UI changes
- ✅ Hot reload in ~1 second after `scp`
- ✅ Same behavior as local development

### Source Code Mounting

Source code is mounted from VM filesystem into containers, allowing code updates without rebuilding images:

```yaml
# roscoe-agents container (LangGraph API)
# The image loads code from /deps/Roscoe/src/roscoe
volumes:
  - /home/aaronwhaley/roscoe/src/roscoe:/deps/Roscoe/src/roscoe
  - /mnt/workspace:/mnt/workspace
  - /mnt/workspace:/app/workspace_paralegal

# roscoe-copilotkit container (legacy, uses site-packages path)
volumes:
  - /home/aaronwhaley/roscoe/src/roscoe:/usr/local/lib/python3.11/site-packages/roscoe
  - /mnt/workspace:/mnt/workspace
```

### UI Configuration

The UI runs in dev mode directly on the VM and connects to the LangGraph API via `.env.local`:

```bash
# /home/aaronwhaley/roscoe-ui/.env.local
NEXT_PUBLIC_LANGGRAPH_API_URL=http://localhost:8123
```

The UI uses a custom LangGraph client (`lib/langgraph-client.ts`) for direct SSE connection:

```typescript
const LANGGRAPH_API_URL = process.env.NEXT_PUBLIC_LANGGRAPH_API_URL || "http://localhost:8123";

export class LangGraphClient {
  async createThread(): Promise<Thread> {
    return fetch(`${LANGGRAPH_API_URL}/threads`, { method: "POST" });
  }

  streamRun(threadId: string, input: any): EventSource {
    return new EventSource(`${LANGGRAPH_API_URL}/threads/${threadId}/runs/stream`);
  }
}
```

**Note:**
- No CopilotKit SDK - direct LangGraph protocol integration
- Since UI runs on the VM host (not in Docker), it uses `localhost:8123`
- Environment variable must be `NEXT_PUBLIC_*` for client-side access

### Syncing Code to VM

```bash
# Sync entire roscoe source to VM (for agent code changes)
gcloud compute scp --recurse "/Volumes/X10 Pro/Roscoe/src/roscoe" \
  aaronwhaley@roscoe-paralegal-vm:/home/aaronwhaley/roscoe/src/ \
  --zone=us-central1-a

# Sync UI file (hot-reloads automatically - NO rebuild needed!)
gcloud compute scp "/Volumes/X10 Pro/Roscoe/roscoe-ui/src/app/page.tsx" \
  aaronwhaley@roscoe-paralegal-vm:/home/aaronwhaley/roscoe-ui/src/app/page.tsx \
  --zone=us-central1-a

# Sync entire UI src folder
gcloud compute scp --recurse "/Volumes/X10 Pro/Roscoe/roscoe-ui/src" \
  aaronwhaley@roscoe-paralegal-vm:/home/aaronwhaley/roscoe-ui/ \
  --zone=us-central1-a

# Sync agent Python file
gcloud compute scp "/Volumes/X10 Pro/Roscoe/src/roscoe/agents/paralegal/tools.py" \
  aaronwhaley@roscoe-paralegal-vm:/home/aaronwhaley/roscoe/src/roscoe/agents/paralegal/tools.py \
  --zone=us-central1-a
```

### Restarting Services on VM

```bash
# Restart agent containers (picks up mounted code changes)
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  cd /home/aaronwhaley && \
  sudo docker compose restart roscoe-agents
"

# Restart UI dev server (if needed)
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  pkill -f 'next dev'; cd /home/aaronwhaley/roscoe-ui && nohup npm run dev > /tmp/ui-dev.log 2>&1 &
"

# Full restart (all services)
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  cd /home/aaronwhaley && \
  sudo docker compose down && \
  sudo docker compose up -d
"

# Check status
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  sudo docker ps --format 'table {{.Names}}\t{{.Status}}' && \
  echo '---' && \
  curl -s http://localhost:8123/ok
"
```

### UI Dev Server Management

The UI runs in dev mode directly on the VM. No Docker rebuild needed!

```bash
# Check if UI dev server is running
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  curl -s http://localhost:3000 > /dev/null && echo 'UI is running' || echo 'UI is NOT running'
"

# Start UI dev server (if not running)
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  cd /home/aaronwhaley/roscoe-ui && \
  nohup npm run dev > /tmp/ui-dev.log 2>&1 &
"

# View UI dev server logs
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  tail -50 /tmp/ui-dev.log
"

# Stop UI dev server (if needed)
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  pkill -f 'next dev' || echo 'No process found'
"
```

### UI Dependencies (One-time setup)

If `node_modules` needs to be reinstalled:

```bash
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  cd /home/aaronwhaley/roscoe-ui && \
  npm install --legacy-peer-deps
"
```

### LangGraph Configuration (`langgraph.json`)

```json
{
    "dependencies": ["."],
    "graphs": {
        "roscoe_paralegal": "./src/roscoe/agents/paralegal/agent.py:personal_assistant_agent",
        "roscoe_coding": "./src/roscoe/agents/coding/agent.py:coding_agent"
    },
    "env": ".env",
    "python_version": "3.11",
    "store": {
        "uri": "postgres://postgres:postgres@postgres:5432/postgres?sslmode=disable"
    }
}
```

### Local Development

```bash
# Run LangGraph development server locally
langgraph dev

# Run UI locally (connects to local LangGraph dev server)
cd ui && npm run dev
```

### Environment Variables

```bash
# Core agent APIs
ANTHROPIC_API_KEY=sk-...
GOOGLE_API_KEY=...
OPENAI_API_KEY=sk-...

# Research APIs
TAVILY_API_KEY=sk-...
NCBI_EMAIL=user@example.com
NCBI_API_KEY=...
COURTLISTENER_API_KEY=...

# Slack Integration
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_DEFAULT_CHANNEL=#legal-updates

# LangSmith Tracing (required for debugging)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls-...
LANGCHAIN_PROJECT=roscoe

# Google OAuth (Gmail/Calendar)
GOOGLE_CREDENTIALS_FILE=/path/to/client_secret.json  # OAuth2 credentials
GOOGLE_TOKEN_FILE=/path/to/token.json  # Cached OAuth token

# Knowledge Graph (Graphiti)
FALKORDB_HOST=localhost  # FalkorDB host
FALKORDB_PORT=6380       # FalkorDB port

# Production
WORKSPACE_DIR=/mnt/workspace
WORKSPACE_ROOT=/mnt/workspace  # Alternative name used by script executor
LANGGRAPH_DEPLOYMENT=true  # Disables shell tool for checkpointing
ROSCOE_ENABLE_SLACK_BRIDGE=true

# Script Execution Mode
SCRIPT_EXECUTION_MODE=auto  # Options: auto, native, docker

# UI (client-side, must be NEXT_PUBLIC_*)
NEXT_PUBLIC_LANGGRAPH_API_URL=http://localhost:8123
```

---

## Development Commands

### Local Development

```bash
# Install Python dependencies
uv sync

# Run LangGraph development server (port 2024)
langgraph dev

# Run frontend (separate terminal, port 3000)
cd ui && npm run dev --turbopack
```

**Note:** The UI uses Turbopack for faster dev server startup and hot-reload.

### Docker Image Building

```bash
# Build script execution images
cd docker/roscoe-python-runner
./build.sh

# Images created:
# - roscoe-python-runner:latest
# - roscoe-python-runner:playwright
```

### Testing

```bash
# Test Docker images
docker run --rm roscoe-python-runner:latest python -c "import pandas; print('OK')"

# Test with workspace mount
docker run --rm -v /mnt/workspace:/workspace:rw \
  roscoe-python-runner:latest python /workspace/Tools/test_python.sh
```

---

## Key Design Principles

1. **Dynamic Skill Loading**: Skills loaded semantically based on user request, not hardcoded
2. **Zero-Code Skill Addition**: Add unlimited skills by editing files, no deployment needed
3. **Automatic Context Injection**: Case context loaded when client names mentioned
4. **Parallel Sub-Agent Processing**: Spawn multiple sub-agents for batch work
5. **Centralized Reporting**: All outputs go to `/Reports/` directory
6. **Citation Integrity**: Every factual claim must cite source document + page/timestamp
7. **Workspace Sandboxing**: All operations scoped to workspace root with virtual paths
8. **Token Efficiency**: Only relevant skills loaded per conversation
9. **Docker Isolation**: Script execution in containers with resource limits
10. **Generative UI**: Rich interactive components for data visualization

---

## Common Patterns

### Spawning Sub-Agents

```python
# Main agent spawns 3-4 record-extractors simultaneously
# Each processes 1-2 documents
# Main agent synthesizes extraction reports into chronology
```

### Case Lookup Workflow

```python
# 1. Search caselist.json to find project name
# 2. Read project's overview.json from project folder
# 3. Load project-specific JSON files for detailed data
# 4. Access case folder at /projects/{project-name}/
```

### Recording Notes

```python
# ALWAYS write to project-specific notes.json first
write_file("/projects/{case-name}/notes.json", note_data)

# THEN update master notes.json
write_file("/Database/master_lists/notes.json", updated_master)
```

### Medical Records Pipeline

1. Spawn fact-investigator → reads litigation folder (Gemini 3 Pro)
2. Spawn organizer → scans medical_records/ (Haiku)
3. Spawn 3-4 record-extractors in parallel → each reads 1-2 files (Sonnet)
4. Main agent synthesizes extractions into chronology
5. Spawn analysis agents (inconsistency, red-flag, causation, missing-records)
6. Spawn summary-writer → creates FINAL_SUMMARY.md (Sonnet)

---

## File Organization Summary

```
/Volumes/X10 Pro/Roscoe/
├── src/roscoe/                    # Source code (src layout)
│   ├── core/                      # Shared infrastructure
│   │   ├── skill_middleware.py    # Semantic skill selection
│   │   └── case_context_middleware.py
│   ├── agents/
│   │   ├── paralegal/             # Main paralegal agent
│   │   │   ├── agent.py           # Agent entry point
│   │   │   ├── models.py          # Model configuration
│   │   │   ├── prompts.py         # System prompts
│   │   │   ├── tools.py           # Agent tools
│   │   │   ├── sub_agents.py      # Multimodal sub-agent
│   │   │   ├── script_executor.py # Docker execution
│   │   │   └── skills_manifest.json
│   │   └── coding/                # Coding agent (planned)
│   ├── workflow_engine/           # State machine orchestrator
│   │   └── orchestrator/
│   │       └── state_machine.py   # PI case lifecycle management
│   ├── copilotkit_server.py       # Legacy CopilotKit server (unused)
│   └── slack_launcher.py          # Slack bridge auto-start
│
├── ui/                            # Next.js frontend (Custom Lean UI)
│   └── src/
│       ├── app/
│       │   ├── api/chat/route.ts  # LangGraph proxy
│       │   ├── layout.tsx         # App layout
│       │   └── page.tsx           # Main workbench UI
│       ├── components/            # UI components
│       │   ├── chat/              # Chat panel components
│       │   ├── workbench/         # File browser, viewers
│       │   └── ui/                # Shadcn UI primitives
│       ├── hooks/                 # React hooks
│       ├── lib/                   # Utilities
│       │   └── langgraph-client.ts # Direct LangGraph SSE client
│       └── stores/                # Zustand stores
│
├── docker/roscoe-python-runner/   # Script execution images
│   ├── Dockerfile                 # Base image
│   ├── Dockerfile.playwright      # Browser automation
│   └── build.sh                   # Build script
│
├── workspace/                     # Runtime workspace (GCS mirror)
│   ├── Database/                  # JSON databases
│   ├── Skills/                    # Self-contained skill folders
│   ├── Tools/                     # Executable scripts
│   ├── Reports/                   # Analysis outputs
│   ├── workflow_engine/           # Workflow schemas and definitions
│   │   ├── schemas/               # JSON schemas
│   │   ├── checklists/            # Checklist templates
│   │   └── templates/             # Document templates
│   └── projects/                  # Case folders
│
├── langgraph.json                 # LangGraph Cloud config
├── pyproject.toml                 # Python dependencies
└── CLAUDE.md                      # This file
```

---

## Troubleshooting

### "'NoneType' object has no attribute 'bind_tools'" Error

This means a model variable is `None`. The module-level model variables are `None` by design.

```python
# ❌ WRONG - These are None!
from roscoe.agents.paralegal.models import agent_llm, multimodal_llm

# ✅ CORRECT - Use getter functions
from roscoe.agents.paralegal.models import get_agent_llm, get_multimodal_llm
```

Check `sub_agents.py` and `tools.py` to ensure they use getter functions.

### Script Execution Fails

```bash
# Check execution mode
# In agent, call: check_script_execution_mode()

# For native mode (default on VM), ensure:
# 1. Python has required packages (requests, etc.)
# 2. WORKSPACE_ROOT is set correctly
# 3. Script exists at the specified path

# For Docker mode (optional), build images:
cd docker/roscoe-python-runner && ./build.sh
```

### Skill Not Loading

```bash
# Check SKILL.md has valid YAML frontmatter
python -c "
import yaml
with open('workspace_paralegal/Skills/skill-name/SKILL.md') as f:
    content = f.read()
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        yaml_content = content[3:yaml_end]
        print(yaml.safe_load(yaml_content))
"

# Verify skill folder has SKILL.md (or skill.md)
ls workspace_paralegal/Skills/skill-name/SKILL.md  # Case-insensitive match

# Check similarity threshold (may need to lower)
# In agent.py: similarity_threshold=0.3

# Refresh skills mid-session (if added new skill)
# Agent can call: refresh_skills()
```

### Case Context Not Injecting

```bash
# Check caselist.json exists
cat /mnt/workspace/Database/caselist.json | head

# Verify fuzzy threshold (default 80)
# Names must match above threshold
```

### UI Connection Issues

```bash
# Test LangGraph API from VM
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  curl -s http://localhost:8123/ok
"
# Should return: {"ok":true}

# Test UI is running
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  curl -s http://localhost:3000 | head -1
"

# Check UI .env.local config
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  cat /home/aaronwhaley/roscoe-ui/.env.local
"
# Should show: ROSCOE_LANGGRAPH_URL=http://localhost:8123

# Restart UI dev server
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  pkill -f 'next dev'
  cd /home/aaronwhaley/roscoe-ui && nohup npm run dev > /tmp/ui-dev.log 2>&1 &
  sleep 3
  tail -10 /tmp/ui-dev.log
"
```

### LangSmith Not Showing Traces

```bash
# Verify environment variables in docker-compose.yml (roscoe-agents service):
LANGCHAIN_TRACING_V2: 'true'
LANGSMITH_API_KEY: lsv2_pt_...
LANGCHAIN_PROJECT: roscoe

# Restart agent container after changing env
sudo docker compose restart roscoe-agents
```

### Restarting Services on VM (Production)

```bash
# Check all container status (agent, postgres, redis - NOT UI)
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  sudo docker ps --format 'table {{.Names}}\t{{.Status}}'
"

# Restart agent (picks up mounted code changes)
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  cd /home/aaronwhaley && sudo docker compose restart roscoe-agents
"

# Restart UI dev server (runs outside Docker)
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  pkill -f 'next dev'
  cd /home/aaronwhaley/roscoe-ui && nohup npm run dev > /tmp/ui-dev.log 2>&1 &
"

# Full restart of Docker services (agent, postgres, redis)
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  cd /home/aaronwhaley && sudo docker compose down && sudo docker compose up -d
"
```

### Local Development

```bash
# Run LangGraph development server locally
langgraph dev

# Run UI locally (in ui directory)
cd ui && npm run dev --turbopack
```

### Knowledge Graph Issues

```bash
# Check FalkorDB connection
docker exec roscoe-falkordb redis-cli -p 6379 PING
# Should return: PONG

# View Graphiti logs
# Check agent logs for Graphiti errors (KeyError, connection issues)

# Reset knowledge graph (if corrupted)
docker exec roscoe-falkordb redis-cli -p 6379 FLUSHALL
# WARNING: This deletes ALL graph data!

# Test knowledge graph tools
# In agent: call update_case_data() to add test episode
# Then call query_case_graph() to verify retrieval
```

### UI Build Issues

```bash
# Clear Next.js cache and rebuild
cd ui
rm -rf .next node_modules
npm install --legacy-peer-deps
npm run dev --turbopack

# If Tailwind not working, check:
# - tailwind.config.ts uses @tailwindcss/postcss v4
# - No conflicting Tailwind versions in package.json
```
