"""
Second Brain Agent Tools.

Explicit capture tools for tasks, ideas, interactions, people, and notes.
Query tools for listing and searching captures.
Read-only case access for context.
"""

import json
import logging
from datetime import datetime
from typing import Optional, List, Literal

logger = logging.getLogger(__name__)


def _escape_cypher_string(value: str) -> str:
    """Escape string for safe use in Cypher queries."""
    return value.replace("'", "\\'").replace("\n", "\\n")


# =============================================================================
# CAPTURE TOOLS
# =============================================================================

async def capture_task(
    name: str,
    next_action: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Literal["high", "medium", "low"] = "medium",
    case_name: Optional[str] = None,
) -> str:
    """
    Capture a task or reminder.

    Args:
        name: Brief description of the task
        next_action: Specific next step to take
        due_date: When it's due (e.g., "2026-01-15", "tomorrow", "next week")
        priority: high, medium, or low
        case_name: Associated case (optional)

    Returns:
        Confirmation message with task ID

    Example:
        capture_task("Call Dr. Smith about records", due_date="tomorrow", priority="high")
    """
    from roscoe.core.graphiti_client import run_cypher_query

    task_id = f"Task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    # Build properties
    props = {
        "id": task_id,
        "name": name,
        "status": "pending",
        "priority": priority,
        "created_at": datetime.now().isoformat(),
    }
    if next_action:
        props["next_action"] = next_action
    if due_date:
        props["due_date"] = due_date
    if case_name:
        props["case_name"] = case_name

    # Build Cypher property string (FalkorDB inline syntax)
    prop_items = []
    for key, value in props.items():
        if isinstance(value, str):
            escaped = value.replace("'", "\\'").replace("\n", "\\n")
            prop_items.append(f"{key}: '{escaped}'")
        else:
            prop_items.append(f"{key}: {value}")
    props_str = ", ".join(prop_items)

    query = f"CREATE (t:PersonalAssistant_Task {{{props_str}}}) RETURN t.id as id"

    try:
        result = await run_cypher_query(query)
        if result:
            logger.info(f"[SECOND BRAIN] Created task: {task_id}")
            due_str = f" (due: {due_date})" if due_date else ""
            return f"✅ Task captured: \"{name}\"{due_str}"
        return f"❌ Failed to capture task"
    except Exception as e:
        logger.error(f"[SECOND BRAIN] Error creating task: {e}")
        return f"❌ Error: {str(e)}"


async def capture_idea(
    name: str,
    description: Optional[str] = None,
    case_name: Optional[str] = None,
) -> str:
    """
    Capture an idea or concept.

    Args:
        name: Brief title for the idea
        description: Longer explanation (optional)
        case_name: Associated case (optional)

    Returns:
        Confirmation message with idea ID

    Example:
        capture_idea("Argue comparative negligence", description="Defendant was 30% at fault")
    """
    from roscoe.core.graphiti_client import run_cypher_query

    idea_id = f"Idea_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    props = {
        "id": idea_id,
        "name": name,
        "one_liner": description or name,
        "created_at": datetime.now().isoformat(),
    }
    if case_name:
        props["case_name"] = case_name

    prop_items = []
    for key, value in props.items():
        if isinstance(value, str):
            escaped = value.replace("'", "\\'").replace("\n", "\\n")
            prop_items.append(f"{key}: '{escaped}'")
        else:
            prop_items.append(f"{key}: {value}")
    props_str = ", ".join(prop_items)

    query = f"CREATE (i:PersonalAssistant_Idea {{{props_str}}}) RETURN i.id as id"

    try:
        result = await run_cypher_query(query)
        if result:
            logger.info(f"[SECOND BRAIN] Created idea: {idea_id}")
            return f"💡 Idea captured: \"{name}\""
        return f"❌ Failed to capture idea"
    except Exception as e:
        logger.error(f"[SECOND BRAIN] Error creating idea: {e}")
        return f"❌ Error: {str(e)}"


