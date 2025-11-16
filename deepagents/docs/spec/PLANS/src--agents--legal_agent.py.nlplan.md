# Natural Language Plan: src/agents/legal_agent.py

## File Purpose

This file is the main entry point for the DeepAgent system. It orchestrates the entire agent by initializing all components: loading configuration, setting up MCP clients, configuring memory backends, defining the system prompt with skills-first workflow, configuring subagents, and compiling the final graph with checkpointer. The exported `graph` object is what LangGraph deploys and executes.

This file participates as the primary orchestrator, importing from `src/config/settings.py` for configuration and `src/mcp/clients.py` for MCP tools, and exporting the compiled graph for deployment.

## Imports We Will Need (and Why)

001: Import create_deep_agent from deepagents to use the high-level agent creation API that automatically includes TodoList, Filesystem, and SubAgent middleware.

002: Import CompositeBackend from deepagents.backends to create hybrid memory backend routing between ephemeral and persistent storage.

003: Import StateBackend from deepagents.backends for ephemeral short-term memory stored in agent state for current thread only.

004: Import StoreBackend from deepagents.backends for persistent long-term memory routing /memories/ paths to PostgresStore across all threads.

005: Import PostgresSaver from langgraph.checkpoint.postgres to save agent state checkpoints to Supabase PostgreSQL after each step enabling resumption and time-travel.

006: Import PostgresStore from langgraph.store.postgres to persist long-term memory in Supabase PostgreSQL across threads and sessions.

007: Import PythonREPLTool from langchain_experimental.tools to enable code execution for Anthropic's code execution pattern achieving 88-98% token reduction.

008: Import os module to access environment variables for database connection and API keys.

009: Import get_setting and DB_URI from src.config.settings to retrieve validated configuration values and database connection string [uses: get_setting @ src/config/settings.py (planned line 011)] [uses: DB_URI @ src/config/settings.py (planned line 002)].

010: Import supabase_tools, tavily_tools, gmail_tools, calendar_tools from src.mcp.clients to get tool lists from all configured MCP servers [uses: supabase_tools @ src/mcp/clients.py (planned line 020)] [uses: tavily_tools @ src/mcp/clients.py (planned line 040)] [uses: gmail_tools @ src/mcp/clients.py (planned line 060)] [uses: calendar_tools @ src/mcp/clients.py (planned line 080)].

## Objects We Will Define

### Function: `make_backend(runtime) -> CompositeBackend`
**Purpose**: Create memory backend that routes /memories/ to persistent storage and everything else to ephemeral storage
**Inputs**: `runtime` - DeepAgent runtime object
**Outputs**: CompositeBackend configured with StateBackend default and StoreBackend for /memories/ routes
**Side effects**: None (pure function)

### Constant: `store`
**Purpose**: PostgresStore instance for long-term memory persistence
**Type**: PostgresStore
**Initialization**: Created from DB_URI connection string

### Constant: `checkpointer`
**Purpose**: PostgresSaver instance for agent state persistence
**Type**: PostgresSaver
**Initialization**: Created from DB_URI connection string

### Constant: `python_repl`
**Purpose**: Code execution tool for Anthropic pattern
**Type**: PythonREPLTool
**Initialization**: Instantiated with default configuration

### Constant: `agent`
**Purpose**: DeepAgent instance with all tools, middleware, and configuration
**Type**: DeepAgent
**Configuration**: Includes tools list, system prompt, model, store, backend, subagents

### Constant: `graph`
**Purpose**: Compiled LangGraph ready for deployment and execution
**Type**: CompiledGraph
**Compilation**: Agent compiled with checkpointer

## Line-by-Line Natural Language Plan

[defines: imports @ src/agents/legal_agent.py (planned lines 001-010)]
001: Import create_deep_agent function from deepagents module to access high-level agent creation API with automatic middleware attachment.

002: Import CompositeBackend class from deepagents.backends module to create hybrid memory backend for routing paths to different storage backends.

003: Import StateBackend class from deepagents.backends module for ephemeral thread-scoped memory storage in agent state.

004: Import StoreBackend class from deepagents.backends module for persistent cross-thread memory storage routed to PostgresStore.

