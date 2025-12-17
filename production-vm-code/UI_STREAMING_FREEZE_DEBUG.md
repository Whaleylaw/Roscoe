# UI Streaming Freeze Issue - Debug Log

**Date**: December 16, 2025
**Issue**: Frontend freezes when LangGraph agent calls `render_ui_script` tool
**Environment**: http://34.63.223.97:3001/

---

## Problem Description

### Symptoms
- ✅ **Backend works perfectly** - confirmed via LangSmith traces
- ✅ **Simple text messages render fine** (no tools)
- ❌ **UI freezes when agent calls `render_ui_script` tool**
  - Response starts streaming
  - UI shows loading spinner
  - Stream gets ~50% through, then freezes indefinitely
  - Backend completes successfully (visible in LangSmith)
  - Frontend never receives/renders the tool result or final message

### Console Warning
```
Unhandled event received: messages/metadata {lc_run--...}
```

### Reproduction Steps
1. Navigate to http://34.63.223.97:3001/
2. Send message: "Show me tomorrow's calendar using local JSON only"
3. Agent calls `render_ui_script` → UI freezes with spinner
4. Check LangSmith → backend completed successfully with calendar data

---

## Root Cause Analysis

### Confirmed via LangSmith Traces

Backend flow (from trace `019b299e-1f0e-7d00-a60c-58e1a12b88d4`):
1. User message received
2. Agent calls `render_ui_script` with args: `UI/calendar/show_day.py --date 2025-12-17 --include-roscoe true --include-google false`
3. Tool returns valid JSON:
```json
{
  "success": true,
  "title": "Calendar (2025-12-17)",
  "commands": [{
    "type": "workbench.setCenterView",
    "view": "calendar"
  }, {
    "type": "calendar.setEvents",
    "events": [{...}]
  }]
}
```
4. Agent sends final message explaining the calendar was rendered
5. **Stream completes successfully on backend**

But the frontend **never receives/renders** steps 3-5.

### Library Incompatibility

The `@assistant-ui/react-langgraph` library (v0.7.12) has known issues:
- **Issue #2166**: Doesn't handle `values` events from tool results
- **Unhandled metadata**: The `messages/metadata` events cause the stream consumer to choke
- **Partial streaming bugs**: Tool results come as complete snapshots, not streaming chunks

---

## Fixes Attempted (All Failed)

### 1. Stream Mode Changes
**File**: `ui/lib/chatApi.ts:47`

| Mode | Result |
|------|--------|
| `["messages", "updates"]` | ❌ Freeze - duplicate events |
| `["messages"]` | ❌ Freeze - missing tool results |
| `["messages", "values"]` | ❌ Freeze - library doesn't handle values |
| `["values"]` | ❌ Freeze - no streaming, only snapshots |

**Current**: `["values"]` only

### 2. JSON String Parsing
**File**: `ui/components/tools/render-ui-script-tool.tsx:40-54`

**Problem**: Backend returns tool results as JSON strings, not objects
**Fix**: Added `JSON.parse()` in `coerceCommands()` function
**Result**: ✅ Fixed parsing, but stream still freezes

### 3. Timeout Protection
**File**: `ui/app/api/[..._path]/route.ts:36`

**Added**: `signal: AbortSignal.timeout(290000)` (290s)
**Result**: ❌ Timeout doesn't fire - stream hangs before timeout

### 4. Keepalive Configuration
**File**: `ui/app/api/[..._path]/route.ts:34`

**Tried**:
- `keepalive: true` → ❌ Still freezes
- `keepalive: false` → ❌ Still freezes

**Current**: `false` (original value)

### 5. Library Updates
**Updated**:
- `@langchain/langgraph-sdk`: 1.3.0 → 1.3.1
**Result**: ❌ No change

### 6. Error Logging
**File**: `ui/app/assistant.tsx:24-33`

**Added**: Console logging for stream events
**Result**: No errors logged - stream just stops yielding

### 7. Custom Runtime (Latest Attempt)
**Files**:
- `ui/lib/useCustomLangGraphRuntime.tsx` (NEW)
- `ui/app/assistant.tsx` (modified to use custom runtime)

**Approach**: Bypass `@assistant-ui/react-langgraph` completely
- Use `useLocalRuntime` from `@assistant-ui/react`
- Manually consume SSE stream
- Parse `values` events directly
- Ignore `metadata` events

**Status**: ⏳ Deployed, needs testing (Playwright timed out loading page)

---

##Code References

### Key Files