async def capture_interaction(
    person: str,
    interaction_type: Literal["call", "meeting", "email", "text", "other"],
    summary: str,
    occurred_at: Optional[str] = None,
    case_name: Optional[str] = None,
) -> str:
    """
    Capture an interaction (call, meeting, email, etc.).

    Args:
        person: Who you interacted with
        interaction_type: call, meeting, email, text, or other
        summary: Brief summary of what was discussed
        occurred_at: When it happened (defaults to now)
        case_name: Associated case (optional)

    Returns:
        Confirmation message

    Example:
        capture_interaction("Dr. Smith", "call", "Discussed MRI results, surgery recommended")
    """
    from roscoe.core.graphiti_client import run_cypher_query

    interaction_id = f"Interaction_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    props = {
        "id": interaction_id,
        "name": f"{interaction_type.title()} with {person}",
        "interaction_type": interaction_type,
        "participants": json.dumps([person]),
        "notes": summary,
        "occurred_at": occurred_at or datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
    }
    if case_name:
        props["case_name"] = case_name

    prop_items = []
    for key, value in props.items():
        if isinstance(value, str):
            escaped = value.replace("'", "\\'").replace("\n", "\\n")
            prop_items.append(f"{key}: '{escaped}'")
        else:
            prop_items.append(f"{key}: {value}")
    props_str = ", ".join(prop_items)

    query = f"CREATE (i:PersonalAssistant_Interaction {{{props_str}}}) RETURN i.id as id"

    try:
        result = await run_cypher_query(query)
        if result:
            logger.info(f"[SECOND BRAIN] Created interaction: {interaction_id}")
            return f"📞 Interaction captured: {interaction_type} with {person}"
        return f"❌ Failed to capture interaction"
    except Exception as e:
        logger.error(f"[SECOND BRAIN] Error creating interaction: {e}")
        return f"❌ Error: {str(e)}"


async def capture_person(
    name: str,
    role: Literal["attorney", "judge", "adjuster", "doctor", "client", "witness", "other"],
    context: str,
) -> str:
    """
    Capture information about a person.

    Args:
        name: Person's name
        role: Their role (attorney, judge, adjuster, doctor, client, witness, other)
        context: Relevant context about them (preferences, notes, relationship)

    Returns:
        Confirmation message

    Example:
        capture_person("Judge Wilson", "judge", "Prefers short briefs, strict on deadlines")
    """
    from roscoe.core.graphiti_client import run_cypher_query

    # Map role to node label
    role_to_label = {
        "attorney": "PersonalAssistant_Attorney",
        "judge": "PersonalAssistant_Judge",
        "adjuster": "PersonalAssistant_OpposingCounsel",  # Adjusters often opposing
        "doctor": "PersonalAssistant_Attorney",  # Reuse for medical contacts
        "client": "PersonalAssistant_Attorney",  # Reuse
        "witness": "PersonalAssistant_Attorney",  # Reuse
        "other": "PersonalAssistant_Attorney",  # Reuse
    }
    label = role_to_label.get(role, "PersonalAssistant_Attorney")

    person_id = f"{label}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    props = {
        "id": person_id,
        "name": name,
        "person_type": role,
        "context": context,
        "created_at": datetime.now().isoformat(),
    }

    prop_items = []
    for key, value in props.items():
        if isinstance(value, str):
            escaped = value.replace("'", "\\'").replace("\n", "\\n")
            prop_items.append(f"{key}: '{escaped}'")
        else:
            prop_items.append(f"{key}: {value}")
    props_str = ", ".join(prop_items)

    query = f"CREATE (p:{label} {{{props_str}}}) RETURN p.id as id"

    try:
        result = await run_cypher_query(query)
        if result:
            logger.info(f"[SECOND BRAIN] Created person: {person_id}")
            return f"👤 Person captured: {name} ({role})"
        return f"❌ Failed to capture person"
    except Exception as e:
        logger.error(f"[SECOND BRAIN] Error creating person: {e}")
        return f"❌ Error: {str(e)}"