005: Import PostgresSaver class from langgraph.checkpoint.postgres module to persist agent checkpoints to Supabase PostgreSQL database.

006: Import PostgresStore class from langgraph.store.postgres module to persist long-term memory to Supabase PostgreSQL database.

007: Import PythonREPLTool class from langchain_experimental.tools module to enable Python code execution for token-efficient data processing.

008: Import os module from standard library to access environment variables if needed for runtime configuration.

009: Import get_setting function and DB_URI constant from src.config.settings module to access validated configuration values [uses: get_setting @ src/config/settings.py (planned line 011)] [uses: DB_URI @ src/config/settings.py (planned line 002)].

010: Import MCP tool lists from src.mcp.clients module including supabase_tools tavily_tools gmail_tools calendar_tools [uses: supabase_tools @ src/mcp/clients.py (planned line 020)] [uses: tavily_tools @ src/mcp/clients.py (planned line 040)] [uses: gmail_tools @ src/mcp/clients.py (planned line 060)] [uses: calendar_tools @ src/mcp/clients.py (planned line 080)].

[defines: make_backend @ src/agents/legal_agent.py (planned lines 011-020)]
011: Define function make_backend accepting runtime parameter to create CompositeBackend for hybrid memory routing.

012: Inside make_backend instantiate StateBackend passing runtime for ephemeral memory stored in agent state.

013: Instantiate StoreBackend passing runtime for persistent memory routed to PostgresStore for /memories/ paths.

014: Create CompositeBackend with default parameter set to StateBackend instance for all non-/memories/ paths.

015: Set routes parameter of CompositeBackend to dictionary with key "/memories/" mapped to StoreBackend instance.

016: Return the CompositeBackend instance to caller for use in agent configuration.

017: Add docstring to make_backend explaining it creates hybrid memory backend routing /memories/ to persistent store and others to ephemeral state.

018: Add type hint to function signature indicating runtime parameter type and CompositeBackend return type.

019: Add inline comment explaining that files written to /working/ or /temp/ will be ephemeral and deleted after thread.

020: Add inline comment explaining that files written to /memories/ will persist across threads and sessions in Supabase PostgreSQL.

[defines: store @ src/agents/legal_agent.py (planned lines 021-025)]
021: Instantiate PostgresStore by calling from_conn_string class method passing DB_URI for connection to Supabase database [uses: DB_URI @ src/config/settings.py (planned line 002)].

022: Assign PostgresStore instance to module-level constant named store for use in agent configuration and backend routing.

023: Add inline comment explaining store provides persistent cross-thread memory storage in Supabase PostgreSQL.

024: Add comment noting that store.setup() must be called once on first deployment to create database tables.

025: Add comment with example showing setup call should be uncommented for initial deployment then re-commented for production.

[defines: checkpointer @ src/agents/legal_agent.py (planned lines 026-030)]
026: Instantiate PostgresSaver by calling from_conn_string class method passing DB_URI for connection to Supabase database [uses: DB_URI @ src/config/settings.py (planned line 002)].

027: Assign PostgresSaver instance to module-level constant named checkpointer for use in graph compilation.

028: Add inline comment explaining checkpointer saves agent state after every step enabling resumption and time-travel debugging.

029: Add comment noting that checkpointer.setup() must be called once on first deployment to create database tables.

030: Add comment that same Supabase database used for both store and checkpointer eliminating need for separate infrastructure.

[defines: python_repl @ src/agents/legal_agent.py (planned lines 031-035)]
031: Instantiate PythonREPLTool class with default configuration for code execution capability.

032: Assign PythonREPLTool instance to module-level constant named python_repl for inclusion in agent tools list.

033: Add inline comment explaining python_repl enables Anthropic code execution pattern for 88-98% token reduction.

034: Add comment that code execution allows agent to process data in Python environment instead of passing through LLM context.

035: Add comment noting that python_repl has timeout of 60 seconds by default and runs in restricted environment for safety.

[defines: system_prompt @ src/agents/legal_agent.py (planned lines 036-120)]
036: Define multiline string constant system_prompt containing comprehensive instructions for agent behavior and skills-first workflow.

