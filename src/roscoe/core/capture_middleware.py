"""
CaptureMiddleware - Automatic capture detection and classification.

Detects tasks, ideas, interactions, and notes from user messages.
Creates CaptureLog audit trail and entity nodes in FalkorDB.
"""
import json
import re
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain.agents.middleware import AgentMiddleware
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

# Capture categories
CAPTURE_CATEGORIES = [
    'PersonalAssistant_Task',
    'PersonalAssistant_Interaction',
    'PersonalAssistant_Idea',
    'PersonalAssistant_Attorney',
    'PersonalAssistant_Judge',
    'PersonalAssistant_OpposingCounsel',
    'Case_Note',
]

CLASSIFICATION_PROMPT = '''Analyze this message and determine if it contains a capture (something to remember/track).

MESSAGE: "{message}"

CATEGORIES:
- PersonalAssistant_Task: Tasks, reminders, action items, to-dos (e.g., "remind me to call...", "I need to file...")
- PersonalAssistant_Interaction: Calls, meetings, emails, interactions with people (e.g., "I spoke with Dr. Smith...")
- PersonalAssistant_Idea: Ideas, strategies, notes, concepts (e.g., "I'm thinking we should...", "good idea to...")
- PersonalAssistant_Attorney: Attorney contacts and relationships
- PersonalAssistant_Judge: Judge information and preferences
- PersonalAssistant_OpposingCounsel: Opposing counsel information
- Case_Note: Case-specific notes and developments
- NONE: Not a capture - questions, commands, general chat, requests for information

Return ONLY valid JSON:
{{
  "is_capture": true or false,
  "category": "category_name or NONE",
  "confidence": 0.0 to 1.0,
  "confidence_reason": "brief explanation",
  "extracted_data": {{
    // For Task: "name", "next_action", "due_date" (if mentioned)
    // For Interaction: "name", "interaction_type", "participants", "occurred_at", "notes"
    // For Idea: "name", "one_liner"
    // For Case_Note: "case_name", "note_content"
    // For Attorney/Judge/OpposingCounsel: "name", "person_type", "context"
  }}
}}'''


