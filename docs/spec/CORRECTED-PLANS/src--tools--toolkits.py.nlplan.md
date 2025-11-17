# Natural Language Plan: src/tools/toolkits.py

**Status**: Planning Phase - No code written yet
**Purpose**: Initialize all external tool integrations (Gmail, Calendar, Supabase, Tavily)
**Approval Required**: "Approves, spec"

---

## File Purpose

This file provides async initialization functions for all external tool integrations used by the legal agent. It replaces the previous `src/mcp/clients.py` approach by using native LangChain toolkits for Gmail and Calendar (simpler, better maintained) while using corrected MCP packages for Supabase and Tavily.

This file participates as the primary tool provider for the agent's skills-first workflow, enabling email management, calendar scheduling, database operations, and web search capabilities.

---

## Imports We Will Need (and Why)

001: Import os module from standard library to access environment variables for API keys and credential paths throughout initialization functions.

002: Import logging module from standard library to log toolkit initialization status success and failures for debugging and monitoring purposes.

003: Import Optional and List types from typing module to provide type hints for nullable return values and list structures used in tool collections.

004: Import GmailToolkit class from langchain underscore google underscore community package to initialize Gmail operations toolkit with OAuth credentials [Citation: https://python.langchain.com/docs/integrations/tools/google_gmail].

005: Import CalendarToolkit class from langchain underscore google underscore community package to initialize Calendar operations toolkit with OAuth credentials [Citation: https://python.langchain.com/docs/integrations/tools/google_calendar].

006: Import MCPClient class from langchain underscore mcp underscore adapters package to create MCP client instances for Supabase and Tavily servers [Citation: https://python.langchain.com/docs/integrations/tools/mcp].

007: Import BaseTool type from langchain underscore core dot tools to provide consistent return type annotation for all toolkit initialization functions.

---

## Objects We Will Define

### Function: `init_gmail_toolkit()`
**Purpose**: Initialize Gmail toolkit with OAuth credentials
**Inputs**: None (reads from environment)
**Outputs**: list[BaseTool] (5 Gmail tools)
**Side effects**: Reads credentials.json, may trigger OAuth flow
**Async**: True

### Function: `init_calendar_toolkit()`
**Purpose**: Initialize Calendar toolkit with OAuth credentials
**Inputs**: None (reads from environment)
**Outputs**: list[BaseTool] (7 Calendar tools)
**Side effects**: Reads credentials.json, may trigger OAuth flow
**Async**: True

### Function: `init_supabase_mcp()`
**Purpose**: Initialize Supabase MCP client with corrected package
**Inputs**: None (reads from environment)
**Outputs**: list[BaseTool] (Supabase database tools)
**Side effects**: Spawns npx MCP server subprocess
**Async**: True

### Function: `init_tavily_mcp()`
**Purpose**: Initialize Tavily MCP client with corrected package
**Inputs**: None (reads from environment)
**Outputs**: list[BaseTool] (Tavily search tools)
**Side effects**: Spawns npx MCP server subprocess
**Async**: True

---

## Line-by-Line Natural Language Plan

[defines: imports @ src/tools/toolkits.py (planned lines 001-015)]

001: Import os module to read environment variables including GMAIL underscore CREDENTIALS GOOGLE underscore CALENDAR underscore CREDENTIALS SUPABASE underscore URL TAVILY underscore API underscore KEY for toolkit configuration.

002: Import logging module to create logger instance for recording toolkit initialization events including successes graceful degradation and errors that occur during setup.

003: Import Optional and List from typing module to provide type annotations for nullable return values when toolkit initialization fails and list structures for tool collections.

004: Import GmailToolkit from langchain underscore google underscore community package to initialize Gmail toolkit with OAuth credentials per official integration guide.

005: Import CalendarToolkit from langchain underscore google underscore community package to initialize Calendar toolkit with OAuth credentials per official integration guide.

006: Import MCPClient from langchain underscore mcp underscore adapters package to create MCP client instances for Supabase and Tavily MCP servers.

007: Import BaseTool from langchain underscore core dot tools to provide consistent return type for all initialization functions as list of BaseTool instances.

008: Get logger instance by calling logging dot getLogger with dunder name to create module-specific logger for toolkit initialization operations.

009: Add module-level docstring explaining this file provides async initialization functions for all external tool integrations replacing previous MCP-only approach.

010: Add comment with citation to LangChain Google Community integrations: https colon slash slash python dot langchain dot com slash docs slash integrations slash tools slash google underscore gmail.

011: Add comment with citation to LangChain MCP documentation: https colon slash slash python dot langchain dot com slash docs slash integrations slash tools slash mcp.

012: Add comment explaining that Gmail and Calendar use native LangChain toolkits for better stability and simpler authentication compared to MCP approach.

013: Add comment explaining that Supabase and Tavily use corrected MCP packages: at supabase slash mcp-server-postgrest and at mcptools slash mcp-tavily.

014: Add comment that all initialization functions are async and return list of BaseTool instances for consistent interface with agent compilation.

015: Add comment that graceful degradation is implemented so missing credentials for one toolkit do not prevent other toolkits from initializing successfully.

[defines: init_gmail_toolkit @ src/tools/toolkits.py (planned lines 016-045)]

016: Define async function named init underscore gmail underscore toolkit with no parameters to encapsulate Gmail toolkit initialization logic returning list of BaseTool instances.

017: Add function docstring explaining init underscore gmail underscore toolkit initializes Gmail toolkit with OAuth credentials from GMAIL underscore CREDENTIALS environment variable.

018: Add docstring returns section specifying list of BaseTool instances containing 5 Gmail tools or empty list if credentials missing or initialization fails.

019: Add docstring note that credentials file should be path to OAuth 2.0 credentials JSON file downloaded from Google Cloud Console per LangChain documentation.

020: Add docstring listing the 5 Gmail tools returned: create underscore gmail underscore draft send underscore gmail underscore message search underscore gmail get underscore gmail underscore message get underscore gmail underscore thread.

021: Start try block to wrap all initialization logic ensuring errors caught and empty list returned for graceful degradation rather than crashing agent startup.

022: Read GMAIL underscore CREDENTIALS environment variable using os dot getenv to get path to credentials JSON file for OAuth authentication.

023: Check if credentials underscore path is None or empty string and if so log warning message Gmail credentials not configured skipping Gmail toolkit initialization.

024: If credentials missing return empty list immediately allowing agent to start without Gmail functionality rather than failing completely.

025: Log info message Initializing Gmail toolkit with credentials from credentials underscore path to record initialization attempt for debugging and monitoring.

026: Call GmailToolkit constructor passing credentials underscore file equals credentials underscore path to create toolkit instance with OAuth authentication per official docs.

027: Assign toolkit instance to variable named gmail underscore toolkit for calling get underscore tools method to retrieve tool list.

028: Call gmail underscore toolkit dot get underscore tools method to retrieve list of 5 Gmail tools as BaseTool instances per LangChain toolkit pattern.

029: Assign returned tool list to variable named gmail underscore tools for validation and logging before returning to caller.

030: Log info message Successfully initialized Gmail toolkit with len of gmail underscore tools tools to confirm successful initialization without exposing sensitive credentials.

031: Return gmail underscore tools list to caller agent compilation code which will add these tools to agent's available tools for skills-first workflow.

032: Define except FileNotFoundError as e block to catch missing credentials file error specifically for clearer error messaging to user.

033: In FileNotFoundError except block log error message Gmail credentials file not found at path with exception details for user to locate and fix credentials.

034: Return empty list from FileNotFoundError except to allow graceful degradation continuing agent startup without Gmail functionality.

035: Define except Exception as e block to catch all other errors OAuth flow failures API errors network issues et cetera for comprehensive error handling.

036: In general except block log error message Gmail toolkit initialization failed with exception details using str of e for error message recording.

037: Return empty list from general except to ensure agent can start even if Gmail toolkit fails preventing complete agent failure from single toolkit issue.

038: Add inline comment that graceful degradation allows agent to operate with partial functionality informing user which toolkits are unavailable via logs.

039: Add inline comment that empty list return is preferred over raising exception because agent should be resilient to missing optional integrations.

040: Add inline comment that credentials file path should point to credentials dot json downloaded from Google Cloud Console with Gmail API enabled.

041: Add inline comment that first time initialization may trigger OAuth consent flow requiring user interaction to authorize application.

042: Add inline comment that after initial authorization token dot json created for subsequent automatic authentication per LangChain Google Community package behavior.

043: Close init underscore gmail underscore toolkit function returning list of 5 Gmail tools or empty list with all errors gracefully handled.

044: Add function-level comment explaining that toolkit initialization is expensive so this function should only be called once during agent startup not per request.

045: Add citation comment referencing official LangChain Gmail Toolkit documentation: https colon slash slash python dot langchain dot com slash docs slash integrations slash tools slash google underscore gmail.

[defines: init_calendar_toolkit @ src/tools/toolkits.py (planned lines 046-075)]

046: Define async function named init underscore calendar underscore toolkit with no parameters to encapsulate Calendar toolkit initialization logic returning list of BaseTool instances.

047: Add function docstring explaining init underscore calendar underscore toolkit initializes Calendar toolkit with OAuth credentials from GOOGLE underscore CALENDAR underscore CREDENTIALS environment variable.

048: Add docstring returns section specifying list of BaseTool instances containing 7 Calendar tools or empty list if credentials missing or initialization fails.

049: Add docstring note that credentials file should be path to OAuth 2.0 credentials JSON file downloaded from Google Cloud Console with Calendar API enabled.

050: Add docstring listing the 7 Calendar tools returned: create underscore calendar underscore event search underscore calendar underscore events update underscore calendar underscore event get underscore calendars underscore info move underscore calendar underscore event delete underscore calendar underscore event get underscore current underscore datetime.

051: Start try block to wrap all initialization logic ensuring errors caught and empty list returned for graceful degradation rather than crashing agent startup.

052: Read GOOGLE underscore CALENDAR underscore CREDENTIALS environment variable using os dot getenv to get path to credentials JSON file for OAuth authentication.

053: Check if credentials underscore path is None or empty string and if so log warning message Calendar credentials not configured skipping Calendar toolkit initialization.

054: If credentials missing return empty list immediately allowing agent to start without Calendar functionality rather than failing completely.

055: Log info message Initializing Calendar toolkit with credentials from credentials underscore path to record initialization attempt for debugging and monitoring.

056: Call CalendarToolkit constructor passing credentials underscore file equals credentials underscore path to create toolkit instance with OAuth authentication per official docs.

057: Assign toolkit instance to variable named calendar underscore toolkit for calling get underscore tools method to retrieve tool list.

058: Call calendar underscore toolkit dot get underscore tools method to retrieve list of 7 Calendar tools as BaseTool instances per LangChain toolkit pattern.

059: Assign returned tool list to variable named calendar underscore tools for validation and logging before returning to caller.

060: Log info message Successfully initialized Calendar toolkit with len of calendar underscore tools tools to confirm successful initialization without exposing sensitive credentials.

061: Return calendar underscore tools list to caller agent compilation code which will add these tools to agent's available tools for skills-first workflow.

062: Define except FileNotFoundError as e block to catch missing credentials file error specifically for clearer error messaging to user.

063: In FileNotFoundError except block log error message Calendar credentials file not found at path with exception details for user to locate and fix credentials.

064: Return empty list from FileNotFoundError except to allow graceful degradation continuing agent startup without Calendar functionality.

065: Define except Exception as e block to catch all other errors OAuth flow failures API errors network issues et cetera for comprehensive error handling.

066: In general except block log error message Calendar toolkit initialization failed with exception details using str of e for error message recording.

067: Return empty list from general except to ensure agent can start even if Calendar toolkit fails preventing complete agent failure from single toolkit issue.

068: Add inline comment that Calendar toolkit shares same OAuth credential pattern as Gmail toolkit allowing same credentials file if both APIs enabled in project.

069: Add inline comment that get underscore current underscore datetime tool is particularly useful for legal scheduling and deadline calculations providing timezone-aware datetime.

070: Close init underscore calendar underscore toolkit function returning list of 7 Calendar tools or empty list with all errors gracefully handled.

071: Add function-level comment explaining that toolkit initialization is expensive so this function should only be called once during agent startup not per request.

072: Add citation comment referencing official LangChain Calendar Toolkit documentation: https colon slash slash python dot langchain dot com slash docs slash integrations slash tools slash google underscore calendar.

073: Add inline comment that OAuth flow for Calendar may be separate from Gmail requiring user to authorize Calendar API access specifically.

074: Add inline comment that token dot json created after authorization stores refresh token for automatic reauthentication per Google OAuth 2.0 flow.

075: Close Calendar toolkit initialization function with all OAuth flow and error handling implemented for production readiness.

[defines: init_supabase_mcp @ src/tools/toolkits.py (planned lines 076-110)]

076: Define async function named init underscore supabase underscore mcp with no parameters to encapsulate Supabase MCP client initialization logic returning list of BaseTool instances.

077: Add function docstring explaining init underscore supabase underscore mcp initializes Supabase MCP client with corrected package at supabase slash mcp-server-postgrest replacing previous incorrect package.

078: Add docstring returns section specifying list of BaseTool instances containing Supabase database tools or empty list if credentials missing or MCP server fails to start.

079: Add docstring note that requires SUPABASE underscore URL and SUPABASE underscore SERVICE underscore ROLE underscore KEY environment variables for database connection and RLS bypass.

080: Add docstring warning that MCP server spawned as subprocess using npx command requiring Node.js runtime available in system PATH.

081: Start try block to wrap all initialization logic ensuring errors caught and empty list returned for graceful degradation if MCP server unavailable.

082: Read SUPABASE underscore URL environment variable using os dot getenv to get project URL for database connection string.

083: Read SUPABASE underscore SERVICE underscore ROLE underscore KEY environment variable using os dot getenv to get service role key for RLS bypass per backend requirements.

084: Check if either supabase underscore url or service underscore key is None or empty and if so log warning message Supabase credentials not configured skipping MCP initialization.

085: If credentials missing return empty list immediately allowing agent to start without Supabase functionality rather than failing completely.

086: Log info message Initializing Supabase MCP client with corrected package at supabase slash mcp-server-postgrest to record initialization attempt.

087: Call MCPClient constructor passing server underscore config dict with command equals npx and args equals list containing -y at supabase slash mcp-server-postgrest.

088: In server underscore config dict also pass env equals dict mapping SUPABASE underscore URL to supabase underscore url variable and SUPABASE underscore SERVICE underscore ROLE underscore KEY to service underscore key variable.

089: Assign MCPClient instance to variable named supabase underscore client for calling get underscore tools method to retrieve tool list from spawned MCP server.

090: Add await keyword before supabase underscore client dot get underscore tools call as MCP client initialization is async requiring await per LangChain MCP adapter pattern.

091: Assign returned tool list to variable named supabase underscore tools for validation and logging before returning to caller.

092: Log info message Successfully initialized Supabase MCP with len of supabase underscore tools tools to confirm successful MCP server spawn and tool retrieval.

093: Return supabase underscore tools list to caller agent compilation code which will add these database tools to agent's available tools.

094: Define except FileNotFoundError as e block to catch npx command not found error specifically for clearer error messaging about Node.js requirement.

095: In FileNotFoundError except block log error message npx command not found please install Node.js to use Supabase MCP server with installation instructions.

096: Return empty list from FileNotFoundError except to allow graceful degradation continuing agent startup without Supabase functionality.

097: Define except TimeoutError as e block to catch MCP server startup timeout if server takes too long to initialize or fails to respond.

098: In TimeoutError except block log error message Supabase MCP server initialization timeout with exception details for debugging MCP server issues.

099: Return empty list from TimeoutError except to allow agent startup to continue without waiting indefinitely for unresponsive MCP server.

100: Define except Exception as e block to catch all other errors MCP server crashes API errors network issues et cetera for comprehensive error handling.

101: In general except block log error message Supabase MCP initialization failed with exception details using str of e for error message recording.

102: Return empty list from general except to ensure agent can start even if Supabase MCP fails preventing complete agent failure from single integration issue.

103: Add inline comment that corrected package at supabase slash mcp-server-postgrest verified to exist on npm registry replacing previous non-existent package name.

104: Add inline comment that MCP server runs as long-lived subprocess communicating via JSON-RPC protocol per Model Context Protocol specification.

105: Add inline comment that service role key bypasses Row Level Security policies enabling backend agent to access all case data per architecture requirements.

106: Close init underscore supabase underscore mcp function returning list of Supabase database tools or empty list with all MCP server errors gracefully handled.

107: Add function-level comment explaining that MCP client spawns subprocess so cleanup may be needed on agent shutdown to prevent orphaned processes.

108: Add citation comment referencing corrected Supabase MCP package: https colon slash slash www dot npmjs dot com slash package slash at supabase slash mcp-server-postgrest.

109: Add citation comment referencing LangChain MCP integration documentation: https colon slash slash python dot langchain dot com slash docs slash integrations slash tools slash mcp.

110: Close Supabase MCP initialization function with all subprocess spawning and error handling implemented for production readiness.

[defines: init_tavily_mcp @ src/tools/toolkits.py (planned lines 111-145)]

111: Define async function named init underscore tavily underscore mcp with no parameters to encapsulate Tavily MCP client initialization logic returning list of BaseTool instances.

112: Add function docstring explaining init underscore tavily underscore mcp initializes Tavily MCP client with corrected package at mcptools slash mcp-tavily for web search capabilities.

113: Add docstring returns section specifying list of BaseTool instances containing Tavily search tools or empty list if API key missing or MCP server fails to start.

114: Add docstring note that requires TAVILY underscore API underscore KEY environment variable for authenticating with Tavily search API per service requirements.

115: Add docstring warning that MCP server spawned as subprocess using npx command requiring Node.js runtime available in system PATH.

116: Start try block to wrap all initialization logic ensuring errors caught and empty list returned for graceful degradation if MCP server unavailable.

117: Read TAVILY underscore API underscore KEY environment variable using os dot getenv to get API key for authenticating Tavily search requests.

118: Check if tavily underscore api underscore key is None or empty string and if so log warning message Tavily API key not configured skipping MCP initialization.

119: If API key missing return empty list immediately allowing agent to start without Tavily search functionality rather than failing completely.

120: Log info message Initializing Tavily MCP client with corrected package at mcptools slash mcp-tavily to record initialization attempt.

121: Call MCPClient constructor passing server underscore config dict with command equals npx and args equals list containing -y at mcptools slash mcp-tavily.

122: In server underscore config dict also pass env equals dict mapping TAVILY underscore API underscore KEY to tavily underscore api underscore key variable for MCP server authentication.

123: Assign MCPClient instance to variable named tavily underscore client for calling get underscore tools method to retrieve tool list from spawned MCP server.

124: Add await keyword before tavily underscore client dot get underscore tools call as MCP client initialization is async requiring await per LangChain MCP adapter pattern.

125: Assign returned tool list to variable named tavily underscore tools for validation and logging before returning to caller.

126: Log info message Successfully initialized Tavily MCP with len of tavily underscore tools tools to confirm successful MCP server spawn and tool retrieval.

127: Return tavily underscore tools list to caller agent compilation code which will add these search tools to agent's available tools.

128: Define except FileNotFoundError as e block to catch npx command not found error specifically for clearer error messaging about Node.js requirement.

129: In FileNotFoundError except block log error message npx command not found please install Node.js to use Tavily MCP server with installation instructions.

130: Return empty list from FileNotFoundError except to allow graceful degradation continuing agent startup without Tavily functionality.

131: Define except TimeoutError as e block to catch MCP server startup timeout if server takes too long to initialize or fails to respond.

132: In TimeoutError except block log error message Tavily MCP server initialization timeout with exception details for debugging MCP server issues.

133: Return empty list from TimeoutError except to allow agent startup to continue without waiting indefinitely for unresponsive MCP server.

134: Define except Exception as e block to catch all other errors MCP server crashes API errors network issues invalid API key et cetera for comprehensive error handling.

135: In general except block log error message Tavily MCP initialization failed with exception details using str of e for error message recording.

136: Return empty list from general except to ensure agent can start even if Tavily MCP fails preventing complete agent failure from single integration issue.

137: Add inline comment that corrected package at mcptools slash mcp-tavily verified to exist on npm registry replacing previous non-existent package name.

138: Add inline comment that Tavily provides AI-optimized search specifically designed for LLM applications with relevance ranking and answer extraction.

139: Add inline comment that MCP server communicates with Tavily API on behalf of agent avoiding need for Python SDK dependency simplifying architecture.

140: Close init underscore tavily underscore mcp function returning list of Tavily search tools or empty list with all MCP server errors gracefully handled.

141: Add function-level comment explaining that MCP client spawns subprocess so cleanup may be needed on agent shutdown to prevent orphaned processes.

142: Add citation comment referencing corrected Tavily MCP package: https colon slash slash www dot npmjs dot com slash package slash at mcptools slash mcp-tavily.

143: Add citation comment referencing Tavily Search API documentation: https colon slash slash tavily dot com slash docs.

144: Add inline comment that Tavily MCP particularly useful for legal research enabling agent to search case law statutes and legal databases with AI-enhanced relevance.

145: Close Tavily MCP initialization function with all subprocess spawning and error handling implemented for production readiness.

---

## Cross-References

**Imports:**
- [uses: GmailToolkit @ langchain_google_community (external package)]
- [uses: CalendarToolkit @ langchain_google_community (external package)]
- [uses: MCPClient @ langchain_mcp_adapters (external package)]
- [uses: BaseTool @ langchain_core.tools (external package)]
- [uses: os @ Python stdlib]
- [uses: logging @ Python stdlib]
- [uses: typing.Optional, typing.List @ Python stdlib]

**Exports:**
- [defines: init_gmail_toolkit @ src/tools/toolkits.py (planned lines 016-045)]
- [defines: init_calendar_toolkit @ src/tools/toolkits.py (planned lines 046-075)]
- [defines: init_supabase_mcp @ src/tools/toolkits.py (planned lines 076-110)]
- [defines: init_tavily_mcp @ src/tools/toolkits.py (planned lines 111-145)]

**Used by:**
- [used_by: src/agents/legal_agent.py @ tools initialization (planned lines 180-195)]

**References:**
- [uses: GMAIL_CREDENTIALS @ environment variable]
- [uses: GOOGLE_CALENDAR_CREDENTIALS @ environment variable]
- [uses: SUPABASE_URL @ environment variable]
- [uses: SUPABASE_SERVICE_ROLE_KEY @ environment variable]
- [uses: TAVILY_API_KEY @ environment variable]

---

## Notes & Assumptions

- **Gmail/Calendar Toolkits**: Uses native LangChain toolkits per user instruction, simpler than MCP approach
- **OAuth Flow**: First-time initialization may require user interaction for consent, subsequent runs use token.json
- **Credentials Format**: Changed from JSON string (MCP) to file path (native toolkits)
- **MCP Packages**: Corrected package names verified on npm registry
  - Supabase: `@supabase/mcp-server-postgrest`
  - Tavily: `@mcptools/mcp-tavily`
- **Graceful Degradation**: Each toolkit can fail independently without crashing agent startup
- **Async Pattern**: All functions are async, MCP `get_tools()` requires await
- **Logging**: Info for successes, warning for missing credentials, error for failures
- **Tool Counts**: Gmail (5 tools), Calendar (7 tools), Supabase (variable), Tavily (variable)
- **Node.js Requirement**: MCP servers require npx command available in PATH
- **Subprocess Management**: MCP clients spawn subprocesses that may need cleanup on shutdown
- **Service Role Key**: Supabase uses service role key to bypass RLS for backend agent operations
- **Error Returns**: Always return empty list on error, never raise exceptions to caller
- **Initialization Cost**: All functions expensive, should only run once at agent startup
- **Testing**: Should have unit tests mocking toolkit constructors, integration tests with real credentials
- **Security**: Credentials loaded from environment, never hardcoded or logged
- **Future Enhancements**: Could add retry logic, connection pooling, health checks

---

## Validation

- [x] All imports from official LangChain packages
- [x] No circular dependencies
- [x] Async/await pattern for all MCP operations
- [x] Graceful degradation for missing credentials
- [x] Error handling for all toolkit initialization
- [x] Logging for all operations
- [x] Type hints for all parameters and returns
- [x] Docstrings for all functions
- [x] Tool counts documented in symbol index
- [x] Corrected MCP package names verified

**Citations:**
- **LangChain Gmail Toolkit**: https://python.langchain.com/docs/integrations/tools/google_gmail
- **LangChain Calendar Toolkit**: https://python.langchain.com/docs/integrations/tools/google_calendar
- **LangChain MCP Integration**: https://python.langchain.com/docs/integrations/tools/mcp
- **Supabase MCP Package**: https://www.npmjs.com/package/@supabase/mcp-server-postgrest
- **Tavily MCP Package**: https://www.npmjs.com/package/@mcptools/mcp-tavily
- **Tavily API Documentation**: https://tavily.com/docs

---

**Status**: ✅ Plan Complete - Ready for validation
**Estimated LOC**: ~150 lines
**Next**: Create legal_agent-UPDATES.nlplan.md
