# Natural Language Plan: src/agents/legal_agent.py - UPDATES

**Status**: Planning Phase - No code written yet
**Purpose**: Document required changes to legal_agent.py for corrected toolkit integration
**Approval Required**: "Approves, spec"

---

## File Purpose

This plan documents **ONLY THE CHANGES** needed to update `src/agents/legal_agent.py` to use the corrected toolkit approach. This is not a complete rewrite - most of the file remains unchanged. The changes replace PythonREPLTool with RunLoopExecutor and replace MCP client imports with native LangChain toolkits.

---

## Changes Overview

### Breaking Changes
1. **Remove PythonREPLTool** → Replace with RunLoopExecutor (secure sandbox)
2. **Remove MCP client imports** → Replace with async toolkit initialization functions
3. **Update tool references** → Change `python_repl` to `runloop_execute_code` throughout system prompts

### Non-Breaking Changes
- Compilation logic unchanged
- Memory backend unchanged
- Checkpointer unchanged
- Subagent structure unchanged (only tool lists updated)

---

## Import Changes

### REMOVE (Line 007 in original plan)
```
from langchain_experimental.tools import PythonREPLTool
```
**Reason**: PythonREPLTool not found in current LangChain docs, replaced by RunLoop sandbox

### REMOVE (Line 010 in original plan)
```
from src.mcp.clients import supabase_tools, tavily_tools, gmail_tools, calendar_tools
```
**Reason**: File `src/mcp/clients.py` replaced by `src/tools/toolkits.py` with corrected approach

### ADD (New Import 1)
```
from src.tools.runloop_executor import create_runloop_tool
```
**Purpose**: Import factory function for RunLoop-based code execution tool
**Reference**: [uses: create_runloop_tool @ src/tools/runloop_executor.py (planned line 086)]

### ADD (New Import 2)
```
from src.tools.toolkits import init_gmail_toolkit, init_calendar_toolkit, init_supabase_mcp, init_tavily_mcp
```
**Purpose**: Import async initialization functions for all toolkits
**Reference**: [uses: init_gmail_toolkit @ src/tools/toolkits.py (planned line 016)]
**Reference**: [uses: init_calendar_toolkit @ src/tools/toolkits.py (planned line 046)]
**Reference**: [uses: init_supabase_mcp @ src/tools/toolkits.py (planned line 076)]
**Reference**: [uses: init_tavily_mcp @ src/tools/toolkits.py (planned line 111)]

---

## Tool Initialization Changes

### REMOVE (Lines 031-035 in original plan)
```python
# Old approach
python_repl = PythonREPLTool()
```
**Reason**: Replaced by RunLoop sandbox for security and production readiness

### ADD (New Tool Initialization)

**Line-by-Line Plan for New Tool Initialization:**

001: Add comment explaining that toolkit initialization is now async and must be called within async context before agent usage.

002: Define async function named init underscore tools with no parameters to encapsulate all toolkit initialization logic returning dictionary of tool lists.

003: Add function docstring explaining init underscore tools initializes all external toolkits and code executor returning dict with tool lists or empty lists for graceful degradation.

004: Inside init underscore tools call create underscore runloop underscore tool function to instantiate RunLoop code execution wrapper as synchronous operation.

005: Assign RunLoop tool to variable named runloop underscore tool for inclusion in tools dictionary under code executor category.

006: Add await keyword before init underscore gmail underscore toolkit call as toolkit initialization is async per corrected architecture.

007: Assign awaited Gmail toolkit result to variable named gmail underscore tools containing list of 5 Gmail tools or empty list if credentials missing.

008: Add await keyword before init underscore calendar underscore toolkit call as toolkit initialization is async per corrected architecture.

009: Assign awaited Calendar toolkit result to variable named calendar underscore tools containing list of 7 Calendar tools or empty list if credentials missing.

010: Add await keyword before init underscore supabase underscore mcp call as MCP client initialization is async per corrected architecture.

011: Assign awaited Supabase MCP result to variable named supabase underscore tools containing list of Supabase database tools or empty list if credentials missing.

012: Add await keyword before init underscore tavily underscore mcp call as MCP client initialization is async per corrected architecture.

013: Assign awaited Tavily MCP result to variable named tavily underscore tools containing list of Tavily search tools or empty list if API key missing.

014: Return dictionary with keys code executor gmail calendar supabase tavily mapped to corresponding tool lists for organized access by agent configuration.

015: Add inline comment that graceful degradation implemented in toolkit functions so missing credentials return empty lists not exceptions preventing agent startup failures.

016: Add inline comment that runloop underscore tool initialization is synchronous but toolkit initializations are async requiring await keywords per LangChain pattern.

017: Note that init underscore tools function must be awaited before creating agent so tools available for agent configuration and subagent configuration.

---

## System Prompt Changes

### Change 1: Tool Reference (Line 038 in original plan)

**BEFORE:**
```
List available tools starting with python_repl for code execution and data processing.
```

**AFTER:**
```
List available tools starting with runloop_execute_code for sandboxed code execution and data processing.
```

**Reason**: Tool name changed from `python_repl` to `runloop_execute_code` per RunLoopExecutor implementation

