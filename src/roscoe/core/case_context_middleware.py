"""
Case context injection middleware for Roscoe agent.

This module implements automatic case context loading:

CaseContextMiddleware: Detects client/case name mentions and injects case context
- Uses fuzzy string matching to detect client names in user messages
- Loads case overview and related JSON files (contacts, insurance, liens, etc.)
- Injects comprehensive case context into system prompt
- Supports multiple client mentions in a single query

This architecture enables:
- Automatic case context awareness without explicit user commands
- Rich case information available to the agent immediately
- Token-efficient loading of only relevant case data
"""

from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import json
import logging
import asyncio
import re

try:
    from rapidfuzz import fuzz, process
except ImportError:
    # Fallback to fuzzywuzzy if rapidfuzz not available
    from fuzzywuzzy import fuzz, process

from langchain.agents.middleware import AgentMiddleware

# Configure logger
logger = logging.getLogger(__name__)


class CaseContextMiddleware(AgentMiddleware):
    """
    Case context injection middleware.

    Runs before model call to detect client/case mentions and inject relevant
    case context into the system prompt.

    Detection methods:
    - Exact name match: "Caryn McCay"
    - Partial match: "McCay case", "Caryn's case", "the McCay matter"
    - Fuzzy match: "Carmen McCay" → "Caryn McCay" (handles typos)
    - Project name patterns: "Wilson MVA", "Caryn-McCay-MVA-7-30-2023"

    Injected context from case folder:
    - overview.json: case_summary, current_status, phase, financials
    - contacts.json: attorneys, adjusters, providers
    - insurance.json: policies, coverage details
    - liens.json: medical liens
    - expenses.json: case expenses
    - medical_providers.json: treating providers

    Args:
        workspace_dir: Path to workspace directory containing projects/ and Database/
        fuzzy_threshold: Minimum fuzzy match score (0-100) to consider a match (default: 80)
        max_cases: Maximum number of cases to inject context for (default: 2)
    """

    tools: list = []  # Required by AgentMiddleware base class

    # JSON files to load from case folder (exclude pleadings and notes)
    CONTEXT_FILES = [
        "overview.json",
        "contacts.json",
        "expenses.json",
        "insurance.json",
        "liens.json",
        "medical_providers.json",
    ]

    def __init__(
        self,
        workspace_dir: str,
        fuzzy_threshold: int = 80,
        max_cases: int = 2,
    ):
        self.workspace_dir = Path(workspace_dir)
        self.projects_dir = self.workspace_dir / "projects"
        self.database_dir = self.workspace_dir / "Database"
        self.fuzzy_threshold = fuzzy_threshold
        self.max_cases = max_cases

        # Load caselist and build name mappings
        self.caselist = self._load_caselist()
        self.name_to_project = self._build_name_mapping()

        logger.info(f"[CASE CONTEXT] Initialized with {len(self.caselist)} cases")

    def _load_caselist(self) -> List[Dict]:
        """Load caselist.json from Database folder."""
        caselist_path = self.database_dir / "caselist.json"
        if not caselist_path.exists():
            logger.warning(f"[CASE CONTEXT] caselist.json not found at {caselist_path}")
            return []

        try:
            with open(caselist_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[CASE CONTEXT] Error loading caselist: {e}")
            return []

    def _build_name_mapping(self) -> Dict[str, str]:
        """
        Build mapping from client names to project names.

        Creates multiple lookup keys for each case:
        - Full client name: "Caryn McCay" -> project_name
        - Last name only: "McCay" -> project_name
        - First name only: "Caryn" -> project_name (lower priority)
        """
        mapping = {}
        for case in self.caselist:
            project_name = case.get("project_name", "")
            client_name = case.get("client_name", "")

            if not client_name or not project_name:
                continue

            # Normalize client name
            client_name_lower = client_name.lower().strip()

            # Full name mapping (highest priority)
            mapping[client_name_lower] = project_name

            # Extract name parts
            name_parts = client_name.split()
            if len(name_parts) >= 2:
                # Last name (high priority for "McCay case" style mentions)
                last_name = name_parts[-1].lower()
                if last_name not in mapping:
                    mapping[last_name] = project_name

                # First name (lower priority, only if unique)
                first_name = name_parts[0].lower()
                if first_name not in mapping and len(first_name) > 3:
                    mapping[first_name] = project_name

        return mapping

    def _extract_user_query(self, messages: List) -> str:
        """Extract the latest user message content."""
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

    def _detect_case_mentions(self, user_query: str) -> List[Dict]:
        """
        Detect client/case mentions in user query using fuzzy matching.

        Returns list of detected cases with match info.
        """
        if not user_query or not self.caselist:
            return []

        detected_cases = []
        query_lower = user_query.lower()

        # Remove common punctuation for matching
        query_cleaned = re.sub(r"['\"]s?\b", "", query_lower)  # Remove possessives
        query_cleaned = re.sub(r"[.,!?;:]", " ", query_cleaned)

        # Build list of all searchable names
        all_names = list(self.name_to_project.keys())

        # Try exact substring match first
        for name, project in self.name_to_project.items():
            if name in query_cleaned:
                # Avoid matching very short names unless exact
                if len(name) < 4 and name not in query_cleaned.split():
                    continue

                case_info = self._get_case_info(project)
                if case_info and project not in [c.get('project_name') for c in detected_cases]:
                    detected_cases.append({
                        'project_name': project,
                        'client_name': case_info.get('client_name', ''),
                        'match_type': 'exact',
                        'match_score': 100,
                        'matched_term': name,
                    })
                    logger.info(f"[CASE CONTEXT] Exact match: '{name}' -> {project}")

        # If no exact matches, try fuzzy matching on full client names
        if not detected_cases:
            # Extract potential name-like tokens from query (2+ words together)
            words = query_cleaned.split()
            potential_names = []

            # Single words that might be last names
            for word in words:
                if len(word) >= 4:
                    potential_names.append(word)

            # Pairs of words that might be full names
            for i in range(len(words) - 1):
                potential_names.append(f"{words[i]} {words[i+1]}")

            # Get all client full names for fuzzy matching
            client_names = [c.get('client_name', '').lower() for c in self.caselist if c.get('client_name')]

            for potential in potential_names:
                if len(potential) < 4:
                    continue

                # Fuzzy match against client names
                matches = process.extract(potential, client_names, scorer=fuzz.ratio, limit=3)

                for match_name, score, _ in matches:
                    if score >= self.fuzzy_threshold:
                        # Find the project for this client
                        for case in self.caselist:
                            if case.get('client_name', '').lower() == match_name:
                                project = case['project_name']
                                if project not in [c.get('project_name') for c in detected_cases]:
                                    detected_cases.append({
                                        'project_name': project,
                                        'client_name': case.get('client_name', ''),
                                        'match_type': 'fuzzy',
                                        'match_score': score,
                                        'matched_term': potential,
                                    })
                                    logger.info(f"[CASE CONTEXT] Fuzzy match: '{potential}' -> {project} (score: {score})")
                                break

        # Also check for project name patterns (e.g., "Wilson MVA", "Caryn-McCay-MVA-7-30-2023")
        for case in self.caselist:
            project = case.get('project_name', '')
            if not project:
                continue

            # Check if project name or parts appear in query
            project_lower = project.lower()
            if project_lower in query_cleaned.replace('-', ' ').replace('_', ' '):
                if project not in [c.get('project_name') for c in detected_cases]:
                    detected_cases.append({
                        'project_name': project,
                        'client_name': case.get('client_name', ''),
                        'match_type': 'project_name',
                        'match_score': 100,
                        'matched_term': project,
                    })
                    logger.info(f"[CASE CONTEXT] Project name match: {project}")

        # Sort by match score and limit
        detected_cases.sort(key=lambda x: x['match_score'], reverse=True)
        return detected_cases[:self.max_cases]

    def _get_case_info(self, project_name: str) -> Optional[Dict]:
        """Get basic case info from caselist."""
        for case in self.caselist:
            if case.get('project_name') == project_name:
                return case
        return None

    def _load_case_context(self, project_name: str) -> Dict[str, Any]:
        """
        Load all context files for a case.

        Returns dict with data from:
        - overview.json
        - contacts.json
        - expenses.json
        - insurance.json
        - liens.json
        - medical_providers.json
        """
        case_dir = self.projects_dir / project_name
        if not case_dir.exists():
            logger.warning(f"[CASE CONTEXT] Case directory not found: {case_dir}")
            return {}

        context = {}

        for filename in self.CONTEXT_FILES:
            file_path = case_dir / filename
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                        # Handle nested jsonb_agg structure from overview.json
                        if isinstance(data, list) and len(data) > 0:
                            if isinstance(data[0], dict) and 'jsonb_agg' in data[0]:
                                # Flatten jsonb_agg structure
                                data = data[0]['jsonb_agg']
                                if isinstance(data, list) and len(data) > 0:
                                    data = data[0]
                        context[filename.replace('.json', '')] = data
                except Exception as e:
                    logger.error(f"[CASE CONTEXT] Error loading {file_path}: {e}")

        return context

    def _format_context_for_injection(self, detected_cases: List[Dict]) -> str:
        """
        Format detected case contexts for system prompt injection.

        Returns formatted markdown string with all relevant case information.
        """
        if not detected_cases:
            return ""

        sections = []

        for case_info in detected_cases:
            project_name = case_info['project_name']
            client_name = case_info['client_name']

            # Load full context
            context = self._load_case_context(project_name)
            if not context:
                continue

            overview = context.get('overview', {})

            # Build case header
            case_section = f"# Active Case Context: {client_name}\n\n"
            case_section += f"**Case Folder**: `{project_name}`\n"

            if overview:
                case_section += f"**Phase**: {overview.get('phase', 'Unknown')}\n"
                case_section += f"**Accident Date**: {overview.get('accident_date', 'Unknown')}\n"
                case_section += f"**Last Activity**: {overview.get('case_last_activity', 'Unknown')}\n\n"

                # Case Summary
                if overview.get('case_summary'):
                    case_section += "## Case Summary\n"
                    case_section += f"{overview['case_summary']}\n\n"

                # Current Status
                if overview.get('current_status'):
                    case_section += "## Current Status\n"
                    case_section += f"{overview['current_status']}\n\n"

                # Financials
                case_section += "## Financials\n"
                case_section += f"- **Medical Bills**: ${overview.get('total_medical_bills', 0):,.2f}\n"
                case_section += f"- **Liens**: ${overview.get('total_liens', 0):,.2f}\n"
                case_section += f"- **Expenses**: ${overview.get('total_expenses', 0):,.2f}\n\n"

                # Client Contact Info
                case_section += "## Client Contact\n"
                case_section += f"- **Phone**: {overview.get('client_phone', 'N/A')}\n"
                case_section += f"- **Email**: {overview.get('client_email', 'N/A')}\n"
                case_section += f"- **Address**: {overview.get('client_address', 'N/A')}\n\n"

            # Contacts
            contacts = context.get('contacts')
            if contacts and isinstance(contacts, list) and len(contacts) > 0:
                case_section += "## Key Contacts\n"
                for contact in contacts[:10]:  # Limit to 10 contacts
                    if isinstance(contact, dict):
                        name = contact.get('name', contact.get('full_name', 'Unknown'))
                        role = contact.get('role', contact.get('type', ''))
                        phone = contact.get('phone', '')
                        email = contact.get('email', '')
                        case_section += f"- **{name}**"
                        if role:
                            case_section += f" ({role})"
                        if phone:
                            case_section += f" - {phone}"
                        if email:
                            case_section += f" - {email}"
                        case_section += "\n"
                case_section += "\n"

            # Insurance
            insurance = context.get('insurance')
            if insurance and isinstance(insurance, list) and len(insurance) > 0:
                case_section += "## Insurance\n"
                for policy in insurance[:5]:  # Limit to 5 policies
                    if isinstance(policy, dict):
                        carrier = policy.get('carrier', policy.get('company', 'Unknown'))
                        policy_type = policy.get('type', policy.get('coverage_type', ''))
                        limits = policy.get('limits', policy.get('policy_limits', ''))
                        case_section += f"- **{carrier}**"
                        if policy_type:
                            case_section += f" - {policy_type}"
                        if limits:
                            case_section += f" (Limits: {limits})"
                        case_section += "\n"
                case_section += "\n"

            # Liens
            liens = context.get('liens')
            if liens and isinstance(liens, list) and len(liens) > 0:
                case_section += "## Liens\n"
                total_liens = 0
                for lien in liens[:10]:  # Limit to 10 liens
                    if isinstance(lien, dict):
                        provider = lien.get('provider', lien.get('name', 'Unknown'))
                        amount = lien.get('amount', lien.get('balance', 0))
                        if isinstance(amount, (int, float)):
                            total_liens += amount
                            case_section += f"- {provider}: ${amount:,.2f}\n"
                        else:
                            case_section += f"- {provider}: {amount}\n"
                case_section += f"- **Total Liens**: ${total_liens:,.2f}\n\n"

            # Medical Providers
            providers = context.get('medical_providers')
            if providers and isinstance(providers, list) and len(providers) > 0:
                case_section += "## Medical Providers\n"
                for provider in providers[:10]:  # Limit to 10 providers
                    if isinstance(provider, dict):
                        name = provider.get('name', provider.get('provider_name', 'Unknown'))
                        specialty = provider.get('specialty', provider.get('type', ''))
                        case_section += f"- {name}"
                        if specialty:
                            case_section += f" ({specialty})"
                        case_section += "\n"
                case_section += "\n"

            sections.append(case_section)

        if not sections:
            return ""

        # Combine all case sections
        header = "---\n📋 **CASE CONTEXT LOADED** - The following case information has been automatically loaded based on your message:\n\n"
        return header + "\n---\n\n".join(sections) + "---\n"

    def _inject_context(self, request, detected_cases: List[Dict]):
        """
        Inject case context into request messages.

        Modifies system message or inserts new one with case context.
        """
        if not detected_cases:
            return request

        messages = list(request.messages)
        context_text = self._format_context_for_injection(detected_cases)

        if not context_text:
            return request

        from langchain_core.messages import SystemMessage

        # Check if first message is a system message
        if messages and hasattr(messages[0], 'type') and messages[0].type == 'system':
            # Append context to existing system message
            existing_content = messages[0].content
            messages[0] = SystemMessage(content=existing_content + "\n\n" + context_text)
        else:
            # Insert new system message at beginning
            messages.insert(0, SystemMessage(content=context_text))

        # Store case context metadata in request state
        state = dict(request.state) if request.state else {}
        state['detected_cases'] = detected_cases

        return request.override(messages=messages, state=state)

    def wrap_model_call(self, request, handler):
        """Synchronous model call wrapper - detects cases and injects context before calling model."""
        logger.info("=" * 80)
        logger.info("📋 CASE CONTEXT MIDDLEWARE EXECUTING (SYNC)")
        logger.info("=" * 80)

        # Extract user query
        user_query = self._extract_user_query(list(request.messages))
        logger.info(f"[CASE CONTEXT] User query: '{user_query[:100]}...' " if len(user_query) > 100 else f"[CASE CONTEXT] User query: '{user_query}'")

        # Detect case mentions
        detected_cases = self._detect_case_mentions(user_query)

        if detected_cases:
            logger.info(f"[CASE CONTEXT] ✅ Detected cases: {[c['client_name'] for c in detected_cases]}")
            modified_request = self._inject_context(request, detected_cases)
            return handler(modified_request)
        else:
            logger.info("[CASE CONTEXT] No case mentions detected")
            return handler(request)

    async def awrap_model_call(self, request, handler):
        """Asynchronous model call wrapper - detects cases and injects context before calling model."""
        logger.info("=" * 80)
        logger.info("📋 CASE CONTEXT MIDDLEWARE EXECUTING (ASYNC)")
        logger.info("=" * 80)

        # Extract user query
        user_query = self._extract_user_query(list(request.messages))
        logger.info(f"[CASE CONTEXT] User query: '{user_query[:100]}...' " if len(user_query) > 100 else f"[CASE CONTEXT] User query: '{user_query}'")

        # Detect case mentions (run in thread to avoid blocking)
        detected_cases = await asyncio.to_thread(self._detect_case_mentions, user_query)

        if detected_cases:
            logger.info(f"[CASE CONTEXT] ✅ Detected cases: {[c['client_name'] for c in detected_cases]}")
            modified_request = await asyncio.to_thread(self._inject_context, request, detected_cases)
            return await handler(modified_request)
        else:
            logger.info("[CASE CONTEXT] No case mentions detected")
            return await handler(request)

