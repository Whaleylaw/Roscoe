# File Inventory

## Overview
Complete inventory of all files in the Whaley Law Firm DeepAgent system (Backend + Frontend).

---

## Backend Files (Python)

| file | role | why_needed | imports | exports | reads_from | writes_to | owner |
|------|------|------------|---------|---------|------------|-----------|-------|
| `src/agents/legal_agent.py` | Main agent | Define and compile the DeepAgent graph with all tools, middleware, and configuration | deepagents, langgraph, langchain_mcp_adapters, langchain_experimental | `graph` (compiled agent) | `.env`, `src/config/settings.py`, `src/mcp/clients.py` | Supabase PostgreSQL (checkpointer, store) | Backend Team |
| `src/config/settings.py` | Configuration | Load environment variables and provide configuration utilities | os, dotenv | `DB_URI`, `get_setting()` | `.env` | None | Backend Team |
| `src/mcp/clients.py` | MCP clients | Initialize and configure all MCP server clients (Supabase, Tavily, Gmail, Calendar) | langchain_mcp_adapters | `supabase_tools`, `tavily_tools`, `gmail_tools`, `calendar_tools` | `.env`, `src/config/settings.py` | None | Backend Team |
| `langgraph.json` | Deployment config | Configure LangGraph deployment settings (checkpointer, store, dependencies) | N/A (JSON) | N/A | `.env` | None | Backend Team |
| `pyproject.toml` | Dependencies | Define Python package dependencies and project metadata | N/A (TOML) | N/A | None | None | Backend Team |
| `.env` | Secrets | Store API keys and connection strings | N/A | N/A | None | None | Backend Team |
| `README.md` | Documentation | Provide setup and usage instructions for backend | N/A (Markdown) | N/A | None | None | Backend Team |

---

## Frontend Files (TypeScript/React)

### New Components