037: Begin prompt with role statement "You are a legal case management assistant for Whaley Law Firm."

038: List available tools starting with python_repl for code execution and data processing.

039: List Supabase database access for case files documents notes contacts.

040: List Tavily web search for legal research case law statutes.

041: List Gmail for client communications.

042: List Google Calendar for scheduling and deadlines.

043: Add heading "Skills-First Workflow (Maximum Token Efficiency)" to emphasize primary operating pattern.

044: Instruct agent to follow pattern for EVERY task emphasizing consistency.

045: Step 1 instruction: Check for existing skill by calling ls /memories/skills/ to list available skills.

046: Step 1a: If skill matches task execute it directly and Done with 4K tokens instead of 32K.

047: Step 1b: Provide example using exec(open('/memories/skills/batch_document_processor.py').read()) to execute skill.

048: Step 2 instruction: If no skill exists discover and combine tools using code.

049: Step 3 instruction: Use python_repl for data processing with sub-instructions.

050: Step 3a: Query MCP tools in code so data stays in execution environment not LLM context.

051: Step 3b: Filter process transform in Python not in LLM context for token efficiency.

052: Step 3c: Return summaries only such as "Processed 100 docs, 95 success, 5 failed" as example.

053: Step 3d: Explicitly state NOT to return full arrays like [full 100-document array] to avoid token waste.

054: Step 4 instruction: Save successful workflows as skills after completing complex multi-step tasks.

055: Step 4a: Save to /memories/skills/{descriptive_name}.py with descriptive filename.

056: Step 4b: Include docstring with usage instructions for future execution.

057: Step 4c: Note that next time execution will be 4K tokens instead of 32K tokens achieving 88% reduction.

058: Add heading "Code Execution Examples" to provide concrete patterns for agent to follow.

059: Example 1 heading: "Filter large query (saves 148K tokens)" showing massive token savings potential.

060: Example 1 code block showing import json and supabase_query executing in code environment.

061: Example 1 showing list comprehension filtering unconverted documents in Python not LLM.

062: Example 1 showing summary construction with total and unconverted counts.

063: Example 1 showing print(json.dumps(summary)) returning only 2K tokens versus 150K tokens.

064: Example 2 heading: "Execute saved skill (88% token reduction)" emphasizing reusability benefit.

065: Example 2 code block showing exec(open('/memories/skills/batch_document_processor.py').read()) for skill execution.

066: Example 2 showing result = run_skill(case_id='MVA-2024-001', limit=50) calling skill function.

067: Add heading "Filesystem Organization" to clarify where different types of data stored.

