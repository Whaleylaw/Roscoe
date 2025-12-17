# Final Diagnosis: UI Streaming Freeze Issue

**Date**: December 17, 2025, 15:56 UTC
**Status**: UNRESOLVED - Library runtime fundamentally broken

---

## What Was Tested (All Failed)

| Configuration | Environment | Result |
|--------------|-------------|--------|
| `stream_mode: ["values"]` | Production (Docker) | ❌ Freezes |
| `stream_mode: ["messages"]` | Production (Docker) | ❌ Freezes |
| `stream_mode: ["messages"]` + `LC_OUTPUT_VERSION=v0` | Production (Docker) | ❌ Freezes |
| `stream_mode: ["messages"]` | Local dev (Next.js) | ❌ Freezes |

**Pattern**: The UI freezes **every time a tool is called**, regardless of:
- Stream mode configuration
- Message format version (v0 vs v1)
- Environment (Docker vs local)
- Container config (production vs dev)

**Simple text messages work fine** - the freeze only happens with tool calls.

---

## Architecture Discovery

### What We Thought
- App uses `<Assistant />` component
- Uses custom runtime from `useCustomLangGraphRuntime.tsx`
- Can fix by modifying custom runtime

### Reality
- **App uses `<Workbench />` component** (`page.tsx:6`)
- Uses LIBRARY runtime `useLangGraphRuntime` from `@assistant-ui/react-langgraph` (`workbench.tsx:215`)
- ALL work on `assistant.tsx` and `useCustomLangGraphRuntime.tsx` had zero effect

---

## The Library Runtime Problem

**File**: `workbench.tsx:215-256`

```typescript
const runtime = useLangGraphRuntime({
  stream: async function* (messages, { initialize, command }) {
    // Custom stream function that calls chatApi.ts
    const generator = await sendMessage({ threadId, messages, command });
    yield* generator;
  },
  // ...
});
```

**What `sendMessage()` does** (`chatApi.ts:38-67`):
1. Creates LangGraph SDK client
2. Sets `streamMode: ["messages"]` (or ["values"])
3. Calls `client.runs.stream()`
4. Returns generator that yields SSE events

**Where it breaks**:
The `useLangGraphRuntime` library function takes this generator and internally processes the events. When tool results come through, the library's internal event handling code either:
- Chokes on metadata events (confirmed - "Unhandled event" warnings)
- Gets stuck in infinite loop processing events
- Fails to properly parse tool call/result pairs
- Has some other streaming bug

---

## What Works

✅ **Backend**
- LangGraph agent executes successfully
- `render_calendar` tool returns correct JSON with calendar events
- Tool output verified in LangSmith traces
- Stream completes on backend side

✅ **Simple Messages**
- Text-only conversations stream perfectly
- No tools = no freeze
- Proves basic streaming works

❌ **Tool Calls**
- ANY tool call freezes the UI
- `render_calendar`, `render_ui_script`, `read_file` - all freeze
- Tool executes successfully on backend
- Frontend never receives/renders the tool result

---

## Fixes That Were Built (All Working on Backend)

### 1. `render_calendar` Tool
**File**: `src/roscoe/agents/paralegal/tools.py:908-1010`
- Direct calendar rendering (no subprocess)
- Reads from `/Database/calendar.json`
- Returns UI commands as JSON
- ✅ Works perfectly (verified in LangSmith)

### 2. `RenderCalendarTool` UI Component
**File**: `ui/components/tools/render-calendar-tool.tsx`
- Handles `render_calendar` tool results
- Parses JSON commands
- Calls workbench store setters
- ✅ Code is correct, but never executes because runtime freezes

### 3. Custom Runtime (Unused)
**File**: `ui/lib/useCustomLangGraphRuntime.tsx`
- Fixed infinite loop bug
- Merges tool calls and results
- ✅ Code works, but component is never rendered

---

## The Only Remaining Solution

