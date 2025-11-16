# Natural Language Plan: src/mcp/clients.py

## File Purpose

This file initializes and configures all MCP (Model Context Protocol) server clients that provide external tools to the agent. It creates MultiServerMCPClient instances for Supabase, Tavily, Gmail, and Google Calendar, extracts tool lists from each server, and exports those tools for use by the main agent.

This file participates as a dependency for `src/agents/legal_agent.py` which imports the tool lists to configure the DeepAgent with external capabilities.

## Imports We Will Need (and Why)

001: Import MultiServerMCPClient from langchain_mcp_adapters to create MCP client instances that communicate with MCP servers via JSON-RPC protocol.

002: Import os module to access environment variables for API keys and credentials needed by MCP servers.

003: Import get_setting from src.config.settings to safely retrieve optional configuration values with defaults [uses: get_setting @ src/config/settings.py (planned line 011)].

004: Import logging module to log MCP server initialization success or failures for debugging and monitoring.

## Objects We Will Define

### Function: `init_supabase_mcp() -> list`
**Purpose**: Initialize Supabase MCP client and return list of database tools
**Inputs**: None (reads from environment)
**Outputs**: List of Supabase MCP tools or empty list if initialization fails
**Side effects**: Spawns npx process for Supabase MCP server

### Function: `init_tavily_mcp() -> list`
**Purpose**: Initialize Tavily MCP client and return list of web search tools
**Inputs**: None (reads from environment)
**Outputs**: List of Tavily MCP tools or empty list if initialization fails
**Side effects**: Spawns npx process for Tavily MCP server

### Function: `init_gmail_mcp() -> list`
**Purpose**: Initialize Gmail MCP client and return list of email tools
**Inputs**: None (reads from environment)
**Outputs**: List of Gmail MCP tools or empty list if initialization fails
**Side effects**: Spawns npx process for Gmail MCP server

### Function: `init_calendar_mcp() -> list`
**Purpose**: Initialize Google Calendar MCP client and return list of scheduling tools
**Inputs**: None (reads from environment)
**Outputs**: List of Calendar MCP tools or empty list if initialization fails
**Side effects**: Spawns npx process for Calendar MCP server

### Constant: `supabase_tools`
**Purpose**: List of Supabase database tools for agent use
**Type**: list
**Initialization**: Result of init_supabase_mcp()

### Constant: `tavily_tools`
**Purpose**: List of Tavily web search tools for agent use
**Type**: list
**Initialization**: Result of init_tavily_mcp()

### Constant: `gmail_tools`
**Purpose**: List of Gmail email tools for agent use
**Type**: list
**Initialization**: Result of init_gmail_mcp()

### Constant: `calendar_tools`
**Purpose**: List of Google Calendar scheduling tools for agent use
**Type**: list
**Initialization**: Result of init_calendar_mcp()

## Line-by-Line Natural Language Plan

[defines: imports @ src/mcp/clients.py (planned lines 001-004)]
001: Import MultiServerMCPClient class from langchain_mcp_adapters module to create MCP client instances for communication with MCP servers.

002: Import os module from standard library to access environment variables for API keys and credentials.

003: Import get_setting function from src.config.settings module for safe environment variable access with defaults [uses: get_setting @ src/config/settings.py (planned line 011)].

004: Import logging module to create logger instance for recording MCP initialization events and errors.

[defines: logger @ src/mcp/clients.py (planned lines 005-006)]
005: Get logger instance by calling logging.getLogger with __name__ for this module's namespace.

006: Assign logger instance to module-level constant named logger for use in initialization functions.

[defines: init_supabase_mcp @ src/mcp/clients.py (planned lines 007-030)]
007: Define function init_supabase_mcp with no parameters and list return type for Supabase MCP tool initialization.

008: Inside function wrap initialization in try-except block to handle connection failures gracefully.

009: Retrieve SUPABASE_URL from environment using get_setting with None default [uses: get_setting @ src/config/settings.py (planned line 011)].

010: Retrieve SUPABASE_SERVICE_ROLE_KEY from environment using get_setting with None default.

011: Check if either SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is None indicating incomplete configuration.

012: If credentials missing log warning message stating Supabase MCP unavailable and return empty list for graceful degradation.

013: If credentials present create dictionary for Supabase MCP server configuration.

014: Set command key to "npx" as MCP servers run via npx command from npm registry.

015: Set args key to list containing "-y" flag and "@modelcontextprotocol/server-supabase" package name.

016: Set env key to dictionary containing SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables.

017: Create MultiServerMCPClient instance with dictionary mapping "supabase" key to server configuration dictionary.

018: Assign MultiServerMCPClient instance to variable named supabase_mcp.

019: Call list_tools method on supabase_mcp to retrieve list of available database tools.

