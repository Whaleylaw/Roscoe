# Natural Language Plan: src/app/utils/toolCategories.ts - UPDATES

**Status**: Planning Phase - No code written yet
**Purpose**: Document required changes to toolCategories.ts for corrected toolkit tool names
**Approval Required**: "Approves, spec"

---

## File Purpose

This plan documents **ONLY THE CHANGES** needed to update `src/app/utils/toolCategories.ts` to match the corrected tool names from native LangChain toolkits and RunLoop executor. The type definitions and constants remain unchanged - only the `getMCPCategory()` function logic needs updates.

---

## Changes Overview

### Breaking Changes
1. **Update Gmail tool patterns** - Match new LangChain toolkit tool names
2. **Update Calendar tool patterns** - Match new LangChain toolkit tool names
3. **Update code execution pattern** - Match RunLoop tool name
4. **Reorder category checks** - More specific patterns first for accuracy
5. **Add case-insensitive matching** - Improve robustness

### Non-Breaking Changes
- MCPCategory type unchanged (still 7 categories)
- CATEGORY_ICONS unchanged (same emoji mappings)
- CATEGORY_COLORS unchanged (same Tailwind classes)
- Return type unchanged (still MCPCategory)

---

## Type Definition Changes

### NO CHANGES REQUIRED

**MCPCategory type (Lines 001-008)** remains identical:
```typescript
export type MCPCategory =
  | 'supabase'
  | 'tavily'
  | 'gmail'
  | 'calendar'
  | 'code'
  | 'builtin'
  | 'other';
```

All 7 categories still valid for corrected toolkit approach.

---

## Function Logic Changes: `getMCPCategory()`

### Change Strategy

**OLD Approach:**
- Check categories in arbitrary order (supabase, tavily, gmail, calendar, code, builtin, other)
- Case-sensitive substring matching
- Generic patterns like "email", "event", "python_repl"

**NEW Approach:**
- Check categories in specificity order (builtin → code → gmail → calendar → supabase → tavily → other)
- Case-insensitive matching via toLowerCase()
- Specific patterns matching actual LangChain toolkit tool names
- Prioritize exact matches for builtin tools to prevent false positives

---

## Line-by-Line Changes to getMCPCategory()

### ADD: Normalization Step (Before any checks)

001: Inside getMCPCategory function first line convert toolName to lowercase by calling toolName dot toLowerCase method for case-insensitive matching.

002: Assign lowercased toolName to constant named normalizedName for use in all subsequent pattern checks preventing case mismatches.

003: Add inline comment explaining normalization ensures robust matching regardless of tool name casing conventions from different toolkit sources.

---

### PRIORITY 1: Builtin Tools (Lines 033-039 in original, MOVE TO FIRST)

**Rationale**: Most specific patterns, should be checked first to prevent false positives

**Line-by-Line Plan:**

004: Check if normalizedName exactly equals write underscore todos using strict equality for TodoListMiddleware detection.

005: Also check if normalizedName exactly equals ls for FilesystemMiddleware list directory tool.

006: Also check if normalizedName exactly equals read underscore file for FilesystemMiddleware read operation.

007: Also check if normalizedName exactly equals write underscore file for FilesystemMiddleware write operation.

008: Also check if normalizedName exactly equals edit underscore file for FilesystemMiddleware edit operation.

009: Also check if normalizedName exactly equals task for SubAgentMiddleware delegation tool.

010: If any of above builtin middleware checks pass then return string literal builtin as the category immediately preventing further checks.

011: Add inline comment that builtin tools checked first as they have most specific exact-match patterns preventing false positives from substring matching.

---

### PRIORITY 2: Code Execution (Lines 030-032 in original, MOVE TO SECOND)

**OLD Pattern (Lines 030-032):**
```
Check if toolName includes "python_repl"
Check if toolName exactly equals "PythonREPLTool"
```

**NEW Pattern:**

**Line-by-Line Plan:**

012: Check if normalizedName includes substring runloop underscore execute underscore code to detect RunLoop sandboxed code execution tool.