### Change 2: Code Execution Instruction (Line 049 in original plan)

**BEFORE:**
```
Step 3 instruction: Use python_repl for data processing with sub-instructions.
```

**AFTER:**
```
Step 3 instruction: Use runloop_execute_code for data processing in isolated sandbox with sub-instructions.
```

**Reason**: Emphasize sandboxed execution environment for security awareness

### Change 3: Subagent Prompts

**legal-researcher subagent (Line 130 in original plan)**

**BEFORE:**
```
Instruct to "Use python_repl if research produces large result sets to filter and summarize."
```

**AFTER:**
```
Instruct to "Use runloop_execute_code if research produces large result sets to filter and summarize in isolated sandbox."
```

**database-specialist subagent (Lines 151-152 in original plan)**

**BEFORE:**
```
Instruct to "Return summaries not full datasets to save tokens using python_repl for processing."
Instruct to "Use python_repl to filter and aggregate database results before returning to main agent."
```

**AFTER:**
```
Instruct to "Return summaries not full datasets to save tokens using runloop_execute_code for processing in isolated sandbox."
Instruct to "Use runloop_execute_code to filter and aggregate database results in sandbox before returning to main agent."
```

---

## Agent Configuration Changes

### Tool List Assembly (Lines 181-186 in original plan)

**BEFORE (Synchronous):**
```python
agent = create_deep_agent(
    tools=[
        python_repl,
        *supabase_tools,
        *tavily_tools,
        *gmail_tools,
        *calendar_tools
    ],
    # ... other parameters
)
```

**AFTER (Requires Async Context):**

**Line-by-Line Plan:**

001: Define async function named create underscore agent with no parameters to wrap agent creation in async context for toolkit initialization.

002: Add function docstring explaining create underscore agent initializes all toolkits and creates agent instance with async tool loading.

003: Call await init underscore tools to initialize all toolkits and code executor returning dictionary of tool lists.

004: Assign awaited toolkit result to variable named tools underscore dict for organized access to tool categories.

005: Construct flat tools list by starting with tools underscore dict get code executor which returns runloop underscore tool instance.

006: Extend tools list with unpacked tools underscore dict get gmail which returns list of Gmail tools or empty list.

007: Extend tools list with unpacked tools underscore dict get calendar which returns list of Calendar tools or empty list.

008: Extend tools list with unpacked tools underscore dict get supabase which returns list of Supabase tools or empty list.

009: Extend tools list with unpacked tools underscore dict get tavily which returns list of Tavily tools or empty list.

010: Call create underscore deep underscore agent passing assembled tools list to tools parameter for agent configuration.

011: Pass all other parameters unchanged: system underscore prompt model store backend subagents to maintain existing configuration.

012: Return created agent instance to caller for compilation with checkpointer as before.

013: Add inline comment that create underscore agent must be awaited in module-level async context or deployment startup function.

014: Add inline comment that agent creation now async due to toolkit initialization but compilation and graph export remain synchronous.

### Subagent Configuration Changes (Line 153 in original plan)

**database-specialist tools key:**

**BEFORE:**
```python
"tools": [python_repl, *supabase_tools]
```

**AFTER:**
```python
"tools": [tools_dict["code_executor"], *tools_dict["supabase"]]
```

**Reason**: Use tools from dictionary assembled in init_tools function instead of module-level constants

---

## Module-Level Execution Pattern

### OLD Pattern (Synchronous Module Loading):
```python
# Module-level initialization (all synchronous)
store = PostgresStore.from_conn_string(DB_URI)
checkpointer = PostgresSaver.from_conn_string(DB_URI)
python_repl = PythonREPLTool()
agent = create_deep_agent(...)
graph = agent.compile(checkpointer=checkpointer)
```

### NEW Pattern (Async Toolkit Loading):

**Line-by-Line Plan:**

001: Keep store initialization unchanged as PostgresStore dot from underscore conn underscore string DB underscore URI per original plan.

002: Keep checkpointer initialization unchanged as PostgresSaver dot from underscore conn underscore string DB underscore URI per original plan.

003: Remove module-level agent and graph creation since they now require async context for toolkit initialization.

004: Define async function named initialize underscore agent with no parameters to create agent in async context.

005: Inside initialize underscore agent call await create underscore agent to initialize toolkits and create agent instance.

006: Compile agent by calling agent dot compile passing checkpointer parameter for state persistence.

007: Return compiled graph from initialize underscore agent for export and deployment.

008: Add module-level comment explaining that graph must be initialized asynchronously typically in LangGraph deployment startup hook or main function.

009: Add example comment showing usage: graph equals await initialize underscore agent for deployment configuration.

010: Note that LangGraph deployment platform handles async initialization automatically when importing graph from module.

---

## Unchanged Sections

### No Changes Required For:

1. **Memory Backend (Lines 011-020)** - CompositeBackend routing unchanged
2. **Store Setup (Lines 021-025)** - PostgresStore initialization unchanged
3. **Checkpointer Setup (Lines 026-030)** - PostgresSaver initialization unchanged
4. **System Prompt Structure (Lines 036-120)** - Only tool name references changed (3 locations)
5. **Subagent Configurations (Lines 121-180)** - Structure unchanged, only tool lists updated
6. **Compilation Logic (Lines 201-210)** - agent.compile() unchanged

