"""
This file provides async initialization functions for all external tool integrations
used by the legal agent. It replaces the previous src/mcp/clients.py approach by using
native LangChain toolkits for Gmail and Calendar (simpler, better maintained) while
using corrected MCP packages for Supabase and Tavily.

This file participates as the primary tool provider for the agent's skills-first
workflow, enabling email management, calendar scheduling, database operations, and
web search capabilities.

Citations:
- LangChain Google Community integrations: https://python.langchain.com/docs/integrations/tools/google_gmail
- LangChain MCP documentation: https://python.langchain.com/docs/integrations/tools/mcp
"""

import os
import logging
from typing import Optional, List

from langchain_google_community import GmailToolkit
from langchain_google_community import CalendarToolkit
from langchain_mcp_adapters import MCPClient
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

# Gmail and Calendar use native LangChain toolkits for better stability and
# simpler authentication compared to MCP approach.
# Supabase and Tavily use corrected MCP packages: @supabase/mcp-server-postgrest
# and @mcptools/mcp-tavily.
# All initialization functions are async and return list of BaseTool instances
# for consistent interface with agent compilation.
# Graceful degradation is implemented so missing credentials for one toolkit
# do not prevent other toolkits from initializing successfully.


async def init_gmail_toolkit() -> List[BaseTool]:
    """
    Initialize Gmail toolkit with OAuth credentials from GMAIL_CREDENTIALS environment variable.

    Returns:
        list[BaseTool]: List containing 5 Gmail tools (create_gmail_draft, send_gmail_message,
        search_gmail, get_gmail_message, get_gmail_thread) or empty list if credentials
        missing or initialization fails.

    Note:
        Credentials file should be path to OAuth 2.0 credentials JSON file downloaded from
        Google Cloud Console per LangChain documentation.

    Citation: https://python.langchain.com/docs/integrations/tools/google_gmail
    """
    try:
        # Read GMAIL_CREDENTIALS environment variable to get path to credentials JSON file
        # for OAuth authentication
        credentials_path = os.getenv("GMAIL_CREDENTIALS")

        # Check if credentials missing and log warning, return empty list for graceful degradation
        if not credentials_path:
            logger.warning("Gmail credentials not configured, skipping Gmail toolkit initialization")
            return []

        # Log initialization attempt for debugging and monitoring
        logger.info(f"Initializing Gmail toolkit with credentials from {credentials_path}")

        # Create toolkit instance with OAuth authentication per official docs
        gmail_toolkit = GmailToolkit(credentials_file=credentials_path)

        # Retrieve list of 5 Gmail tools as BaseTool instances per LangChain toolkit pattern
        gmail_tools = gmail_toolkit.get_tools()

        # Confirm successful initialization without exposing sensitive credentials
        logger.info(f"Successfully initialized Gmail toolkit with {len(gmail_tools)} tools")

        # Return tools to caller agent compilation code which will add these to agent's available tools
        return gmail_tools

    except FileNotFoundError as e:
        # Catch missing credentials file error for clearer error messaging
        logger.error(f"Gmail credentials file not found at path: {e}")
        return []  # Graceful degradation: continue agent startup without Gmail functionality

    except Exception as e:
        # Catch all other errors: OAuth flow failures, API errors, network issues, etc.
        logger.error(f"Gmail toolkit initialization failed: {str(e)}")
        return []  # Empty list is preferred over raising exception for agent resilience

    # Credentials file path should point to credentials.json downloaded from Google Cloud Console
    # with Gmail API enabled.
    # First time initialization may trigger OAuth consent flow requiring user interaction to
    # authorize application.
    # After initial authorization, token.json created for subsequent automatic authentication
    # per LangChain Google Community package behavior.
    # Toolkit initialization is expensive so this function should only be called once during
    # agent startup not per request.


