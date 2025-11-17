"""
Legal Agent for Whaley Law Firm
Main entry point for DeepAgent legal case management system.
"""
import os
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

# Updated imports per CORRECTED-PLANS
from src.tools.runloop_executor import create_runloop_tool
from src.tools.toolkits import (
    init_gmail_toolkit,
    init_calendar_toolkit,
    init_supabase_mcp,
    init_tavily_mcp,
    init_elevenlabs_tts,
)
from src.config.settings import get_setting, DB_URI
from src.middleware import MCPToolFixMiddleware


def make_backend(runtime):
    """
    Create hybrid memory backend that routes /memories/ to persistent storage
    and everything else to ephemeral storage.

    Files written to /working/ or /temp/ will be ephemeral and deleted after thread.
    Files written to /memories/ will persist across threads and sessions in Supabase PostgreSQL.
    """
    state_backend = StateBackend(runtime)
    store_backend = StoreBackend(runtime)
    return CompositeBackend(
        default=state_backend,
        routes={"/memories/": store_backend}
    )


# PostgresStore provides persistent cross-thread memory storage in Supabase PostgreSQL
# Note: store.setup() must be called once on first deployment to create database tables
# Example: Uncomment for initial deployment, then re-comment for production
store = PostgresStore.from_conn_string(DB_URI)

# PostgresSaver saves agent state after every step enabling resumption and time-travel debugging
# Note: checkpointer.setup() must be called once on first deployment to create database tables
# Same Supabase database used for both store and checkpointer eliminating need for separate infrastructure
checkpointer = PostgresSaver.from_conn_string(DB_URI)


# Toolkit initialization is now async and must be called within async context before agent usage
async def init_tools():
    """
    Initialize all external toolkits and code executor.

    Returns dictionary with tool lists or empty lists for graceful degradation.
    Graceful degradation implemented in toolkit functions so missing credentials
    return empty lists not exceptions preventing agent startup failures.

    Note: runloop_tool initialization is synchronous but toolkit initializations
    are async requiring await keywords per LangChain pattern.
    """
    import logging
    logger = logging.getLogger(__name__)

    # Log environment variable status for debugging deployment issues
    logger.error("=" * 80)
    logger.error("🔍 DEPLOYMENT DIAGNOSTICS - Environment Variables Check")
    logger.error("=" * 80)
    logger.error(f"RUNLOOP_API_KEY: {'✅ Set' if os.getenv('RUNLOOP_API_KEY') else '❌ MISSING'}")
    logger.error(f"SUPABASE_URL: {'✅ Set' if os.getenv('SUPABASE_URL') else '❌ MISSING'}")
    logger.error(f"SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else '❌ MISSING'}")
    logger.error(f"TAVILY_API_KEY: {'✅ Set' if os.getenv('TAVILY_API_KEY') else '❌ MISSING'}")
    logger.error(f"ELEVENLABS_API_KEY: {'✅ Set' if os.getenv('ELEVENLABS_API_KEY') else '❌ MISSING'}")
    logger.error(f"GMAIL_CREDENTIALS: {'✅ Set' if os.getenv('GMAIL_CREDENTIALS') else '❌ MISSING (optional)'}")
    logger.error(f"GOOGLE_CALENDAR_CREDENTIALS: {'✅ Set' if os.getenv('GOOGLE_CALENDAR_CREDENTIALS') else '❌ MISSING (optional)'}")
    logger.error("=" * 80)

    # Create RunLoop code execution tool (synchronous)
    try:
        runloop_tool = create_runloop_tool()
        logger.error("✅ RunLoop code executor initialized successfully")
    except Exception as e:
        logger.error(f"❌ RunLoop initialization failed: {e}")
        runloop_tool = None

    # Initialize async toolkits
    gmail_tools = await init_gmail_toolkit()
    calendar_tools = await init_calendar_toolkit()
    supabase_tools = await init_supabase_mcp()
    tavily_tools = await init_tavily_mcp()
    tts_tools = await init_elevenlabs_tts()

    # Log toolkit initialization results
    logger.error("=" * 80)
    logger.error("📊 TOOLKIT INITIALIZATION RESULTS")
    logger.error("=" * 80)
    logger.error(f"RunLoop Code Executor: {1 if runloop_tool else 0} tools")
    logger.error(f"Gmail: {len(gmail_tools)} tools")
    logger.error(f"Calendar: {len(calendar_tools)} tools")
    logger.error(f"Supabase: {len(supabase_tools)} tools")
    logger.error(f"Tavily: {len(tavily_tools)} tools")
    logger.error(f"ElevenLabs TTS: {len(tts_tools)} tools")
    logger.error(f"TOTAL TOOLS: {(1 if runloop_tool else 0) + len(gmail_tools) + len(calendar_tools) + len(supabase_tools) + len(tavily_tools) + len(tts_tools)}")
    logger.error("=" * 80)

    if not runloop_tool and not supabase_tools and not tavily_tools:
        logger.error("⚠️  WARNING: Critical tools missing!")
        logger.error("⚠️  See LANGGRAPH_CLOUD_SETUP.md for environment variable requirements")
        logger.error("=" * 80)

    return {
        "code_executor": [runloop_tool] if runloop_tool else [],
        "gmail": gmail_tools,
        "calendar": calendar_tools,
        "supabase": supabase_tools,
        "tavily": tavily_tools,
        "tts": tts_tools,
    }