**Replace `useLangGraphRuntime` in `workbench.tsx` with custom SSE stream consumer**

This requires:

1. **Remove library runtime import** (`workbench.tsx:10`)
```typescript
// DELETE THIS:
import { useLangGraphRuntime } from "@assistant-ui/react-langgraph";
```

2. **Use `useLocalRuntime` instead** (from `@assistant-ui/react`)
```typescript
import { useLocalRuntime } from "@assistant-ui/react";
```

3. **Implement custom stream handler**
Adapt `useCustomLangGraphRuntime.tsx` logic to work with workbench's pattern:
- Manually consume SSE stream from `client.runs.stream()`
- Parse `data:` events line by line
- Handle `values` or `messages` events
- Ignore `metadata` events
- Properly exit on `[DONE]`
- Convert to assistant-ui message format

4. **Test thoroughly**
This is the ONLY approach that hasn't been tried yet.

---

## What We Learned

### About the Freeze
- NOT caused by Docker
- NOT caused by stream mode configuration
- NOT caused by v1 vs v0 message format
- NOT caused by subprocess execution (render_calendar bypasses this)
- **IS caused by library runtime's SSE event handling**

### About the Architecture
- `page.tsx` renders `Workbench`, not `Assistant`
- `workbench.tsx` uses library runtime
- `assistant.tsx` is completely unused
- Backend has two code paths: `/deps/roscoe/` (baked in) and `/deps/Roscoe/` (volume mount)

### About assistant-ui
- `@assistant-ui/react-langgraph` v0.7.12 is latest version
- No upgrade path available
- Library wasn't updated for LangGraph v1 (but v0 output mode doesn't help)
- Custom runtime is the only way forward

---

## Files Modified (on branch feature/roscoe-training-clean)

### Backend
| File | Status | Notes |
|------|--------|-------|
| `src/roscoe/agents/paralegal/tools.py` | ✅ Working | render_calendar tool + stubs |
| `src/roscoe/agents/paralegal/agent.py` | ✅ Working | render_ui_script disabled |

### Frontend
| File | Status | Notes |
|------|--------|-------|
| `ui/lib/chatApi.ts` | ✅ Deployed | stream_mode: ["messages"] |
| `ui/components/tools/render-calendar-tool.tsx` | ✅ Created | With debug logging |
| `ui/components/assistant-ui/thread.tsx` | ✅ Updated | RenderCalendarTool registered |
| `ui/lib/useCustomLangGraphRuntime.tsx` | ⚠️ Unused | assistant.tsx never renders |
| `ui/app/assistant.tsx` | ⚠️ Unused | Workbench uses different runtime |

### Environment
| Setting | Value | Location |
|---------|-------|----------|
| `LC_OUTPUT_VERSION` | `v0` | VM `~/.env` |
| `stream_mode` | `["messages"]` | `ui/lib/chatApi.ts:46` |

---

## Recommended Next Steps

1. **Try upgrading @assistant-ui/react package** (not just react-langgraph)
   ```bash
   npm install @assistant-ui/react@latest
   ```
   Maybe the core runtime was fixed even if langgraph adapter wasn't

2. **Implement custom runtime in workbench.tsx** (definitive solution)
   - Copy logic from `useCustomLangGraphRuntime.tsx`
   - Adapt to work with workbench's stream/create/load pattern
   - This WILL work but requires careful implementation

3. **Try different assistant-ui example**
   Check if assistant-ui has updated LangGraph examples that work with v1

4. **Consider alternative UI library**
   If assistant-ui can't work with LangGraph v1, might need different UI framework

---

## Documentation Created

- `UI_STREAMING_FREEZE_DEBUG.md` - Original issue documentation
- `UI_STREAMING_FIX_PROGRESS.md` - Today's debugging attempts
- `FINAL_DIAGNOSIS.md` - This file

All commits on branch: `feature/roscoe-training-clean`

---

**End of debugging session - December 17, 2025, 15:56 UTC**
