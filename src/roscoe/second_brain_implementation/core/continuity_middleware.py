"""
ContinuityMiddleware - Membox-inspired topic continuity detection.

This module implements topic continuity tracking across conversation sessions:

ContinuityMiddleware: Detects topic continuation and links captures into memory boxes
- Loads recent memory boxes from knowledge graph at session start
- Checks if current message continues a recent topic using LLM-based detection
- Links related captures into event traces (Membox pattern)
- Uses Claude Haiku for fast, deterministic continuity classification

Membox Pattern:
- Captures are grouped into "boxes" based on topic continuity
- Each box represents a conversation segment about a specific topic
- Boxes contain related captures ordered by time
- New captures either continue existing box OR start new box

This architecture enables:
- Topic-based memory formation (no fixed time windows)
- Automatic event trace building
- Context-aware capture retrieval
- Conversation flow tracking

LLM-based Detection:
- Uses Claude Haiku (claude-haiku-4-5-20251001) for classification
- Temperature=0 for deterministic behavior
- Compares current message against recent box topic and summary
- Extracts events and topics from messages in structured JSON format
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import json
import logging
import asyncio

from langchain.agents.middleware import AgentMiddleware
from sentence_transformers import SentenceTransformer

# Configure logger
logger = logging.getLogger(__name__)


class ContinuityMiddleware(AgentMiddleware):
    """
    Detect topic continuity and link captures into memory boxes.

    Based on Membox research: topic continuity-based memory formation.

    Workflow:
    1. before_agent: Load recent memory boxes for this thread
    2. On new capture: Check continuity with recent boxes
    3. If continues: Link to existing box (append to event trace)
    4. If new topic: Create new box

    Memory Box Schema (in FalkorDB):
    - MemoryBox node with properties:
      - box_id: Unique identifier
      - topic: Brief topic description (e.g., "Martinez settlement")
      - started_at: Timestamp when box was created
      - last_updated: Timestamp of most recent capture
      - thread_id: Session thread ID
    - Relationships:
      - (MemoryBox)-[:CONTAINS]->(Capture)
      - (Capture)-[:NEXT]->(Capture) for temporal ordering

    Args:
        graph_client: FalkorDB client for querying/writing boxes
    """

    name: str = "continuity"  # Unique name required by LangChain middleware framework
    tools: list = []  # Required by AgentMiddleware base class

    def __init__(self, graph_client):
        """
        Initialize ContinuityMiddleware.

        Args:
            graph_client: FalkorDB client for graph queries (to be determined how to pass this)
        """
        self.graph_client = graph_client

        # Initialize lightweight embedding model for semantic similarity
        # Same model as SkillSelectorMiddleware for consistency
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        logger.info("[CONTINUITY] Initialized ContinuityMiddleware")
        print("🔗 CONTINUITY MIDDLEWARE INITIALIZED", flush=True)

    def before_agent(self, state, runtime):
        """
        Load recent memory boxes for continuity checking.

        Called at session start to populate state with recent boxes.

        Args:
            state: Agent state dict
            runtime: Runtime context (may or may not have config)

        Returns:
            Dict with recent_memory_boxes and current_thread_id, or None if unavailable
        """
        try:
            # Try to extract thread_id from runtime config (may not be available)
            thread_id = None
            if hasattr(runtime, 'config') and runtime.config:
                thread_id = runtime.config.get('configurable', {}).get('thread_id')

            if not thread_id:
                logger.debug("[CONTINUITY] No thread_id available in before_agent, skipping box preload")
                return None

            # Get recent boxes from graph
            recent_boxes = self._get_recent_boxes(thread_id, limit=5)

            logger.info(f"[CONTINUITY] Loaded {len(recent_boxes)} recent boxes for thread {thread_id}")

            return {
                "recent_memory_boxes": recent_boxes,
                "current_thread_id": thread_id
            }
        except Exception as e:
            logger.warning(f"[CONTINUITY] before_agent failed (non-fatal): {e}")
            return None

    def _get_recent_boxes(self, thread_id: str, limit: int = 5) -> List[Dict]:
        """
        Query graph for recent memory boxes.

        Args:
            thread_id: Current session thread ID
            limit: Maximum number of boxes to retrieve

        Returns:
            List of box dicts with box_id, topic, started_at, last_updated
        """
        try:
            query = """
                MATCH (box:MemoryBox {thread_id: $thread_id})
                RETURN box.box_id as box_id,
                       box.topic as topic,
                       box.started_at as started_at,
                       box.last_updated as last_updated
                ORDER BY box.last_updated DESC
                LIMIT $limit
            """

            # Mock for now since MemoryBox nodes don't exist yet (Task 7)
            # In production, this will use graph_client.run(query, params)
            result = self.graph_client.run(query, {"thread_id": thread_id, "limit": limit})

            return [row for row in result] if result else []

        except Exception as e:
            logger.error(f"[CONTINUITY] Error querying recent boxes: {e}")
            return []

    def _check_continuity(self, recent_box: Dict, current_message: str) -> Dict[str, Any]:
        """
        Check if current message continues topic of recent box.

        Uses LLM-based continuity detection (Membox pattern).

        Args:
            recent_box: Dict with box_id, topic, content_summary, etc.
            current_message: User's current message text

        Returns:
            Dict with:
            - continues: bool (True if topic continues, False if new topic)
            - new_topic: str or None (topic description if new topic detected)
            - events: list (extracted events from current message)
        """
        from langchain_anthropic import ChatAnthropic
        from langchain_core.messages import HumanMessage
        import re

        # Extract previous topic information
        prev_topic = recent_box.get('topic', '')
        prev_summary = recent_box.get('content_summary', '')

        # Build continuity detection prompt
        prompt = f"""Please determine whether the current message continues with the main