---

## Cross-References

**Removed Dependencies:**
- ~~[uses: PythonREPLTool @ langchain_experimental.tools]~~
- ~~[uses: supabase_tools @ src/mcp/clients.py]~~
- ~~[uses: tavily_tools @ src/mcp/clients.py]~~
- ~~[uses: gmail_tools @ src/mcp/clients.py]~~
- ~~[uses: calendar_tools @ src/mcp/clients.py]~~

**New Dependencies:**
- [uses: create_runloop_tool @ src/tools/runloop_executor.py (planned line 086)]
- [uses: init_gmail_toolkit @ src/tools/toolkits.py (planned line 016)]
- [uses: init_calendar_toolkit @ src/tools/toolkits.py (planned line 046)]
- [uses: init_supabase_mcp @ src/tools/toolkits.py (planned line 076)]
- [uses: init_tavily_mcp @ src/tools/toolkits.py (planned line 111)]

**Unchanged Dependencies:**
- [uses: get_setting @ src/config/settings.py (planned line 011)] ✓
- [uses: DB_URI @ src/config/settings.py (planned line 002)] ✓

---

## Migration Notes

### Breaking Changes for Deployment:

1. **Environment Variable Format Change**:
   - **BEFORE**: Gmail/Calendar credentials as JSON strings for MCP
   - **AFTER**: Gmail/Calendar credentials as file paths for native toolkits
   ```bash
   # Old (MCP)
   GMAIL_CREDENTIALS='{"installed":{...}}'

   # New (Native Toolkit)
   GMAIL_CREDENTIALS='/path/to/credentials.json'
   GOOGLE_CALENDAR_CREDENTIALS='/path/to/credentials.json'
   ```

2. **New Environment Variable Required**:
   ```bash
   RUNLOOP_API_KEY=your-api-key-here
   ```

3. **MCP Package Names Changed**:
   - Supabase: `@supabase/mcp-server-postgrest` (was: `@modelcontextprotocol/server-supabase`)
   - Tavily: `@mcptools/mcp-tavily` (was: `@modelcontextprotocol/server-tavily`)

4. **Async Initialization Pattern**:
   - Agent creation now requires async context
   - LangGraph deployment handles this automatically
   - For local testing: `graph = await initialize_agent()`

### Non-Breaking Changes:

- Database connection unchanged (same DB_URI)
- Checkpointer unchanged (same PostgreSQL)
- Model unchanged (claude-sonnet-4-5-20250929)
- Subagent structure unchanged
- System prompt philosophy unchanged (skills-first workflow)

---

## Testing Checklist

### Before Deployment:
- [ ] Verify RUNLOOP_API_KEY environment variable set
- [ ] Verify Gmail credentials file exists at GMAIL_CREDENTIALS path
- [ ] Verify Calendar credentials file exists at GOOGLE_CALENDAR_CREDENTIALS path
- [ ] Test RunLoop devbox creation with `create_runloop_tool()`
- [ ] Test Gmail toolkit initialization with valid credentials.json
- [ ] Test Calendar toolkit initialization with valid credentials.json
- [ ] Verify Supabase MCP package installed: `npx -y @supabase/mcp-server-postgrest`
- [ ] Verify Tavily MCP package installed: `npx -y @mcptools/mcp-tavily`
- [ ] Test agent compilation succeeds with all toolkits
- [ ] Test agent compilation succeeds with partial toolkits (graceful degradation)

### After Deployment:
- [ ] Verify code execution works in RunLoop sandbox
- [ ] Verify Gmail tools accessible to agent
- [ ] Verify Calendar tools accessible to agent
- [ ] Verify Supabase tools accessible to agent
- [ ] Verify Tavily tools accessible to agent
- [ ] Test skills-first workflow saves and executes skills
- [ ] Monitor token efficiency metrics vs. baseline

---

## Validation

- [x] Import changes documented
- [x] Tool initialization changes documented
- [x] System prompt changes documented (3 locations)
- [x] Agent configuration changes documented
- [x] Subagent changes documented
- [x] Module-level execution pattern documented
- [x] Migration notes provided
- [x] Testing checklist provided
- [x] No changes to compilation logic
- [x] Graceful degradation maintained

**Citations:**
- **RunLoop Python SDK**: https://github.com/runloopai/api-client-python
- **LangChain Gmail Toolkit**: https://python.langchain.com/docs/integrations/tools/google_gmail
- **LangChain Calendar Toolkit**: https://python.langchain.com/docs/integrations/tools/google_calendar
- **LangChain MCP Integration**: https://python.langchain.com/docs/integrations/tools/mcp

---

**Status**: ✅ Plan Complete - Ready for validation
**Estimated Changes**: ~50 lines modified (imports, tool init, prompt references)
**Original File**: ~210 lines total
**Change Percentage**: ~24% of file updated
**Next**: Create toolCategories-UPDATES.nlplan.md