| File | Purpose | Current State |
|------|---------|---------------|
| `ui/lib/chatApi.ts` | LangGraph API client | Stream mode: `["values"]` |
| `ui/app/assistant.tsx` | Runtime initialization | Using `useCustomLangGraphRuntime` |
| `ui/lib/useCustomLangGraphRuntime.tsx` | Custom SSE consumer | Bypasses langgraph library |
| `ui/components/tools/render-ui-script-tool.tsx` | Tool UI component | JSON parsing added |
| `ui/app/api/[..._path]/route.ts` | API proxy | Timeout + keepalive config |

### Backend Tool
**Location**: `src/roscoe/agents/paralegal/tools.py:761-905`

The `render_ui_script()` function:
- Executes Python scripts from `/mnt/workspace/Tools/UI/`
- Returns JSON via subprocess stdout
- Backend execution works perfectly (confirmed)

### Test Script
**Location**: `/mnt/workspace/Tools/UI/calendar/show_day.py`

Tested with args:
```bash
--date 2025-12-17 --days 1 --include-roscoe true --include-google false
```

Returns valid JSON every time.

---

## Network Analysis

### Successful Flow (Simple Messages)
```
POST /api/threads → 200 OK
POST /api/threads/{id}/runs/stream → 200 OK
  - Stream opens
  - Events flow
  - Stream closes naturally
  - UI updates
```

### Failed Flow (With Tools)
```
POST /api/threads → 200 OK
POST /api/threads/{id}/runs/stream → 200 OK
  - Stream opens ✅
  - Initial events flow ✅
  - Tool call event ✅
  - Tool result event... ❌ FREEZE
  - Connection hangs open
  - No more events processed
  - Backend completed (LangSmith shows full conversation)
```

### SSE Events Not Handled
Based on console warnings, these events are being sent but not processed:
- `messages/metadata` - **CRITICAL**: This causes the freeze
- Possibly other metadata events

---

## Testing Matrix

| Test Case | Backend | Frontend | Notes |
|-----------|---------|----------|-------|
| "What is 2+2?" | ✅ Works | ✅ Works | No tools, pure text |
| "Show calendar" (calls tool) | ✅ Works | ❌ Freezes | Tool result never renders |
| "Show dashboard" (calls tool) | ✅ Works | ❌ Freezes | Same freeze pattern |

Pattern: **ANY tool call causes freeze**

---

## Next Steps for Debugging

### Immediate (With Chrome DevTools MCP)

1. **Inspect Network Tab**:
   - Open http://34.63.223.97:3001/
   - Send: "Show me tomorrow's calendar using local JSON only"
   - Watch `/api/threads/{id}/runs/stream` request
   - Check if stream is still receiving data or if connection closed
   - Look for SSE events in the "EventStream" tab

2. **Check Console for Custom Runtime Logs**:
   ```
   [Custom Runtime] run() called with X messages
   [Custom Runtime] Got state with X messages
   [Custom Runtime] Ignoring metadata
   [Custom Runtime] Stream ended
   [Custom Runtime] Returning: {...}
   ```

   If these logs appear, the custom runtime is working
   If they don't appear, there's a JavaScript error

3. **Check for JavaScript Errors**:
   - Look for any red errors in Console
   - Check if `useCustomLangGraphRuntime` is defined
   - Verify no import/module errors

### If Custom Runtime Works

The freeze should be fixed! You should see:
- Tool result card appears
- Calendar iframe populates with event
- Final assistant message renders
- No infinite spinner

### If Custom Runtime Also Freezes

Possible causes:
1. **JavaScript error in convertMessage()** - check console
2. **SSE stream never closes** - check Network tab
3. **React re-render loop** - check React DevTools
4. **AbortSignal incompatibility** - try removing line 56 in `useCustomLangGraphRuntime.tsx`

---

## Workarounds (If All Else Fails)

### Option A: Polling Instead of Streaming
Change to non-streaming mode:
```typescript
// In chatApi.ts
const response = await client.runs.create(threadId, assistantId, payload);
// Poll for completion instead of streaming
```

### Option B: Separate Thread for Tools
Create a dedicated thread for tool-heavy interactions:
- Use streaming for text-only conversations
- Use polling for tool calls
- Switch based on detected tool usage

### Option C: Revert to Old UI
If the new assistant-ui doesn't work, revert to previous UI implementation (if one exists).

---

## Git Commits

Recent commits on branch `feature/roscoe-training-clean`:

| Commit | Description |
|--------|-------------|
| `60964382` | Fix UI streaming freeze by using only 'messages' stream mode |
| `a2b23728` | Fix UI streaming issues: parse JSON strings and enable keepalive |
| `ec46dee7` | Add stream error handling and update LangGraph SDK |
| `8cce19e1` | Try values-only stream mode to fix freezing |
| `28e408e1` | Implement custom LangGraph runtime bypassing library |
| `2750d37a` | Fix custom runtime API signature for useLocalRuntime |