async def capture_note(
    subject: str,
    content: str,
    case_name: Optional[str] = None,
) -> str:
    """
    Capture a general note.

    Args:
        subject: Brief subject/title
        content: The note content
        case_name: Associated case (optional)

    Returns:
        Confirmation message

    Example:
        capture_note("Defendant liability", "Strong evidence of negligence based on police report")
    """
    from roscoe.core.graphiti_client import run_cypher_query

    note_id = f"Note_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    props = {
        "id": note_id,
        "case_name": case_name or "",
        "note_content": content,
        "subject": subject,
        "created_at": datetime.now().isoformat(),
    }

    prop_items = []
    for key, value in props.items():
        if isinstance(value, str):
            escaped = value.replace("'", "\\'").replace("\n", "\\n")
            prop_items.append(f"{key}: '{escaped}'")
        else:
            prop_items.append(f"{key}: {value}")
    props_str = ", ".join(prop_items)

    query = f"CREATE (n:Case_Note {{{props_str}}}) RETURN n.id as id"

    try:
        result = await run_cypher_query(query)
        if result:
            logger.info(f"[SECOND BRAIN] Created note: {note_id}")
            return f"📝 Note captured: \"{subject}\""
        return f"❌ Failed to capture note"
    except Exception as e:
        logger.error(f"[SECOND BRAIN] Error creating note: {e}")
        return f"❌ Error: {str(e)}"


# =============================================================================
# QUERY TOOLS
# =============================================================================

async def list_captures(
    capture_type: Optional[Literal["task", "idea", "interaction", "person", "note", "all"]] = "all",
    limit: int = 10,
    status: Optional[Literal["pending", "completed", "all"]] = "all",
) -> str:
    """
    List recent captures.

    Args:
        capture_type: Filter by type (task, idea, interaction, person, note, or all)
        limit: Maximum number to return (default 10)
        status: For tasks, filter by status (pending, completed, or all)

    Returns:
        Formatted list of captures

    Example:
        list_captures("task", limit=5, status="pending")
    """
    from roscoe.core.graphiti_client import run_cypher_query

    type_to_label = {
        "task": "PersonalAssistant_Task",
        "idea": "PersonalAssistant_Idea",
        "interaction": "PersonalAssistant_Interaction",
        "person": ["PersonalAssistant_Attorney", "PersonalAssistant_Judge", "PersonalAssistant_OpposingCounsel"],
        "note": "Case_Note",
    }

    results = []

    if capture_type == "all":
        labels = ["PersonalAssistant_Task", "PersonalAssistant_Idea", "PersonalAssistant_Interaction",
                  "PersonalAssistant_Attorney", "PersonalAssistant_Judge", "PersonalAssistant_OpposingCounsel",
                  "Case_Note"]
    elif capture_type == "person":
        labels = type_to_label["person"]
    else:
        labels = [type_to_label.get(capture_type, "PersonalAssistant_Task")]

    for label in labels:
        query = f"""
            MATCH (n:{label})
            RETURN n.id as id, n.name as name, n.created_at as created_at,
                   labels(n)[0] as type, n.status as status
            ORDER BY n.created_at DESC
            LIMIT {limit}
        """
        try:
            result = await run_cypher_query(query)
            if result:
                results.extend(result)
        except Exception as e:
            logger.warning(f"Error querying {label}: {e}")

    if not results:
        return f"No captures found for type: {capture_type}"

    # Sort by created_at and limit
    results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    results = results[:limit]

    # Format output
    output = [f"**Recent {capture_type} captures:**\n"]
    for r in results:
        type_emoji = {
            "PersonalAssistant_Task": "✓",
            "PersonalAssistant_Idea": "💡",
            "PersonalAssistant_Interaction": "📞",
            "PersonalAssistant_Attorney": "👤",
            "PersonalAssistant_Judge": "⚖️",
            "PersonalAssistant_OpposingCounsel": "👤",
            "Case_Note": "📝",
        }.get(r.get('type', ''), "•")

        name = r.get('name', 'Unnamed')
        status_str = f" [{r.get('status')}]" if r.get('status') else ""
        output.append(f"{type_emoji} {name}{status_str}")

    return "\n".join(output)


