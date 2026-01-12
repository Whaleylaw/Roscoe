"""
Case context injection middleware for Roscoe agent.

This module implements automatic case context loading from the FalkorDB knowledge graph:

CaseContextMiddleware: Detects client/case name mentions and injects case context
- Uses fuzzy string matching to detect client names in user messages
- Queries FalkorDB knowledge graph for case data (NO JSON file fallback)
- Injects comprehensive case context into system prompt
- Supports multiple client mentions in a single query

Context Chunk Injection:
- Loads modular prompt chunks based on user query semantics
- Exact trigger matching for specific patterns (e.g., "[SLACK CONVERSATION]")
- Semantic trigger matching for general topics (calendar, notes, organization)
- Reduces base prompt size by loading context only when needed

This architecture enables:
- Automatic case context awareness without explicit user commands
- Rich case information available to the agent immediately
- Token-efficient loading of only relevant case data
- Modular prompt injection for specialized instructions

NOTE: All case data comes from the knowledge graph. JSON files are NOT used.
"""

from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json
import logging
import asyncio
import re
import pytz
import os

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

    Injected context from FalkorDB knowledge graph:
    - Case overview: case_type, accident_date, client info
    - Insurance claims: BIClaim, PIPClaim, UMClaim with policies and adjusters
    - Medical providers: Facilities, Locations with 3-tier hierarchy
    - Liens: Lien amounts and holders
    - Litigation: Attorneys, defendants, court info

    NOTE: All data comes from the knowledge graph. JSON files are NOT used.

    Args:
        workspace_dir: Path to workspace directory containing projects/ and Database/
        fuzzy_threshold: Minimum fuzzy match score (0-100) to consider a match (default: 80)
        max_cases: Maximum number of cases to inject context for (default: 1)
    """

    name: str = "case_context"  # Unique name required by LangChain middleware framework
    tools: list = []  # Required by AgentMiddleware base class

    def __init__(
        self,
        workspace_dir: str,
        fuzzy_threshold: int = 80,
        max_cases: int = 1,
        max_chunks: int = 2,
        chunk_threshold: float = 0.35,
    ):
        self.workspace_dir = Path(workspace_dir)
        self.projects_dir = self.workspace_dir / "projects"
        self.database_dir = self.workspace_dir / "Database"
        self.prompts_dir = self.workspace_dir / "Prompts"
        self.fuzzy_threshold = fuzzy_threshold
        self.max_cases = max_cases
        self.max_chunks = max_chunks
        self.chunk_threshold = chunk_threshold

        # Load caselist and build name mappings
        self.caselist = self._load_caselist()
        self.name_to_project = self._build_name_mapping()

        # Load context chunks manifest
        self.chunks_manifest = self._load_chunks_manifest()

        # Cache for loaded case contexts per thread
        # Key: (thread_id, case_name), Value: context dict
        self._context_cache = {}

        print(f"🔥🔥🔥 CASE CONTEXT MIDDLEWARE INITIALIZED - {len(self.caselist)} cases, {len(self.chunks_manifest.get('chunks', []))} chunks loaded 🔥🔥🔥", flush=True)
        logger.info(f"[CASE CONTEXT] Initialized with {len(self.caselist)} cases and {len(self.chunks_manifest.get('chunks', []))} context chunks")

    def _get_datetime_header(self) -> str:
        """Generate current date/time header for injection into system prompt."""
        # Use Eastern Time (Kentucky law firm)
        eastern = pytz.timezone('America/New_York')
        now = datetime.now(eastern)
        
        # Format: "Monday, December 1, 2025 at 11:45 PM EST"
        formatted = now.strftime("%A, %B %d, %Y at %I:%M %p %Z")
        day_of_week = now.strftime("%A")
        
        return f"""## 📅 Current Date & Time

**Today is {formatted}**
- Day of week: {day_of_week}
- Use this for scheduling, deadlines, and understanding document timelines.

---

