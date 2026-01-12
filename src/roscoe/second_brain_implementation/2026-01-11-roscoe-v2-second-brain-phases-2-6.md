# Roscoe v2 Second Brain Implementation Plan (Phases 2-6)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build attorney's personal second brain system on top of Roscoe v1 with memory architecture, topic continuity, proactive surfacing, and relationship tracking

**Architecture:** Layer personal assistant features using Deep Agents middleware + FalkorDB graph + /memories/ filesystem, integrating concepts from Second Brain, PAI, and Membox

**Tech Stack:** Deep Agents, FalkorDB, LangGraph, CompositeBackend, Claude Haiku/Sonnet, sentence-transformers, Next.js

**Context:** Phase 1 (CaptureMiddleware) is complete. This plan covers Phases 2-6.

---

## Phase 2: Memory Architecture

### Task 1: CompositeBackend Setup with /memories/ Routes

**Files:**
- Modify: `Roscoe_v1_essentials/paralegal/agent.py`
- Create: `Roscoe_v1_essentials/core/memory_backend.py`

**Step 1: Write test for CompositeBackend routing**

```python
# tests/core/test_memory_backend.py
import pytest
from roscoe.core.memory_backend import create_memory_backend
from deepagents.backends import CompositeBackend

def test_memory_backend_routes_to_store():
    """Test that /memories/ paths route to persistent store."""
    backend = create_memory_backend(mock_runtime)

    # Should route /memories/ to StoreBackend
    assert backend.resolve_path("/memories/TELOS/mission.md") == "store"

    # Should route everything else to StateBackend
    assert backend.resolve_path("/workspace/file.py") == "state"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/core/test_memory_backend.py::test_memory_backend_routes_to_store -v`
Expected: FAIL with "module 'roscoe.core.memory_backend' not found"

**Step 3: Implement create_memory_backend()**

```python
# Roscoe_v1_essentials/core/memory_backend.py
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

def create_memory_backend(runtime):
    """
    Create hybrid filesystem routing backend.

    - /memories/ → Persistent (PostgresStore via StoreBackend)
    - Everything else → Ephemeral (StateBackend)

    Based on PAI memory architecture pattern.
    """
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={
            "/memories/": StoreBackend(runtime),
        }
    )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/core/test_memory_backend.py::test_memory_backend_routes_to_store -v`
Expected: PASS

**Step 5: Integrate into agent.py**

```python
# In paralegal/agent.py
from roscoe.core.memory_backend import create_memory_backend

# Replace FilesystemBackend with create_memory_backend
personal_assistant_agent = create_deep_agent(
    system_prompt=minimal_personal_assistant_prompt,
    backend=create_memory_backend,  # Changed
    # ... rest unchanged
)
```

**Step 6: Commit**

```bash
git add Roscoe_v1_essentials/core/memory_backend.py Roscoe_v1_essentials/paralegal/agent.py tests/core/test_memory_backend.py
git commit -m "feat: add CompositeBackend for /memories/ persistent storage

- Routes /memories/ to StoreBackend (persistent)
- Routes everything else to StateBackend (ephemeral)
- Enables cross-session memory persistence"
```

---

### Task 2: TELOS Directory Structure

**Files:**
- Create: `Roscoe_v1_essentials/workspace/memories/TELOS/mission.md`
- Create: `Roscoe_v1_essentials/workspace/memories/TELOS/goals.md`
- Create: `Roscoe_v1_essentials/workspace/memories/TELOS/preferences.md`
- Create: `Roscoe_v1_essentials/workspace/memories/TELOS/contacts.md`
- Create: `Roscoe_v1_essentials/workspace/memories/TELOS/strategies.md`

**Step 1: Create directory structure script**

```bash
# Roscoe_v1_essentials/scripts/init_telos_structure.sh
#!/bin/bash
MEMORIES_DIR="${WORKSPACE_DIR:-/mnt/workspace}/memories"

mkdir -p "$MEMORIES_DIR/TELOS"
mkdir -p "$MEMORIES_DIR/Work"
mkdir -p "$MEMORIES_DIR/Learning"/{OBSERVE,THINK,PLAN,BUILD,EXECUTE,VERIFY,LEARN}
mkdir -p "$MEMORIES_DIR/Signals"
mkdir -p "$MEMORIES_DIR/History"/{sessions,research,decisions,learnings}
mkdir -p "$MEMORIES_DIR/Continuity"

echo "Created /memories/ directory structure"
```

**Step 2: Create TELOS template files**

```markdown
# workspace/memories/TELOS/mission.md
# Professional Mission

## Primary Practice Areas
- Personal injury (motor vehicle accidents)
- Medical malpractice
- Workers' compensation

## Mission Statement
[Attorney fills this in]

## Core Values
[Attorney fills this in]
```