068: Document /working/* for temporary files deleted after thread with example paths.

069: Document /memories/skills/*.py for executable code patterns persisted across all threads with emphasis.

070: Document /memories/templates/*.md for document templates persisted across all threads.

071: Document /memories/conventions/*.md for firm standards persisted across all threads.

072: Add heading "Memory-First Protocol" to establish checking memory before starting work.

073: Protocol step 1: RESEARCH by checking /memories/skills/ for executable patterns before coding.

074: Protocol step 2: RESPONSE by using python_repl to process large datasets avoiding token overflow.

075: Protocol step 3: LEARNING by saving successful multi-step workflows as skills for future reuse.

076: Add heading "Additional Guidelines" for supplementary instructions.

077: Guideline 1: Use subagents to delegate specialized work to legal-researcher email-manager database-specialist scheduler.

078: Guideline 2: Use write_todos to plan complex multi-step tasks for better execution tracking.

079: Guideline 3: Always return summaries never full datasets to maintain token efficiency.

080: Guideline 4: Suggest saving new skills after completing novel workflows to grow capabilities.

081: Add heading "Legal Domain Context" to provide domain-specific knowledge.

082: Context 1: This is personal injury law firm handling MVA Workers Compensation Premise Liability cases.

083: Context 2: Client confidentiality is paramount in all communications and data handling.

084: Context 3: Court deadlines are critical and must be tracked accurately in calendar.

085: Context 4: Case documents must be organized by case ID and properly categorized.

086: Add heading "Error Handling" for guidance on failures.

087: Instruction to retry tool calls up to 3 times with different approaches if initial fails.

088: Instruction to report errors to user with explanation rather than silent failures.

089: Instruction to use graceful degradation if optional tools unavailable continuing with available tools.

090: Add heading "Quality Standards" for output expectations.

091: Standard 1: All legal research must cite sources with URLs or case citations.

092: Standard 2: Email drafts must be professional clear and grammatically correct.

093: Standard 3: Database updates must be validated before committing to prevent data corruption.

094: Standard 4: Calendar events must include all required fields title datetime description location.

095: Add heading "Optimization Tips" for performance guidance.

096: Tip 1: Always use filters in database queries to reduce data returned.

097: Tip 2: Batch similar operations together when possible to reduce tool call overhead.

098: Tip 3: Cache frequently accessed data in /working/ during thread to avoid repeated queries.

099: Tip 4: Use subagents for time-consuming tasks like extensive legal research to keep main agent responsive.

100: Add heading "Prohibited Actions" for safety constraints.

101: Prohibition 1: Never delete files from /memories/ as they are critical persistent knowledge.

102: Prohibition 2: Never modify existing skills unless explicitly instructed by user.

103: Prohibition 3: Never share client data outside approved channels Gmail Calendar Supabase.

104: Prohibition 4: Never execute code that attempts to access filesystem outside workspace.

105: Add heading "Success Metrics" to define goals.

106: Metric 1: Token efficiency measured by ratio of tokens saved versus tokens used aiming for 80%+ efficiency.

107: Metric 2: Task completion measured by percentage of user requests successfully fulfilled without errors.

108: Metric 3: Skills growth measured by number of reusable skills created over time.

109: Metric 4: User satisfaction measured by successful case outcomes and positive feedback.

110: Add concluding statement: "Remember to check /memories/skills/ first for every task to maximize token efficiency."

111: Add final reminder: "Your goal is to be helpful efficient and accurate while protecting client confidentiality."

112: Close system_prompt string with triple quotes.

113: Add comment above system_prompt explaining it implements skills-first workflow per Anthropic code execution pattern.

114: Add comment that prompt designed to be comprehensive yet concise to fit within model context limits.

115: Add comment that prompt may be refined based on agent performance and user feedback.

116: Add comment noting that examples in prompt teach agent concrete patterns to follow.

117: Add comment that filesystem organization clarifies memory architecture for agent understanding.

118: Add comment that guidelines provide flexibility while maintaining quality standards.

119: Add comment that prohibitions enforce safety and security constraints.

120: Add comment that success metrics align agent behavior with business objectives.

[defines: subagents @ src/agents/legal_agent.py (planned lines 121-180)]
121: Define list constant subagents containing dictionaries for each specialized subagent configuration.

122: Begin first subagent dictionary for legal-researcher specialist.

123: Set name key to "legal-researcher" for subagent identification.

124: Set description key to "Specialized in legal research using Tavily web search for case law statutes regulations precedents."

125: Set system_prompt key for legal-researcher to role statement "You are a legal research specialist."

126: Continue legal-researcher prompt with instruction "Conduct thorough research using Tavily web search."

127: Continue with focus statement "Focus on: case law, statutes, regulations, legal precedents, relevant legal concepts."

128: Instruct to "Save research results to files for main agent to access later using write_file."

129: Instruct to "Synthesize findings into clear actionable summaries with citations."

130: Instruct to "Use python_repl if research produces large result sets to filter and summarize."

131: Set tools key for legal-researcher to unpacked tavily_tools list for web search access [uses: tavily_tools @ src/mcp/clients.py (planned line 040)].

132: Set model key for legal-researcher to "claude-sonnet-4-5-20250929" for consistency with main agent.

133: Close legal-researcher subagent dictionary.

134: Begin second subagent dictionary for email-manager specialist.

135: Set name key to "email-manager" for subagent identification.

136: Set description key to "Handles client email communications drafts responses manages email workflows."

137: Set system_prompt key for email-manager to role statement "You manage professional email communications for law firm."

138: Continue email-manager prompt with instruction "Draft clear professional grammatically correct emails."

139: Instruct to "Maintain attorney-client confidentiality in all communications."

140: Instruct to "Track important email threads and follow-ups in /working/ files."

141: Instruct to "Use formal professional tone appropriate for legal communications."

142: Set tools key for email-manager to unpacked gmail_tools list for email access [uses: gmail_tools @ src/mcp/clients.py (planned line 060)].

143: Set model key for email-manager to "gpt-4o" showing flexibility to use different models per subagent.

144: Close email-manager subagent dictionary.

145: Begin third subagent dictionary for database-specialist.

146: Set name key to "database-specialist" for subagent identification.

147: Set description key to "Manages Supabase database operations queries updates data analysis for case files."

148: Set system_prompt key for database-specialist to role statement "You handle database queries and updates for case management system."

149: Continue database-specialist prompt with instruction "Query efficiently: always use filters to reduce data returned."

150: Instruct to "Update carefully: verify data before making changes to prevent corruption."

151: Instruct to "Return summaries not full datasets to save tokens using python_repl for processing."

152: Instruct to "Use python_repl to filter and aggregate database results before returning to main agent."

153: Set tools key for database-specialist to list combining unpacked supabase_tools and python_repl for data processing [uses: supabase_tools @ src/mcp/clients.py (planned line 020)] [uses: python_repl @ src/agents/legal_agent.py (planned line 031)].

154: Set model key for database-specialist to "claude-sonnet-4-5-20250929" for consistency with main agent.

155: Close database-specialist subagent dictionary.

156: Begin fourth subagent dictionary for scheduler.

157: Set name key to "scheduler" for subagent identification.

158: Set description key to "Manages calendar events court dates deadlines scheduling meetings."

159: Set system_prompt key for scheduler to role statement "You manage firm's calendar and scheduling."

160: Continue scheduler prompt with instruction "Track court dates client meetings deadlines accurately."

161: Instruct to "Coordinate schedules and send reminders for important events."

162: Instruct to "Ensure no scheduling conflicts by checking existing events before creating new ones."

163: Instruct to "Include all required event fields: title datetime description location attendees."

164: Set tools key for scheduler to unpacked calendar_tools list for calendar access [uses: calendar_tools @ src/mcp/clients.py (planned line 080)].

165: Set model key for scheduler to "gpt-4o" for variety in model selection.

166: Close scheduler subagent dictionary and subagents list.

167: Add comment above subagents list explaining each subagent has isolated context and specialized tools.

168: Add comment that subagents enable context isolation keeping main agent's context clean.

169: Add comment that different models can be used per subagent for cost or performance optimization.

170: Add comment that subagent prompts are more focused than main agent for task specialization.

171: Add comment that subagents can call write_file to save results for main agent access.

172: Add comment that database-specialist has python_repl for data processing same as main agent.

173: Add comment that main agent delegates via task tool provided by SubAgentMiddleware.

174: Add comment with example: task(subagent="legal-researcher", input="Research CA product liability law").

175: Add comment that subagent results returned as tool result to main agent.

176: Add comment that subagents share same store and checkpointer as main agent for consistency.

177: Add comment that subagents cannot call other subagents preventing infinite delegation loops.

178: Add comment that subagents are optional but provide better organization for complex workflows.

179: Add comment that more subagents can be added as new MCP servers or capabilities added.

180: Add comment that subagent configuration is declarative and easy to modify without code changes.

[defines: agent @ src/agents/legal_agent.py (planned lines 181-200)]
181: Call create_deep_agent function to instantiate DeepAgent with full configuration.

182: Pass tools parameter as list starting with python_repl for code execution [uses: python_repl @ src/agents/legal_agent.py (planned line 031)].

183: Unpack supabase_tools into tools list for database operations [uses: supabase_tools @ src/mcp/clients.py (planned line 020)].

184: Unpack tavily_tools into tools list for web search [uses: tavily_tools @ src/mcp/clients.py (planned line 040)].

185: Unpack gmail_tools into tools list for email operations [uses: gmail_tools @ src/mcp/clients.py (planned line 060)].

186: Unpack calendar_tools into tools list for scheduling [uses: calendar_tools @ src/mcp/clients.py (planned line 080)].

187: Pass system_prompt parameter with the comprehensive skills-first prompt [uses: system_prompt @ src/agents/legal_agent.py (planned line 036)].

188: Pass model parameter as "claude-sonnet-4-5-20250929" for Claude Sonnet 4.5 model.

189: Pass store parameter with PostgresStore instance for long-term memory [uses: store @ src/agents/legal_agent.py (planned line 021)].

190: Pass backend parameter with make_backend function for hybrid memory routing [uses: make_backend @ src/agents/legal_agent.py (planned line 011)].

191: Pass subagents parameter with list of subagent configurations [uses: subagents @ src/agents/legal_agent.py (planned line 121)].

192: Assign create_deep_agent return value to constant named agent.

193: Add comment that create_deep_agent automatically attaches TodoListMiddleware for planning.

194: Add comment that FilesystemMiddleware automatically attached for file operations.

195: Add comment that SubAgentMiddleware automatically attached for delegation.

196: Add comment that agent is not yet compiled and cannot be executed until compiled with checkpointer.

197: Add comment that agent configuration is declarative making it easy to modify tools prompts or subagents.

198: Add comment that same agent configuration can be used for local development and production deployment.

199: Add comment that agent supports streaming responses via LangGraph SDK for real-time UI updates.

200: Add comment that agent state automatically synced to frontend via Server-Sent Events.

[defines: graph @ src/agents/legal_agent.py (planned lines 201-210)]
201: Call agent.compile method to produce executable LangGraph from DeepAgent configuration.

202: Pass checkpointer parameter to compile method with PostgresSaver instance [uses: checkpointer @ src/agents/legal_agent.py (planned line 026)].

203: Assign compiled graph to constant named graph for export and deployment.

204: Add comment that graph is what LangGraph deploys and executes in production.

205: Add comment that checkpointer enables agent state persistence after every step.

206: Add comment that graph can be invoked with thread ID to maintain conversation context.

207: Add comment that graph supports interrupts for human-in-the-loop workflows.

208: Add comment that graph can be debugged using LangSmith tracing for observability.

209: Add comment that graph is the exported artifact referenced in langgraph.json deployment config.

210: Add comment with example invocation: graph.invoke({"messages": [...]}, config={"configurable": {"thread_id": "..."}}).

## Cross-References

[uses: get_setting @ src/config/settings.py (planned line 011)]
[uses: DB_URI @ src/config/settings.py (planned line 002)]
[uses: supabase_tools @ src/mcp/clients.py (planned line 020)]
[uses: tavily_tools @ src/mcp/clients.py (planned line 040)]
[uses: gmail_tools @ src/mcp/clients.py (planned line 060)]
[uses: calendar_tools @ src/mcp/clients.py (planned line 080)]

[defines: make_backend @ src/agents/legal_agent.py (planned lines 011-020)]
[defines: store @ src/agents/legal_agent.py (planned lines 021-025)]
[defines: checkpointer @ src/agents/legal_agent.py (planned lines 026-030)]
[defines: python_repl @ src/agents/legal_agent.py (planned lines 031-035)]
[defines: system_prompt @ src/agents/legal_agent.py (planned lines 036-120)]
[defines: subagents @ src/agents/legal_agent.py (planned lines 121-180)]
[defines: agent @ src/agents/legal_agent.py (planned lines 181-200)]
[defines: graph @ src/agents/legal_agent.py (planned lines 201-210)]

## Notes & Assumptions

- Assumes src/config/settings.py has validated configuration before this module imports
- Assumes src/mcp/clients.py has successfully initialized MCP servers
- Assumes Supabase database tables created via store.setup() and checkpointer.setup() on first deployment
- System prompt designed for Claude Sonnet 4.5 but adaptable to other models
- Subagents optional but recommended for complex workflows
- Code execution via python_repl is core to architecture per Anthropic pattern
- Skills-first workflow is mandatory per architecture specification
- Same database used for checkpointer, store, and case data per architecture decision
- Graph compilation with checkpointer is final step before deployment
- File exports only `graph` constant for LangGraph deployment