---

## Environment Info

### Production VM
- **IP**: 34.63.223.97
- **UI Port**: 3001
- **LangGraph API**: http://roscoe:8000 (internal Docker network)

### Package Versions
```json
{
  "@assistant-ui/react": "^0.11.51",
  "@assistant-ui/react-langgraph": "^0.7.12",
  "@langchain/langgraph-sdk": "^1.3.1",
  "next": "16.0.10",
  "react": "^19.2.3"
}
```

### Docker Services
```bash
# Check UI status
docker ps | grep ui

# View logs
docker compose logs ui --tail 50

# Restart UI
docker compose restart ui
```

---

## LangSmith Access

**Project**: `roscoe-local`
**API Key**: (stored in VM `/home/aaronwhaley/.env`)

### Fetch Recent Traces
```bash
export LANGSMITH_API_KEY=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
export LANGSMITH_PROJECT="roscoe-local"
langsmith-fetch traces /tmp/traces --limit 3
```

Traces show backend completes successfully every time.

---

## Discord Post (For Assistant UI Community)

If you need help from the assistant-ui team, post this:

**Subject**: LangGraph streaming freezes when agent calls tools

**Body**: [See above - generic version without custom tool references]

Key points:
- v0.7.12 on latest packages
- `messages/metadata` warning
- Backend works (LangSmith confirmed)
- Frontend freezes mid-stream
- ANY tool call causes freeze
- Simple messages work fine

---

## Known Related Issues

1. **#2166**: https://github.com/assistant-ui/assistant-ui/issues/2166
   - Values events not being processed properly
   - Manually added messages (like tool results) emit `values` not `message:partial`
   - Library doesn't handle this

2. **#1899**: https://github.com/assistant-ui/assistant-ui/issues/1899
   - Human-in-the-loop interrupt flows not working
   - Similar streaming issues with LangGraph Python

---

## Quick Start for New Debugging Session

1. **Test if UI loads**:
   ```bash
   curl -I http://34.63.223.97:3001/
   # Should return 200 OK
   ```

2. **Check what runtime is active**:
   ```bash
   ssh to VM
   cat ~/roscoe/ui/app/assistant.tsx | grep -A 3 "import.*Runtime"
   ```

   If you see `useCustomLangGraphRuntime` → custom runtime is active
   If you see `useLangGraphRuntime` → library runtime is active

3. **Test simple message** (should work):
   - Open http://34.63.223.97:3001/
   - Send: "What is 2 plus 2?"
   - Should respond without freezing

4. **Test tool call** (will freeze):
   - Send: "Show me tomorrow's calendar using local JSON only"
   - Opens browser console (F12)
   - Watch for `[Custom Runtime]` logs or errors
   - Should freeze with spinner

5. **Check LangSmith**:
   - Visit: https://smith.langchain.com/projects/roscoe-local
   - Find the frozen run
   - Verify backend completed (it will have)

---

## Current State (As of Last Deploy)

### Active Configuration
- **Stream Mode**: `["values"]` only
- **Runtime**: `useCustomLangGraphRuntime` (custom implementation)
- **Timeout**: 290s AbortSignal
- **Keepalive**: `false`

### Files Modified (Check Git Status)
```bash
cd /Volumes/X10 Pro/Roscoe/production-vm-code
git log --oneline -10
```

Latest commits show progression of fix attempts.

### Deployment Status
- ✅ UI container rebuilt
- ✅ Latest code deployed to VM
- ⏳ Custom runtime needs browser testing (Playwright timed out)

---

## Diagnostic Commands

### Check if UI is responding
```bash
curl http://34.63.223.97:3001/ -I --max-time 5
```

### View UI logs in real-time
```bash
gcloud compute ssh roscoe-paralegal-vm --zone us-central1-a
cd ~/roscoe
docker compose logs ui -f
```

### Check which stream mode is active
```bash
gcloud compute ssh roscoe-paralegal-vm --zone us-central1-a --command "cat ~/roscoe/ui/lib/chatApi.ts | grep -A 3 'streamMode'"
```

### Test backend directly (bypass UI)
```bash
# Create thread
curl -X POST http://34.63.223.97:8123/threads -H "Content-Type: application/json" -d '{}'

# Use returned thread_id in next command:
# Stream a message (this will work)
curl -N http://34.63.223.97:8123/threads/THREAD_ID/runs/stream \
  -H "Content-Type: application/json" \
  -d '{"assistant_id":"roscoe_paralegal","input":{"messages":[{"role":"user","content":"Show tomorrow calendar local JSON only"}]},"stream_mode":["values"]}'
```

This confirms backend works - you'll see complete SSE events.

---