```markdown
# workspace/memories/TELOS/goals.md
# Current Goals

## Short-Term (3 months)
- [ ] Goal 1
- [ ] Goal 2

## Long-Term (1 year)
- [ ] Goal 1
- [ ] Goal 2

## Career Development
[Attorney fills this in]
```

```markdown
# workspace/memories/TELOS/preferences.md
# Work Preferences

## Communication Style
[Attorney fills this in]

## Work Schedule
[Attorney fills this in]

## Tool Preferences
[Attorney fills this in]

## Case Priorities
[Attorney fills this in]
```

```markdown
# workspace/memories/TELOS/contacts.md
# VIP Contacts

## Key Judges
[Attorney fills this in]

## Frequent Opposing Counsel
[Attorney fills this in]

## Expert Witnesses
[Attorney fills this in]

## Referral Sources
[Attorney fills this in]
```

```markdown
# workspace/memories/TELOS/strategies.md
# Legal Strategies & Approaches

## Negotiation Tactics
[Attorney fills this in]

## Motion Practice
[Attorney fills this in]

## Discovery Strategies
[Attorney fills this in]
```

**Step 3: Run init script**

Run: `bash Roscoe_v1_essentials/scripts/init_telos_structure.sh`
Expected: Directories and template files created

**Step 4: Verify structure**

Run: `tree workspace/memories/ -L 2`
Expected: See TELOS/, Work/, Learning/, Signals/, History/, Continuity/ directories

**Step 5: Commit**

```bash
git add Roscoe_v1_essentials/scripts/init_telos_structure.sh workspace/memories/
git commit -m "feat: create TELOS and /memories/ directory structure

- Added TELOS template files (mission, goals, preferences, etc.)
- Created PAI-style directory structure (Learning/OBSERVE-LEARN, Signals, History)
- Added Membox-style Continuity directory
- Init script for easy setup"
```

---

### Task 3: TELOSMiddleware Implementation

**Files:**
- Create: `Roscoe_v1_essentials/core/telos_middleware.py`
- Create: `tests/core/test_telos_middleware.py`
- Modify: `Roscoe_v1_essentials/paralegal/agent.py`

**Step 1: Write failing test**

```python
# tests/core/test_telos_middleware.py
def test_telos_middleware_loads_on_startup():
    """Test that TELOS files are loaded once per session."""
    middleware = TELOSMiddleware()

    # Create mock TELOS files
    state = {}
    runtime = MockRuntime()

    result = middleware.before_agent(state, runtime)

    assert result['telos_loaded'] == True
    assert 'telos_content' in result
    assert 'mission' in result['telos_content'].lower()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/core/test_telos_middleware.py -v`
Expected: FAIL

**Step 3: Implement TELOSMiddleware**

```python
# Roscoe_v1_essentials/core/telos_middleware.py
"""
TELOSMiddleware - Loads attorney context at session start.

Based on PAI TELOS pattern: deep goal understanding for better recommendations.
"""
import os
from pathlib import Path
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import SystemMessage

class TELOSMiddleware(AgentMiddleware):
    """
    Load attorney context from /memories/TELOS/ at session start.

    Files loaded:
    - mission.md - Professional mission
    - goals.md - Current goals
    - preferences.md - Work style preferences
    - contacts.md - VIP contacts (optional)
    - strategies.md - Legal strategies (optional)
    """

    name: str = "telos"
    tools: list = []

    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or os.getenv('WORKSPACE_DIR', '/mnt/workspace')
        self.telos_dir = Path(self.workspace_dir) / 'memories' / 'TELOS'

    def before_agent(self, state, runtime):
        """Load TELOS files once per session."""
        # Check if already loaded
        if state.get('telos_loaded'):
            return None

        # Read TELOS files
        telos_files = [
            'mission.md',
            'goals.md',
            'preferences.md',
        ]

        telos_content_parts = []
        for filename in telos_files:
            file_path = self.telos_dir / filename
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    if content.strip() and '[Attorney fills this in]' not in content:
                        telos_content_parts.append(f"## {filename}\n\n{content}")
            except FileNotFoundError:
                continue

        if not telos_content_parts:
            return None

        telos_content = "\n\n".join([
            "# Attorney Context (TELOS)",
            "The following context helps you understand the attorney's goals and preferences:",
            "\n\n".join(telos_content_parts)
        ])

        return {
            'telos_loaded': True,
            'telos_content': telos_content
        }

    def wrap_model_call(self, request, handler):
        """Inject TELOS into system message if loaded."""
        telos_content = request.state.get('telos_content')

        if not telos_content:
            return handler(request)

        # Inject into system message
        new_system_message = SystemMessage(
            content=f"{request.system_message.content}\n\n{telos_content}"
        )

        return handler(request.override(system_message=new_system_message))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/core/test_telos_middleware.py -v`