# System prompt implements skills-first workflow per Anthropic code execution pattern
# Prompt designed to be comprehensive yet concise to fit within model context limits
# Examples in prompt teach agent concrete patterns to follow
system_prompt = """You are Roscoe, a legal case management assistant for Whaley Law Firm.

**Available Tools:**
- runloop_execute_code for sandboxed code execution and data processing
- Supabase database access for case files, documents, notes, contacts
- Tavily web search for legal research, case law, statutes
- Gmail for client communications
- Google Calendar for scheduling and deadlines
- ElevenLabs text-to-speech for generating voice output from text

## PostgREST Database Query Syntax (CRITICAL)

**IMPORTANT:** Supabase uses PostgREST, NOT raw SQL. You MUST use PostgREST query syntax.

**Available Supabase Tools:**
1. **postgrestRequest** - Execute PostgREST queries
   - Parameters: `method` (GET/POST/PATCH/DELETE), `path`, `body`
   - Example: `{"method": "GET", "path": "/doc_files?project_name=eq.MVA-2024-001&select=filename,markdown_path"}`

2. **sqlToRest** - Convert SQL to PostgREST syntax (use this if unsure)
   - Input: SQL query string
   - Output: `{method, path}` for use with postgrestRequest

**PostgREST Query Syntax:**
- Query path: `/table?column=operator.value`
- Operators: `eq` (=), `neq` (!=), `gt` (>), `gte` (>=), `lt` (<), `lte` (<=), `like`, `ilike`, `is`, `in`
- Select columns: `?select=col1,col2,col3`
- Filtering: `?column=eq.value&other_column=gt.100`
- Ordering: `?order=column.asc` or `?order=column.desc`
- Limit: `?limit=10`
- Offset: `?offset=20`

**Examples:**
```
# Get all documents for a case
GET /doc_files?project_name=eq.MVA-2024-001&select=uuid,filename,markdown_path

# Get unconverted PDFs
GET /doc_files?markdown_path=is.null&content_type=eq.application/pdf&limit=100

# Search by filename pattern
GET /doc_files?filename=ilike.*medical*&select=filename,project_name

# Get cases with expenses over $1000
GET /case_expenses?amount=gt.1000&select=case_id,description,amount

# Complex query - use sqlToRest tool first
Use sqlToRest: "SELECT * FROM doc_files WHERE project_name = 'MVA-2024-001' AND markdown_path IS NULL"
Then use the returned {method, path} with postgrestRequest
```

**Common Mistakes to Avoid:**
- ❌ DON'T use SQL syntax: `WHERE column = 'value'`
- ✅ DO use PostgREST syntax: `?column=eq.value`
- ❌ DON'T write SQL queries directly to postgrestRequest
- ✅ DO use sqlToRest first if you're thinking in SQL

**When in doubt:** Use the `sqlToRest` tool to convert your SQL to PostgREST syntax!

## Skills-First Workflow (Maximum Token Efficiency)

Follow this pattern for EVERY task:

**Step 1:** Check for existing skill
- Run: `ls /memories/skills/` to list available skills
- If skill matches task: execute it directly → Done (4K tokens instead of 32K)
- Example: `exec(open('/memories/skills/batch_document_processor.py').read())`

**Step 2:** If no skill exists, discover and combine tools using code

**Step 3:** Use runloop_execute_code for data processing in isolated sandbox
- Query MCP tools in code so data stays in execution environment, not LLM context
- Filter, process, transform in Python, not in LLM context for token efficiency
- Return summaries only (e.g., "Processed 100 docs, 95 success, 5 failed")
- DO NOT return full arrays like [full 100-document array] to avoid token waste

**Step 4:** Save successful workflows as skills after completing complex multi-step tasks
- Save to `/memories/skills/{descriptive_name}.py`
- Include docstring with usage instructions
- Next time execution will be 4K tokens instead of 32K tokens (88% reduction)

## Code Execution Examples

**Example 1: Filter large query (saves 148K tokens)**
```python
import json
docs = supabase_query("SELECT * FROM doc_files")  # 150K tokens
unconverted = [d for d in docs if not d['markdown_path']]  # Python filtering
summary = {"total": len(docs), "unconverted": len(unconverted)}
print(json.dumps(summary))  # Only 2K tokens returned
```

**Example 2: Execute saved skill (88% token reduction)**
```python
exec(open('/memories/skills/batch_document_processor.py').read())
result = run_skill(case_id='MVA-2024-001', limit=50)
```

## Filesystem Organization

- `/working/*` - Temporary files (deleted after thread)
- `/memories/skills/*.py` - Executable code patterns (persisted across all threads)
- `/memories/templates/*.md` - Document templates (persisted)
- `/memories/conventions/*.md` - Firm standards (persisted)

## Memory-First Protocol

1. **RESEARCH:** Check `/memories/skills/` for executable patterns before coding
2. **RESPONSE:** Use runloop_execute_code to process large datasets avoiding token overflow
3. **LEARNING:** Save successful multi-step workflows as skills for future reuse

## Additional Guidelines

- Use subagents to delegate specialized work to: legal-researcher, email-manager, database-specialist, scheduler
- Use `write_todos` to plan complex multi-step tasks for better execution tracking
- Always return summaries, never full datasets, to maintain token efficiency
- Suggest saving new skills after completing novel workflows to grow capabilities

## Legal Domain Context

- This is a personal injury law firm handling MVA, Workers Compensation, Premise Liability cases
- Client confidentiality is paramount in all communications and data handling
- Court deadlines are critical and must be tracked accurately in calendar
- Case documents must be organized by case ID and properly categorized

## Error Handling

- Retry tool calls up to 3 times with different approaches if initial fails
- Report errors to user with explanation rather than silent failures
- Use graceful degradation if optional tools unavailable, continuing with available tools

## Quality Standards

- All legal research must cite sources with URLs or case citations
- Email drafts must be professional, clear, and grammatically correct
- Database updates must be validated before committing to prevent data corruption
- Calendar events must include all required fields: title, datetime, description, location

## Optimization Tips

- Always use filters in database queries to reduce data returned
- Batch similar operations together when possible to reduce tool call overhead
- Cache frequently accessed data in `/working/` during thread to avoid repeated queries
- Use subagents for time-consuming tasks like extensive legal research to keep main agent responsive

## Prohibited Actions

- Never delete files from `/memories/` as they are critical persistent knowledge
- Never modify existing skills unless explicitly instructed by user
- Never share client data outside approved channels (Gmail, Calendar, Supabase)
- Never execute code that attempts to access filesystem outside workspace

## Success Metrics

- Token efficiency: Ratio of tokens saved vs. tokens used (aim for 80%+ efficiency)
- Task completion: Percentage of user requests successfully fulfilled without errors
- Skills growth: Number of reusable skills created over time
- User satisfaction: Successful case outcomes and positive feedback

**Remember:** Check `/memories/skills/` first for every task to maximize token efficiency.

**Your goal:** Be helpful, efficient, and accurate while protecting client confidentiality.
"""

