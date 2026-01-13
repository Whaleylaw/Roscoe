# CLAUDE.md - Second Brain Implementation

## Overview

**Status:** Implementation complete (Phases 2-6), NOT YET INTEGRATED into main Roscoe agent.

This folder contains a standalone implementation of the "Second Brain" system - middleware and tools for persistent memory, attorney context (TELOS), topic continuity, and proactive surfacing (morning digests).

## Key Components

| File | Purpose |
|------|---------|
| `core/memory_backend.py` | CompositeBackend: routes `/memories/` to persistent storage |
| `core/telos_middleware.py` | Loads attorney context (mission, goals, preferences) at session start |
| `core/continuity_middleware.py` | Detects topic continuity, creates MemoryBox segments |
| `core/proactive_surfacing_middleware.py` | Triggers morning digests at 7 AM |
| `paralegal/fix_capture_tool.py` | Tool to correct misclassified captures |
| `paralegal/digest_generator/` | Subagent that generates morning briefings |

## TELOS System

Attorney context files (to be placed in `/memories/TELOS/`):
- `mission.md` - Firm mission/purpose
- `goals.md` - Current priorities
- `preferences.md` - Working style preferences
- `contacts.md` - Key contacts
- `strategies.md` - Legal strategies

## Graph Schema Extensions

```cypher
# CaptureLog - tracks all captures
(:CaptureLog {id, entity_type, entity_id, confidence, status, created_at})

# MemoryBox - topic-coherent conversation segments
(:MemoryBox {id, topic, summary, created_at})

# EventTrace - linked narrative chains
(:EventTrace {id, trace_type, participants, created_at})

# Relationships
(:MemoryBox)-[:CONTINUES_FROM]->(:MemoryBox)
(:Message)-[:PART_OF]->(:MemoryBox)
```

## Integration (Not Yet Done)

To integrate into main agent, add to `src/roscoe/agents/paralegal/agent.py`:

```python
from roscoe.second_brain_implementation.core.memory_backend import create_memory_backend
from roscoe.second_brain_implementation.core.telos_middleware import TELOSMiddleware
from roscoe.second_brain_implementation.core.continuity_middleware import ContinuityMiddleware
from roscoe.second_brain_implementation.core.proactive_surfacing_middleware import ProactiveSurfacingMiddleware

# In agent config:
middleware=[
    TELOSMiddleware(workspace_dir=workspace_dir),
    ContinuityMiddleware(graph_client=graph_client),
    ProactiveSurfacingMiddleware(graph_client=graph_client, slack_client=slack_client),
    # ... existing middleware
]
```

## Migrations Required

Before integration, run:
```bash
python migrations/add_inbox_log_indexes.py
python migrations/add_memorybox_schema.py
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Integration tests
python -m pytest tests/integration/test_second_brain_flow.py -v
```

## Important Notes

1. This is a **staging area** - code here is complete but not integrated
2. The main agent in `src/roscoe/agents/paralegal/` does NOT use these yet
3. TELOS files need to be created in workspace `/memories/TELOS/` before use
4. Morning digests require Slack integration or write to `/memories/digests/`

## Reference

- Full plan: `2026-01-11-roscoe-v2-second-brain-phases-2-6.md`
- Progress tracking: `progress.json`, `progress.txt`
- Detailed README: `README.md`