Expected: PASS

**Step 5: Add to agent middleware stack**

```python
# In paralegal/agent.py
from roscoe.core.telos_middleware import TELOSMiddleware

middleware=[
    # Capture detection
    CaptureMiddleware(...),

    # Attorney context (NEW)
    TELOSMiddleware(workspace_dir=workspace_dir),

    # Case context
    case_context_middleware,
    # ... rest unchanged
]
```

**Step 6: Commit**

```bash
git add Roscoe_v1_essentials/core/telos_middleware.py tests/core/test_telos_middleware.py Roscoe_v1_essentials/paralegal/agent.py
git commit -m "feat: add TELOSMiddleware for attorney context loading

- Loads mission, goals, preferences at session start
- Injects into system prompt automatically
- Based on PAI TELOS pattern for deep goal understanding"
```

---

### Task 4: Inbox Log Schema in Graph

**Files:**
- Create: `Roscoe_v1_essentials/core/migrations/add_inbox_log_indexes.py`
- Modify: `Roscoe_v1_essentials/core/capture_middleware.py`

**Step 1: Write migration for inbox log indexes**

```python
# Roscoe_v1_essentials/core/migrations/add_inbox_log_indexes.py
"""Add indexes for CaptureLog inbox tracking."""

INBOX_INDEXES = [
    IndexDefinition("CaptureLog", "captured_at"),
    IndexDefinition("CaptureLog", "status"),  # filed|needs_review|corrected
    IndexDefinition("CaptureLog", "confidence"),
]
```

**Step 2: Run migration**

Run: `FALKORDB_HOST=localhost FALKORDB_PORT=6380 python add_inbox_log_indexes.py`
Expected: 3 indexes created

**Step 3: Update capture_middleware to use status field**

```python
# In capture_middleware.py _write_capture_log method
query = """
    CREATE (l:CaptureLog {
        id: $id,
        raw_text: $raw_text,
        category: $category,
        confidence: $confidence,
        status: $status,  # NEW: filed|needs_review
        entity_id: $entity_id,
        timestamp: timestamp()
    })
    RETURN l.id as log_id
"""

params = {
    # ...
    'status': 'filed' if confidence >= 0.6 else 'needs_review',
}
```

**Step 4: Test inbox log query**

```python
def test_query_inbox_needs_review():
    """Test querying captures that need review."""
    # Create test captures with low confidence
    # Query for needs_review status
    # Verify results
```

**Step 5: Commit**

```bash
git add Roscoe_v1_essentials/core/migrations/add_inbox_log_indexes.py Roscoe_v1_essentials/core/capture_middleware.py
git commit -m "feat: add inbox log status tracking

- Added status field to CaptureLog (filed|needs_review)
- Created indexes for querying inbox
- Low confidence captures marked needs_review"
```

---

### Task 5: Fix Capture Tool

**Files:**
- Create: `Roscoe_v1_essentials/agents/paralegal/fix_capture_tool.py`
- Modify: `Roscoe_v1_essentials/agents/paralegal/tools.py`

**Step 1: Write test for fix_capture tool**

```python
def test_fix_capture_reclassifies():
    """Test that fix_capture reclassifies and updates graph."""
    # Create test capture with wrong category
    log_id = create_test_capture(category="ideas", should_be="tasks")

    # Fix it
    result = fix_capture(
        log_id=log_id,
        correction="This should be a task, not an idea"
    )

    # Verify reclassified
    assert result.success == True
    assert result.new_category == "tasks"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/agents/paralegal/test_fix_capture_tool.py -v`
Expected: FAIL

**Step 3: Implement fix_capture tool**

