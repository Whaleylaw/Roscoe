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
