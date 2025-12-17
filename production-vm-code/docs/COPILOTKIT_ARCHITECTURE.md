# CopilotKit Modular UI Architecture

## Overview

Roscoe uses CopilotKit 1.5 with a modular, composable component architecture that enables agent-generated UI artifacts. UI components are atomic "Lego blocks" that the agent can combine to create rich interfaces dynamically, following the "build once, use many" philosophy.

**Why CopilotKit?** Replaced assistant-ui v0.7.12 which had LangChain v1 compatibility issues. CopilotKit 1.5 provides native AG-UI protocol support for LangGraph agents with better streaming, tool integration, and artifact capabilities.

---

## Architecture Layers

### Layer 1: Atomic Components

**Location:** `ui/components/artifacts/`

Reusable UI components with Zod schemas for validation:

| Component | File | Purpose | Category |
|-----------|------|---------|----------|
| `ContactCard` | `contact-card.tsx` | Display contact info (attorney, client, witness) | contact |
| `MedicalProviderCard` | `medical-provider-card.tsx` | Healthcare provider details with treatments | medical |
| `InsuranceCard` | `insurance-card.tsx` | Insurance carrier, policy, adjuster info | insurance |

**Component Structure:**

Each atomic component follows this pattern:

```typescript
// 1. Define Zod schema
export const componentSchema = z.object({
  field: z.string().min(1),
  optionalField: z.string().optional(),
});

export type ComponentData = z.infer<typeof componentSchema>;

// 2. Create React component with ArtifactProps
interface ComponentProps extends ArtifactProps {
  data: ComponentData;
}

export function Component({ data, onAction }: ComponentProps) {
  const validated = componentSchema.parse(data);

  return (
    <Card>
      {/* Component UI */}
    </Card>
  );
}

// 3. Register in artifact registry
const componentArtifact: ArtifactComponent<ComponentProps> = {
  id: "component-id",
  name: "Component Name",
  description: "Description for agent to understand when to use this",
  component: Component,
  schema: componentSchema,
  category: "contact" | "medical" | "insurance" | "legal" | "document" | "ui",
};

artifactRegistry.register(componentArtifact);
```

**Key Properties:**

- **Atomic**: Each component has a single, clear responsibility
- **Self-contained**: No external state dependencies
- **Validated**: Zod schema ensures type safety at runtime
- **Registered**: Automatically available to agent once imported
- **Interactive**: Can trigger actions via `onAction` callback

### Layer 2: Artifact Canvas

**Location:** `ui/components/artifacts/artifact-canvas.tsx`

The canvas is the rendering system for dynamic UI components. It manages the lifecycle of artifacts and provides a global API for creation, updates, and removal.

**How It Works:**

```typescript
<ArtifactCanvas
  initialArtifacts={[]}
  onArtifactAction={(artifactId, action, payload) => {
    // Handle user interactions with artifacts
    console.log(`Artifact ${artifactId} triggered ${action}`, payload);
  }}
/>
```

**Canvas API (exposed to window):**

```javascript
window.__artifactCanvas = {
  add: (componentId, data) => artifactId,  // Create new artifact
  update: (artifactId, data) => void,      // Update existing artifact
  remove: (artifactId) => void,            // Remove artifact
}
```

**Artifact Instance Structure:**

```typescript
interface ArtifactInstance {
  id: string;           // Unique instance ID (artifact-timestamp-random)
  componentId: string;  // Component type (e.g., "contact-card")
  data: Record<string, any>;  // Component props
}
```

**Rendering Process:**

1. Agent calls `create_artifact` CopilotKit tool
2. Tool validates data against component's Zod schema
3. Canvas adds instance to state
4. Canvas looks up component in registry
5. Component renders with validated data
6. User interactions callback to agent

### Layer 3: CopilotKit Tools

**Location:** `ui/lib/copilotkit-artifact-tools.tsx`

CopilotKit tools connect the agent's capabilities to the artifact canvas. These are React hooks that register actions the agent can call.

**Available Tools:**

#### `create_artifact`

Create a new UI artifact and display it to the user.