```python
# Roscoe_v1_essentials/agents/paralegal/fix_capture_tool.py
from langchain.tools import tool
from roscoe.core.graphiti_client import run_cypher_query

@tool
def fix_capture(log_id: str, correction: str) -> str:
    """
    Fix incorrectly classified capture (Second Brain Fix Button).

    Args:
        log_id: CaptureLog ID from inbox
        correction: What's wrong and how to fix it

    Returns:
        Confirmation message with new classification

    Example:
        fix_capture("CaptureLog_123", "This should be a task, not an idea")
    """
    # Get original log and entity
    query = """
        MATCH (log:CaptureLog {id: $log_id})
        OPTIONAL MATCH (log)-[r:FILED_AS]->(old_entity)
        RETURN log, old_entity, r
    """
    result = run_cypher_query(query, {"log_id": log_id})

    if not result:
        return f"❌ Capture log {log_id} not found"

    log_data = result[0]['log']
    old_entity = result[0].get('old_entity')

    # Parse correction to determine new category
    from roscoe.core.capture_prompts import build_classification_prompt
    from langchain_anthropic import ChatAnthropic

    correction_prompt = f"""
    Original capture: "{log_data['raw_text']}"
    Original classification: {log_data['category']}
    User correction: "{correction}"

    Reclassify this capture based on the correction.
    Return JSON with new category and extracted fields.
    """

    llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
    response = llm.invoke(correction_prompt)
    new_classification = json.loads(response.content)

    # Delete old entity
    if old_entity:
        delete_query = "MATCH (e) WHERE id(e) = $id DETACH DELETE e"
        run_cypher_query(delete_query, {"id": old_entity.id})

    # Create new entity
    from roscoe.core.capture_middleware import CaptureMiddleware
    middleware = CaptureMiddleware()
    new_entity_id = await middleware._write_to_graph(new_classification, log_data['raw_text'])

    # Update log
    update_query = """
        MATCH (log:CaptureLog {id: $log_id})
        SET log.category = $new_category,
            log.status = 'corrected',
            log.correction_count = coalesce(log.correction_count, 0) + 1,
            log.filed_to_entity_id = $new_entity_id
        RETURN log
    """
    run_cypher_query(update_query, {
        "log_id": log_id,
        "new_category": new_classification['category'],
        "new_entity_id": new_entity_id
    })

    return f"✅ Corrected: {log_data['raw_text'][:50]}... → {new_classification['category']}"
```

**Step 4: Add to tools list**

```python
# In paralegal/tools.py
from roscoe.agents.paralegal.fix_capture_tool import fix_capture

# Add to agent tools list
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/agents/paralegal/test_fix_capture_tool.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add Roscoe_v1_essentials/agents/paralegal/fix_capture_tool.py tests/agents/paralegal/test_fix_capture_tool.py
git commit -m "feat: add fix_capture tool for correction workflow

- Reclassifies incorrectly categorized captures
- Deletes old entity, creates new one
- Updates CaptureLog with correction count
- Implements Second Brain Fix Button pattern"
```

---

## Phase 3: Continuity & Traces

### Task 6: ContinuityMiddleware Skeleton

**Files:**
- Create: `Roscoe_v1_essentials/core/continuity_middleware.py`
- Create: `tests/core/test_continuity_middleware.py`

**Step 1: Write test for topic continuity detection**

```python
def test_detects_topic_continuation():
    """Test that middleware detects topic continuation."""
    middleware = ContinuityMiddleware(graph_client)

    # Simulate recent box about "Martinez settlement"
    recent_boxes = [{"box_id": "box1", "topic": "Martinez settlement"}]

    # New message also about Martinez settlement
    message = "Talked to adjuster, they agreed to $50K"

    result = middleware._check_continuity(recent_boxes[0], message)

    assert result['continues'] == True
```

**Step 2: Run test**

Run: `pytest tests/core/test_continuity_middleware.py::test_detects_topic_continuation -v`
Expected: FAIL

**Step 3: Implement ContinuityMiddleware skeleton**

```python
# Roscoe_v1_essentials/core/continuity_middleware.py
"""
ContinuityMiddleware - Membox-inspired topic continuity detection.

Tracks conversation segments and links related captures into event traces.
"""
from langchain.agents.middleware import AgentMiddleware
from sentence_transformers import SentenceTransformer

class ContinuityMiddleware(AgentMiddleware):
    """
    Detect topic continuity and link captures into memory boxes.

    Based on Membox research: topic continuity-based memory formation.
    """

    name: str = "continuity"
    tools: list = []

    def __init__(self, graph_client):
        self.graph_client = graph_client
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def before_agent(self, state, runtime):
        """Load recent memory boxes for continuity checking."""
        thread_id = runtime.config.get('configurable', {}).get('thread_id')

        # Get recent boxes from graph
        recent_boxes = self._get_recent_boxes(thread_id, limit=5)

        return {
            "recent_memory_boxes": recent_boxes,
            "current_thread_id": thread_id
        }

    def _get_recent_boxes(self, thread_id: str, limit: int = 5):
        """Query graph for recent memory boxes."""
        query = """
            MATCH (box:MemoryBox {thread_id: $thread_id})
            RETURN box
            ORDER BY box.started_at DESC
            LIMIT $limit
        """
        result = self.graph_client.run(query, {"thread_id": thread_id, "limit": limit})
        return [row['box'] for row in result] if result else []

    def _check_continuity(self, recent_box, current_message):
        """
        Check if current message continues topic of recent box.

        Uses LLM-based continuity detection (Membox pattern).
        """
        # To be implemented in next task
        return {'continues': False}
```

**Step 4: Run test**