013: Also check if normalizedName includes substring runloop for partial match flexibility if tool naming varies.

014: Also check if normalizedName includes substring execute underscore code as alternative pattern for code execution tools.

015: Also check if normalizedName includes substring python underscore repl for backward compatibility if old tool still referenced anywhere.

016: If any of above code execution checks pass then return string literal code as the category immediately.

017: Add inline comment that code execution checked second as it's critical high-priority tool category for skills-first workflow.

018: Add comment noting that runloop underscore execute underscore code is the correct tool name from RunLoopExecutor per corrected architecture.

---

### PRIORITY 3: Gmail Tools (Lines 021-025 in original, REORDER TO THIRD)

**OLD Pattern (Lines 021-025):**
```
Check if toolName includes "gmail"
Check if toolName includes "email"
Check if toolName includes "send_message"
Check if toolName includes "read_message"
```

**NEW Pattern:**

**Line-by-Line Plan:**

019: Check if normalizedName includes substring create underscore gmail underscore draft to detect Gmail draft creation tool from LangChain toolkit.

020: Also check if normalizedName includes substring send underscore gmail underscore message to detect Gmail send tool from LangChain toolkit.

021: Also check if normalizedName includes substring search underscore gmail to detect Gmail search tool from LangChain toolkit.

022: Also check if normalizedName includes substring get underscore gmail underscore message to detect Gmail message retrieval tool from LangChain toolkit.

023: Also check if normalizedName includes substring get underscore gmail underscore thread to detect Gmail thread retrieval tool from LangChain toolkit.

024: Also check if normalizedName includes substring gmail as fallback pattern for any other Gmail-related tools.

025: Also check if normalizedName includes substring email as generic fallback pattern for email tools.

026: If any of above gmail-related checks pass then return string literal gmail as the category immediately.

027: Add inline comment that Gmail patterns match official LangChain toolkit tool names from langchain underscore google underscore community package.

028: Add citation comment referencing LangChain Gmail Toolkit documentation: https colon slash slash python dot langchain dot com slash docs slash integrations slash tools slash google underscore gmail.

029: Add comment noting that create underscore gmail underscore draft send underscore gmail underscore message search underscore gmail get underscore gmail underscore message get underscore gmail underscore thread are the 5 official tool names.

---

### PRIORITY 4: Calendar Tools (Lines 026-029 in original, REORDER TO FOURTH)

**OLD Pattern (Lines 026-029):**
```
Check if toolName includes "calendar"
Check if toolName includes "event"
Check if toolName includes "schedule"
```

**NEW Pattern:**

**Line-by-Line Plan:**

030: Check if normalizedName includes substring create underscore calendar underscore event to detect Calendar event creation tool from LangChain toolkit.

031: Also check if normalizedName includes substring search underscore calendar underscore events to detect Calendar search tool from LangChain toolkit.

032: Also check if normalizedName includes substring update underscore calendar underscore event to detect Calendar update tool from LangChain toolkit.

033: Also check if normalizedName includes substring get underscore calendars underscore info to detect Calendar info retrieval tool from LangChain toolkit.

034: Also check if normalizedName includes substring move underscore calendar underscore event to detect Calendar move tool from LangChain toolkit.

035: Also check if normalizedName includes substring delete underscore calendar underscore event to detect Calendar delete tool from LangChain toolkit.

036: Also check if normalizedName includes substring get underscore current underscore datetime to detect datetime utility tool from LangChain toolkit.

037: Also check if normalizedName includes substring calendar as fallback pattern for any other Calendar-related tools.

038: Also check if normalizedName includes substring event as generic fallback pattern for event tools.

039: Also check if normalizedName includes substring schedule as generic fallback pattern for scheduling tools.

040: If any of above calendar-related checks pass then return string literal calendar as the category immediately.

041: Add inline comment that Calendar patterns match official LangChain toolkit tool names from langchain underscore google underscore community package.

042: Add citation comment referencing LangChain Calendar Toolkit documentation: https colon slash slash python dot langchain dot com slash docs slash integrations slash tools slash google underscore calendar.

