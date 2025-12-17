# UI Streaming Fix Progress - December 17, 2025

## Current Status: LIBRARY RUNTIME STILL IN USE

**✅ No longer freezing**: UI streams without hanging
**❌ Calendar not rendering**: Tool UI component not executing workbench commands
**❌ Custom runtime not being used**: Console shows library runtime warnings ("Unhandled event received: values")
**❌ DevTools not appearing**: Lower-right corner should show DevTools modal but doesn't
**❌ Debug logs not appearing**: No [Custom Runtime] or [RenderCalendarTool] logs in console

**CRITICAL DISCOVERY**: Despite deploying custom runtime code, the browser is still using the old `@assistant-ui/react-langgraph` library runtime. This means:
- Next.js build might have cached old client-side code
- OR import path issue preventing custom runtime from loading
- OR JavaScript error silently failing custom runtime initialization

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