Run: `pytest tests/core/test_continuity_middleware.py::test_detects_topic_continuation -v`
Expected: FAIL (returns False, should be True)

**Step 5: Commit skeleton**

```bash
git add Roscoe_v1_essentials/core/continuity_middleware.py tests/core/test_continuity_middleware.py
git commit -m "feat: add ContinuityMiddleware skeleton

- Loads recent memory boxes from graph
- Prepares for topic continuity detection
- Based on Membox research pattern"
```

---

### Task 7: MemoryBox Graph Schema

**Files:**
- Create: `Roscoe_v1_essentials/core/migrations/add_memorybox_schema.py`

**Step 1: Write migration**

```python
# add_memorybox_schema.py
MEMORYBOX_INDEXES = [
    IndexDefinition("MemoryBox", "box_id"),
    IndexDefinition("MemoryBox", "thread_id"),
    IndexDefinition("MemoryBox", "started_at"),
    IndexDefinition("EventTrace", "trace_id"),
]

MEMORYBOX_SCHEMA = """
// MemoryBox - Topic-coherent conversation segment
CREATE (box:MemoryBox {
  box_id: randomUUID(),
  thread_id: $thread_id,
  started_at: timestamp(),
  topic: $topic,
  keywords: $keywords,
  events: $events_array,
  content_summary: $summary
})

// EventTrace - Linked narrative chain
CREATE (trace:EventTrace {
  trace_id: randomUUID(),
  theme: $theme,
  started_at: timestamp(),
  event_count: 1
})

// Link box to trace
CREATE (box)-[:PART_OF_TRACE {
  event: $event,
  order: 0,
  linked_at: timestamp()
}]->(trace)
"""
```

**Step 2: Run migration**

Run: `FALKORDB_HOST=localhost FALKORDB_PORT=6380 python add_memorybox_schema.py`
Expected: Indexes created

**Step 3: Test creating a MemoryBox**

```python
def test_create_memory_box():
    """Test creating MemoryBox node in graph."""
    box_data = {
        "thread_id": "thread_123",
        "topic": "Martinez settlement discussion",
        "keywords": ["settlement", "Martinez", "adjuster"],
        "events_array": ["Initial discussion about offer"],
        "summary": "Discussed settlement offer with adjuster"
    }

    query = """
        CREATE (box:MemoryBox {
          box_id: randomUUID(),
          thread_id: $thread_id,
          started_at: timestamp(),
          topic: $topic,
          keywords: $keywords,
          events: $events_array,
          content_summary: $summary
        })
        RETURN box.box_id as box_id
    """

    result = graph.run(query, box_data)
    assert result[0]['box_id'] is not None
```

**Step 4: Commit**

```bash
git add Roscoe_v1_essentials/core/migrations/add_memorybox_schema.py
git commit -m "feat: add MemoryBox and EventTrace schema

- MemoryBox for topic-coherent segments
- EventTrace for linked narratives
- Based on Membox architecture"
```

---

### Task 8: Implement Topic Continuity Detection

**Files:**
- Modify: `Roscoe_v1_essentials/core/continuity_middleware.py`

**Step 1: Implement _check_continuity with LLM**

```python
def _check_continuity(self, recent_box, current_message):
    """
    LLM-based continuity check (Membox pattern).

    Prompt: "Does current message continue topic of previous messages?"
    """
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage

    prev_topic = recent_box.get('topic', '')
    prev_summary = recent_box.get('content_summary', '')

    prompt = f"""Please determine whether the current message continues with the main
topic of the previous messages. Only answer Yes/No.

Previous topic: {prev_topic}
Previous messages: {prev_summary}
Current message: {current_message}

Answer:"""

    llm = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0)
    response = llm.invoke([HumanMessage(content=prompt)])

    continues = 'yes' in response.content.lower()

    # Extract events/topics for linking
    extraction = self._extract_events_and_topic(current_message)

    return {
        'continues': continues,
        'new_topic': extraction.get('topic') if not continues else None,
        'events': extraction.get('events', [])
    }

def _extract_events_and_topic(self, message):
    """Extract topic and events from message."""
    from langchain_anthropic import ChatAnthropic

    prompt = f"""Extract the main topic and any events mentioned in this message.

Message: {message}

Return JSON:
{{
  "topic": "brief topic description",
  "events": ["event 1", "event 2"]
}}"""

    llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
    response = llm.invoke([HumanMessage(content=prompt)])

    return json.loads(response.content)
```

**Step 2: Update test**

Run: `pytest tests/core/test_continuity_middleware.py::test_detects_topic_continuation -v`
Expected: PASS

**Step 3: Add test for topic change**

