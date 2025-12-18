# Roscoe Legal Workbench (Custom Lean UI)

AI-powered legal workspace for case management and document drafting with direct LangGraph integration.

## Architecture

This is a **lean, custom UI** that talks **directly to LangGraph** without any CopilotKit overhead. The implementation achieves better results with less complexity.

```
┌────────────────────────────────────────────────────────────┐
│  Left Sidebar      │   Center View     │   Chat Panel     │
│  - File Browser    │   - Doc Viewer    │   - Messages     │
│  - Threads         │   - Calendar      │   - Streaming    │
│                    │   - Artifacts     │   - Markdown     │
└────────────────────────────────────────────────────────────┘
         │                   │                    │
         └───────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Zustand Store  │
                    │  (workbench)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  LangGraph API  │
                    │  (direct HTTP)  │
                    │  :8123          │
                    └─────────────────┘
```

## Features

- **Direct LangGraph Integration**: HTTP calls to `/runs/stream` with SSE streaming
- **Thread Management**: Create, switch, delete conversations with localStorage persistence
- **Thread Status**: Color-coded (blue=active, green=complete, red=error)
- **File Browser**: Navigate workspace filesystem
- **Document Viewer**: PDF with zoom/pagination, Markdown rendering
- **Artifact Canvas**: Contact cards, medical provider cards, insurance cards
- **HTML Sandbox**: Secure iframe rendering for agent-generated HTML
- **Streaming Responses**: Character-by-character streaming with typing indicator

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Next.js 16 (App Router) |
| UI | React 19 + Radix UI |
| State | Zustand |
| Styling | Tailwind CSS 4 |
| Markdown | react-markdown + remark-gfm |
| PDF | react-pdf |
| Editor | TipTap (for document editing) |
| API | Direct fetch to LangGraph |

## Development

### Local

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

Visit http://localhost:3000

### Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_LANGGRAPH_URL=http://localhost:8123
NEXT_PUBLIC_WORKSPACE_ROOT=/mnt/workspace
```

### VM Deployment

```bash
# Deploy to VM
./deploy-to-vm.sh

# Start dev server on VM (hot-reload)
./start-dev-vm.sh
```

Visit http://34.63.223.97:3000

## Project Structure

```
src/
├── app/
│   ├── page.tsx              # Entry point → Workbench
│   ├── layout.tsx            # Root layout
│   └── api/
│       ├── workspace/list/   # Directory listing
│       ├── workspace/file/   # File reading
│       └── calendar/         # Calendar events
│
├── components/
│   ├── chat/                 # Custom chat UI
│   │   ├── chat-panel.tsx    # Main container + streaming
│   │   ├── message-list.tsx  # Message display
│   │   ├── message-input.tsx # Input component
│   │   └── message-bubble.tsx# Message with markdown
│   │
│   ├── workbench/
│   │   ├── workbench.tsx     # Three-column layout
│   │   ├── left-sidebar.tsx  # Files + Threads tabs
│   │   ├── center-view.tsx   # Viewer/Calendar/Artifacts
│   │   ├── file-browser.tsx  # File navigation
│   │   ├── thread-manager.tsx# Thread list
│   │   ├── document-viewer.tsx
│   │   ├── pdf-viewer.tsx
│   │   └── markdown-viewer.tsx
│   │
│   ├── artifacts/
│   │   ├── artifact-canvas.tsx
│   │   ├── html-sandbox.tsx
│   │   ├── contact-card.tsx
│   │   ├── medical-provider-card.tsx
│   │   └── insurance-card.tsx
│   │
│   └── ui/                   # Shadcn/Radix primitives
│
├── hooks/
│   ├── use-simple-threads.ts # Thread management
│   ├── use-workspace.ts      # File operations
│   ├── use-artifact-listener.ts
│   └── use-pdf-annotations.ts
│
├── lib/
│   ├── langgraph-client.ts   # Direct LangGraph API
│   └── utils.ts
│
├── stores/
│   └── workbench-store.ts    # Zustand global state
│
└── types/
    └── index.ts
```

## Key Design Decisions

1. **No CopilotKit**: Direct HTTP calls to LangGraph are simpler and more reliable
2. **No LangChain SDK**: Just fetch + SSE parsing - ~100 lines vs SDK complexity
3. **localStorage Threads**: Simple persistence without backend complexity
4. **Zustand State**: Single store for all UI state, supports functional updates
5. **Markdown Everywhere**: Agent responses and file viewer both render markdown

## Comparison to CopilotKit Approach

| Aspect | CopilotKit | Custom Lean UI |
|--------|------------|----------------|
| Lines of code | ~2500+ | ~600 |
| Dependencies | 550+ packages | 0 extra |
| Frontend tools | ❌ Don't reach agent | N/A (use backend tools) |
| State sync | ❌ Causes freezes | ✅ Works via Zustand |
| Debugging | Opaque | Simple HTTP/SSE |
| Build size | Large | Minimal |

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/api/workspace/list` | GET | List directory contents |
| `/api/workspace/file` | GET | Read file contents |
| `/api/calendar` | GET | Get calendar events |

## Next Steps

- [ ] Add document saving (write back to workspace)
- [ ] Implement real Google Calendar integration
- [ ] Add more artifact types (timeline, table)
- [ ] PDF annotation persistence
- [ ] TipTap collaborative editing
