# File Inventory - Corrected Implementation

**Purpose**: Lists all files requiring corrections based on verification report findings
**Status**: Planning Phase - No code written yet
**Approval Required**: "Approves, spec"

---

## Files to Modify

| File | Role | Why Needed | Imports | Exports | Reads From | Writes To | Owner |
|------|------|------------|---------|---------|------------|-----------|-------|
| `src/tools/toolkits.py` | toolkit_init | Initialize LangChain Gmail/Calendar toolkits + corrected MCP clients | `GmailToolkit` from langchain-google-community, `CalendarToolkit` from langchain-google-community, `MultiServerMCPClient` from langchain_mcp_adapters | `gmail_tools`, `calendar_tools`, `supabase_tools`, `tavily_tools` | Environment variables via `src.config.settings` | None | Backend |
| `src/agents/legal_agent.py` | agent_orchestrator | Update code execution to use RunLoop sandbox | `runloop_api_client.Runloop`, remove `PythonREPLTool`, update tool list | `graph` (compiled agent) | `src.tools.toolkits`, `src.config.settings` | Agent state, PostgreSQL checkpoints | Backend |
| `src/app/utils/toolCategories.ts` | tool_categorization | Update tool name patterns for LangChain toolkits | None (pure utility) | `MCPCategory` type, `getMCPCategory`, `CATEGORY_ICONS`, `CATEGORY_COLORS` | None | None | Frontend |
| `src/components/ui/badge.tsx` | ui_component | Create missing Badge component for CodeExecutionBox | React, class-variance-authority, cn utility | `Badge` component, `BadgeProps`, `badgeVariants` | None | None | Frontend |

---

## Files Replaced/Removed

| Old File | Status | Reason | Replacement |
|----------|--------|--------|-------------|
| `src/mcp/clients.py` | REPLACED | Was using incorrect MCP approach for Gmail/Calendar | `src/tools/toolkits.py` |

---

## New Files Created

| File | Role | Why Needed | Dependencies |
|------|------|------------|--------------|
| `src/tools/__init__.py` | module_init | Python package initialization | None |
| `src/tools/toolkits.py` | toolkit_init | Centralized toolkit initialization | langchain-google-community, langchain-mcp-adapters, runloop-api-client |
| `src/tools/runloop_executor.py` | code_executor | RunLoop sandbox execution wrapper | runloop-api-client |
| `src/components/ui/badge.tsx` | ui_component | Badge component for skill execution indicators | React, class-variance-authority |

---

## External Dependencies Added

| Package | Version | Purpose | Installation |
|---------|---------|---------|--------------|
| `langchain-google-community[gmail,calendar]` | Latest | Gmail and Calendar toolkits | `pip install langchain-google-community[gmail,calendar]` |
| `runloop-api-client` | Latest | Sandboxed code execution | `pip install runloop-api-client` |

---

## External Dependencies Removed

| Package | Reason |
|---------|--------|
| `langchain-experimental` (conditional) | PythonREPLTool not found in docs; replaced with RunLoop |

---

## Configuration Changes Required

| Environment Variable | Purpose | Previous | New |
|---------------------|---------|----------|-----|
| `GMAIL_CREDENTIALS` | Gmail API OAuth | MCP server format | LangChain toolkit format (credentials.json path) |
| `GOOGLE_CALENDAR_CREDENTIALS` | Calendar API OAuth | MCP server format | LangChain toolkit format (credentials.json path) |
| `RUNLOOP_API_KEY` | RunLoop sandbox access | N/A (new) | Required for code execution |

---

## Impact Analysis

### Backend Changes
- **src/tools/toolkits.py**: Complete rewrite from MCP approach
  - Gmail: MCP → GmailToolkit (langchain-google-community)
  - Calendar: MCP → CalendarToolkit (langchain-google-community)
  - Supabase: Keep MCP but fix package name
  - Tavily: Keep MCP but fix package name
  - Code Execution: Add RunLoop executor

- **src/agents/legal_agent.py**: Update imports and tool initialization
  - Remove `PythonREPLTool` import
  - Add `RunLoopExecutor` import
  - Update tools list with new toolkit tools
  - Update system prompt to reference RunLoop instead of python_repl

### Frontend Changes
- **src/app/utils/toolCategories.ts**: Update tool name patterns
  - Gmail tools: `create_gmail_draft`, `send_gmail_message`, `search_gmail`, `get_gmail_message`, `get_gmail_thread`
  - Calendar tools: `create_calendar_event`, `search_calendar_events`, `update_calendar_event`, `get_calendars_info`, `move_calendar_event`, `delete_calendar_event`, `get_current_datetime`
  - RunLoop tools: `runloop_execute_code` (custom tool name)

- **src/components/ui/badge.tsx**: New component creation
  - No impact on existing code
  - Enables CodeExecutionBox.tsx to work

---

## Dependency Graph

```
src/agents/legal_agent.py
  └─ imports: src/tools/toolkits.py
       ├─ imports: src/tools/runloop_executor.py
       │    └─ imports: runloop_api_client.Runloop
       └─ imports: langchain-google-community.GmailToolkit
       └─ imports: langchain-google-community.CalendarToolkit
       └─ imports: langchain_mcp_adapters.MultiServerMCPClient

src/app/components/CodeExecutionBox.tsx
  └─ imports: src/components/ui/badge.tsx (NEW)
       └─ imports: class-variance-authority

src/app/utils/toolCategories.ts
  └─ (no dependencies, pure utility)
```

---

## Testing Requirements

### Backend Testing
1. Test GmailToolkit initialization with credentials.json
2. Test CalendarToolkit initialization with credentials.json
3. Test Supabase MCP with corrected package (`@supabase/mcp-server-postgrest`)
4. Test Tavily MCP with corrected package (`@mcptools/mcp-tavily`)
5. Test RunLoop executor with sample code execution
6. Verify agent compiles with new tools

### Frontend Testing
1. Test Badge component renders with all variants
2. Test toolCategories.ts correctly categorizes all new tool names
3. Test CodeExecutionBox displays with Badge component

---

## Migration Notes

### Breaking Changes
1. **Gmail/Calendar credentials format change**:
   - Old: Environment variable with JSON string for MCP
   - New: Path to credentials.json file for LangChain toolkits
   - Migration: Create credentials.json via Google API console

2. **Code execution tool interface change**:
   - Old: `python_repl` tool (synchronous, unsafe)
   - New: `runloop_execute_code` tool (async, sandboxed)
   - Migration: Update any saved skills that reference python_repl

3. **MCP server removal**:
   - Gmail MCP server: No longer used
   - Calendar MCP server: No longer used
   - Migration: Remove npx commands from deployment

### Non-Breaking Changes
1. Supabase MCP: Package name change but interface remains same
2. Tavily MCP: Package name change but interface remains same
3. Tool categorization: Internal logic change, no external API impact

---

## Validation Checklist

- [ ] All imports resolve to planned files
- [ ] All exports are consumed by dependent files
- [ ] No circular dependencies
- [ ] All environment variables documented
- [ ] All external dependencies listed with installation commands
- [ ] Migration path documented for breaking changes
- [ ] Testing requirements specified
- [ ] Dependency graph is acyclic

---

**Status**: ✅ Inventory Complete - Ready for Architecture planning
**Next Step**: Create CORRECTED-ARCHITECTURE.md