```python
def test_detects_topic_change():
    """Test that new topic is detected."""
    recent_box = {"topic": "Martinez settlement", "content_summary": "Discussed offer"}
    new_message = "What's the weather like today?"

    result = middleware._check_continuity(recent_box, new_message)

    assert result['continues'] == False
    assert result['new_topic'] is not None
```

**Step 4: Commit**

```bash
git add Roscoe_v1_essentials/core/continuity_middleware.py tests/core/test_continuity_middleware.py
git commit -m "feat: implement LLM-based topic continuity detection

- Uses Claude Haiku for fast continuity check
- Extracts events and topics from messages
- Follows Membox continuity detection pattern"
```

---

## Phase 4: Proactive Surfacing

### Task 9: ProactiveSurfacingMiddleware Setup

**Files:**
- Create: `Roscoe_v1_essentials/core/proactive_surfacing_middleware.py`
- Create: `tests/core/test_proactive_surfacing.py`

**Step 1: Write test for morning digest trigger**

```python
def test_triggers_morning_digest_at_7am():
    """Test that morning digest triggers on first invocation after 7 AM."""
    middleware = ProactiveSurfacingMiddleware(graph_client, slack_client)

    # Simulate first invocation at 7:05 AM
    current_time = datetime(2026, 1, 12, 7, 5)

    result = middleware.before_agent(state, runtime, current_time=current_time)

    # Should trigger digest
    assert result['digest_triggered'] == True
```

**Step 2: Implement ProactiveSurfacingMiddleware**

```python
# proactive_surfacing_middleware.py
from datetime import datetime, time
from langchain.agents.middleware import AgentMiddleware

class ProactiveSurfacingMiddleware(AgentMiddleware):
    """
    Generate and deliver proactive digests (Second Brain Tap + PAI patterns).

    - Morning digest: 7 AM first invocation
    - Weekly review: Sunday first invocation
    """

    name: str = "proactive_surfacing"
    tools: list = []

    def __init__(self, graph_client, slack_client=None):
        self.graph_client = graph_client
        self.slack_client = slack_client
        self.last_digest_dates = {}  # user_id -> date

    def before_agent(self, state, runtime, current_time=None):
        """Check if digest is due and generate."""
        if current_time is None:
            current_time = datetime.now()

        user_id = runtime.config.get('configurable', {}).get('user_id', 'default')
        today = current_time.date()

        # Check if already generated today
        last_digest_date = self.last_digest_dates.get(user_id)
        if last_digest_date == today:
            return None

        # Check if it's after 7 AM
        if current_time.time() < time(7, 0):
            return None

        # Generate digest
        digest = self._generate_morning_digest(user_id, runtime.config.get('configurable', {}).get('thread_id'))

        # Deliver
        if digest:
            self._deliver_digest(digest, user_id)
            self.last_digest_dates[user_id] = today

            return {
                'digest_triggered': True,
                'digest_content': digest
            }

        return None

    def _generate_morning_digest(self, user_id, thread_id):
        """Generate morning digest (placeholder)."""
        # To be implemented with subagent
        return None

    def _deliver_digest(self, digest, user_id):
        """Deliver digest to Slack/UI."""
        # To be implemented
        pass
```

**Step 3: Commit skeleton**

```bash
git add Roscoe_v1_essentials/core/proactive_surfacing_middleware.py tests/core/test_proactive_surfacing.py
git commit -m "feat: add ProactiveSurfacingMiddleware skeleton

- Triggers morning digest at 7 AM first invocation
- Prevents duplicate digests same day
- Based on Second Brain Tap on Shoulder pattern"
```

---

### Task 10: Digest Generator Subagent

**Files:**
- Create: `Roscoe_v1_essentials/agents/digest_generator/agent.py`
- Create: `Roscoe_v1_essentials/agents/digest_generator/prompts.py`

**Step 1: Write digest generator system prompt**

```python
# agents/digest_generator/prompts.py
DIGEST_GENERATOR_PROMPT = """You are a digest generator for an attorney's second brain.

Query sources:
1. Graph: Tasks with due_date <= today OR status != 'complete'
2. Graph: People with follow_ups != null
3. Graph: Cases with upcoming SOL or court dates
4. Calendar: Today's events
5. /memories/Work/: Active work items
6. /memories/Signals/: Recent ratings/patterns

Generate a digest with:
- TOP 3 ACTIONS (most important concrete steps for today)
- CALENDAR (today's events from Google Calendar)
- STUCK/AVOIDING (one thing that might be getting stuck)
- SMALL WIN (one accomplishment or progress to notice)

Keep under 150 words. Be specific and actionable.
No fluff or motivation speak. (Second Brain principle #6)
"""
```

**Step 2: Create digest generator subagent**