**Parameters:**
- `componentId` (string): Type of artifact (contact-card, medical-provider-card, insurance-card)
- `data` (object): Component data matching schema

**Returns:**
```json
{
  "success": true,
  "artifactId": "artifact-1734453600000-xyz",
  "message": "Created Contact Card artifact"
}
```

**Example Agent Usage:**
```
User: Show me John Doe's contact information
Agent: create_artifact({
  componentId: "contact-card",
  data: {
    name: "John Doe",
    role: "Attorney",
    email: "john@law.com",
    phone: "555-1234"
  }
})
```

#### `update_artifact`

Update an existing artifact with new data.

**Parameters:**
- `artifactId` (string): ID of artifact to update
- `data` (object): New component data

**Example:**
```
Agent: update_artifact({
  artifactId: "artifact-1734453600000-xyz",
  data: {
    name: "John Doe",
    role: "Senior Partner",  // Updated
    email: "john@law.com",
    phone: "555-1234"
  }
})
```

#### `remove_artifact`

Remove an artifact from the canvas.

**Parameters:**
- `artifactId` (string): ID of artifact to remove

#### `list_artifact_types`

Get a list of all available artifact component types.

**Returns:**
```json
{
  "success": true,
  "artifacts": [
    {
      "id": "contact-card",
      "name": "Contact Card",
      "description": "Display contact information for a person",
      "category": "contact"
    },
    // ... more components
  ]
}
```

**Tool Implementation Pattern:**

```typescript
export function useCopilotArtifactTools() {
  useCopilotAction({
    name: "tool_name",
    description: "What this tool does (agent reads this)",
    parameters: [
      {
        name: "param",
        type: "string",
        description: "Parameter description",
        required: true,
      },
    ],
    handler: async ({ param }) => {
      // Tool implementation
      const canvas = (window as any).__artifactCanvas;
      // ... logic ...
      return { success: true };
    },
  });
}
```

### Layer 4: Backend Integration (AG-UI Protocol)

**Location:** `src/roscoe/copilotkit_server.py`

The Python backend provides the AG-UI protocol endpoint that CopilotKit connects to. This wraps the LangGraph agent and exposes it via CopilotKit's streaming protocol.

**Server Configuration:**

```python
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import LangGraphAGUIAgent
from fastapi import FastAPI

app = FastAPI()

# Wrap LangGraph agent for CopilotKit
agent = LangGraphAGUIAgent(
    graph=personal_assistant_agent,
    config={"recursion_limit": 500}
)

# Add AG-UI endpoint
add_langgraph_fastapi_endpoint(
    app=app,
    agent=agent,
    path="/copilotkit",
)

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "roscoe-copilotkit"}
```

**Endpoint Details:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/copilotkit` | POST | AG-UI protocol handler (streaming) |
| `/health` | GET | Health check |

**Docker Service:**

```yaml
copilotkit:
  build: .
  container_name: roscoe-copilotkit
  ports:
    - "8124:8124"
  command: python -m roscoe.copilotkit_server
  environment:
    - LANGGRAPH_DEPLOYMENT=true
    - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    # ... other env vars
```

**API Flow:**

```
User Message (UI)
  ↓
CopilotKit React (port 3001)
  ↓
Next.js API Proxy (/api/copilotkit)
  ↓
CopilotKit Server (port 8124)
  ↓
LangGraph Agent (with tools/middleware)
  ↓
Streaming Response
  ↓
CopilotKit React (renders artifacts)
```

### Layer 5: Workspace Tools

**Location:** `ui/lib/copilotkit-workspace-tools.tsx`

Additional CopilotKit tools for workspace interaction (file browsing, document viewing).

**Available Tools:**

- `get_active_viewer` - Get currently viewed file path
- `get_file_browser_path` - Get current browser directory
- `workspace_list` - List files/folders in directory
- `workspace_read_text` - Read text file contents
- `workspace_get_file_url` - Get downloadable file URL
- `get_viewer_text` - Get text from active viewer

These tools enable the agent to:
- Navigate the workspace file system
- Read case documents
- Reference specific files in conversation
- Generate file URLs for user download

---

## Adding New Artifact Components

Follow this step-by-step process to add a new artifact component:

### Step 1: Create Component File

Create `ui/components/artifacts/my-component.tsx`:

```typescript
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { z } from "zod";
import { ArtifactComponent, ArtifactProps } from "./types";
import { artifactRegistry } from "./registry";