async def search_captures(
    query: str,
    capture_type: Optional[Literal["task", "idea", "interaction", "person", "note", "all"]] = "all",
    limit: int = 10,
) -> str:
    """
    Search captures by keyword.

    Args:
        query: Search term
        capture_type: Filter by type (optional)
        limit: Maximum results (default 10)

    Returns:
        Matching captures

    Example:
        search_captures("Dr. Smith", capture_type="interaction")
    """
    from roscoe.core.graphiti_client import run_cypher_query

    type_to_label = {
        "task": ["PersonalAssistant_Task"],
        "idea": ["PersonalAssistant_Idea"],
        "interaction": ["PersonalAssistant_Interaction"],
        "person": ["PersonalAssistant_Attorney", "PersonalAssistant_Judge", "PersonalAssistant_OpposingCounsel"],
        "note": ["Case_Note"],
        "all": ["PersonalAssistant_Task", "PersonalAssistant_Idea", "PersonalAssistant_Interaction",
                "PersonalAssistant_Attorney", "PersonalAssistant_Judge", "PersonalAssistant_OpposingCounsel",
                "Case_Note"],
    }

    labels = type_to_label.get(capture_type, type_to_label["all"])
    results = []
    search_term = _escape_cypher_string(query.lower())

    for label in labels:
        cypher = f"""
            MATCH (n:{label})
            WHERE toLower(n.name) CONTAINS '{search_term}'
               OR toLower(coalesce(n.notes, '')) CONTAINS '{search_term}'
               OR toLower(coalesce(n.context, '')) CONTAINS '{search_term}'
               OR toLower(coalesce(n.note_content, '')) CONTAINS '{search_term}'
            RETURN n.id as id, n.name as name, n.created_at as created_at,
                   labels(n)[0] as type
            ORDER BY n.created_at DESC
            LIMIT {limit}
        """
        try:
            result = await run_cypher_query(cypher)
            if result:
                results.extend(result)
        except Exception as e:
            logger.warning(f"Error searching {label}: {e}")

    if not results:
        return f"No captures found matching: \"{query}\""

    results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    results = results[:limit]

    output = [f"**Search results for \"{query}\":**\n"]
    for r in results:
        type_name = r.get('type', '').replace('PersonalAssistant_', '').replace('Case_', '')
        output.append(f"• [{type_name}] {r.get('name', 'Unnamed')}")

    return "\n".join(output)


async def fix_capture(log_id: str, correction: str) -> str:
    """
    Fix incorrectly classified capture.

    Args:
        log_id: CaptureLog ID from list_captures
        correction: What's wrong and how to fix it

    Returns:
        Confirmation message

    Example:
        fix_capture("CaptureLog_123", "This should be a task, not an idea")
    """
    # Reuse existing fix_capture implementation
    from roscoe.second_brain_implementation.paralegal.fix_capture_tool import fix_capture as _fix_capture
    return await _fix_capture(log_id, correction)


async def delete_capture(capture_id: str) -> str:
    """
    Delete a capture by ID.

    Args:
        capture_id: The capture ID to delete

    Returns:
        Confirmation message

    Example:
        delete_capture("Task_20260113_120000")
    """
    from roscoe.core.graphiti_client import run_cypher_query

    query = """
        MATCH (n {id: $capture_id})
        DETACH DELETE n
        RETURN count(n) as deleted
    """

    try:
        result = await run_cypher_query(query, {"capture_id": capture_id})
        if result and result[0].get('deleted', 0) > 0:
            return f"🗑️ Deleted capture: {capture_id}"
        return f"❌ Capture not found: {capture_id}"
    except Exception as e:
        return f"❌ Error deleting capture: {str(e)}"


# =============================================================================
# READ-ONLY CASE ACCESS
# =============================================================================