## Theory: Why It Freezes

Based on testing:

1. **Library expects `messages/partial` events** for streaming text
2. **Backend sends `values` events** when tools complete (full state snapshots)
3. **Library doesn't know how to process `values` events**
4. **Library also chokes on `messages/metadata` events**
5. **Stream hangs open**, frontend waiting for events it can parse
6. **Backend already closed stream**, sent `[DONE]`
7. **Frontend never sees `[DONE]`** because it stopped processing events

The custom runtime should fix this by:
- Explicitly handling `values` events
- Ignoring `metadata` events
- Consuming entire stream until `[DONE]`
- Converting final state to assistant-ui format

---

## Testing the Custom Runtime

### Expected Console Output
```
[Custom Runtime] run() called with 1 messages
[Custom Runtime] Got state with 2 messages
[Custom Runtime] Got state with 3 messages
[Custom Runtime] Got state with 4 messages
[Custom Runtime] Ignoring metadata
[Custom Runtime] Stream ended
[Custom Runtime] Returning: {role: "assistant", content: [...]}
```

### If You See Errors
Common issues:
- **"Cannot read property X of undefined"** → `convertMessage()` function has bug
- **"Network error"** → API proxy issue, check route.ts
- **No logs at all** → Runtime not initialized, check assistant.tsx import

---

## Chrome DevTools Debugging (When MCP Available)

### What to Check

1. **Network Tab**:
   - Filter to `/runs/stream`
   - Check "EventStream" sub-tab
   - See if events are still flowing or if connection closed
   - Look for the exact event that caused freeze

2. **Console Tab**:
   - Look for `[Custom Runtime]` logs
   - Check for any red errors
   - Watch for the metadata warning

3. **Sources Tab**:
   - Set breakpoint in `ui/lib/useCustomLangGraphRuntime.tsx:97` (event parsing)
   - Step through to see which event causes hang

4. **Performance Tab**:
   - Record during freeze
   - Check if main thread is blocked
   - Look for long tasks or infinite loops

---

## Alternative Solutions

### If Custom Runtime Also Fails

The nuclear option is to **not use `render_ui_script` through the chat stream**. Instead:

1. **Agent returns a special marker in text**:
   ```
   [UI_COMMAND:calendar:2025-12-17]
   ```

2. **Frontend parses text for markers**:
   ```typescript
   const uiCommandMatch = text.match(/\[UI_COMMAND:(.*?)\]/);
   if (uiCommandMatch) {
     // Make separate API call to execute UI script
     // Update UI directly, outside of streaming
   }
   ```

3. **Separate API endpoint for UI commands**:
   ```
   POST /api/ui-command
   { command: "calendar", args: {date: "2025-12-17"} }
   ```

This completely sidesteps the streaming issue.

---

## Files to Review

### If You Need to Understand the Setup

1. **Backend tool implementation**:
   ```
   /Volumes/X10 Pro/Roscoe/production-vm-code/src/roscoe/agents/paralegal/tools.py
   Lines 761-905
   ```

2. **UI script that executes**:
   ```
   /Volumes/X10 Pro/Roscoe/workspace_paralegal/Tools/UI/calendar/show_day.py
   ```

3. **Frontend streaming logic**:
   ```
   /Volumes/X10 Pro/Roscoe/production-vm-code/ui/lib/useCustomLangGraphRuntime.tsx
   ```

4. **Tool UI component**:
   ```
   /Volumes/X10 Pro/Roscoe/production-vm-code/ui/components/tools/render-ui-script-tool.tsx
   ```

---

## Questions for Assistant UI Discord

If posting for help:

1. Does `@assistant-ui/react-langgraph` support `values` stream mode?
2. How should we handle `messages/metadata` events?
3. Is there a way to make the library consume the entire stream even with unknown events?
4. Should we be using a different runtime for tool-heavy agents?

---

## Success Criteria

You'll know it's fixed when:
1. ✅ Navigate to http://34.63.223.97:3001/
2. ✅ Send: "Show me tomorrow's calendar using local JSON only"
3. ✅ See agent text response streaming
4. ✅ See tool UI card appear
5. ✅ See calendar iframe populate with event
6. ✅ See final assistant message
7. ✅ No infinite spinner
8. ✅ "Copy" and "Refresh" buttons appear below message

Current state: **Fails at step 4** - freezes with infinite spinner

---

## Contact Info for Help

- **Assistant UI Discord**: Search "LangGraph streaming freeze"
- **GitHub Issue**: Consider opening issue with repro
- **LangSmith Project**: `roscoe-local` (has all successful backend traces)

---

**End of Debug Log**

*Good luck! The custom runtime should theoretically work, but needs browser testing to confirm.*
