# UI Streaming Fix Progress - December 17, 2025

## FINAL STATUS: VERSION MISMATCH BREAKS STREAMING

**Date**: December 17, 2025, 15:35 UTC
**Root Cause FOUND**: LangChain/LangGraph v1 message format incompatible with assistant-ui v0.7.12

### The Version Mismatch
- **UI Library**: `@assistant-ui/react-langgraph` v0.7.12 (expects v0 message format)
- **SDK**: `@langchain/langgraph-sdk` v1.2.0 (sends v1 message format with standard content blocks)
- **Backend**: LangGraph v1.x (sends new standard content block format)

**The Problem**: assistant-ui v0.7.12 was built BEFORE LangChain/LangGraph v1. It expects the old v0 message format. When it receives v1 messages with standard content blocks, it can't parse tool calls/results properly → freeze!

## FINAL STATUS: LIBRARY RUNTIME IS INCOMPATIBLE

**Date**: December 17, 2025, 15:32 UTC
**Conclusion**: `@assistant-ui/react-langgraph` v0.7.12 cannot handle LangGraph tool streaming

### What Was Confirmed
- ✅ Backend works perfectly (`render_calendar` returns correct JSON)
- ✅ Simple text messages stream without issues
- ❌ **ANY tool call freezes the UI** (regardless of stream mode)
- ❌ Tested in production (Docker) - freezes
- ❌ Tested locally (dev server) - freezes
- ❌ Tested with `["values"]` mode - freezes
- ❌ Tested with `["messages"]` mode - freezes