| file | role | why_needed | imports | exports | reads_from | writes_to | owner |
|------|------|------------|---------|---------|------------|-----------|-------|
| `src/app/components/CodeExecutionBox.tsx` | Code display | Display Python code execution with syntax highlighting and status | react, react-syntax-highlighter, @/components/ui/* | `CodeExecutionBox` | Agent state (via props) | None | Frontend Team |
| `src/app/components/SkillsPanel.tsx` | Skills browser | Display and manage skills library from `/memories/skills/` | react, @/components/ui/*, SkillCard, SkillViewDialog | `SkillsPanel` | Agent state (skills field) | Chat input (populate usage example) | Frontend Team |
| `src/app/components/SkillCard.tsx` | Skill display | Display individual skill with metadata and actions | react, @/components/ui/* | `SkillCard` | SkillMetadata (via props) | None | Frontend Team |
| `src/app/components/SkillViewDialog.tsx` | Skill viewer | Dialog to view full skill source code | react, @/components/ui/*, react-syntax-highlighter | `SkillViewDialog` | SkillMetadata (via props) | None | Frontend Team |
| `src/app/components/MemoryStorePanel.tsx` | Memory browser | Tree view of persistent memory from `/memories/` | react, @/components/ui/*, MemoryTreeView, MemoryItemViewer | `MemoryStorePanel` | Agent state (memory field) | None | Frontend Team |
| `src/app/components/MemoryTreeView.tsx` | Tree navigation | Collapsible tree view for memory paths | react, @/components/ui/* | `MemoryTreeView` | Memory items (via props) | None | Frontend Team |
| `src/app/components/MemoryItemViewer.tsx` | Memory item | Display individual memory item details | react, @/components/ui/* | `MemoryItemViewer` | MemoryItem (via props) | None | Frontend Team |
| `src/app/components/MetricsPanel.tsx` | Metrics dashboard | Display token efficiency metrics and cost savings | react, @/components/ui/* | `MetricsPanel` | Agent state (metrics field) | None | Frontend Team |
| `src/app/utils/toolCategories.ts` | Tool categorization | Categorize tools by MCP server with icons and colors | None (pure utility) | `getMCPCategory()`, `CATEGORY_ICONS`, `CATEGORY_COLORS` | None | None | Frontend Team |

### Updated Components

| file | role | why_needed | imports | exports | reads_from | writes_to | owner |
|------|------|------------|---------|---------|------------|-----------|-------|
| `src/app/components/ToolCallBox.tsx` | Tool display | UPDATE: Detect `python_repl` and render CodeExecutionBox | react, @/components/ui/*, CodeExecutionBox, toolCategories | `ToolCallBox` | ToolCall (via props) | None | Frontend Team |
| `src/app/components/ChatInterface.tsx` | Main UI | UPDATE: Add tabs for Skills, Memory, Metrics panels | react, @/components/ui/*, SkillsPanel, MemoryStorePanel, MetricsPanel | `ChatInterface` | Agent state (via useChatContext) | Agent (via sendMessage) | Frontend Team |
| `src/app/hooks/useChat.ts` | State hook | UPDATE: Extend StateType to include skills, memory, metrics | @langchain/langgraph-sdk/react | `useChat` hook | LangGraph SDK stream | LangGraph API | Frontend Team |
| `src/lib/config.ts` | Config management | UPDATE: Add Supabase URL and anon key fields | None | `StandaloneConfig` interface, `getConfig()`, `saveConfig()` | localStorage | localStorage | Frontend Team |
| `src/app/types/types.ts` | Type definitions | UPDATE: Add SkillMetadata, MemoryItem, extend StateType | None | `SkillMetadata`, `MemoryItem`, `StateType` | None | None | Frontend Team |

### Existing Components (No Changes)

| file | role | why_needed | imports | exports | reads_from | writes_to | owner |
|------|------|------------|---------|---------|------------|-----------|-------|
| `src/providers/ClientProvider.tsx` | LangGraph client | Provide LangGraph SDK client to all components | @langchain/langgraph-sdk, react | `ClientProvider`, `useClient` | Config (deploymentUrl, apiKey) | None | Frontend Team |
| `src/providers/ChatProvider.tsx` | Chat context | Provide chat state and methods to components | react, useChat | `ChatProvider`, `useChatContext` | useChat hook | None | Frontend Team |
| `src/app/components/ChatMessage.tsx` | Message display | Display individual chat messages | react, @/components/ui/* | `ChatMessage` | Message (via props) | None | Frontend Team |
| `src/app/components/TasksFilesSidebar.tsx` | Sidebar | Display todos and files in sidebar | react, @/components/ui/* | `TasksFilesSidebar` | Agent state (todos, files) | None | Frontend Team |
| `src/app/components/ConfigDialog.tsx` | Configuration | Settings dialog for deployment URL and API key | react, @/components/ui/* | `ConfigDialog` | localStorage | localStorage | Frontend Team |
| `src/app/components/ThreadList.tsx` | Thread history | Display list of conversation threads | react, @/components/ui/* | `ThreadList` | LangGraph API | None | Frontend Team |
| `src/app/page.tsx` | Root page | Main application page component | react, next, ClientProvider, ChatProvider, ChatInterface | Default export | None | None | Frontend Team |
| `package.json` | Dependencies | Define npm package dependencies | N/A (JSON) | N/A | None | None | Frontend Team |
| `.env.local` | Env vars | Store public environment variables for frontend | N/A | N/A | None | None | Frontend Team |

---

## Shared Resources

| file | role | why_needed | imports | exports | reads_from | writes_to | owner |
|------|------|------------|---------|---------|------------|-----------|-------|
| Supabase PostgreSQL | Database | Persist agent state (checkpointer), long-term memory (store), case data | N/A | N/A | Backend writes, Frontend reads metadata | Backend writes | DevOps |
| LangGraph Deployment | API | Host and run the DeepAgent graph, stream state to frontend | N/A | N/A | Backend code, .env | Supabase PostgreSQL | DevOps |

---

## File Counts

- **Backend (Python)**: 7 files (5 code, 2 config)
- **Frontend (TypeScript/React)**: 20 files (9 new, 5 updated, 6 existing)
- **Shared Resources**: 2 (Database, API deployment)

**Total**: 29 files

---

## Dependencies Summary

### Backend → Backend
- `src/agents/legal_agent.py` reads from `src/config/settings.py`, `src/mcp/clients.py`
- `src/mcp/clients.py` reads from `src/config/settings.py`
- All Python files read from `.env` (via `src/config/settings.py`)

### Backend → Shared
- `src/agents/legal_agent.py` writes to Supabase PostgreSQL (checkpointer, store)
- Backend deployed to LangGraph Deployment

### Frontend → Frontend
- `ChatInterface.tsx` uses `SkillsPanel`, `MemoryStorePanel`, `MetricsPanel`
- `SkillsPanel.tsx` uses `SkillCard`, `SkillViewDialog`
- `MemoryStorePanel.tsx` uses `MemoryTreeView`, `MemoryItemViewer`
- `ToolCallBox.tsx` uses `CodeExecutionBox`, `toolCategories`
- `page.tsx` uses `ClientProvider`, `ChatProvider`, `ChatInterface`
- All components import from `@/components/ui/*` (shadcn/ui components)

### Frontend → Shared
- `ClientProvider` connects to LangGraph Deployment API
- `useChat` hook receives state stream from LangGraph Deployment
- (Optional) Direct Supabase queries from frontend (read-only with RLS)

### Shared → Shared
- LangGraph Deployment reads/writes Supabase PostgreSQL

---

## Critical Paths

### Path 1: User Message → Agent Response
```
User types in ChatInterface
  → useChat.sendMessage()
  → ClientProvider (LangGraph SDK)
  → LangGraph Deployment API
  → src/agents/legal_agent.py (DeepAgent graph)
  → Execute tools (MCP servers, python_repl)
  → Update state (skills, memory, metrics)
  → Stream state back to frontend
  → useChat hook receives update
  → ChatInterface re-renders
  → User sees response
```

### Path 2: Skills Library Display
```
Backend executes skill
  → Updates state["skills"] with metadata
  → Streams to frontend
  → useChat.stream.values.skills updated
  → SkillsPanel receives new data
  → Re-renders skill list
  → User browses skills
```

### Path 3: Code Execution Display
```
Agent calls python_repl tool
  → Includes metadata (is_skill_execution, skill_name)
  → Tool call added to messages
  → Streams to frontend
  → ChatMessage processes tool calls
  → ToolCallBox detects python_repl
  → Renders CodeExecutionBox
  → User sees syntax-highlighted code
```

---

## Notes

- All file paths are relative to project root
- Backend files assume Python 3.10+
- Frontend files assume Node.js 18+ with TypeScript
- Imports listed are high-level categories (not exhaustive)
- Owner indicates primary responsibility (can be shared)
