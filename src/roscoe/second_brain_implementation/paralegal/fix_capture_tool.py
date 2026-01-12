"""
Fix Capture Tool - Second Brain Fix Button

Allows correcting misclassified captures by:
1. Getting original CaptureLog and entity
2. Reclassifying using LLM with user's correction
3. Deleting old entity
4. Creating new entity with correct classification
5. Updating CaptureLog with new category, status='corrected', incrementing correction_count

Usage:
    fix_capture(
        log_id="CaptureLog_20260111_120000",
        correction="This should be a task, not an idea"
    )
"""

import json
import re
from typing import Dict, Any
from datetime import datetime
from langchain.tools import tool


async def fix_capture(log_id: str, correction: str) -> str:
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
    from roscoe.core.graphiti_client import run_cypher_query
    from roscoe.core.capture_middleware import CaptureMiddleware
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage

    # Get original log and entity
    query = """
        MATCH (log:CaptureLog {id: $log_id})
        RETURN log
    """
    result = await run_cypher_query(query, {"log_id": log_id})

    if not result:
        return f"❌ Capture log {log_id} not found"

    log_data = result[0]['log']
    old_entity_id = log_data.get('entity_id')
    old_category = log_data.get('category')
    raw_text = log_data.get('raw_text')

    # Build reclassification prompt
    correction_prompt = f"""You are reclassifying a capture that was incorrectly classified.

ORIGINAL CAPTURE: "{raw_text}"
ORIGINAL CLASSIFICATION: {old_category}
USER CORRECTION: "{correction}"

Based on the user's correction, reclassify this capture into the correct category.

CATEGORIES (use these EXACT category names):
- PersonalAssistant_Task: Tasks, reminders, action items, to-dos
- PersonalAssistant_Interaction: Calls, meetings, emails, interactions with people
- PersonalAssistant_Idea: Ideas, strategies, notes, concepts
- PersonalAssistant_Attorney: Attorney contacts and relationships
- PersonalAssistant_Judge: Judge information and preferences
- PersonalAssistant_OpposingCounsel: Opposing counsel information
- Case_Note: Case-specific notes and developments

Return ONLY valid JSON in this format:
{{
  "category": "PersonalAssistant_Task|PersonalAssistant_Interaction|PersonalAssistant_Idea|PersonalAssistant_Attorney|PersonalAssistant_Judge|PersonalAssistant_OpposingCounsel|Case_Note",
  "confidence": 0.9,
  "confidence_reason": "Why this is the correct category",
  "extracted_fields": {{
    // Category-specific fields based on the schemas
  }}
}}

Remember:
- For PersonalAssistant_Task: include "name" and "next_action" fields
- For PersonalAssistant_Interaction: include "name", "interaction_type", "participants", "occurred_at", "notes" fields
- For PersonalAssistant_Idea: include "name" and "one_liner" fields
- For Case_Note: include "case_name" and "note_content" fields
- For PersonalAssistant_Attorney/Judge/OpposingCounsel: include "name", "person_type", "context" fields
"""

    # Call LLM for reclassification
    llm = ChatAnthropic(
        model="claude-haiku-4-5-20251001",
        max_retries=2,
        temperature=0
    )

    try:
        response = await llm.ainvoke([HumanMessage(content=correction_prompt)])
        response_text = response.content

        # Extract JSON from markdown code block if present
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)

        new_classification = json.loads(response_text)

        # Basic validation: ensure required fields exist
        if 'category' not in new_classification:
            return f"❌ Reclassification failed: Missing 'category' field"
        if 'confidence' not in new_classification:
            return f"❌ Reclassification failed: Missing 'confidence' field"
        if 'extracted_fields' not in new_classification:
            return f"❌ Reclassification failed: Missing 'extracted_fields' field"

        # Validate category is one of the expected categories
        valid_categories = [
            'PersonalAssistant_Task',
            'PersonalAssistant_Interaction',
            'PersonalAssistant_Idea',
            'PersonalAssistant_Attorney',
            'PersonalAssistant_Judge',
            'PersonalAssistant_OpposingCounsel',
            'Case_Note'
        ]
        if new_classification['category'] not in valid_categories:
            return f"❌ Reclassification failed: Invalid category '{new_classification['category']}'"

        # Fix field key mismatch: LLM returns 'extracted_fields' but _write_to_graph expects 'extracted_data'
        if 'extracted_fields' in new_classification:
            new_classification['extracted_data'] = new_classification.pop('extracted_fields')

    except Exception as e:
        return f"❌ Error reclassifying capture: {str(e)}"

    # Delete old entity if it exists
    if old_entity_id:
        delete_query = """
            MATCH (e {id: $entity_id})
            DETACH DELETE e
        """
        await run_cypher_query(delete_query, {"entity_id": old_entity_id})

    # Create new entity using CaptureMiddleware
    middleware = CaptureMiddleware()
    new_entity_id = await middleware._write_to_graph(new_classification, raw_text)

    if not new_entity_id:
        return f"❌ Failed to create new entity for {new_classification['category']}"

    # Update CaptureLog
    update_query = """
        MATCH (log:CaptureLog {id: $log_id})
        SET log.category = $new_category,
            log.status = 'corrected',
            log.correction_count = coalesce(log.correction_count, 0) + 1,
            log.entity_id = $new_entity_id,
            log.corrected_at = timestamp()
        RETURN log.category as category, log.correction_count as count
    """
    update_result = await run_cypher_query(update_query, {
        "log_id": log_id,
        "new_category": new_classification['category'],
        "new_entity_id": new_entity_id
    })

    if not update_result:
        return f"❌ Failed to update CaptureLog {log_id}"

    # Format success message
    new_category = update_result[0]['category']
    correction_count = update_result[0]['count']
    preview = raw_text[:50] + "..." if len(raw_text) > 50 else raw_text

    return f"✅ Corrected: '{preview}' → {new_category} (correction #{correction_count})"