// Define schema
export const myComponentSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
  // ... more fields
});

export type MyComponentData = z.infer<typeof myComponentSchema>;

interface MyComponentProps extends ArtifactProps {
  data: MyComponentData;
}

// Create component
export function MyComponent({ data, onAction }: MyComponentProps) {
  const validated = myComponentSchema.parse(data);

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>{validated.title}</CardTitle>
      </CardHeader>
      <CardContent>
        {validated.description && <p>{validated.description}</p>}
      </CardContent>
    </Card>
  );
}

// Register component
const myComponentArtifact: ArtifactComponent<MyComponentProps> = {
  id: "my-component",
  name: "My Component",
  description: "Clear description for agent to understand when to use this component",
  component: MyComponent,
  schema: myComponentSchema,
  category: "ui", // or "contact", "medical", "insurance", "legal", "document"
};

artifactRegistry.register(myComponentArtifact);
```

### Step 2: Import Component in Workbench

Add to `ui/app/workbench.tsx`:

```typescript
// Import to trigger registration
import "@/components/artifacts/my-component";
```

### Step 3: Rebuild UI

```bash
cd /Volumes/X10\ Pro/Roscoe/production-vm-code/ui
npm run build
```

### Step 4: Test

```bash
# Start dev server
npm run dev

# In chat, ask agent:
# "Create a my-component with title 'Test' and description 'Hello'"
```

### Step 5: Deploy to Production

```bash
# On VM
cd ~/roscoe
git pull origin main
docker compose build ui
docker compose restart ui
```

**That's it!** The component is now available to the agent. No backend changes needed.

---

## Philosophy: Build Once, Use Many

The modular architecture follows these principles:

### 1. Atomic Design

Each component is a single, reusable unit:

```typescript
// ❌ Bad: Monolithic component with multiple responsibilities
function CaseOverview({ contact, medical, insurance }) {
  return (
    <div>
      <ContactSection data={contact} />
      <MedicalSection data={medical} />
      <InsuranceSection data={insurance} />
    </div>
  );
}

// ✅ Good: Atomic components composed by agent
Agent creates:
  - ContactCard artifact
  - MedicalProviderCard artifact
  - InsuranceCard artifact
```

### 2. Agent-Driven Composition

The agent decides what to display and when:

```
User: "Show me details about the Smith case"

Agent reasoning:
- User wants case overview
- Load case data from /Database
- Create ContactCard for client
- Create MedicalProviderCard for treating physician
- Create InsuranceCard for liability carrier
- Display all in artifacts canvas

Agent actions:
create_artifact(componentId: "contact-card", data: {...})
create_artifact(componentId: "medical-provider-card", data: {...})
create_artifact(componentId: "insurance-card", data: {...})
```

### 3. Schema-Driven Validation

Zod schemas enforce type safety:

```typescript
// Schema defines contract
const contactCardSchema = z.object({
  name: z.string().min(1),
  email: z.string().email().optional(),
});

// Component validates at render
const validated = contactCardSchema.parse(data);

// Agent gets clear error if invalid
Error: "Invalid data for contact-card: name is required"
```

### 4. Zero Backend Changes

Adding components requires zero backend modifications:

- No Python code changes
- No server restart
- No API route updates
- Just create component, import, deploy

### 5. Discoverable

Agent can introspect available components:

```javascript
// Agent calls list_artifact_types
{
  "artifacts": [
    {
      "id": "contact-card",
      "name": "Contact Card",
      "description": "Display contact information...",
      "category": "contact"
    }
  ]
}