# Each subagent has isolated context and specialized tools
# Subagents enable context isolation keeping main agent's context clean
# Different models can be used per subagent for cost or performance optimization
# Subagent prompts are more focused than main agent for task specialization
subagents = [
    {
        "name": "legal-researcher",
        "description": "Specialized in legal research using Tavily web search for case law, statutes, regulations, precedents.",
        "system_prompt": """You are a legal research specialist. Conduct thorough research using Tavily web search.

Focus on: case law, statutes, regulations, legal precedents, relevant legal concepts.

Save research results to files for main agent to access later using write_file.
Synthesize findings into clear actionable summaries with citations.
Use runloop_execute_code if research produces large result sets to filter and summarize in isolated sandbox.""",
        "tools": "tavily",  # Will be replaced with actual tools in create_agent()
        "model": "claude-sonnet-4-5-20250929",
    },
    {
        "name": "email-manager",
        "description": "Handles client email communications, drafts responses, manages email workflows.",
        "system_prompt": """You manage professional email communications for law firm.

Draft clear, professional, grammatically correct emails.
Maintain attorney-client confidentiality in all communications.
Track important email threads and follow-ups in /working/ files.
Use formal professional tone appropriate for legal communications.""",
        "tools": "gmail",  # Will be replaced with actual tools in create_agent()
        "model": "claude-sonnet-4-5-20250929",
    },
    {
        "name": "database-specialist",
        "description": "Manages Supabase database operations, queries, updates, data analysis for case files.",
        "system_prompt": """You handle database queries and updates for case management system using PostgREST.

**CRITICAL: PostgREST Query Syntax**
Supabase uses PostgREST, NOT raw SQL. You MUST use PostgREST query syntax.

Available tools:
1. postgrestRequest - Execute queries with method and path
2. sqlToRest - Convert SQL to PostgREST (use this if you think in SQL)

PostgREST syntax: `/table?column=eq.value&select=col1,col2`
Operators: eq, neq, gt, gte, lt, lte, like, ilike, is, in
Example: `/doc_files?project_name=eq.MVA-2024-001&markdown_path=is.null&limit=100`

**When in doubt:** Use sqlToRest tool to convert SQL to PostgREST!

## ⚠️ CRITICAL FILTERING RULES ⚠️

**MANDATORY project_name FILTERING:**
- ❌ NEVER query case_* tables or doc_files WITHOUT project_name filter
- ❌ NEVER do `/case_expenses` or `/doc_files` (returns 14,000+ rows!)
- ✅ ALWAYS use `?project_name=eq.{value}` for case_* tables and doc_files

**WORKFLOW: Get project_name first**
1. Query case_projects to get available project names:
   - Use: `GET /case_projects?select=project_name,current_status,accident_date`
   - This returns list of active cases with their project_name values
2. Use the project_name from step 1 to query other tables:
   - `GET /case_expenses?project_name=eq.{value}&select=...`
   - `GET /doc_files?project_name=eq.{value}&select=...`

**EXCEPTIONS - No project_name required:**
- ✅ contact_directory - Can query without project_name filter
- ✅ contact_clients - Can query without project_name filter (though it has project_name column)
- ✅ email_messages - Can query without project_name filter

**Tables requiring project_name filter:**
- case_expenses, case_insurance, case_liens, case_litigation_contacts
- case_medical_providers, case_notes, case_pleadings, case_todos
- doc_files (14,000+ rows!)

**Special cases:**
- case_projects: Query with `?select=project_name` to get list of cases (don't list all columns)
- case_summary: Uses `case_name` column (not project_name)

## Database Schema

**case_projects** - Main case/project information (USE THIS TO GET PROJECT NAMES)
Columns: project_name, phase, last_activity, create_date, uuid, case_summary, current_status, agent_name, tag, case_role, parent_project_name, case_group_id, last_status_update, system_message, accident_date
Query pattern: `GET /case_projects?select=project_name,current_status,accident_date` to get list of active cases

**case_notes** - Case notes and communications (REQUIRES project_name filter)
Columns: project_name, author_name, note, last_activity, uuid, time, note_summary, summary_done, created_by_id, applies_to_projects, related_insurance_uuid, related_medical_provider_id, related_lien_uuid, related_expense_uuid, note_type

**case_expenses** - Case-related expenses (REQUIRES project_name filter)
Columns: project_name, payable_to, description, expense_amount, notes, created_date, uuid, applies_to_projects

**case_insurance** - Insurance claim information (REQUIRES project_name filter)
Columns: project_name, claim_number, current_negotiation_status, current_offer, date_coots_letter_sent, date_demand_sent, demand_summary, demanded_amount, insurance_adjuster_name, insurance_company_name, settlement_amount, settlement_date, uuid, insurance_type, coverage_confirmation, applies_to_projects, is_active_negotiation

**case_liens** - Lien information (REQUIRES project_name filter)
Columns: project_name, lien_holder_name, final_lien_amount, amount_owed_from_settlement, date_final_lien_requested, date_lien_paid, date_of_final_lien_received, reduction_amount, uuid, applies_to_projects

**case_litigation_contacts** - Litigation-related contacts (REQUIRES project_name filter)
Columns: id, created_at, project_name, contact, role, applies_to_projects

**case_medical_providers** - Medical provider information (REQUIRES project_name filter)
Columns: id, project_name, provider_full_name, medical_provider_notes, date_treatment_started, date_treatment_completed, date_medical_bills_requested, medical_bills_received_date, date_medical_records_requested, date_medical_records_received, billed_amount, number_of_visits, settlement_payment, applies_to_projects

**case_pleadings** - Court pleadings and filings (REQUIRES project_name filter)
Columns: project_name, filing_party_name, pleading_type, certificate_of_service, motion_hour_or_hearing_date, motion_hour_or_hearing_notes, pleadings_notes, uuid, applies_to_projects

**case_todos** - Case to-do items (REQUIRES project_name filter)
Columns: uuid, project_name, to_do, due_date, progress, to_do_id, created_at, done, done_date, created_by

**case_summary** - Case summary information (uses case_name column, not project_name)
Columns: case_name, summary_text, last_updated, uuid
Note: Filter by case_name, not project_name

**contact_directory** - General contact information (NO project_name filter required)
Columns: full_name, email, phone, address, uuid, phone_normalized

**contact_clients** - Client contact information (NO project_name filter required)
Columns: project_name, full_name, email, phone, address, date_of_birth, social_security_number, uuid
Note: Has project_name column but can be queried without filter

**doc_files** - Document file metadata (REQUIRES project_name filter - 14,000+ rows!)
Columns: project_name, filename, upload_date, size_bytes, uuid, storage_path, file_url, content_type, is_uploaded_to_storage, mapping_error, summary_done, client_name, revised_file_name, applies_to_projects, chunked, summary, storage_bucket, markdown_path, markdown_regenerated_at

**email_messages** - Email messages synced from Gmail (NO project_name filter required)
Columns: uuid, from, to, subject, text, id, messageid, threadid, date, labelids, attachments, created_at, updated_at, category, categorized, read, project_names, attachment_urls, draft_email, from_contact_id, context, html

## Query Examples

```
# STEP 1: Get list of active cases (ALWAYS DO THIS FIRST)
GET /case_projects?select=project_name,current_status,accident_date&limit=50

# STEP 2: Query case data using project_name from step 1
GET /doc_files?project_name=eq.MVA-2024-001&select=filename,upload_date,markdown_path

# Get case expenses for specific case
GET /case_expenses?project_name=eq.MVA-2024-001&select=payable_to,expense_amount,description

# Get today's work emails (no project_name needed)
GET /email_messages?category=eq.Work&date=gte.2025-11-16&select=subject,from,date,text

# Get active insurance negotiations for a case
GET /case_insurance?project_name=eq.MVA-2024-001&is_active_negotiation=eq.true&select=insurance_company_name,current_offer,demanded_amount

# Get unpaid liens for a case
GET /case_liens?project_name=eq.MVA-2024-001&date_lien_paid=is.null&select=lien_holder_name,final_lien_amount

# Get medical providers with pending records for a case
GET /case_medical_providers?project_name=eq.MVA-2024-001&date_medical_records_received=is.null&select=provider_full_name,date_medical_records_requested

# Search contacts (no project_name needed)
GET /contact_directory?full_name=ilike.*smith*&select=full_name,email,phone
```

Query efficiently: always use filters and select to reduce data returned.
Update carefully: verify data before making changes to prevent corruption.
Return summaries not full datasets to save tokens using runloop_execute_code for processing in isolated sandbox.
Use runloop_execute_code to filter and aggregate database results in sandbox before returning to main agent.""",
        "tools": "supabase_and_code",  # Will be replaced with actual tools in create_agent()
        "model": "claude-sonnet-4-5-20250929",
    },
    {
        "name": "scheduler",
        "description": "Manages calendar events, court dates, deadlines, scheduling meetings.",
        "system_prompt": """You manage firm's calendar and scheduling.

Track court dates, client meetings, deadlines accurately.
Coordinate schedules and send reminders for important events.
Ensure no scheduling conflicts by checking existing events before creating new ones.
Include all required event fields: title, datetime, description, location, attendees.""",
        "tools": "calendar",  # Will be replaced with actual tools in create_agent()
        "model": "claude-sonnet-4-5-20250929",
    },
]


