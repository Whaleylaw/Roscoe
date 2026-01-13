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