// Agent learns what's available and when to use each
```

---

## Integration with Workbench

The workbench provides a multi-panel interface with CopilotKit sidebar:

### Workbench Layout

```
┌─────────────────────────────────────────────────────────────┐
│  File Browser  │  Center Panel (4 views)  │  CopilotKit    │
│  (Workspace)   │                           │  Sidebar       │
│                │  • Viewer (docs/PDFs)     │                │
│  Database/     │  • Monaco (code editor)   │  Chat with     │
│  Tools/        │  • Calendar (deadlines)   │  Roscoe        │
│  Skills/       │  • Artifacts (UI canvas)  │                │
│  projects/     │                           │                │
└─────────────────────────────────────────────────────────────┘
```

### Center Panel Views

The center panel has four views controlled by tabs:

#### 1. Viewer (Default)

Document preview for workspace files:
- PDF rendering
- Markdown rendering
- Text file display
- JSON pretty-print

#### 2. Monaco

Code editor for scripts and tools:
- Syntax highlighting
- TypeScript/Python support
- Read-only mode for workspace files
- Future: Tiptap for legal documents

#### 3. Calendar

Case deadlines and events:
- Calendar iframe integration
- Event list view
- Deadline tracking
- Sync with Google Calendar

#### 4. Artifacts (New)

Agent-generated UI components:
- ContactCard instances
- MedicalProviderCard instances
- InsuranceCard instances
- Future: Charts, tables, forms

### View Switching

The agent can't directly switch views, but can create artifacts that suggest switching:

```typescript
// Agent creates artifact
create_artifact({
  componentId: "contact-card",
  data: { name: "John Doe", ... }
})

// User sees artifact in Artifacts view
// (Or we could add a tool for view switching)
```

### CopilotKit Sidebar

The sidebar provides chat interface:

```typescript
<CopilotSidebar
  defaultOpen
  labels={{
    title: "Roscoe AI Paralegal",
    initial: "How can I help you today?",
  }}
/>
```

**Features:**

- Streaming message responses
- Tool call indicators
- Artifact creation feedback
- Error handling
- Message history
- Markdown rendering

---

## Docker Services

CopilotKit runs as multiple cooperating services:

### Service Architecture

```yaml
services:
  postgres:
    # LangGraph checkpointing

  redis:
    # Caching layer

  roscoe:
    # LangGraph API (port 8123)
    # Original agent endpoint

  copilotkit:
    # AG-UI backend (port 8124)
    # Wraps LangGraph for CopilotKit

  ui:
    # Next.js frontend (port 3001)
    # CopilotKit React components

  uploads:
    # File upload service
```

### Network Flow

```
User Browser
  ↓
UI Container (port 3001)
  ↓ /api/copilotkit proxy
CopilotKit Container (port 8124)
  ↓ Internal LangGraph client
LangGraph Container (port 8000)
  ↓
Postgres/Redis
```

### Environment Variables

**CopilotKit Service:**

```bash
LANGGRAPH_DEPLOYMENT=true
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
GOOGLE_API_KEY=${GOOGLE_API_KEY}
TAVILY_API_KEY=${TAVILY_API_KEY}
LANGSMITH_API_KEY=${LANGSMITH_API_KEY}
LANGCHAIN_TRACING_V2=true
DATABASE_URI=postgres://postgres:postgres@postgres:5432/postgres
REDIS_URI=redis://redis:6379
WORKSPACE_ROOT=/mnt/workspace
```

**UI Service:**

```bash
LANGGRAPH_API_URL=http://roscoe:8000  # Legacy endpoint
COPILOTKIT_LANGGRAPH_URL=http://copilotkit:8124  # CopilotKit endpoint
WORKSPACE_ROOT=/mnt/workspace
```

### Service Communication

| From | To | Protocol | Purpose |
|------|-----|----------|---------|
| Browser | UI | HTTPS | Next.js frontend |
| UI | CopilotKit | HTTP (internal) | AG-UI protocol |
| CopilotKit | LangGraph | HTTP (internal) | Agent execution |
| LangGraph | Postgres | PostgreSQL | Checkpointing |
| LangGraph | Redis | Redis | Caching |
| All | Workspace | GCS mount | File access |

---

## Updating UI

### Local Development

```bash
cd /Volumes/X10\ Pro/Roscoe/production-vm-code/ui

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

### Production Deployment

#### Option 1: UI Changes Only