async def init_calendar_toolkit() -> List[BaseTool]:
    """
    Initialize Calendar toolkit with OAuth credentials from GOOGLE_CALENDAR_CREDENTIALS environment variable.

    Returns:
        list[BaseTool]: List containing 7 Calendar tools (create_calendar_event, search_calendar_events,
        update_calendar_event, get_calendars_info, move_calendar_event, delete_calendar_event,
        get_current_datetime) or empty list if credentials missing or initialization fails.

    Note:
        Credentials file should be path to OAuth 2.0 credentials JSON file downloaded from
        Google Cloud Console with Calendar API enabled.

    Citation: https://python.langchain.com/docs/integrations/tools/google_calendar
    """
    try:
        # Read GOOGLE_CALENDAR_CREDENTIALS environment variable to get path to credentials JSON file
        # for OAuth authentication
        credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")

        # Check if credentials missing and log warning, return empty list for graceful degradation
        if not credentials_path:
            logger.warning("Calendar credentials not configured, skipping Calendar toolkit initialization")
            return []

        # Log initialization attempt for debugging and monitoring
        logger.info(f"Initializing Calendar toolkit with credentials from {credentials_path}")

        # Create toolkit instance with OAuth authentication per official docs
        calendar_toolkit = CalendarToolkit(credentials_file=credentials_path)

        # Retrieve list of 7 Calendar tools as BaseTool instances per LangChain toolkit pattern
        calendar_tools = calendar_toolkit.get_tools()

        # Confirm successful initialization without exposing sensitive credentials
        logger.info(f"Successfully initialized Calendar toolkit with {len(calendar_tools)} tools")

        # Return tools to caller agent compilation code which will add these to agent's available tools
        return calendar_tools

    except FileNotFoundError as e:
        # Catch missing credentials file error for clearer error messaging
        logger.error(f"Calendar credentials file not found at path: {e}")
        return []  # Graceful degradation: continue agent startup without Calendar functionality

    except Exception as e:
        # Catch all other errors: OAuth flow failures, API errors, network issues, etc.
        logger.error(f"Calendar toolkit initialization failed: {str(e)}")
        return []  # Empty list ensures agent can start even if Calendar toolkit fails

    # Calendar toolkit shares same OAuth credential pattern as Gmail toolkit allowing same
    # credentials file if both APIs enabled in project.
    # get_current_datetime tool is particularly useful for legal scheduling and deadline
    # calculations providing timezone-aware datetime.
    # OAuth flow for Calendar may be separate from Gmail requiring user to authorize Calendar
    # API access specifically.
    # token.json created after authorization stores refresh token for automatic reauthentication
    # per Google OAuth 2.0 flow.
    # Toolkit initialization is expensive so this function should only be called once during
    # agent startup not per request.


async def init_supabase_mcp() -> List[BaseTool]:
    """
    Initialize Supabase MCP client with corrected package @supabase/mcp-server-postgrest
    replacing previous incorrect package.

    Returns:
        list[BaseTool]: List containing Supabase database tools or empty list if credentials
        missing or MCP server fails to start.

    Note:
        Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables for
        database connection and RLS bypass.

    Warning:
        MCP server spawned as subprocess using npx command requiring Node.js runtime
        available in system PATH.

    Citations:
        - Package: https://www.npmjs.com/package/@supabase/mcp-server-postgrest
        - LangChain MCP: https://python.langchain.com/docs/integrations/tools/mcp
    """
    try:
        # Read SUPABASE_URL environment variable to get project URL for database connection
        supabase_url = os.getenv("SUPABASE_URL")

        # Read SUPABASE_SERVICE_ROLE_KEY environment variable for RLS bypass per backend requirements
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        # Check if either credential missing and log warning, return empty list for graceful degradation
        if not supabase_url or not service_key:
            logger.warning("Supabase credentials not configured, skipping MCP initialization")
            return []

        # Log initialization attempt with corrected package name
        logger.info("Initializing Supabase MCP client with corrected package @supabase/mcp-server-postgrest")

        # Create MCP client with corrected package and environment variables
        # Corrected package @supabase/mcp-server-postgrest verified to exist on npm registry
        supabase_client = MCPClient(
            server_config={
                "command": "npx",
                "args": ["-y", "@supabase/mcp-server-postgrest"],
                "env": {
                    "SUPABASE_URL": supabase_url,
                    "SUPABASE_SERVICE_ROLE_KEY": service_key
                }
            }
        )

        # MCP client initialization is async requiring await per LangChain MCP adapter pattern
        supabase_tools = await supabase_client.get_tools()

        # Confirm successful MCP server spawn and tool retrieval
        logger.info(f"Successfully initialized Supabase MCP with {len(supabase_tools)} tools")

        # Return database tools to caller agent compilation code
        return supabase_tools

    except FileNotFoundError as e:
        # Catch npx command not found error for clearer error messaging
        logger.error(f"npx command not found, please install Node.js to use Supabase MCP server: {e}")
        return []  # Graceful degradation: continue agent startup without Supabase functionality

    except TimeoutError as e:
        # Catch MCP server startup timeout if server takes too long or fails to respond
        logger.error(f"Supabase MCP server initialization timeout: {e}")
        return []  # Continue agent startup without waiting indefinitely

    except Exception as e:
        # Catch all other errors: MCP server crashes, API errors, network issues, etc.
        logger.error(f"Supabase MCP initialization failed: {str(e)}")
        return []  # Prevent complete agent failure from single integration issue

    # MCP server runs as long-lived subprocess communicating via JSON-RPC protocol per
    # Model Context Protocol specification.
    # Service role key bypasses Row Level Security policies enabling backend agent to access
    # all case data per architecture requirements.
    # MCP client spawns subprocess so cleanup may be needed on agent shutdown to prevent
    # orphaned processes.