020: Assign tool list to variable named tools.

021: Log info message with count of tools retrieved and "Supabase MCP initialized successfully" message.

022: Return tools list to caller.

023: In except block catch Exception to handle any initialization errors.

024: Log error message with exception details stating "Failed to initialize Supabase MCP" with error info.

025: Return empty list in except block to enable graceful degradation without crashing agent.

026: Add docstring explaining function initializes Supabase MCP client and returns database tools or empty list on failure.

027: Add docstring note that function implements graceful degradation per architecture error handling strategy.

028: Add docstring example showing expected tool names like "supabase_query" "supabase_insert" "supabase_update".

029: Add inline comment that npx -y flag automatically answers yes to install prompt for MCP server package.

030: Add inline comment that service role key bypasses Row Level Security for backend operations per architecture requirements.

[defines: init_tavily_mcp @ src/mcp/clients.py (planned lines 031-050)]
031: Define function init_tavily_mcp with no parameters and list return type for Tavily MCP tool initialization.

032: Inside function wrap initialization in try-except block to handle connection failures gracefully.

033: Retrieve TAVILY_API_KEY from environment using get_setting with None default [uses: get_setting @ src/config/settings.py (planned line 011)].

034: Check if TAVILY_API_KEY is None indicating missing configuration.

035: If API key missing log warning message stating Tavily MCP unavailable and return empty list for graceful degradation.

036: If API key present create dictionary for Tavily MCP server configuration.

037: Set command key to "npx" as MCP servers run via npx command.

038: Set args key to list containing "-y" flag and "@modelcontextprotocol/server-tavily" package name.

039: Set env key to dictionary containing TAVILY_API_KEY environment variable.

040: Create MultiServerMCPClient instance with dictionary mapping "tavily" key to server configuration.

041: Call list_tools method to retrieve list of available web search tools.

042: Assign tool list to variable named tools.

043: Log info message with count of tools and "Tavily MCP initialized successfully" message.

044: Return tools list to caller.

045: In except block catch Exception for any initialization errors.

046: Log error message with exception details stating "Failed to initialize Tavily MCP".

047: Return empty list in except block for graceful degradation.

048: Add docstring explaining function initializes Tavily MCP for web search and returns tools or empty list.

049: Add docstring note that Tavily used for legal research case law and statute searching.

050: Add inline comment that Tavily provides high-quality web search optimized for factual retrieval.

[defines: init_gmail_mcp @ src/mcp/clients.py (planned lines 051-070)]
051: Define function init_gmail_mcp with no parameters and list return type for Gmail MCP tool initialization.

052: Inside function wrap initialization in try-except block to handle connection failures gracefully.

053: Retrieve GMAIL_CREDENTIALS from environment using get_setting with None default [uses: get_setting @ src/config/settings.py (planned line 011)].

054: Check if GMAIL_CREDENTIALS is None indicating missing configuration.

055: If credentials missing log warning message stating Gmail MCP unavailable and return empty list as Gmail optional for MVP.

056: If credentials present create dictionary for Gmail MCP server configuration.

057: Set command key to "npx" as MCP servers run via npx.

058: Set args key to list containing "-y" and "@modelcontextprotocol/server-gmail" package name.

059: Set env key to dictionary containing GMAIL_CREDENTIALS environment variable with OAuth credentials JSON.

060: Create MultiServerMCPClient instance with dictionary mapping "gmail" key to server configuration.

061: Call list_tools method to retrieve list of available email tools.

062: Assign tool list to variable named tools.

063: Log info message with count of tools and "Gmail MCP initialized successfully" message.

064: Return tools list to caller.

065: In except block catch Exception for initialization errors.

066: Log error message with exception details stating "Failed to initialize Gmail MCP".

067: Return empty list in except block for graceful degradation as Gmail is optional service.

068: Add docstring explaining function initializes Gmail MCP for email operations returning tools or empty list.

069: Add docstring note that Gmail credentials are OAuth JSON requiring user consent for email access.

070: Add inline comment that Gmail is optional for MVP per architecture allowing agent to function without email capability.

[defines: init_calendar_mcp @ src/mcp/clients.py (planned lines 071-090)]
071: Define function init_calendar_mcp with no parameters and list return type for Calendar MCP tool initialization.

072: Inside function wrap initialization in try-except block to handle connection failures gracefully.

073: Retrieve GOOGLE_CALENDAR_CREDENTIALS from environment using get_setting with None default [uses: get_setting @ src/config/settings.py (planned line 011)].

074: Check if GOOGLE_CALENDAR_CREDENTIALS is None indicating missing configuration.

075: If credentials missing log warning message stating Calendar MCP unavailable and return empty list as Calendar optional for MVP.

076: If credentials present create dictionary for Calendar MCP server configuration.