```bash
# On VM
cd ~/roscoe
git pull origin main
docker compose build ui
docker compose restart ui
docker compose logs -f ui
```

#### Option 2: Backend + UI Changes

```bash
# On VM
cd ~/roscoe
git pull origin main
docker compose build
docker compose up -d
docker compose logs -f copilotkit ui
```

#### Option 3: New Artifact Component

```bash
# On local machine
# 1. Create component in ui/components/artifacts/
# 2. Import in ui/app/workbench.tsx
# 3. Test locally: npm run dev
# 4. Commit and push

# On VM
cd ~/roscoe
git pull origin main
docker compose build ui
docker compose restart ui
```

### Troubleshooting UI

```bash
# Check container status
docker ps | grep roscoe-ui

# Check UI logs
docker compose logs ui | tail -100

# Check CopilotKit logs
docker compose logs copilotkit | tail -100

# Verify environment
docker exec roscoe-ui env | grep COPILOTKIT

# Test proxy
curl http://localhost:3001/api/copilotkit
# Expected: {"status":"ok","service":"copilotkit-proxy"}

# Test backend
curl http://localhost:8124/health
# Expected: {"status":"ok","service":"roscoe-copilotkit"}

# Rebuild from scratch
docker compose down
docker compose build --no-cache ui copilotkit
docker compose up -d
```

---

## Development Workflow

### Adding a New Feature

1. **Design Component**
   - Determine what data it needs
   - Sketch UI layout
   - Consider user interactions

2. **Create Schema**
   - Define Zod schema with validation rules
   - Export TypeScript type
   - Document required vs optional fields

3. **Build Component**
   - Create React component with ArtifactProps
   - Parse data with schema
   - Implement UI with shadcn/ui
   - Add interaction handlers

4. **Register Component**
   - Create ArtifactComponent descriptor
   - Call artifactRegistry.register()
   - Choose appropriate category

5. **Test Locally**
   - Import in workbench
   - Start dev server
   - Ask agent to create component
   - Verify rendering and interactions

6. **Deploy**
   - Commit component file
   - Push to repo
   - Pull on VM
   - Rebuild UI container
   - Test in production

### Testing Checklist

- [ ] Schema validates correct data
- [ ] Schema rejects invalid data
- [ ] Component renders with minimal data
- [ ] Component renders with all data
- [ ] Interactions trigger onAction callback
- [ ] Component is responsive (mobile/tablet/desktop)
- [ ] Component follows design system (shadcn/ui)
- [ ] Component registered in artifact registry
- [ ] Agent can create component via tool
- [ ] Component appears in artifacts view
- [ ] No console errors
- [ ] TypeScript compiles without errors

---

## Best Practices

### Component Design

1. **Keep it atomic**: One component = one responsibility
2. **Make it reusable**: Don't hardcode case-specific logic
3. **Use shadcn/ui**: Consistent design system
4. **Validate everything**: Zod schemas catch errors early
5. **Handle edge cases**: Optional fields, empty arrays, null values
6. **Provide feedback**: Loading states, error states, success states

### Schema Design

```typescript
// ✅ Good: Clear, validated, documented
export const contactCardSchema = z.object({
  name: z.string().min(1, "Name is required"),
  role: z.string().optional(),
  email: z.string().email("Invalid email").optional(),
  phone: z.string().regex(/^\d{3}-\d{4}$/, "Format: 555-1234").optional(),
});

// ❌ Bad: Weak validation, unclear
export const contactCardSchema = z.object({
  name: z.string(),
  role: z.string(),
  email: z.string(),
  phone: z.string(),
});
```

### Description Writing

Write clear descriptions for the agent:

```typescript
// ✅ Good: Agent understands when to use this
{
  id: "medical-provider-card",
  description: "Display information about a medical provider, doctor, or healthcare facility involved in a case. Use this when showing details about physicians, hospitals, clinics, physical therapists, or other healthcare providers."
}

// ❌ Bad: Too vague
{
  id: "medical-provider-card",
  description: "Medical provider component"
}
```

### Error Handling