topic of the previous messages. Only answer Yes/No.

Previous topic: {prev_topic}
Previous messages: {prev_summary}
Current message: {current_message}

Answer:"""

        try:
            # Use Claude Haiku for fast classification (same as CaptureMiddleware)
            llm = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0)
            response = llm.invoke([HumanMessage(content=prompt)])

            # Check if response indicates continuation
            continues = 'yes' in response.content.lower()

            logger.info(f"[CONTINUITY] Topic continuation check: {continues}")
            logger.debug(f"[CONTINUITY] LLM response: {response.content}")

            # Extract events and topic from current message
            extraction = self._extract_events_and_topic(current_message)

            return {
                'continues': continues,
                'new_topic': extraction.get('topic') if not continues else None,
                'events': extraction.get('events', [])
            }

        except Exception as e:
            logger.error(f"[CONTINUITY] Error checking continuity: {e}", exc_info=True)
            # On error, assume new topic (safer default)
            return {
                'continues': False,
                'new_topic': None,
                'events': []
            }

    def _extract_events_and_topic(self, message: str) -> Dict[str, Any]:
        """
        Extract topic and events from message using LLM.

        Args:
            message: User message text

        Returns:
            Dict with:
            - topic: str (brief topic description)
            - events: list (list of event strings)
        """
        from langchain_anthropic import ChatAnthropic
        from langchain_core.messages import HumanMessage
        import re

        prompt = f"""Extract the main topic and any events mentioned in this message.

Message: {message}