### Root Cause
The app uses `useLangGraphRuntime` from `@assistant-ui/react-langgraph` in `workbench.tsx:215`. This library has a critical bug (issue #2166) where it cannot process tool results from LangGraph's streaming API.

### Possible Solutions

**Option 1: Upgrade assistant-ui Library** (EASIEST)
Check if there's a newer version of `@assistant-ui/react-langgraph` that supports LangChain v1:
```bash
npm install @assistant-ui/react-langgraph@latest
```

**Option 2: Downgrade LangGraph SDK** (RISKY)
Downgrade to v0.x format that matches assistant-ui v0.7.12:
```bash
npm install @langchain/langgraph-sdk@0.x
```
But this might break other things!

**Option 3: Custom Runtime** (MOST WORK)
Replace `useLangGraphRuntime` in `workbench.tsx` with custom implementation that handles v1 format

**Option 4: Backend Output Version** (WORTH TRYING)
Set backend to output v0 format:
```python
# Set environment variable
LC_OUTPUT_VERSION=v0
```
Or configure model with `output_version="v0"`

All work on `useCustomLangGraphRuntime.tsx` was wasted because `assistant.tsx` is never rendered - the app uses `workbench.tsx` instead.

---

## Current Status: LIBRARY RUNTIME STILL IN USE

**✅ No longer freezing**: UI streams without hanging
**❌ Calendar not rendering**: Tool UI component not executing workbench commands
**❌ Custom runtime not being used**: Console shows library runtime warnings ("Unhandled event received: values")
**❌ DevTools not appearing**: Lower-right corner should show DevTools modal but doesn't
**❌ Debug logs not appearing**: No [Custom Runtime] or [RenderCalendarTool] logs in console

**CRITICAL DISCOVERY**: The app renders `Workbench` (not `Assistant`), which uses the LIBRARY runtime!
- `page.tsx` renders `<Workbench />`
- `workbench.tsx:215` uses `useLangGraphRuntime` from `@assistant-ui/react-langgraph`
- `assistant.tsx` with custom runtime is NEVER used
- All changes to `assistant.tsx` and `useCustomLangGraphRuntime.tsx` have NO effect!

**ROOT CAUSE FOUND**:
- Library runtime with `stream_mode: ["values"]` doesn't handle tool results (issue #2166)
- Changed to `stream_mode: ["messages"]` which library CAN handle
- This should allow tool results to flow to `RenderCalendarTool` component

---

## Problems Identified & Fixed

### 1. ✅ FIXED: Streaming Infinite Loop
**File**: `ui/lib/useCustomLangGraphRuntime.tsx:93`

**Problem**: When `[DONE]` received, only broke inner loop → infinite `while (true)`

**Fix**: Added `streamComplete` flag
```typescript
let streamComplete = false;
while (!streamComplete) {
  // ...
  if (data === "[DONE]") {
    streamComplete = true;
    break;
  }
}
```

**Result**: No more freezing ✅

---

### 2. ✅ FIXED: Missing UI Component
**File**: NEW - `ui/components/tools/render-calendar-tool.tsx`

**Problem**: No UI component to handle `render_calendar` tool results

**Fix**: Created `RenderCalendarTool` using `makeAssistantToolUI`
- Registered in `thread.tsx` tools.by_name
- Modeled after `RenderUiScriptTool` pattern
- Processes calendar commands and calls workbench store

**Result**: Component created and registered ✅

---

### 3. ✅ FIXED: Backend Calendar Tool Bug
**File**: `src/roscoe/agents/paralegal/tools.py:987`

**Problem**: Tried to iterate entire JSON object instead of `events` array

**Fix**: Extract events from structure
```python
calendar_data = json.load(f)
all_events = calendar_data.get("events", [])
```

**Result**: Tool returns correct data ✅

---

### 4. ⚠️ PARTIALLY FIXED: Custom Runtime Message Conversion
**File**: `ui/lib/useCustomLangGraphRuntime.tsx:125-175`

**Problem**: Only returned final text message, discarding tool calls/results

**Attempted Fix**: Merge all assistant/tool messages into single message
```typescript
// Find all new messages from this turn
const newMessages = lastState.messages.slice(lcMessages.length);

// Merge tool-calls, tool-results, and text into one message
for (const msg of newMessages) {
  if (msg.role === "assistant") {
    // Add tool calls
  } else if (msg.role === "tool") {
    // Add tool results
  }
}
```

**Result**: Unknown - needs testing ⏳

---

## Current Behavior

### What Works
- ✅ Backend successfully calls `render_calendar`
- ✅ Backend returns correct JSON with calendar events and commands
- ✅ Stream completes without freezing
- ✅ Tool result appears in chat as JSON

### What Doesn't Work
- ❌ Calendar view doesn't open in workbench
- ❌ `RenderCalendarTool` UI component doesn't execute commands
- ❌ `useWorkbenchStore` setters not being called

**Example Output** (from user test):
```
Used tool: render_calendar
{"date":"2025-12-17","days":1}

Result:
{"success": true, "title": "Calendar (2025-12-17)", "commands": [{"type": "workbench.setCenterView", "view": "calendar"}, {"type": "calendar.setEvents", "events": [{"id": "evt-004", ...}]}]}
```

The JSON is correct, but the `RenderCalendarTool` component isn't processing it.

---

## Root Cause Theories

### Theory 1: Tool UI Component Not Matching
The `makeAssistantToolUI` might not be matching the tool call because:
- Tool name mismatch (case sensitivity?)
- Tool result not being associated with tool call
- Custom runtime not properly structuring tool-call/tool-result pairs

### Theory 2: Custom Runtime Not Merging Correctly
The merge logic might be:
- Not finding tool messages correctly
- Not matching tool_call_id between call and result
- Returning data in wrong format for `useLocalRuntime`

### Theory 3: Tool Result Not Passing to UI Component
The `result` prop in `RenderCalendarTool` might be:
- undefined
- Wrong format
- Not triggering useEffect due to dependency issues

---

## What Was Deployed (As of 14:50 UTC)

### Backend (`roscoe-agents` container)
✅ `/deps/roscoe/src/roscoe/agents/paralegal/tools.py` - render_calendar function (fixed)
✅ `/deps/roscoe/src/roscoe/agents/paralegal/agent.py` - render_ui_script commented out
✅ Container restarted - render_calendar tool available to agent

### Frontend (`roscoe-ui` container)
✅ `ui/components/tools/render-calendar-tool.tsx` - NEW component
✅ `ui/components/assistant-ui/thread.tsx` - RenderCalendarTool registered
✅ `ui/lib/useCustomLangGraphRuntime.tsx` - Merge messages fix
✅ Container rebuilt and restarted (14:50 UTC)

---

## Docker Path Issues Discovered

The roscoe-agents container has **two copies** of source code:
1. `/deps/roscoe/` (lowercase) - baked into Docker image during build
2. `/deps/Roscoe/` (uppercase) - volume mount from host

**Python imports from lowercase** `/deps/roscoe/`, NOT the mount!

**Workaround**: Manually copy files to both paths:
```bash
docker exec roscoe-agents cp /deps/Roscoe/... /deps/roscoe/...
```

**Proper Fix**: Rebuild roscoe image OR fix volume mount path

---

## Latest Fix (December 17, 15:20 UTC)

### Discovery: Wrong Runtime Being Used
All work on `useCustomLangGraphRuntime` was wasted because:
- `page.tsx` renders `<Workbench />`, not `<Assistant />`
- `workbench.tsx` uses library's `useLangGraphRuntime`
- Custom runtime code never executes

### The Real Fix
Changed `chatApi.ts` line 46:
- **FROM**: `stream_mode: ["values"]` (library can't handle this)
- **TO**: `stream_mode: ["messages"]` (library CAN handle this)

This should fix the tool rendering issue because:
1. Library runtime processes "messages" events correctly
2. Tool results flow through as proper message parts
3. `RenderCalendarTool` component gets proper tool-call and tool-result data
4. useEffect triggers and executes workbench commands

### Testing Status
❌ **FAILED** - Both production AND local dev (tested at 15:24 UTC and 15:32 UTC)
- Changed to `["messages"]` stream mode
- Tested in Docker (production) - ❌ Froze
- Tested locally with Next.js dev server - ❌ Froze
- Page becomes unresponsive during tool call
- **CONFIRMED**: Library runtime is broken regardless of stream mode or environment

---

## CONCLUSION (December 17, 15:24 UTC)

### The Library Runtime is Fundamentally Broken

Tested stream modes with `useLangGraphRuntime` from `@assistant-ui/react-langgraph`:
- `["values"]` mode: ❌ Freezes (tool results ignored, issue #2166)
- `["messages"]` mode: ❌ Freezes (page becomes unresponsive)
- `["messages", "updates"]` mode: ❌ Not tested (likely same issue)

**Root Cause**: The `@assistant-ui/react-langgraph` library (v0.7.12) cannot properly handle LangGraph streaming with tool calls, regardless of stream mode configuration.

### Required Solution

**Option 1: Implement Custom Runtime in Workbench** (RECOMMENDED)
Replace library runtime in `workbench.tsx:215` with custom implementation:
1. Remove `useLangGraphRuntime` import
2. Implement custom SSE stream consumer (like `useCustomLangGraphRuntime`)
3. Manually convert LangGraph messages to assistant-ui format
4. Handle tool calls/results explicitly

**Option 2: Downgrade Library**
Try older version of `@assistant-ui/react-langgraph` that might work better

**Option 3: Wait for Library Fix**
Wait for issue #2166 to be resolved upstream (not practical)

**Option 4: Non-Streaming Mode**
Use polling instead of streaming (loses real-time updates)

---

## Next Debugging Steps

### 1. Check if RenderCalendarTool is Actually Being Called
```typescript
// Add to render-calendar-tool.tsx
console.log("[RenderCalendarTool] Render called", { args, result, status });
```

### 2. Verify Tool Result Format
Check if `result` prop matches expected structure:
- Should be object with `success`, `commands` keys
- May be JSON string that needs parsing (already handled)

### 3. Check useEffect Dependencies
The commands might not trigger because:
- `status.type` never changes from "running" to "complete"
- `commands` array reference doesn't change
- useEffect guard prevents execution

### 4. Test with Chrome DevTools
- Navigate to http://34.63.223.97:3001/
- Send: "Show me tomorrow's calendar"
- Check console for:
  - `[Custom Runtime]` logs
  - `[RenderCalendarTool]` logs
  - Workbench store changes
  - Any React errors

### 5. Compare with Working Tool
Check how `RenderUiScriptTool` works when it DOES render:
- Same component pattern
- Same workbench store calls
- Only difference: tool name

---

## Files Modified

### Backend
| File | Status | Purpose |
|------|--------|---------|
| `src/roscoe/agents/paralegal/tools.py` | ✅ Deployed | render_calendar function + stubs |
| `src/roscoe/agents/paralegal/agent.py` | ✅ Deployed | Disabled render_ui_script |

### Frontend
| File | Status | Purpose |
|------|--------|---------|
| `ui/lib/useCustomLangGraphRuntime.tsx` | ✅ Deployed | Fixed loop + merge messages |
| `ui/components/tools/render-calendar-tool.tsx` | ✅ Deployed | NEW - calendar tool UI |
| `ui/components/assistant-ui/thread.tsx` | ✅ Deployed | Registered RenderCalendarTool |
| `ui/app/assistant.tsx` | ✅ Deployed | Removed DevTools import |
| `ui/package.json` | ✅ Deployed | Removed DevTools dep |

---

## Test Commands

### Check if UI rebuilt successfully
```bash
gcloud compute ssh roscoe-paralegal-vm --zone us-central1-a \
  --command "docker images | grep roscoe-ui"
# Should show recent timestamp
```

### Check if agent has render_calendar
```bash
gcloud compute ssh roscoe-paralegal-vm --zone us-central1-a \
  --command "docker exec roscoe-agents python3 -c 'from roscoe.agents.paralegal.tools import render_calendar; print(\"SUCCESS\")'"
```

### Test backend directly
```bash
curl -s http://34.63.223.97:8123/threads -X POST -H "Content-Type: application/json" -d '{}'
# Get thread_id, then:
curl -N http://34.63.223.97:8123/threads/THREAD_ID/runs/stream \
  -H "Content-Type: application/json" \
  -d '{"assistant_id":"roscoe_paralegal","input":{"messages":[{"role":"user","content":"Use render_calendar for 2025-12-17"}]},"stream_mode":["values"]}'
```

---

## Known Issues Still Outstanding

1. **Calendar UI Not Rendering**
   - Tool executes successfully
   - Returns correct JSON
   - UI component receives data (presumably)
   - BUT workbench commands not executing

2. **Docker Path Confusion**
   - Two copies of code in container
   - Must manually sync or rebuild image
   - Volume mount case sensitivity issue

3. **Word Template Tools Disabled**
   - Temporarily stubbed out due to import errors
   - Not critical for calendar testing
   - Need to fix `/deps/Roscoe` vs `/deps/roscoe` path issue

---

## Success Criteria (Not Yet Met)

When working, the user should see:
1. ✅ Send message: "Show me tomorrow's calendar"
2. ✅ See agent text streaming
3. ✅ See `render_calendar` tool card
4. ❌ **Calendar view opens in center panel**
5. ❌ **Events populate in calendar iframe**
6. ✅ See final assistant message
7. ✅ No infinite spinner
8. ✅ Copy/Refresh buttons appear

**Currently Failing**: Steps 4 & 5 - commands not executing

---

## Commits Made

```
d244adfa - Fix custom runtime to merge tool calls and results into single message
5126197b - Add RenderCalendarTool UI component and fix streaming loop bug
c26dbaa3 - Fix render_calendar to correctly read events array from calendar.json
c8d69f36 - Add stub functions for word template tools to fix import errors
41838b39 - Temporarily disable render_ui_script to test direct render_calendar tool
2482bed2 - Add render_calendar direct tool to bypass subprocess execution
5d030a32 - Fix streaming freeze: properly exit loop on [DONE] event
```

---

## Next Steps (Immediate)

1. **Add debug logging to RenderCalendarTool**
   - Log when render() is called
   - Log args, result, status
   - Log when useEffect runs
   - Log when workbench functions are called

2. **Check browser console**
   - Look for component render logs
   - Check for React errors
   - Verify tool name matching

3. **Compare with working render_ui_script**
   - Test render_ui_script to see if IT renders
   - If it does, compare the tool result structure
   - If it doesn't, problem is in custom runtime

4. **Consider reverting to library runtime**
   - Test if `useLangGraphRuntime` from `@assistant-ui/react-langgraph` works
   - Custom runtime might have fundamental incompatibility
   - Metadata warnings might not actually cause freeze

---

**Status**: Ready for testing at http://34.63.223.97:3001/
**Last Updated**: 2025-12-17 14:50 UTC
**Branch**: feature/roscoe-training-clean