async def init_tavily_mcp() -> List[BaseTool]:
    """
    Initialize Tavily MCP client with corrected package @mcptools/mcp-tavily for
    web search capabilities.

    Returns:
        list[BaseTool]: List containing Tavily search tools or empty list if API key
        missing or MCP server fails to start.

    Note:
        Requires TAVILY_API_KEY environment variable for authenticating with Tavily
        search API per service requirements.

    Warning:
        MCP server spawned as subprocess using npx command requiring Node.js runtime
        available in system PATH.

    Citations:
        - Package: https://www.npmjs.com/package/@mcptools/mcp-tavily
        - Tavily API: https://tavily.com/docs
    """
    try:
        # Read TAVILY_API_KEY environment variable to get API key for authenticating search requests
        tavily_api_key = os.getenv("TAVILY_API_KEY")

        # Check if API key missing and log warning, return empty list for graceful degradation
        if not tavily_api_key:
            logger.warning("Tavily API key not configured, skipping MCP initialization")
            return []

        # Log initialization attempt with corrected package name
        logger.info("Initializing Tavily MCP client with corrected package @mcptools/mcp-tavily")

        # Create MCP client with corrected package and API key environment variable
        # Corrected package @mcptools/mcp-tavily verified to exist on npm registry
        tavily_client = MCPClient(
            server_config={
                "command": "npx",
                "args": ["-y", "@mcptools/mcp-tavily"],
                "env": {
                    "TAVILY_API_KEY": tavily_api_key
                }
            }
        )

        # MCP client initialization is async requiring await per LangChain MCP adapter pattern
        tavily_tools = await tavily_client.get_tools()

        # Confirm successful MCP server spawn and tool retrieval
        logger.info(f"Successfully initialized Tavily MCP with {len(tavily_tools)} tools")

        # Return search tools to caller agent compilation code
        return tavily_tools

    except FileNotFoundError as e:
        # Catch npx command not found error for clearer error messaging
        logger.error(f"npx command not found, please install Node.js to use Tavily MCP server: {e}")
        return []  # Graceful degradation: continue agent startup without Tavily functionality

    except TimeoutError as e:
        # Catch MCP server startup timeout if server takes too long or fails to respond
        logger.error(f"Tavily MCP server initialization timeout: {e}")
        return []  # Continue agent startup without waiting indefinitely

    except Exception as e:
        # Catch all other errors: MCP server crashes, API errors, invalid API key, etc.
        logger.error(f"Tavily MCP initialization failed: {str(e)}")
        return []  # Prevent complete agent failure from single integration issue

    # Tavily provides AI-optimized search specifically designed for LLM applications with
    # relevance ranking and answer extraction.
    # MCP server communicates with Tavily API on behalf of agent avoiding need for Python SDK
    # dependency simplifying architecture.
    # Tavily MCP particularly useful for legal research enabling agent to search case law
    # statutes and legal databases with AI-enhanced relevance.
    # MCP client spawns subprocess so cleanup may be needed on agent shutdown to prevent
    # orphaned processes.