"""

    def _load_calendar_context(self) -> str:
        """
        Load today's tasks and overdue items from calendar.json.

        Reads the calendar file and filters events into:
        - Today's tasks: date == today AND status != "completed"
        - Overdue: date < today AND status != "completed"

        Returns formatted markdown for injection into system prompt.
        """
        calendar_path = self.database_dir / "calendar.json"

        try:
            if not calendar_path.exists():
                logger.info("[CALENDAR] calendar.json not found, skipping calendar context")
                return ""
        except PermissionError:
            logger.warning("[CALENDAR] Permission denied accessing calendar.json, skipping")
            return ""

        try:
            eastern = pytz.timezone('America/New_York')
            today = datetime.now(eastern).date()
            
            with open(calendar_path) as f:
                data = json.load(f)
            
            events = data.get("events", [])
            today_tasks = []
            overdue = []
            
            for evt in events:
                # Skip completed events
                if evt.get("status") == "completed":
                    continue
                
                # Parse event date
                evt_date_str = evt.get("date")
                if not evt_date_str:
                    continue
                    
                try:
                    evt_date = datetime.strptime(evt_date_str, "%Y-%m-%d").date()
                except ValueError:
                    logger.warning(f"[CALENDAR] Invalid date format: {evt_date_str}")
                    continue
                
                # Categorize by date
                if evt_date == today:
                    today_tasks.append(evt)
                elif evt_date < today:
                    overdue.append(evt)
            
            # If no tasks, return empty
            if not today_tasks and not overdue:
                logger.info("[CALENDAR] No pending tasks for today or overdue")
                return ""
            
            # Build formatted output
            sections = []
            sections.append("## 📅 Calendar Overview\n")
            
            # Overdue section
            if overdue:
                # Sort by date (oldest first) then priority
                priority_order = {"high": 0, "medium": 1, "low": 2}
                overdue.sort(key=lambda x: (x.get("date", ""), priority_order.get(x.get("priority", "low"), 2)))
                
                sections.append(f"### ⚠️ OVERDUE ({len(overdue)} item{'s' if len(overdue) != 1 else ''})")
                sections.append("| Task | Due | Case | Priority |")
                sections.append("|------|-----|------|----------|")
                
                for evt in overdue:
                    title = evt.get("title", "Untitled")
                    due_date = evt.get("date", "Unknown")
                    # Format date nicely
                    try:
                        due_formatted = datetime.strptime(due_date, "%Y-%m-%d").strftime("%b %d")
                    except:
                        due_formatted = due_date
                    project = evt.get("project_name", "")
                    # Extract client name from project name (first part before hyphen pattern)
                    case_display = project.split("-")[0] + " " + project.split("-")[1] if "-" in project and len(project.split("-")) > 1 else project
                    priority = evt.get("priority", "medium")
                    sections.append(f"| {title} | {due_formatted} | {case_display} | {priority} |")
                
                sections.append("")
            
            # Today's tasks section
            if today_tasks:
                # Sort by priority
                priority_order = {"high": 0, "medium": 1, "low": 2}
                today_tasks.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))
                
                sections.append(f"### 📋 TODAY'S TASKS ({len(today_tasks)} item{'s' if len(today_tasks) != 1 else ''})")
                sections.append("| Task | Case | Priority | Notes |")
                sections.append("|------|------|----------|-------|")
                
                for evt in today_tasks:
                    title = evt.get("title", "Untitled")
                    project = evt.get("project_name", "")
                    # Extract client name from project name
                    case_display = project.split("-")[0] + " " + project.split("-")[1] if "-" in project and len(project.split("-")) > 1 else project
                    priority = evt.get("priority", "medium")
                    notes = evt.get("notes", "")[:50] + "..." if len(evt.get("notes", "")) > 50 else evt.get("notes", "")
                    sections.append(f"| {title} | {case_display} | {priority} | {notes} |")
                
                sections.append("")
            
            result = "\n".join(sections) + "\n---\n\n"
            logger.info(f"[CALENDAR] Loaded {len(overdue)} overdue and {len(today_tasks)} today's tasks")
            print(f"📅 [CALENDAR] Loaded {len(overdue)} overdue and {len(today_tasks)} today's tasks", flush=True)
            return result
            
        except Exception as e:
            logger.error(f"[CALENDAR] Error loading calendar: {e}")
            return ""

    def _inject_datetime(self, request) -> Any:
        """Inject current datetime and calendar context at the start of the system message."""
        from langchain_core.messages import SystemMessage
        
        messages = list(request.messages)
        datetime_header = self._get_datetime_header()
        calendar_context = self._load_calendar_context()
        
        # Combine datetime header and calendar context
        combined_header = datetime_header + calendar_context
        
        # Check if first message is a system message
        if messages and hasattr(messages[0], 'type') and messages[0].type == 'system':
            # Prepend datetime + calendar to existing system message
            existing_content = messages[0].content
            messages[0] = SystemMessage(content=combined_header + existing_content)
        else:
            # Insert new system message with datetime + calendar at beginning
            messages.insert(0, SystemMessage(content=combined_header))
        
        return request.override(messages=messages)

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

    def _load_chunks_manifest(self) -> Dict:
        """Load context chunks manifest from Prompts folder."""
        manifest_path = self.prompts_dir / "chunks_manifest.json"
        if not manifest_path.exists():
            logger.warning(f"[CONTEXT CHUNKS] chunks_manifest.json not found at {manifest_path}")
            return {"chunks": []}

        try:
            with open(manifest_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[CONTEXT CHUNKS] Error loading chunks manifest: {e}")
            return {"chunks": []}

    def _load_chunk_content(self, filename: str) -> str:
        """Load content of a context chunk markdown file."""
        chunk_path = self.prompts_dir / filename
        if not chunk_path.exists():
            logger.warning(f"[CONTEXT CHUNKS] Chunk file not found: {chunk_path}")
            return ""

        try:
            with open(chunk_path) as f:
                return f.read()
        except Exception as e:
            logger.error(f"[CONTEXT CHUNKS] Error loading chunk {filename}: {e}")
            return ""

    def _detect_context_chunks(self, user_query: str) -> List[Dict]:
        """
        Detect which context chunks should be injected based on user query.

        Uses two matching strategies:
        1. Exact triggers: For specific patterns like "[SLACK CONVERSATION]"
        2. Semantic triggers: For topic-based matching (calendar, notes, etc.)

        Returns list of matched chunks with their content loaded.
        """
        if not user_query or not self.chunks_manifest.get('chunks'):
            return []

        matched_chunks = []
        query_lower = user_query.lower()
        # Also create a word set for efficient lookup
        query_words = set(query_lower.split())

        for chunk in self.chunks_manifest['chunks']:
            chunk_name = chunk.get('name', '')
            
            # Check exact triggers first (highest priority)
            exact_triggers = chunk.get('exact_triggers', [])
            for trigger in exact_triggers:
                if trigger in user_query:  # Case-sensitive for exact triggers
                    content = self._load_chunk_content(chunk['file'])
                    if content:
                        matched_chunks.append({
                            'name': chunk_name,
                            'content': content,
                            'match_type': 'exact',
                            'match_score': 1.0,
                            'priority': chunk.get('priority', 5),
                        })
                        logger.info(f"[CONTEXT CHUNKS] Exact match: '{trigger}' -> {chunk_name}")
                    break  # Only match once per chunk

            # Skip semantic matching if already matched by exact trigger
            if any(c['name'] == chunk_name for c in matched_chunks):
                continue

            # Check semantic triggers (keyword matching)
            semantic_triggers = chunk.get('triggers', [])
            if semantic_triggers:
                match_count = 0
                matched_triggers = []
                
                for trigger in semantic_triggers:
                    trigger_lower = trigger.lower()
                    trigger_words = trigger_lower.split()
                    
                    # Multi-word trigger: check if all words appear in query
                    if len(trigger_words) > 1:
                        if all(tw in query_lower for tw in trigger_words):
                            match_count += 1
                            matched_triggers.append(trigger)
                            continue
                    
                    # Single word trigger: check for substring match in query
                    # This allows "calendar" to match "calendar", "calendars", etc.
                    if trigger_lower in query_lower:
                        match_count += 1
                        matched_triggers.append(trigger)
                        continue
                    
                    # Also check if any query word contains the trigger or vice versa
                    # This handles stemming: "scheduling" contains "schedule"
                    for word in query_words:
                        if trigger_lower in word or word in trigger_lower:
                            match_count += 1
                            matched_triggers.append(trigger)
                            break

                if match_count > 0:
                    # Calculate match score: at least 1 match = base score, more matches = higher
                    # Use logarithmic scaling so 1 match = 0.5, 2 matches = 0.7, 3+ = 0.8+
                    import math
                    match_score = min(0.5 + (0.2 * math.log2(match_count + 1)), 1.0)
                    
                    # Only include if above threshold (default 0.35, so 1 match is enough)
                    if match_score >= self.chunk_threshold:
                        content = self._load_chunk_content(chunk['file'])
                        if content:
                            matched_chunks.append({
                                'name': chunk_name,
                                'content': content,
                                'match_type': 'semantic',
                                'match_score': match_score,
                                'matched_triggers': matched_triggers,
                                'priority': chunk.get('priority', 5),
                            })
                            logger.info(f"[CONTEXT CHUNKS] Semantic match: {matched_triggers} -> {chunk_name} (score: {match_score:.2f})")

        # Sort by priority (lower = higher priority), then by match score
        matched_chunks.sort(key=lambda x: (x['priority'], -x['match_score']))

        # Limit to max_chunks
        return matched_chunks[:self.max_chunks]

    def _format_chunks_for_injection(self, chunks: List[Dict]) -> str:
        """Format matched context chunks for system prompt injection."""
        if not chunks:
            return ""

        sections = []
        for chunk in chunks:
            sections.append(chunk['content'])

        header = "\n---\n📚 **CONTEXT LOADED** - The following context has been loaded based on your request:\n\n"
        return header + "\n\n---\n\n".join(sections)

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
            client_names = [(c.get('client_name') or '').lower() for c in self.caselist if c.get('client_name')]

            for potential in potential_names:
                if len(potential) < 4:
                    continue

                # Fuzzy match against client names
                matches = process.extract(potential, client_names, scorer=fuzz.ratio, limit=3)

                for match_name, score, _ in matches:
                    if score >= self.fuzzy_threshold:
                        # Find the project for this client
                        for case in self.caselist:
                            client_name = case.get('client_name') or ''
                            if client_name.lower() == match_name:
                                project = case.get('project_name')
                                if project and project not in [c.get('project_name') for c in detected_cases]:
                                    detected_cases.append({
                                        'project_name': project,
                                        'client_name': client_name,
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

    async def _load_case_context_from_graph(self, project_name: str) -> Dict[str, Any]:
        """
        Load case context from FalkorDB knowledge graph using direct Cypher queries.

        Uses relationship-based queries to get structured case data from the unified graph.
        Returns a structured dict with case overview, insurance, providers, liens, etc.
        """
        
        try:
            from roscoe.core.graphiti_client import run_cypher_query
            
            context = {
                'overview': {},
                'insurance': [],
                'medical_providers': [],
                'contacts': [],
                'liens': [],
                'client': {},
                'litigation': [],
            }
            
            # Get case and client info
            case_query = """
                MATCH (case:Case {name: $case_name})
                OPTIONAL MATCH (case)-[:HAS_CLIENT]->(client:Client)
                RETURN case.name as case_name, case.case_type as case_type,
                       client.name as client_name, client.phone as client_phone, client.email as client_email
                LIMIT 1
            """
            case_results = await run_cypher_query(case_query, {"case_name": project_name})
            if case_results:
                r = case_results[0]
                context['overview'] = {
                    'case_name': r.get('case_name'),
                    'case_type': r.get('case_type'),
                }
                context['client'] = {
                    'name': r.get('client_name'),
                    'phone': r.get('client_phone'),
                    'email': r.get('client_email'),
                }
            
            # Get insurance claims with policies, insurers and adjusters
            insurance_query = """
                MATCH (case:Case {name: $case_name})-[:HAS_CLAIM]->(claim)
                WHERE claim:BIClaim OR claim:PIPClaim OR claim:UMClaim OR claim:UIMClaim OR claim:WCClaim
                OPTIONAL MATCH (claim)-[:UNDER_POLICY]->(policy:InsurancePolicy)
                OPTIONAL MATCH (policy)-[:WITH_INSURER]->(insurer:Insurer)
                OPTIONAL MATCH (claim)-[:HANDLED_BY]->(adjuster:Adjuster)
                RETURN claim.claim_number as claim_number,
                       labels(claim)[0] as claim_type,
                       policy.policy_number as policy_number,
                       insurer.name as insurer_name,
                       adjuster.name as adjuster_name,
                       adjuster.phone as adjuster_phone,
                       adjuster.email as adjuster_email,
                       policy.bi_limit as bi_limit,
                       policy.pip_limit as pip_limit,
                       policy.um_limit as um_limit,
                       claim.status as claim_status,
                       claim.amount_demanded as demand_amount,
                       claim.amount_offered as current_offer
            """
            insurance_results = await run_cypher_query(insurance_query, {"case_name": project_name})
            for r in insurance_results:
                context['insurance'].append({
                    'claim_number': r.get('claim_number'),
                    'claim_type': r.get('claim_type'),
                    'policy_number': r.get('policy_number'),
                    'insurer': r.get('insurer_name'),
                    'adjuster': r.get('adjuster_name'),
                    'adjuster_phone': r.get('adjuster_phone'),
                    'adjuster_email': r.get('adjuster_email'),
                    'bi_limit': r.get('bi_limit'),
                    'pip_limit': r.get('pip_limit'),
                    'um_limit': r.get('um_limit'),
                    'status': r.get('claim_status'),
                    'demand_amount': r.get('demand_amount'),
                    'current_offer': r.get('current_offer'),
                })
            
            # Get medical providers using three-tier hierarchy (Client -TREATED_AT-> Facility/Location)
            provider_query = """
                MATCH (case:Case {name: $case_name})-[:HAS_CLIENT]->(client:Client)-[:TREATED_AT]->(provider)
                WHERE provider:Facility OR provider:Location
                OPTIONAL MATCH (provider)-[:PART_OF]->(parent)
                WHERE parent:Facility OR parent:HealthSystem
                OPTIONAL MATCH (parent)-[:PART_OF]->(grandparent:HealthSystem)
                RETURN provider.name as name,
                       labels(provider)[0] as provider_type,
                       provider.specialty as specialty,
                       provider.phone as phone,
                       provider.fax as fax,
                       provider.address as address,
                       parent.name as parent_name,
                       grandparent.name as health_system
            """
            provider_results = await run_cypher_query(provider_query, {"case_name": project_name})
            for r in provider_results:
                context['medical_providers'].append({
                    'name': r.get('name'),
                    'type': r.get('provider_type'),
                    'specialty': r.get('specialty'),
                    'phone': r.get('phone'),
                    'fax': r.get('fax'),
                    'address': r.get('address'),
                    'parent': r.get('parent_name'),
                    'health_system': r.get('health_system') or (r.get('parent_name') if r.get('parent_name') and not r.get('health_system') else None),
                })
            
            # Get liens
            lien_query = """
                MATCH (case:Case {name: $case_name})-[:HAS_LIEN]->(lien:Lien)
                OPTIONAL MATCH (lien)-[:HELD_BY]->(holder:LienHolder)
                RETURN lien.name as lien_name, holder.name as holder_name,
                       lien.lien_type as lien_type, lien.amount as amount
            """
            lien_results = await run_cypher_query(lien_query, {"case_name": project_name})
            for r in lien_results:
                context['liens'].append({
                    'holder': r.get('holder_name') or r.get('lien_name'),
                    'lien_type': r.get('lien_type'),
                    'amount': r.get('amount'),
                })
            
            # Get litigation contacts (attorneys, defendants)
            litigation_query = """
                MATCH (case:Case {name: $case_name})-[r]->(entity:Entity)
                WHERE entity:Attorney OR entity:Defendant OR entity:Court
                RETURN entity.name as name, entity.entity_type as entity_type,
                       entity.role as role, entity.phone as phone, entity.email as email
            """
            litigation_results = await run_cypher_query(litigation_query, {"case_name": project_name})
            for r in litigation_results:
                context['litigation'].append({
                    'name': r.get('name'),
                    'type': r.get('entity_type'),
                    'role': r.get('role'),
                    'phone': r.get('phone'),
                    'email': r.get('email'),
                })
            
            total_items = (len(context['insurance']) + len(context['medical_providers']) + 
                          len(context['liens']) + len(context['litigation']))
            logger.info(f"[GRAPHITI] Loaded context for {project_name}: {total_items} entities")
            print(f"📊 [GRAPHITI] Loaded {total_items} entities for {project_name}", flush=True)
            
            return context
            
        except ImportError:
            logger.warning("[GRAPHITI] graphiti_client not available, falling back to JSON")
            return {}
        except Exception as e:
            logger.error(f"[GRAPHITI] Error loading context from graph: {e}")
            return {}

    def _format_graph_context(self, project_name: str, client_name: str, graph_context: Dict) -> str:
        """
        Format graph-sourced context for system prompt injection.

        Creates a markdown summary from graph data.
        """
        if not graph_context:
            return ""
        
        sections = []
        sections.append(f"# Active Case Context: {client_name}\n")
        sections.append(f"**Case Folder**: `{project_name}`\n")
        sections.append("*Context loaded from knowledge graph*\n")

        # Overview
        overview = graph_context.get('overview', {})
        if overview:
            sections.append("## Case Overview")
            if overview.get('case_type'):
                sections.append(f"- **Case Type**: {overview['case_type']}")
            if overview.get('case_name'):
                sections.append(f"- **Case Name**: {overview['case_name']}")
            sections.append("")

        # Client info
        client = graph_context.get('client', {})
        if client and any(client.values()):
            sections.append("## Client Information")
            if client.get('name'):
                sections.append(f"- **Name**: {client['name']}")
            if client.get('phone'):
                sections.append(f"- **Phone**: {client['phone']}")
            if client.get('email'):
                sections.append(f"- **Email**: {client['email']}")
            sections.append("")

        # Insurance claims - concise: type, insurer, adjuster only
        insurance = graph_context.get('insurance', [])
        if insurance:
            sections.append("## Insurance Claims")
            for claim in insurance[:10]:
                if isinstance(claim, dict):
                    claim_type = claim.get('claim_type', 'Unknown')
                    insurer = claim.get('insurer') or 'Unknown'
                    adjuster = claim.get('adjuster')
                    # Simple format: Type - Insurer (Adjuster: Name)
                    line = f"- **{claim_type}**: {insurer}"
                    if adjuster:
                        line += f" (Adjuster: {adjuster})"
                    sections.append(line)
                else:
                    sections.append(f"- {claim}")
            sections.append("")

        # Medical providers - concise: name only
        providers = graph_context.get('medical_providers', [])
        if providers:
            sections.append("## Medical Providers")
            for provider in providers[:10]:
                if isinstance(provider, dict):
                    name = provider.get('name') or 'Unknown'
                    sections.append(f"- {name}")
                else:
                    sections.append(f"- {provider}")
            sections.append("")

        # Liens - concise: holder and amount only
        liens = graph_context.get('liens', [])
        if liens:
            sections.append("## Liens")
            for lien in liens[:10]:
                if isinstance(lien, dict):
                    holder = lien.get('holder') or 'Unknown'
                    amount = lien.get('amount')
                    line = f"- {holder}"
                    if amount:
                        line += f": ${amount:,.2f}" if isinstance(amount, (int, float)) else f": {amount}"
                    sections.append(line)
                else:
                    sections.append(f"- {lien}")
            sections.append("")

        # Litigation - concise: name and role only
        litigation = graph_context.get('litigation', [])
        if litigation:
            sections.append("## Litigation Contacts")
            for entity in litigation[:10]:
                if isinstance(entity, dict):
                    name = entity.get('name') or 'Unknown'
                    role = entity.get('role')
                    line = f"- {name}"
                    if role:
                        line += f" ({role})"
                    sections.append(line)
                else:
                    sections.append(f"- {entity}")
            sections.append("")

        return "\n".join(sections)

    def _sanitize_messages(self, messages: List) -> List:
        """
        Sanitize message history to fix orphaned tool_use and tool_result blocks.
        
        CRITICAL: Anthropic requires:
        1. Each tool_result must reference a tool_use in the IMMEDIATELY PREVIOUS message
        2. Each tool_use must have a tool_result in the IMMEDIATELY FOLLOWING message(s)
        
        This happens when a thread is interrupted mid-tool-call and the checkpoint
        saves partial state.
        """
        from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, SystemMessage
        
        if not messages or len(messages) < 2:
            return messages
        
        print(f"🧹 [SANITIZE] Starting sanitization of {len(messages)} messages", flush=True)
        logger.info(f"[SANITIZE] Starting sanitization of {len(messages)} messages")
        
        # Helper to get tool_use IDs from an AIMessage
        def get_tool_use_ids(msg):
            ids = set()
            if isinstance(msg, AIMessage):
                # Check tool_calls attribute
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tc_id = tc.get('id') if isinstance(tc, dict) else getattr(tc, 'id', None)
                        if tc_id:
                            ids.add(tc_id)
                # Check content for tool_use blocks
                if hasattr(msg, 'content') and isinstance(msg.content, list):
                    for block in msg.content:
                        if isinstance(block, dict) and block.get('type') == 'tool_use':
                            tc_id = block.get('id')
                            if tc_id:
                                ids.add(tc_id)
            return ids
        
        # Helper to get tool_call_id from a ToolMessage
        def get_tool_result_id(msg):
            if isinstance(msg, ToolMessage):
                return getattr(msg, 'tool_call_id', None)
            return None
        
        # Build a clean message list by iterating and checking adjacency
        sanitized = []
        i = 0
        
        while i < len(messages):
            msg = messages[i]
            
            # Always keep system and human messages
            if isinstance(msg, (SystemMessage, HumanMessage)):
                sanitized.append(msg)
                i += 1
                continue
            
            # For AIMessage, check if it has tool_use blocks
            if isinstance(msg, AIMessage):
                tool_use_ids = get_tool_use_ids(msg)
                
                if not tool_use_ids:
                    # No tool calls, keep the message
                    sanitized.append(msg)
                    i += 1
                    continue
                
                # Collect all following ToolMessages
                tool_results = {}
                j = i + 1
                while j < len(messages) and isinstance(messages[j], ToolMessage):
                    result_id = get_tool_result_id(messages[j])
                    if result_id:
                        tool_results[result_id] = messages[j]
                    j += 1
                
                # Check if all tool_use_ids have matching tool_results
                missing_results = tool_use_ids - set(tool_results.keys())
                extra_results = set(tool_results.keys()) - tool_use_ids
                
                if missing_results:
                    print(f"⚠️ [SANITIZE] AIMessage at index {i} has tool_use without results: {missing_results}", flush=True)
                    logger.warning(f"[SANITIZE] AIMessage at index {i} has tool_use without results: {missing_results}")
                    # Skip this AIMessage and its partial results
                    print(f"🗑️ [SANITIZE] Skipping AIMessage and {len(tool_results)} partial tool results", flush=True)
                    logger.warning(f"[SANITIZE] Skipping AIMessage and {len(tool_results)} partial tool results")
                    i = j  # Jump past the tool results
                    continue
                
                if extra_results:
                    print(f"⚠️ [SANITIZE] Found extra tool_results not in AIMessage: {extra_results}", flush=True)
                    logger.warning(f"[SANITIZE] Found extra tool_results not in AIMessage: {extra_results}")
                    # Keep the AIMessage but skip extra results
                
                # AIMessage is valid, add it and matching tool results
                sanitized.append(msg)
                for tool_id in tool_use_ids:
                    if tool_id in tool_results:
                        sanitized.append(tool_results[tool_id])
                
                i = j  # Move past the tool results
                continue
            
            # For ToolMessage without a preceding AIMessage with matching tool_use
            if isinstance(msg, ToolMessage):
                tool_id = get_tool_result_id(msg)
                
                # Check if the previous message in sanitized has this tool_use
                if sanitized and isinstance(sanitized[-1], AIMessage):
                    prev_tool_ids = get_tool_use_ids(sanitized[-1])
                    if tool_id in prev_tool_ids:
                        sanitized.append(msg)
                        i += 1
                        continue
                
                # Also check if it follows another ToolMessage that shares an AIMessage
                # (multiple tool results for one AIMessage)
                found_parent = False
                for k in range(len(sanitized) - 1, -1, -1):
                    if isinstance(sanitized[k], AIMessage):
                        prev_tool_ids = get_tool_use_ids(sanitized[k])
                        if tool_id in prev_tool_ids:
                            sanitized.append(msg)
                            found_parent = True
                            break
                        else:
                            # Hit an AIMessage that doesn't have this tool_id
                            break
                    elif isinstance(sanitized[k], (HumanMessage, SystemMessage)):
                        # Hit a non-tool message
                        break
                
                if not found_parent:
                    print(f"🗑️ [SANITIZE] Skipping orphaned tool_result: {tool_id}", flush=True)
                    logger.warning(f"[SANITIZE] Skipping orphaned tool_result: {tool_id}")
                
                i += 1
                continue
            
            # Unknown message type, keep it
            sanitized.append(msg)
            i += 1
        
        if len(sanitized) != len(messages):
            print(f"✂️ [SANITIZE] Removed {len(messages) - len(sanitized)} messages. Original: {len(messages)}, Sanitized: {len(sanitized)}", flush=True)
            logger.warning(f"[SANITIZE] Removed {len(messages) - len(sanitized)} messages. Original: {len(messages)}, Sanitized: {len(sanitized)}")
        else:
            print(f"✅ [SANITIZE] No changes needed, {len(messages)} messages kept", flush=True)
            logger.info(f"[SANITIZE] No changes needed, {len(messages)} messages kept")
        
        return sanitized

    def _inject_context_sync(self, request, detected_cases: List[Dict], detected_chunks: List[Dict] = None):
        """
        Sync version of context injection - ONLY injects context chunks, NOT case context.

        Case context requires async graph queries and is handled by _inject_context_async.
        This sync fallback only handles context chunks for backwards compatibility.
        """
        messages = list(request.messages)
        context_parts = []

        # NOTE: Case context is NOT injected in sync mode - requires async graph queries
        if detected_cases:
            logger.warning("[CASE CONTEXT] Sync mode - case context requires async. Use awrap_model_call for case context.")
            print("⚠️ [CASE CONTEXT] Sync mode detected - case context not loaded (requires async graph queries)", flush=True)

        # Add context chunks if any detected (these are from local files, can be sync)
        if detected_chunks:
            chunk_context = self._format_chunks_for_injection(detected_chunks)
            if chunk_context:
                context_parts.append(chunk_context)

        if not context_parts:
            return request

        context_text = "\n\n".join(context_parts)

        from langchain_core.messages import SystemMessage

        # Check if first message is a system message
        if messages and hasattr(messages[0], 'type') and messages[0].type == 'system':
            existing_content = messages[0].content
            messages[0] = SystemMessage(content=existing_content + "\n\n" + context_text)
        else:
            messages.insert(0, SystemMessage(content=context_text))

        # Store context metadata in request state
        state = dict(request.state) if request.state else {}
        if detected_cases:
            state['detected_cases'] = detected_cases
            state['context_source'] = 'none'  # No case context in sync mode
        if detected_chunks:
            state['detected_chunks'] = [c['name'] for c in detected_chunks]

        return request.override(messages=messages, state=state)

    def wrap_model_call(self, request, handler):
        """Synchronous model call wrapper - detects cases/chunks and injects context before calling model."""
        print("🔥🔥🔥 CASE CONTEXT MIDDLEWARE - wrap_model_call CALLED 🔥🔥🔥", flush=True)
        logger.error("=" * 80)
        logger.error("📋 CASE CONTEXT MIDDLEWARE EXECUTING (SYNC)")
        logger.error("=" * 80)

        # ALWAYS sanitize messages to fix orphaned tool_use/tool_result from interrupted runs
        # This is critical for Anthropic which requires strict adjacency
        sanitized_messages = self._sanitize_messages(list(request.messages))
        request = request.override(messages=sanitized_messages)

        # ALWAYS inject current datetime at the start of system prompt
        request = self._inject_datetime(request)

        # Extract user query from sanitized messages (use updated messages)
        user_query = self._extract_user_query(list(request.messages))
        logger.error(f"[CASE CONTEXT] User query: '{user_query[:100]}...' " if len(user_query) > 100 else f"[CASE CONTEXT] User query: '{user_query}'")

        # Detect case mentions
        detected_cases = self._detect_case_mentions(user_query)
        
        # Detect context chunks
        detected_chunks = self._detect_context_chunks(user_query)

        # Log detections
        if detected_cases:
            logger.error(f"[CASE CONTEXT] ✅ Detected cases: {[c['client_name'] for c in detected_cases]}")
        else:
            logger.error("[CASE CONTEXT] No case mentions detected")
            
        if detected_chunks:
            logger.error(f"[CONTEXT CHUNKS] ✅ Detected chunks: {[c['name'] for c in detected_chunks]}")
        else:
            logger.error("[CONTEXT CHUNKS] No context chunks matched")

        # Inject context if any detections
        # NOTE: Sync mode only injects chunks, NOT case context (requires async graph queries)
        if detected_cases or detected_chunks:
            modified_request = self._inject_context_sync(request, detected_cases, detected_chunks)
            return handler(modified_request)
        else:
            return handler(request)

    async def awrap_model_call(self, request, handler):
        """Asynchronous model call wrapper - detects cases/chunks and injects context before calling model."""
        print("🔥🔥🔥 CASE CONTEXT MIDDLEWARE - awrap_model_call CALLED 🔥🔥🔥", flush=True)
        logger.error("=" * 80)
        logger.error("📋 CASE CONTEXT MIDDLEWARE EXECUTING (ASYNC)")
        logger.error("=" * 80)

        # ALWAYS sanitize messages to fix orphaned tool_use/tool_result from interrupted runs
        # This is critical for Anthropic which requires strict adjacency
        sanitized_messages = await asyncio.to_thread(self._sanitize_messages, list(request.messages))
        request = request.override(messages=sanitized_messages)

        # ALWAYS inject current datetime at the start of system prompt
        request = self._inject_datetime(request)

        # Extract user query from sanitized messages (use updated messages)
        user_query = self._extract_user_query(list(request.messages))
        logger.error(f"[CASE CONTEXT] User query: '{user_query[:100]}...' " if len(user_query) > 100 else f"[CASE CONTEXT] User query: '{user_query}'")

        # Detect case mentions (run in thread to avoid blocking)
        detected_cases = await asyncio.to_thread(self._detect_case_mentions, user_query)
        
        # Detect context chunks (run in thread to avoid blocking)
        detected_chunks = await asyncio.to_thread(self._detect_context_chunks, user_query)

        # Log detections
        if detected_cases:
            logger.error(f"[CASE CONTEXT] ✅ Detected cases: {[c['client_name'] for c in detected_cases]}")
        else:
            logger.error("[CASE CONTEXT] No case mentions detected")
            
        if detected_chunks:
            logger.error(f"[CONTEXT CHUNKS] ✅ Detected chunks: {[c['name'] for c in detected_chunks]}")
        else:
            logger.error("[CONTEXT CHUNKS] No context chunks matched")

        # Inject context if any detections
        if detected_cases or detected_chunks:
            modified_request = await self._inject_context_async(request, detected_cases, detected_chunks)
            return await handler(modified_request)
        else:
            return await handler(request)

    async def _inject_context_async(self, request, detected_cases: List[Dict], detected_chunks: List[Dict] = None):
        """
        Async context injection using knowledge graph ONLY.

        All case data comes from FalkorDB via direct Cypher queries.
        NO JSON file fallback - if graph is empty, no case context is injected.
        """
        from langchain_core.messages import SystemMessage

        messages = list(request.messages)
        context_parts = []

        print("=" * 80, flush=True)
        print("🔍 [CASE CONTEXT] Starting context injection from knowledge graph", flush=True)
        print(f"   Detected cases: {len(detected_cases) if detected_cases else 0}", flush=True)
        print("=" * 80, flush=True)
        logger.info(f"[CASE CONTEXT] Starting context injection, cases={len(detected_cases) if detected_cases else 0}")

        # Load case context from knowledge graph
        if detected_cases:
            print("🧠 [GRAPH] Loading case context from FalkorDB...", flush=True)
            logger.info("[GRAPH] Loading case context from knowledge graph")

            # Get thread_id from request config/state for caching
            thread_id = None
            if hasattr(request, 'config') and isinstance(request.config, dict):
                thread_id = request.config.get('configurable', {}).get('thread_id')

            for case_info in detected_cases:
                project_name = case_info['project_name']
                client_name = case_info['client_name']

                print(f"   📂 Processing case: {project_name} ({client_name})", flush=True)
                logger.info(f"[GRAPH] Processing case: {project_name}")

                # Check cache first
                cache_key = (thread_id, project_name) if thread_id else None
                graph_context = None

                if cache_key and cache_key in self._context_cache:
                    graph_context = self._context_cache[cache_key]
                    print(f"   ✅ Using CACHED context for {project_name}", flush=True)
                    logger.info(f"[GRAPH] Using cached context for {project_name}")
                else:
                    # Load from graph
                    try:
                        print(f"   🔄 Querying graph for {project_name}...", flush=True)
                        logger.info(f"[GRAPH] Querying graph: {project_name}")

                        graph_context = await self._load_case_context_from_graph(project_name)

                        # Cache it if we have a thread_id
                        if cache_key and graph_context:
                            self._context_cache[cache_key] = graph_context
                            print(f"   💾 Cached context for future calls", flush=True)

                    except Exception as e:
                        print(f"   ❌ ERROR querying graph: {str(e)}", flush=True)
                        logger.error(f"[GRAPH] Error loading context: {e}", exc_info=True)
                        continue

                # Format the context (whether cached or fresh)
                if graph_context and any(graph_context.values()):
                    # Count entities returned
                    entity_count = sum(
                        len(v) if isinstance(v, list) else (1 if v else 0)
                        for v in graph_context.values()
                    )
                    print(f"   📊 Graph returned {entity_count} entities", flush=True)
                    logger.info(f"[GRAPH] Returned {entity_count} entities")

                    formatted = self._format_graph_context(project_name, client_name, graph_context)
                    if formatted:
                        context_parts.append(formatted)
                        print(f"   ✅ SUCCESS: Loaded graph data for {client_name}", flush=True)
                        logger.info(f"[GRAPH] ✅ SUCCESS: Using graph data for {project_name}")
                    else:
                        print(f"   ⚠️ Graph data returned but formatting failed", flush=True)
                        logger.warning(f"[GRAPH] Data returned but formatting failed for {project_name}")
                else:
                    print(f"   ⚠️ No data in graph for {project_name}", flush=True)
                    logger.warning(f"[GRAPH] No data found for {project_name}")

        # Add context chunks if any detected
        if detected_chunks:
            chunk_context = self._format_chunks_for_injection(detected_chunks)
            if chunk_context:
                context_parts.append(chunk_context)
                print(f"   📚 Added {len(detected_chunks)} context chunks", flush=True)
                logger.info(f"[CONTEXT CHUNKS] Added {len(detected_chunks)} chunks")

        if not context_parts:
            print("⚠️ [CASE CONTEXT] No context to inject", flush=True)
            logger.warning("[CASE CONTEXT] No context to inject")
            return request

        context_text = "\n\n".join(context_parts)

        # Add source indicator
        context_text = "# 🧠 CASE DATA FROM KNOWLEDGE GRAPH\n\n" + context_text
        print("=" * 80, flush=True)
        print("✅ KNOWLEDGE GRAPH DATA INJECTED", flush=True)
        print("=" * 80, flush=True)
        logger.info("✅ KNOWLEDGE GRAPH DATA INJECTED")

        # Inject into system message
        if messages and hasattr(messages[0], 'type') and messages[0].type == 'system':
            existing_content = messages[0].content
            messages[0] = SystemMessage(content=existing_content + "\n\n" + context_text)
        else:
            messages.insert(0, SystemMessage(content=context_text))

        # Store context metadata in request state
        state = dict(request.state) if request.state else {}
        if detected_cases:
            state['detected_cases'] = detected_cases
            state['context_source'] = 'graph'
        if detected_chunks:
            state['detected_chunks'] = [c['name'] for c in detected_chunks]

        return request.override(messages=messages, state=state)