async def query_cases(
    query_type: Literal["list", "search", "details"],
    case_name: Optional[str] = None,
    search_term: Optional[str] = None,
    limit: int = 5,
) -> str:
    """
    Query case information (read-only).

    Args:
        query_type: "list" for all cases, "search" for keyword search, "details" for specific case
        case_name: For "details" - the case name to look up
        search_term: For "search" - keyword to search
        limit: Maximum results for list/search

    Returns:
        Case information

    Example:
        query_cases("details", case_name="Wilson-MVA-2024")
        query_cases("search", search_term="State Farm")
    """
    from roscoe.core.graphiti_client import run_cypher_query

    if query_type == "list":
        query = f"""
            MATCH (c:Case)
            RETURN c.name as name, c.case_type as type, c.accident_date as accident_date
            ORDER BY c.created_at DESC
            LIMIT {limit}
        """
        result = await run_cypher_query(query)
        if not result:
            return "No cases found"

        output = ["**Cases:**\n"]
        for r in result:
            output.append(f"• {r.get('name', 'Unknown')} ({r.get('type', 'Unknown')})")
        return "\n".join(output)

    elif query_type == "search" and search_term:
        search_term_escaped = _escape_cypher_string(search_term)
        query = f"""
            MATCH (c:Case)
            WHERE toLower(c.name) CONTAINS toLower('{search_term_escaped}')
            RETURN c.name as name, c.case_type as type
            LIMIT {limit}
        """
        result = await run_cypher_query(query)
        if not result:
            return f"No cases found matching: \"{search_term}\""

        output = [f"**Cases matching \"{search_term}\":**\n"]
        for r in result:
            output.append(f"• {r.get('name', 'Unknown')}")
        return "\n".join(output)

    elif query_type == "details" and case_name:
        query = """
            MATCH (c:Case {name: $case_name})
            OPTIONAL MATCH (c)-[:HAS_CLIENT]->(client:Client)
            OPTIONAL MATCH (c)-[:HAS_DEFENDANT]->(defendant:Defendant)
            RETURN c.name as name, c.case_type as type, c.accident_date as accident_date,
                   client.name as client_name, defendant.name as defendant_name
        """
        result = await run_cypher_query(query, {"case_name": case_name})
        if not result:
            return f"Case not found: {case_name}"

        r = result[0]
        output = [
            f"**{r.get('name', 'Unknown')}**",
            f"Type: {r.get('type', 'Unknown')}",
            f"Accident Date: {r.get('accident_date', 'Unknown')}",
            f"Client: {r.get('client_name', 'Unknown')}",
            f"Defendant: {r.get('defendant_name', 'Unknown')}",
        ]
        return "\n".join(output)

    return "Invalid query. Use query_type='list', 'search', or 'details'"


async def get_morning_brief() -> str:
    """
    Generate an on-demand morning brief.

    Returns a summary of:
    - Top 3 priorities for today
    - Pending tasks with due dates
    - Recent interactions to follow up

    Returns:
        Formatted morning brief
    """
    from roscoe.core.graphiti_client import run_cypher_query

    output = ["# 🌅 Morning Brief\n"]

    # Pending tasks
    tasks_query = """
        MATCH (t:PersonalAssistant_Task)
        WHERE t.status = 'pending'
        RETURN t.name as name, t.due_date as due_date, t.priority as priority
        ORDER BY t.priority DESC, t.created_at DESC
        LIMIT 5
    """
    tasks = await run_cypher_query(tasks_query)

    output.append("## ✓ Pending Tasks")
    if tasks:
        for t in tasks:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t.get('priority', 'medium'), "⚪")
            due = f" (due: {t.get('due_date')})" if t.get('due_date') else ""
            output.append(f"{priority_icon} {t.get('name', 'Unnamed')}{due}")
    else:
        output.append("No pending tasks")

    output.append("")

    # Recent interactions
    interactions_query = """
        MATCH (i:PersonalAssistant_Interaction)
        RETURN i.name as name, i.notes as notes
        ORDER BY i.created_at DESC
        LIMIT 3
    """
    interactions = await run_cypher_query(interactions_query)

    output.append("## 📞 Recent Interactions")
    if interactions:
        for i in interactions:
            output.append(f"• {i.get('name', 'Unknown')}")
    else:
        output.append("No recent interactions")

    output.append("")

    # Ideas
    ideas_query = """
        MATCH (i:PersonalAssistant_Idea)
        RETURN i.name as name
        ORDER BY i.created_at DESC
        LIMIT 3
    """
    ideas = await run_cypher_query(ideas_query)

    output.append("## 💡 Recent Ideas")
    if ideas:
        for i in ideas:
            output.append(f"• {i.get('name', 'Unknown')}")
    else:
        output.append("No recent ideas")

    return "\n".join(output)


# =============================================================================
# TOOL LIST (for agent registration)
# =============================================================================

def get_all_tools():
    """Return all Second Brain tools for agent registration."""
    return [
        # Capture tools
        capture_task,
        capture_idea,
        capture_interaction,
        capture_person,
        capture_note,
        # Query tools
        list_captures,
        search_captures,
        fix_capture,
        delete_capture,
        # Read-only case access
        query_cases,
        get_morning_brief,
    ]
