# Roscoe v2 Second Brain Implementation

Complete implementation of Phases 2-6 from the Roscoe v2 Second Brain plan.

## Completion Status

**All 12 tasks completed** ✅

- Phase 2: Memory Architecture (Tasks 1-5) ✅
- Phase 3: Continuity & Traces (Tasks 6-8) ✅
- Phase 4: Proactive Surfacing (Tasks 9-10) ✅
- Phase 5: Skills & Tools (Task 11) ✅
- Phase 6: Integration Testing (Task 12) ✅

## Directory Structure

```
second_brain_implementation/
├── core/                           # Core middleware components
│   ├── memory_backend.py          # CompositeBackend routing (/memories/ persistence)
│   ├── telos_middleware.py        # Attorney context loading
│   ├── continuity_middleware.py   # Topic continuity detection
│   └── proactive_surfacing_middleware.py  # Morning digest triggers
│
├── paralegal/                      # Paralegal agent extensions
│   ├── digest_generator/          # Morning digest subagent
│   │   ├── agent.py              # Subagent implementation
│   │   ├── prompts.py            # Digest generation prompts
│   │   └── __init__.py
│   └── fix_capture_tool.py       # Capture correction tool
│
├── workspace/                      # Workspace files
│   ├── Skills/
│   │   └── MorningBrief/         # Morning brief skill
│   │       └── SKILL.md
│   └── memories/
│       └── TELOS/                # Attorney context templates
│           ├── mission.md
│           ├── goals.md
│           ├── preferences.md
│           ├── contacts.md
│           └── strategies.md
│
├── migrations/                     # Database schema migrations
│   ├── add_inbox_log_indexes.py  # CaptureLog indexes
│   └── add_memorybox_schema.py   # MemoryBox/EventTrace schema
│
├── scripts/                        # Setup scripts
│   └── init_telos_structure.sh   # Initialize /memories/ structure
│
├── tests/                          # Test suite
│   ├── core/                      # Unit tests for middleware
│   │   ├── test_telos_middleware.py
│   │   ├── test_continuity_middleware.py
│   │   └── test_proactive_surfacing.py
│   ├── integration/               # Integration tests
│   │   └── test_second_brain_flow.py
│   └── test_digest_generator.py  # Digest generator tests
│
├── 2026-01-11-roscoe-v2-second-brain-phases-2-6.md  # Original plan
├── progress.json                   # Task completion tracking
├── progress.txt                    # Session log
└── README.md                       # This file
```

## Features Implemented

### 1. Memory Architecture (Phase 2)
- **CompositeBackend**: Routes /memories/ to persistent storage, everything else ephemeral
- **TELOS System**: Attorney context (mission, goals, preferences, contacts, strategies)
- **TELOSMiddleware**: Loads attorney context at session start
- **Inbox Logging**: CaptureLog nodes track all captures with status (filed/needs_review)
- **Fix Capture Tool**: Corrects misclassified captures with reclassification

### 2. Continuity & Traces (Phase 3)
- **ContinuityMiddleware**: Detects topic continuity between messages
- **MemoryBox Schema**: Topic-coherent conversation segments
- **EventTrace Schema**: Linked narrative chains
- **Topic Detection**: LLM-based continuity checking (Membox pattern)

### 3. Proactive Surfacing (Phase 4)
- **ProactiveSurfacingMiddleware**: Triggers morning digests at 7 AM
- **Digest Generator Subagent**: Queries graph + calendar for daily briefing
- **<150 Word Digests**: TOP 3 ACTIONS, CALENDAR, STUCK/AVOIDING, SMALL WIN
- **Duplicate Prevention**: One digest per day per user

### 4. Skills & Tools (Phase 5)
- **MorningBrief Skill**: User-invoked briefing skill with Cypher queries
- **Auto-Discovery**: Skills scanned from workspace/Skills/ directory
- **Semantic Matching**: Triggers based on user query similarity

### 5. Integration Testing (Phase 6)
- **3 Integration Tests**: Capture flow, continuity detection, digest generation
- **Mock-Based**: No database required for CI/CD
- **All Tests Passing**: 3/3 tests pass in 2.76 seconds

## Installation

### 1. Copy Files to Roscoe Installation

```bash
# Copy middleware
cp -r core/* /path/to/Roscoe_v1_essentials/core/

# Copy paralegal extensions
cp -r paralegal/* /path/to/Roscoe_v1_essentials/paralegal/

# Copy workspace files
cp -r workspace/* /path/to/Roscoe_v1_essentials/workspace/

# Copy tests
cp -r tests/* /path/to/Roscoe_v1_essentials/tests/
```

### 2. Run Migrations