```python
# agents/digest_generator/agent.py
from deepagents import create_agent
from roscoe.agents.paralegal.models import get_agent_llm

digest_generator_subagent = create_agent(
    name="digest-generator",
    system_prompt=DIGEST_GENERATOR_PROMPT,
    model=get_agent_llm(),
    tools=[
        graph_query,
        list_events,  # Calendar
        read_file,
    ]
)

def generate_morning_digest(user_id: str, thread_id: str, target_date: str):
    """
    Generate morning digest using subagent.

    Returns dict with top_3_actions, calendar, stuck, small_win.
    """
    task = {
        "messages": [HumanMessage(content=f"""
Generate morning digest for {target_date}.

Query the graph for:
- Pending tasks (due today or overdue)
- People with pending follow-ups
- Cases with approaching deadlines

Query Google Calendar for today's events.

Return digest in JSON format:
{{
  "top_3_actions": ["action 1", "action 2", "action 3"],
  "calendar": ["event 1 at time", "event 2 at time"],
  "stuck_or_avoiding": "one thing that might be stuck",
  "small_win": "one recent accomplishment"
}}
""")]
    }

    result = digest_generator_subagent.invoke(task)

    # Parse JSON response
    digest_json = json.loads(result['messages'][-1].content)

    return digest_json
```

**Step 3: Integrate with ProactiveSurfacingMiddleware**

```python
# In proactive_surfacing_middleware.py
def _generate_morning_digest(self, user_id, thread_id):
    """Generate morning digest using subagent."""
    from roscoe.agents.digest_generator.agent import generate_morning_digest

    today = datetime.now().date().isoformat()
    digest = generate_morning_digest(user_id, thread_id, today)

    return digest
```

**Step 4: Commit**

```bash
git add Roscoe_v1_essentials/agents/digest_generator/
git commit -m "feat: add digest-generator subagent

- Queries graph + calendar for daily info
- Generates <150 word digest
- Returns top 3 actions, calendar, stuck item, small win
- Uses subagent for context isolation"
```

---

## Phase 5: Skills & Tools

### Task 11: MorningBrief Skill

**Files:**
- Create: `Roscoe_v1_essentials/workspace/Skills/MorningBrief/SKILL.md`

**Step 1: Create MorningBrief skill file**

```yaml
---
name: MorningBrief
description: "Generate attorney's morning briefing with calendar, tasks, relationships, and case priorities"
triggers:
  - "morning brief"
  - "what's on my calendar"
  - "what should i focus on"
  - "daily digest"
tools_required:
  - list_events
  - graph_query
  - get_case_workflow_status
---

# Morning Brief Skill

Generate < 150 word morning briefing (Second Brain principle #6).

## Query Sources

1. **Calendar (Google Calendar API):**
   ```python
   today_events = list_events(
       time_min=today_start,
       time_max=today_end,
       max_results=10
   )
   ```

2. **Tasks (Graph):**
   ```cypher
   MATCH (t:PersonalAssistant_Task)
   WHERE t.status != 'complete'
     AND (t.due_date = date() OR t.due_date < date())
   RETURN t
   ORDER BY t.priority DESC, t.due_date ASC
   LIMIT 10
   ```

3. **Follow-Ups (Graph):**
   ```cypher
   MATCH (p)
   WHERE (p:PersonalAssistant_Attorney OR p:PersonalAssistant_Judge OR p:PersonalAssistant_OpposingCounsel)
     AND p.follow_ups IS NOT NULL
     AND p.follow_ups <> ''
   RETURN p.name, p.follow_ups, p.last_contacted
   ORDER BY p.last_contacted ASC
   LIMIT 5
   ```

4. **Case Priorities (Graph):**
   ```cypher
   MATCH (c:Case)-[:IN_PHASE]->(phase:Phase)
   MATCH (c)-[:HAS_STATUS]->(status:LandmarkStatus)-[:FOR_LANDMARK]->(lm:Landmark)
   WHERE lm.hard_blocker = true
     AND status.status != 'complete'
   RETURN c.name, lm.display_name
   ```

## Output Format

```
🌅 MORNING BRIEF - {date}

TOP 3 ACTIONS:
1. File motion in Martinez case (due today)
2. Call Judge Smith re: Wilson hearing time
3. Follow up with State Farm adjuster on Johnson settlement

📅 CALENDAR:
• 10 AM: Client meeting - Martinez case
• 2 PM: Deposition - Wilson MVA
• 4 PM: Settlement conference call - Thompson case

⚠️ MIGHT BE STUCK:
Medical records request for Garcia case (waiting 3 weeks)

✨ SMALL WIN:
Successfully negotiated $45K increase in Martinez settlement offer
```

## Workflow

1. Use `list_events()` to get today's calendar
2. Use `graph_query()` with custom_cypher to get tasks
3. Use `graph_query()` with custom_cypher to get follow-ups
4. Use `graph_query()` with custom_cypher to get case blockers
5. Format output (< 150 words total)
6. Return formatted brief
```