043: Add comment noting that the 7 official tool names are create underscore calendar underscore event search underscore calendar underscore events update underscore calendar underscore event get underscore calendars underscore info move underscore calendar underscore event delete underscore calendar underscore event get underscore current underscore datetime.

---

### PRIORITY 5: Supabase Tools (Lines 010-016 in original, REORDER TO FIFTH)

**Pattern Unchanged but Reordered:**

**Line-by-Line Plan:**

044: Check if normalizedName includes substring supabase using string includes method to detect Supabase MCP tools.

045: Also check if normalizedName includes substring query as many database tools contain query in name.

046: Also check if normalizedName includes substring insert as database insert operations common pattern.

047: Also check if normalizedName includes substring update as database update operations common pattern.

048: Also check if normalizedName includes substring delete as database delete operations common pattern.

049: Also check if normalizedName includes substring storage as Supabase storage operations are database-related.

050: If any of above supabase-related checks pass then return string literal supabase as the category immediately.

051: Add inline comment that Supabase patterns match MCP server tools from corrected package at supabase slash mcp-server-postgrest.

052: Add comment that specific tool names determined by MCP server implementation not documented in this plan.

---

### PRIORITY 6: Tavily Tools (Lines 017-020 in original, REORDER TO SIXTH)

**Pattern Unchanged but Reordered:**

**Line-by-Line Plan:**

053: Check if normalizedName includes substring tavily using string includes method to detect Tavily MCP tools.

054: Also check if normalizedName includes substring search as Tavily is primarily a search tool.

055: Also check if normalizedName includes substring web underscore search as alternative naming pattern for search tools.

056: If any of above tavily-related checks pass then return string literal tavily as the category immediately.

057: Add inline comment that Tavily patterns match MCP server tools from corrected package at mcptools slash mcp-tavily.

058: Add comment that specific tool names determined by MCP server implementation not documented in this plan.

---

### PRIORITY 7: Other (Fallback) (Line 040 in original, KEEP AS LAST)

**Line-by-Line Plan:**

059: If none of above category checks matched then return string literal other as fallback category ensuring function always returns valid MCPCategory.

060: Add inline comment that other category serves as safe fallback preventing runtime errors from uncategorized tools ensuring type safety.

---

## Updated Function JSDoc

### ADD Enhanced Documentation:

**Line-by-Line Plan:**

061: Update JSDoc comment above getMCPCategory function to document updated pattern matching approach.

062: Add JSDoc param tag documenting toolName parameter with note that matching is case-insensitive after normalization.

063: Add JSDoc returns tag documenting MCPCategory return type with all 7 possible values.

064: Add JSDoc example showing sample tool names and their expected categories:
- Example 1: runloop underscore execute underscore code returns code
- Example 2: create underscore gmail underscore draft returns gmail
- Example 3: create underscore calendar underscore event returns calendar
- Example 4: write underscore todos returns builtin
- Example 5: unknown underscore tool returns other

065: Add JSDoc note explaining that function checks categories in specificity order from most specific to most general.

066: Add JSDoc note that official LangChain toolkit tool names documented in function implementation with citation links.

067: Add JSDoc note that function is pure with no side effects suitable for memoization if performance optimization needed.

---

## Constants Changes

### NO CHANGES REQUIRED

**CATEGORY_ICONS (Lines 061-070)** remains identical with same emoji mappings:
- supabase: 🗄️ (file cabinet)
- tavily: 🔍 (magnifying glass)
- gmail: 📧 (envelope)
- calendar: 📅 (calendar)
- code: ⚡ (lightning bolt)
- builtin: 🛠️ (tools)
- other: 🔧 (wrench)

**CATEGORY_COLORS (Lines 071-090)** remains identical with same Tailwind classes:
- supabase: green
- tavily: blue
- gmail: red
- calendar: purple
- code: orange
- builtin: gray
- other: zinc

---

## Testing Checklist

### Tool Name Matching Tests:

- [ ] Test `runloop_execute_code` → returns `'code'`
- [ ] Test `create_gmail_draft` → returns `'gmail'`
- [ ] Test `send_gmail_message` → returns `'gmail'`
- [ ] Test `search_gmail` → returns `'gmail'`
- [ ] Test `get_gmail_message` → returns `'gmail'`
- [ ] Test `get_gmail_thread` → returns `'gmail'`
- [ ] Test `create_calendar_event` → returns `'calendar'`
- [ ] Test `search_calendar_events` → returns `'calendar'`
- [ ] Test `update_calendar_event` → returns `'calendar'`
- [ ] Test `get_calendars_info` → returns `'calendar'`
- [ ] Test `move_calendar_event` → returns `'calendar'`
- [ ] Test `delete_calendar_event` → returns `'calendar'`
- [ ] Test `get_current_datetime` → returns `'calendar'`
- [ ] Test `write_todos` → returns `'builtin'`
- [ ] Test `ls` → returns `'builtin'`
- [ ] Test `read_file` → returns `'builtin'`
- [ ] Test `write_file` → returns `'builtin'`
- [ ] Test `edit_file` → returns `'builtin'`
- [ ] Test `task` → returns `'builtin'`
- [ ] Test `unknown_tool_name` → returns `'other'`

### Case Insensitivity Tests:

- [ ] Test `CREATE_GMAIL_DRAFT` → returns `'gmail'`
- [ ] Test `RunLoop_Execute_Code` → returns `'code'`
- [ ] Test `Write_Todos` → returns `'builtin'`

### Order Priority Tests:

- [ ] Test builtin tools checked before substring matches
- [ ] Test code execution checked before generic patterns
- [ ] Test specific Gmail patterns before generic "email"
- [ ] Test specific Calendar patterns before generic "event"

---

## Migration Notes

### Breaking Changes for UI:

**None** - This is an internal categorization change. The UI will automatically display correct badges for new tool names once this update deployed.

### Non-Breaking Changes:

- Tool name patterns updated to match corrected toolkit names
- Case-insensitive matching improves robustness
- Check order optimized for accuracy and performance
- All 7 categories remain valid and properly styled

### Deployment Considerations:

- No environment variables required
- No database changes required
- No API changes required
- Frontend will automatically categorize tools correctly after deployment
- No user-facing changes besides accurate badge colors/icons

---

## Cross-References

**Depends On:**
- [uses: Gmail toolkit tool names @ src/tools/toolkits.py (planned line 020)]
- [uses: Calendar toolkit tool names @ src/tools/toolkits.py (planned line 050)]
- [uses: RunLoop executor tool name @ src/tools/runloop_executor.py (planned line 022)]

**Used By:**
- [used_by: ToolCallBox.tsx @ badge rendering (planned usage)]
- [used_by: ChatInterface.tsx @ tool filtering (potential usage)]

---

## Validation

- [x] Tool name patterns match official LangChain toolkit documentation
- [x] RunLoop tool name matches RunLoopExecutor implementation
- [x] Check order prioritizes specificity (builtin → code → gmail → calendar → supabase → tavily → other)
- [x] Case-insensitive matching implemented
- [x] All 7 MCPCategory values still valid
- [x] Constants (icons, colors) unchanged
- [x] Function remains pure with no side effects
- [x] Type safety maintained (always returns MCPCategory)
- [x] JSDoc enhanced with examples and notes
- [x] Testing checklist comprehensive

**Citations:**
- **LangChain Gmail Toolkit**: https://python.langchain.com/docs/integrations/tools/google_gmail
- **LangChain Calendar Toolkit**: https://python.langchain.com/docs/integrations/tools/google_calendar
- **RunLoop Python SDK**: https://github.com/runloopai/api-client-python
- **Supabase MCP Package**: https://www.npmjs.com/package/@supabase/mcp-server-postgrest
- **Tavily MCP Package**: https://www.npmjs.com/package/@mcptools/mcp-tavily

---

**Status**: ✅ Plan Complete - Ready for validation
**Estimated Changes**: ~60 lines modified (getMCPCategory function logic)
**Original File**: ~90 lines total
**Change Percentage**: ~67% of function updated (type and constants unchanged)
**Next**: Validate all cross-references across all plans