```typescript
// ✅ Good: Graceful error handling
export function MyComponent({ data, onAction }: MyComponentProps) {
  try {
    const validated = myComponentSchema.parse(data);
    return <Card>{/* render */}</Card>;
  } catch (error) {
    return (
      <Card>
        <CardContent>
          <p className="text-red-500">Invalid data: {error.message}</p>
        </CardContent>
      </Card>
    );
  }
}

// ❌ Bad: Errors crash component
export function MyComponent({ data, onAction }: MyComponentProps) {
  const validated = myComponentSchema.parse(data); // throws
  return <Card>{/* render */}</Card>;
}
```

---

## Future Enhancements

### Planned Components

- **TimelineCard**: Case event timeline with milestones
- **DocumentCard**: Document preview with metadata
- **DeadlineCard**: Statute of limitations tracker
- **ExpenseCard**: Medical bills and case expenses
- **NoteCard**: Case notes with attachments
- **FormCard**: Interactive forms (demand letters, etc)

### Planned Features

- **Canvas persistence**: Save artifact state across sessions
- **Artifact export**: Export artifacts as PDF/JSON
- **Artifact sharing**: Share artifact URLs with team
- **Artifact templates**: Pre-built artifact collections
- **Artifact search**: Search artifacts by content
- **Artifact history**: Track changes over time

### Tiptap Integration

Replace Monaco editor with Tiptap for legal documents:

- Rich text editing
- Document templates
- Track changes
- Comments and annotations
- Export to DOCX/PDF
- Integration with artifact system

---

## Technical Reference

### Key Files

| File | Purpose |
|------|---------|
| `ui/components/artifacts/types.ts` | Type definitions |
| `ui/components/artifacts/registry.tsx` | Component registry |
| `ui/components/artifacts/artifact-canvas.tsx` | Canvas renderer |
| `ui/lib/copilotkit-artifact-tools.tsx` | CopilotKit tools |
| `ui/lib/copilotkit-workspace-tools.tsx` | Workspace tools |
| `ui/app/workbench.tsx` | Main UI layout |
| `ui/app/api/copilotkit/route.ts` | API proxy |
| `src/roscoe/copilotkit_server.py` | Backend server |

### Dependencies

**UI (package.json):**

```json
{
  "@copilotkit/react-core": "^1.5.0",
  "@copilotkit/react-ui": "^1.5.0",
  "react": "^19.0.0",
  "next": "^16.0.0",
  "zod": "^3.22.0"
}
```

**Backend (pyproject.toml):**

```toml
[project]
dependencies = [
    "copilotkit>=1.5.0",
    "ag-ui-langgraph>=0.1.0",
    "fastapi>=0.100.0",
    "langgraph>=0.2.0",
]
```

### Type Definitions

```typescript
// Artifact component definition
interface ArtifactComponent<TProps = any> {
  id: string;
  name: string;
  description: string;
  component: ComponentType<TProps>;
  schema: ZodSchema;
  category: "contact" | "medical" | "insurance" | "legal" | "document" | "ui";
}

// Props passed to components
interface ArtifactProps {
  artifactId: string;
  data: Record<string, any>;
  onAction?: (action: string, payload: any) => void;
}

// Artifact instance in canvas
interface ArtifactInstance {
  id: string;
  componentId: string;
  data: Record<string, any>;
}
```

---

## Resources

- **CopilotKit Docs**: https://docs.copilotkit.ai/
- **AG-UI Protocol**: https://ag-ui.dev/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Zod**: https://zod.dev/
- **shadcn/ui**: https://ui.shadcn.com/
- **Tailwind CSS**: https://tailwindcss.com/

---

## Support

For questions or issues:

1. Check logs: `docker compose logs copilotkit ui`
2. Review this documentation
3. Test with minimal example
4. Check CopilotKit GitHub issues
5. Contact team lead

**Common Issues:**

- **Artifact not appearing**: Check component is imported in workbench
- **Schema validation failing**: Check Zod schema matches data structure
- **Tool not available**: Check useCopilotArtifactTools() is called
- **Backend not responding**: Check copilotkit service is running
- **UI not updating**: Rebuild and restart UI container