**Step 2: Test skill loading**

Run: `python -c "from roscoe.agents.paralegal.tools import refresh_skills; refresh_skills()"`
Expected: MorningBrief skill discovered

**Step 3: Commit**

```bash
git add Roscoe_v1_essentials/workspace/Skills/MorningBrief/
git commit -m "feat: add MorningBrief skill for daily briefing

- Queries calendar, tasks, follow-ups, case priorities
- Generates <150 word formatted brief
- Based on Second Brain daily digest pattern"
```

---

## Phase 6: Polish & Testing

### Task 12: Integration Testing Suite

**Files:**
- Create: `tests/integration/test_second_brain_flow.py`

**Step 1: Write end-to-end capture flow test**

```python
def test_complete_capture_flow():
    """Test complete flow: capture → classify → store → retrieve."""
    # Send capture message
    message = "remind me to call Judge Smith tomorrow about Martinez continuance"

    result = agent.invoke({"messages": [HumanMessage(content=message)]})

    # Verify capture was classified
    assert "Filed as Task" in result['messages'][-1].content

    # Verify stored in graph
    query = """
        MATCH (t:PersonalAssistant_Task)
        WHERE t.name CONTAINS 'Judge Smith'
        RETURN t
    """
    graph_result = graph.run(query)
    assert len(graph_result) > 0

    # Verify CaptureLog created
    log_query = """
        MATCH (l:CaptureLog)
        WHERE l.raw_text CONTAINS 'Judge Smith'
        RETURN l
    """
    log_result = graph.run(log_query)
    assert len(log_result) > 0
```

**Step 2: Write continuity detection test**

```python
def test_topic_continuity_detection():
    """Test that related captures are linked."""
    # First capture about Martinez
    msg1 = "Talked to Martinez adjuster about settlement"
    agent.invoke({"messages": [HumanMessage(content=msg1)]})

    # Second capture also about Martinez (should detect continuation)
    msg2 = "They agreed to $50K structured over 2 years"
    agent.invoke({"messages": [HumanMessage(content=msg2)]})

    # Verify MemoryBoxes linked
    query = """
        MATCH (box1:MemoryBox)-[:CONTINUES_FROM]->(box2:MemoryBox)
        WHERE box1.topic CONTAINS 'Martinez'
        RETURN box1, box2
    """
    result = graph.run(query)
    assert len(result) > 0
```

**Step 3: Write morning digest test**

```python
def test_morning_digest_generation():
    """Test that morning digest is generated and delivered."""
    # Set time to 7:05 AM
    middleware = ProactiveSurfacingMiddleware(graph, slack)

    current_time = datetime(2026, 1, 12, 7, 5)
    result = middleware.before_agent(state, runtime, current_time)

    assert result['digest_triggered'] == True
    assert 'TOP 3 ACTIONS' in result['digest_content']
```

**Step 4: Commit**

```bash
git add tests/integration/test_second_brain_flow.py
git commit -m "test: add integration tests for second brain flows

- End-to-end capture flow
- Topic continuity detection
- Morning digest generation
- Verifies all components work together"
```

---

## If Session Crashes or You Need to Resume

**CRITICAL: Before starting OR resuming, run these checks:**

```bash
# 1. Check where you are
pwd
git status

# 2. Review recent progress
git log --oneline -10

# 3. Read progress files
cat .claude/progress.json
cat .claude/progress.txt

# 4. Identify highest-priority unfinished task
# Look for first task with "status": "pending" in progress.json
```

**Then:**
1. Update progress.txt with what you found
2. Continue from highest-priority unfinished task
3. Update progress files after EACH task completion
4. Commit frequently (minimum: after each passing test)

---

## Summary

**Total Tasks:** 12 tasks across 5 phases
**Estimated Time:** 10 weeks
**Key Technologies:** Deep Agents, FalkorDB, LangGraph, CompositeBackend, sentence-transformers

**Phase Breakdown:**
- Phase 2 (Tasks 1-5): Memory Architecture - 5 tasks
- Phase 3 (Tasks 6-8): Continuity & Traces - 3 tasks
- Phase 4 (Tasks 9-10): Proactive Surfacing - 2 tasks
- Phase 5 (Task 11): Skills & Tools - 1 task
- Phase 6 (Task 12): Integration Testing - 1 task

**Each task follows TDD:**
1. Write failing test
2. Run to verify failure
3. Implement minimum code to pass
4. Run to verify pass
5. Commit

**Progress tracked in:**
- `.claude/progress.json` - Machine-readable task tracking
- `.claude/progress.txt` - Human-readable progress log
- Git commits - Each task creates checkpoint