```bash
cd /path/to/Roscoe_v1_essentials

# Add inbox log indexes
FALKORDB_HOST=localhost FALKORDB_PORT=6380 python core/migrations/add_inbox_log_indexes.py

# Add MemoryBox schema
FALKORDB_HOST=localhost FALKORDB_PORT=6380 python core/migrations/add_memorybox_schema.py
```

### 3. Initialize TELOS Structure

```bash
cd /path/to/Roscoe_v1_essentials
bash scripts/init_telos_structure.sh
```

### 4. Update Agent Configuration

Add middleware to your agent in `paralegal/agent.py`:

```python
from core.memory_backend import create_memory_backend
from core.telos_middleware import TELOSMiddleware
from core.continuity_middleware import ContinuityMiddleware
from core.proactive_surfacing_middleware import ProactiveSurfacingMiddleware

personal_assistant_agent = create_deep_agent(
    system_prompt=personal_assistant_prompt,
    backend=create_memory_backend,  # Enable /memories/ persistence
    middleware=[
        # Capture detection (existing)
        CaptureMiddleware(...),

        # Attorney context (NEW)
        TELOSMiddleware(workspace_dir=workspace_dir),

        # Case context (existing)
        case_context_middleware,

        # Workflow (existing)
        workflow_middleware,

        # Topic continuity (NEW)
        ContinuityMiddleware(graph_client=graph_client),

        # Proactive surfacing (NEW)
        ProactiveSurfacingMiddleware(
            graph_client=graph_client,
            slack_client=slack_client
        ),

        # Skills, UI, Shell (existing)
        skill_selector_middleware,
        ui_context_middleware,
        shell_tool_middleware,
    ],
    # ... rest of config
)
```

## Running Tests

```bash
# Run all tests
cd /path/to/Roscoe_v1_essentials
python -m pytest tests/ -v

# Run integration tests only
python -m pytest tests/integration/test_second_brain_flow.py -v

# Run specific middleware tests
python -m pytest tests/core/test_telos_middleware.py -v
python -m pytest tests/core/test_continuity_middleware.py -v
python -m pytest tests/core/test_proactive_surfacing.py -v
```

## Usage

### Morning Digest (Automatic)
- Triggers at 7 AM on first agent invocation
- Delivers to Slack or `/memories/digests/`
- One digest per day per user

### Morning Brief (Manual)
- User asks: "what's on my calendar?" or "morning brief"
- MorningBrief skill activates via semantic matching
- Queries graph + calendar for current info

### Capture & Fix
- Agent automatically detects capture patterns
- Creates Task/Note/Idea entities in graph
- Low confidence → "needs review" in inbox
- Use `fix_capture(log_id, correction)` to reclassify

### Topic Continuity
- Related messages automatically linked via MemoryBox
- Creates CONTINUES_FROM relationships in graph
- Enables trace queries across conversation threads

### TELOS Context
- Edit files in `/memories/TELOS/` to personalize
- Context loaded automatically at session start
- Influences agent recommendations and priorities

## Architecture Notes

### Middleware Execution Order
1. CaptureMiddleware (detect captures)
2. TELOSMiddleware (load attorney context)
3. CaseContextMiddleware (inject case data)
4. WorkflowMiddleware (compute phase/landmarks)
5. ContinuityMiddleware (link related messages)
6. ProactiveSurfacingMiddleware (morning digests)
7. SkillSelectorMiddleware (match skills)
8. UIContextMiddleware (bridge UI state)
9. ShellToolMiddleware (file system access)

### Graph Schema Extensions
- **CaptureLog**: Tracks all captures with status/confidence
- **MemoryBox**: Topic-coherent conversation segments
- **EventTrace**: Linked narrative chains
- **CONTINUES_FROM**: Relationship between MemoryBoxes

### Backend Architecture
- **CompositeBackend**: Routes paths to different backends
  - `/memories/` → StoreBackend (PostgresStore, persistent)
  - Everything else → StateBackend (ephemeral)

## Implementation Workflow

This implementation used the **subagent-driven-development** workflow:
- Each task executed by fresh subagent
- Two-stage review: spec compliance → code quality
- Progress tracked in JSON + text files
- Crash-resistant via checkpoints

## References

- **Plan**: `2026-01-11-roscoe-v2-second-brain-phases-2-6.md`
- **Progress**: `progress.json` and `progress.txt`
- **CLAUDE.md**: See repository root for architecture overview
- **Deep Agents**: Framework documentation in `/deep_agents/`
- **PAI**: Reference implementation in `/PAI/`
- **Membox**: Research papers in `/Membox/`

## Credits

Implementation completed: 2026-01-12
Tasks: 12/12 complete
Framework: Deep Agents + LangGraph
Testing: pytest with mock-based integration tests