class CaptureMiddleware(AgentMiddleware):
    """
    Detect and classify captures from user messages.

    Creates:
    - CaptureLog node (audit trail with confidence score)
    - Entity node (Task, Idea, Interaction, etc.)

    Low confidence captures (< threshold) get status='needs_review'.
    """

    name: str = "capture"
    tools: list = []

    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize CaptureMiddleware.

        Args:
            confidence_threshold: Minimum confidence to auto-file (default 0.7).
                                  Below this, status='needs_review'.
        """
        self.confidence_threshold = confidence_threshold
        self._llm = None  # Lazy init to avoid pickle issues
        logger.info(f"[CAPTURE] Initialized with threshold={confidence_threshold}")
        print("📥 CAPTURE MIDDLEWARE INITIALIZED", flush=True)

    def _get_llm(self):
        """Lazy initialize LLM to avoid pickle errors with LangGraph checkpointing."""
        if self._llm is None:
            self._llm = ChatAnthropic(
                model="claude-haiku-4-5-20251001",
                temperature=0,
                max_retries=2
            )
        return self._llm

    def _extract_user_message(self, messages: List) -> Optional[str]:
        """Extract the latest user message content."""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                content = msg.content
                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    # Handle multimodal messages
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get('type') == 'text':
                            text_parts.append(block.get('text', ''))
                        elif isinstance(block, str):
                            text_parts.append(block)
                    return ' '.join(text_parts)
        return None

    async def _classify_message(self, message: str) -> Optional[Dict]:
        """
        Classify message using LLM to detect captures.

        Args:
            message: User message text

        Returns:
            Classification dict with is_capture, category, confidence, extracted_data
            or None if classification fails
        """
        if not message or len(message.strip()) < 5:
            return None

        try:
            prompt = CLASSIFICATION_PROMPT.format(message=message[:2000])  # Truncate long messages
            response = await self._get_llm().ainvoke([HumanMessage(content=prompt)])

            # Parse JSON response
            text = response.content

            # Extract JSON from markdown code block if present
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1)

            classification = json.loads(text)

            # Validate required fields
            if 'is_capture' not in classification:
                classification['is_capture'] = False
            if 'category' not in classification:
                classification['category'] = 'NONE'
            if 'confidence' not in classification:
                classification['confidence'] = 0.5

            logger.debug(f"[CAPTURE] Classification: {classification}")
            return classification

        except json.JSONDecodeError as e:
            logger.warning(f"[CAPTURE] Failed to parse LLM response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"[CAPTURE] Classification failed: {e}", exc_info=True)
            return None

    async def _write_to_graph(self, classification: Dict, raw_text: str) -> Optional[str]:
        """
        Create entity node in graph based on classification.

        Args:
            classification: Dict with category and extracted_data
            raw_text: Original message text

        Returns:
            Entity ID if created, None on failure
        """
        from roscoe.core.graphiti_client import run_cypher_query

        category = classification['category']
        data = classification.get('extracted_data', {}) or {}
        entity_id = f"{category}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Build entity properties based on category
        props = {
            "id": entity_id,
            "created_at": datetime.now().isoformat(),
            "raw_text": raw_text[:500]  # Store truncated original
        }

        if category == 'PersonalAssistant_Task':
            props.update({
                "name": data.get("name", raw_text[:50]),
                "next_action": data.get("next_action", ""),
                "due_date": data.get("due_date"),
                "status": "pending"
            })
        elif category == 'PersonalAssistant_Idea':
            props.update({
                "name": data.get("name", raw_text[:50]),
                "one_liner": data.get("one_liner", raw_text[:100])
            })
        elif category == 'PersonalAssistant_Interaction':
            props.update({
                "name": data.get("name", "Interaction"),
                "interaction_type": data.get("interaction_type", "unknown"),
                "participants": json.dumps(data.get("participants", [])),
                "occurred_at": data.get("occurred_at"),
                "notes": data.get("notes", raw_text[:200])
            })
        elif category == 'Case_Note':
            props.update({
                "case_name": data.get("case_name", ""),
                "note_content": data.get("note_content", raw_text)
            })
        else:
            # Attorney, Judge, OpposingCounsel
            props.update({
                "name": data.get("name", "Unknown"),
                "person_type": data.get("person_type", category.split('_')[-1]),
                "context": data.get("context", raw_text[:200])
            })

        # Remove None values
        props = {k: v for k, v in props.items() if v is not None}

        # Create entity node
        query = f"CREATE (e:{category} $props) RETURN e.id as id"
        try:
            result = await run_cypher_query(query, {"props": props})
            if result and len(result) > 0:
                logger.info(f"[CAPTURE] Created entity: {entity_id}")
                return entity_id
            return None
        except Exception as e:
            logger.error(f"[CAPTURE] Failed to create entity: {e}", exc_info=True)
            return None

    async def _create_capture_log(
        self,
        raw_text: str,
        classification: Dict,
        entity_id: Optional[str]
    ) -> Optional[str]:
        """
        Create CaptureLog audit node.

        Args:
            raw_text: Original message
            classification: Classification result
            entity_id: ID of created entity (if any)

        Returns:
            CaptureLog ID
        """
        from roscoe.core.graphiti_client import run_cypher_query

        log_id = f"CaptureLog_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        confidence = classification.get('confidence', 0.5)
        status = 'filed' if confidence >= self.confidence_threshold else 'needs_review'

        query = """
        CREATE (log:CaptureLog {
            id: $log_id,
            raw_text: $raw_text,
            category: $category,
            confidence: $confidence,
            confidence_reason: $confidence_reason,
            status: $status,
            entity_id: $entity_id,
            correction_count: 0,
            captured_at: timestamp()
        })
        RETURN log.id as id
        """

        try:
            await run_cypher_query(query, {
                "log_id": log_id,
                "raw_text": raw_text[:1000],
                "category": classification.get('category', 'NONE'),
                "confidence": confidence,
                "confidence_reason": classification.get('confidence_reason', ''),
                "status": status,
                "entity_id": entity_id
            })
            logger.info(f"[CAPTURE] Created log: {log_id} (status={status})")
            return log_id
        except Exception as e:
            logger.error(f"[CAPTURE] Failed to create log: {e}", exc_info=True)
            return None