077: Set command key to "npx" as MCP servers run via npx.

078: Set args key to list containing "-y" and "@modelcontextprotocol/server-google-calendar" package name.

079: Set env key to dictionary containing GOOGLE_CALENDAR_CREDENTIALS environment variable with OAuth credentials JSON.

080: Create MultiServerMCPClient instance with dictionary mapping "calendar" key to server configuration.

081: Call list_tools method to retrieve list of available scheduling tools.

082: Assign tool list to variable named tools.

083: Log info message with count of tools and "Google Calendar MCP initialized successfully" message.

084: Return tools list to caller.

085: In except block catch Exception for initialization errors.

086: Log error message with exception details stating "Failed to initialize Calendar MCP".

087: Return empty list in except block for graceful degradation as Calendar is optional service.

088: Add docstring explaining function initializes Calendar MCP for scheduling returning tools or empty list.

089: Add docstring note that Calendar credentials are OAuth JSON requiring user consent for calendar access.

090: Add inline comment that Calendar is optional for MVP per architecture allowing agent to function without scheduling capability.

[defines: module_initialization @ src/mcp/clients.py (planned lines 091-110)]
091: Log info message stating "Initializing MCP clients..." before calling initialization functions.

092: Call init_supabase_mcp function and assign result to module-level constant supabase_tools [defines: supabase_tools @ src/mcp/clients.py (planned line 092)].

093: Call init_tavily_mcp function and assign result to module-level constant tavily_tools [defines: tavily_tools @ src/mcp/clients.py (planned line 093)].

094: Call init_gmail_mcp function and assign result to module-level constant gmail_tools [defines: gmail_tools @ src/mcp/clients.py (planned line 094)].

095: Call init_calendar_mcp function and assign result to module-level constant calendar_tools [defines: calendar_tools @ src/mcp/clients.py (planned line 095)].

096: Log info message with total count of tools across all MCP servers for summary.

097: Calculate total by adding lengths of supabase_tools tavily_tools gmail_tools calendar_tools lists.

098: Include in log message which MCP servers successfully initialized versus failed or unavailable.

099: Add comment that module initialization happens at import time so errors appear early in startup.

100: Add comment that graceful degradation allows agent to function with subset of MCP servers if some unavailable.

101: Add comment that empty tool lists will not break agent configuration in legal_agent.py.

102: Add comment that Supabase and Tavily considered critical for MVP while Gmail and Calendar optional.

103: Add comment that Node.js and npm must be installed on system for npx command to work.

104: Add comment that MCP servers run as child processes managed by langchain_mcp_adapters library.

105: Add comment that MCP protocol uses JSON-RPC for communication between agent and servers.

106: Add comment that MultiServerMCPClient handles connection lifecycle automatically.

107: Add comment that tools returned are LangChain Tool objects ready for agent use.

108: Add comment that tool names and schemas defined by MCP server implementations not this code.

109: Add comment that MCP servers can be tested independently using npx command before agent integration.

110: Add comment with example: npx @modelcontextprotocol/server-supabase to test Supabase MCP server manually.

## Cross-References

[uses: get_setting @ src/config/settings.py (planned line 011)]

[defines: init_supabase_mcp @ src/mcp/clients.py (planned lines 007-030)]
[defines: init_tavily_mcp @ src/mcp/clients.py (planned lines 031-050)]
[defines: init_gmail_mcp @ src/mcp/clients.py (planned lines 051-070)]
[defines: init_calendar_mcp @ src/mcp/clients.py (planned lines 071-090)]
[defines: supabase_tools @ src/mcp/clients.py (planned line 092)]
[defines: tavily_tools @ src/mcp/clients.py (planned line 093)]
[defines: gmail_tools @ src/mcp/clients.py (planned line 094)]
[defines: calendar_tools @ src/mcp/clients.py (planned line 095)]

## Notes & Assumptions

- Assumes Node.js and npm installed on system for npx command execution
- Assumes MCP server packages available on npm registry with @modelcontextprotocol scope
- Assumes environment variables set in .env file loaded by src/config/settings.py
- All MCP initialization wrapped in try-except for graceful degradation per architecture
- Supabase and Tavily considered critical, Gmail and Calendar optional for MVP
- Empty tool lists safe to pass to create_deep_agent (agent will function without those capabilities)
- MCP servers run as child processes spawned by MultiServerMCPClient
- MCP protocol is JSON-RPC based, handled transparently by langchain_mcp_adapters
- Tool schemas and names defined by MCP server implementations, not modifiable here
- Module initialization happens at import time for fail-fast behavior
- Logging provides visibility into which MCP servers successfully initialized
- File has no external file dependencies beyond environment variables
- Each MCP server independent, failure of one does not affect others
- Function design allows testing each MCP server independently