Return JSON:
{{
  "topic": "brief topic description",
  "events": ["event 1", "event 2"]
}}"""

        try:
            # Use Claude Haiku for extraction
            llm = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0)
            response = llm.invoke([HumanMessage(content=prompt)])

            # Extract JSON from response (may be in code block)
            response_text = response.content

            # Try to extract from markdown code block
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)

            # Parse JSON
            result = json.loads(response_text)

            logger.debug(f"[CONTINUITY] Extracted topic: {result.get('topic')}, events: {result.get('events')}")

            return result

        except Exception as e:
            logger.error(f"[CONTINUITY] Error extracting events/topic: {e}", exc_info=True)
            # Return minimal fallback
            return {
                'topic': 'Unknown topic',
                'events': []
            }

    def _extract_user_query(self, messages: List) -> str:
        """
        Extract the latest user message content.

        Copied from CaptureMiddleware for consistency.

        Args:
            messages: List of message objects

        Returns:
            str: User message text or empty string
        """
        from langchain_core.messages import HumanMessage

        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                content = msg.content
                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    return ' '.join(
                        block.get('text', '') if isinstance(block, dict) else str(block)
                        for block in content
                        if block
                    )
        return ""

    async def _append_to_box(self, box_id: str, message: str) -> None:
        """
        Append message to existing MemoryBox in graph.

        Creates a new Capture node and links it to the box.

        Args:
            box_id: ID of the memory box to append to
            message: User message text to append
        """
        try:
            from roscoe.core.graphiti_client import run_cypher_query
            from datetime import datetime

            # Generate capture ID
            capture_id = f"Capture_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            # Create Capture node and link to box
            query = """
                MATCH (box:MemoryBox {box_id: $box_id})
                CREATE (c:Capture {
                    id: $capture_id,
                    content: $content,
                    timestamp: timestamp(),
                    created_at: $created_at
                })
                CREATE (box)-[:CONTAINS]->(c)
                SET box.last_updated = timestamp()
                RETURN c.id as capture_id
            """

            params = {
                'box_id': box_id,
                'capture_id': capture_id,
                'content': message,
                'created_at': datetime.now().isoformat()
            }

            await run_cypher_query(query, params)
            logger.info(f"[CONTINUITY] ✅ Appended capture {capture_id} to box {box_id}")

        except Exception as e:
            logger.error(f"[CONTINUITY] Error appending to box: {e}", exc_info=True)

    async def _create_new_box(self, thread_id: str, topic: str, message: str) -> None:
        """
        Create new MemoryBox in graph with initial message.

        Args:
            thread_id: Current session thread ID
            topic: Topic description for the box
            message: Initial user message to store in box
        """
        try:
            from roscoe.core.graphiti_client import run_cypher_query
            from datetime import datetime

            # Generate IDs
            box_id = f"MemoryBox_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            capture_id = f"Capture_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            # Create MemoryBox and initial Capture
            query = """
                CREATE (box:MemoryBox {
                    box_id: $box_id,
                    topic: $topic,
                    thread_id: $thread_id,
                    started_at: timestamp(),
                    last_updated: timestamp()
                })
                CREATE (c:Capture {
                    id: $capture_id,
                    content: $content,
                    timestamp: timestamp(),
                    created_at: $created_at
                })
                CREATE (box)-[:CONTAINS]->(c)
                RETURN box.box_id as box_id, c.id as capture_id
            """

            params = {
                'box_id': box_id,
                'topic': topic or 'Unknown topic',
                'thread_id': thread_id,
                'capture_id': capture_id,
                'content': message,
                'created_at': datetime.now().isoformat()
            }

            await run_cypher_query(query, params)
            logger.info(f"[CONTINUITY] ✅ Created new box {box_id} with topic: '{topic}'")

        except Exception as e:
            logger.error(f"[CONTINUITY] Error creating new box: {e}", exc_info=True)

    def wrap_model_call(self, request, handler):
        """Synchronous model call wrapper - continuity detection not needed in sync mode."""
        logger.debug("[CONTINUITY] Sync mode - skipping continuity detection")
        return handler(request)

    async def awrap_model_call(self, request, handler):
        """Check continuity and update/create memory boxes."""
        logger.info("="*60)
        logger.info("🔗 CONTINUITY MIDDLEWARE EXECUTING (ASYNC)")
        logger.info("="*60)

        # Extract recent boxes from state (loaded by before_agent)
        state = request.state or {}
        recent_boxes = state.get('recent_memory_boxes', [])

        if not recent_boxes:
            logger.debug("[CONTINUITY] No recent boxes to check")
            return await handler(request)

        # Extract user message
        user_message = self._extract_user_query(list(request.messages))
        if not user_message:
            logger.debug("[CONTINUITY] No user message found")
            return await handler(request)

        logger.info(f"[CONTINUITY] Checking continuity for: '{user_message[:50]}...'")

        # Check continuity with most recent box
        most_recent = recent_boxes[0]
        logger.info(f"[CONTINUITY] Most recent box topic: '{most_recent.get('topic', 'Unknown')}'")

        continuity_result = self._check_continuity(most_recent, user_message)

        if continuity_result['continues']:
            # Append to existing box
            logger.info(f"[CONTINUITY] ✅ Continues topic - appending to box {most_recent['box_id']}")
            await self._append_to_box(most_recent['box_id'], user_message)
        else:
            # Create new box
            logger.info(f"[CONTINUITY] 🆕 New topic detected: '{continuity_result.get('new_topic', 'Unknown')}'")
            thread_id = state.get('current_thread_id')
            await self._create_new_box(
                thread_id=thread_id,
                topic=continuity_result['new_topic'],
                message=user_message
            )

        # Continue with rest of middleware chain (don't short-circuit)
        return await handler(request)