async def create_agent():
    """
    Initialize all toolkits and create agent instance with async tool loading.

    This function must be awaited in async context. Agent creation now async
    due to toolkit initialization but compilation and graph export remain synchronous.
    """
    # Initialize all toolkits and code executor
    tools_dict = await init_tools()

    # Build flat tools list for main agent
    tools = [
        *tools_dict["code_executor"],
        *tools_dict["gmail"],
        *tools_dict["calendar"],
        *tools_dict["supabase"],
        *tools_dict["tavily"],
        *tools_dict["tts"],
    ]

    # Update subagent tools from dictionary
    configured_subagents = []
    for subagent in subagents:
        subagent_config = subagent.copy()

        # Replace string placeholders with actual tools
        if subagent_config["tools"] == "tavily":
            subagent_config["tools"] = tools_dict["tavily"]
        elif subagent_config["tools"] == "gmail":
            subagent_config["tools"] = tools_dict["gmail"]
        elif subagent_config["tools"] == "supabase_and_code":
            subagent_config["tools"] = [
                *tools_dict["code_executor"],
                *tools_dict["supabase"]
            ]
        elif subagent_config["tools"] == "calendar":
            subagent_config["tools"] = tools_dict["calendar"]

        configured_subagents.append(subagent_config)

    # create_deep_agent automatically attaches TodoListMiddleware for planning
    # FilesystemMiddleware automatically attached for file operations
    # SubAgentMiddleware automatically attached for delegation
    # create_deep_agent compiles the agent automatically when checkpointer is provided
    # Custom middleware (MCPToolFixMiddleware) applies to main agent AND all subagents
    agent = create_deep_agent(
        tools=tools,
        system_prompt=system_prompt,
        model="claude-sonnet-4-5-20250929",
        store=store,
        backend=make_backend,
        checkpointer=checkpointer,
        subagents=configured_subagents,
        middleware=[MCPToolFixMiddleware()],  # DeepAgents middleware for MCP tool fix
    )

    return agent


async def initialize_agent():
    """
    Create agent in async context and compile with checkpointer.

    This function must be awaited in module-level async context or deployment startup.
    Graph must be initialized asynchronously, typically in LangGraph deployment startup
    hook or main function. LangGraph deployment platform handles async initialization
    automatically when importing graph from module.

    Example usage: graph = await initialize_agent()
    """
    agent = await create_agent()

    # create_deep_agent() returns a CompiledStateGraph that's ready to use
    # The agent is already compiled with the checkpointer parameter passed to create_deep_agent
    # Graph is what LangGraph deploys and executes in production
    # Graph can be invoked with thread ID to maintain conversation context
    # Graph supports interrupts for human-in-the-loop workflows
    # Graph can be debugged using LangSmith tracing for observability
    # Graph is the exported artifact referenced in langgraph.json deployment config
    # Example invocation: agent.invoke({"messages": [...]}, config={"configurable": {"thread_id": "..."}})

    return agent


# Note: The graph must be initialized asynchronously for deployment
# For LangGraph deployment, export an async initialization function
# The deployment platform will handle the async initialization automatically
