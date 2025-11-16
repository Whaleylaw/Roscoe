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
)
from src.config.settings import get_setting, DB_URI


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
    # Create RunLoop code execution tool (synchronous)
    runloop_tool = create_runloop_tool()

    # Initialize async toolkits
    gmail_tools = await init_gmail_toolkit()
    calendar_tools = await init_calendar_toolkit()
    supabase_tools = await init_supabase_mcp()
    tavily_tools = await init_tavily_mcp()

    return {
        "code_executor": [runloop_tool],
        "gmail": gmail_tools,
        "calendar": calendar_tools,
        "supabase": supabase_tools,
        "tavily": tavily_tools,
    }


# System prompt implements skills-first workflow per Anthropic code execution pattern
# Prompt designed to be comprehensive yet concise to fit within model context limits
# Examples in prompt teach agent concrete patterns to follow
system_prompt = """You are a legal case management assistant for Whaley Law Firm.

**Available Tools:**
- runloop_execute_code for sandboxed code execution and data processing
- Supabase database access for case files, documents, notes, contacts
- Tavily web search for legal research, case law, statutes
- Gmail for client communications
- Google Calendar for scheduling and deadlines

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
        "model": "gpt-4o",
    },
    {
        "name": "database-specialist",
        "description": "Manages Supabase database operations, queries, updates, data analysis for case files.",
        "system_prompt": """You handle database queries and updates for case management system.

Query efficiently: always use filters to reduce data returned.
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
        "model": "gpt-4o",
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
    # Agent is not yet compiled and cannot be executed until compiled with checkpointer
    agent = create_deep_agent(
        tools=tools,
        system_prompt=system_prompt,
        model="claude-sonnet-4-5-20250929",
        store=store,
        backend=make_backend,
        subagents=configured_subagents,
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

    # Graph is what LangGraph deploys and executes in production
    # Checkpointer enables agent state persistence after every step
    # Graph can be invoked with thread ID to maintain conversation context
    # Graph supports interrupts for human-in-the-loop workflows
    # Graph can be debugged using LangSmith tracing for observability
    # Graph is the exported artifact referenced in langgraph.json deployment config
    # Example invocation: graph.invoke({"messages": [...]}, config={"configurable": {"thread_id": "..."}})
    graph = agent.compile(checkpointer=checkpointer)

    return graph


# Note: The graph must be initialized asynchronously for deployment
# For LangGraph deployment, export an async initialization function
# The deployment platform will handle the async initialization automatically
