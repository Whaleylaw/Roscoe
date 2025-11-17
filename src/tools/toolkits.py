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
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool, StructuredTool

logger = logging.getLogger(__name__)


def fix_mcp_tool_signature(tool: BaseTool) -> BaseTool:
    """
    Fix MCP tool signature to prevent 'got multiple values for argument self' error.

    MCP tools sometimes have incorrect signatures where self is included as a parameter.
    This fixes the issue by:
    1. Removing 'self' from args_schema (prevents LangChain from passing it)
    2. Monkey-patching _run/_arun to filter 'self' from kwargs (safety net)

    Args:
        tool: The MCP tool to fix

    Returns:
        BaseTool: The fixed tool with correct signature
    """
    # If tool is not a StructuredTool, return as-is
    if not isinstance(tool, StructuredTool):
        logger.debug(f"Tool {tool.name} is not a StructuredTool, skipping fix")
        return tool

    logger.info(f"Applying signature fix to tool: {tool.name}")

    # Store the original _run method
    original_run = tool._run
    original_arun = tool._arun if hasattr(tool, '_arun') else None

    # CRITICAL DEBUGGING: Inspect the _run method signature directly
    import inspect
    logger.error(f"🔍 Tool {tool.name} - Inspecting _run method:")
    logger.error(f"  - original_run type: {type(original_run)}")
    logger.error(f"  - is bound method: {hasattr(original_run, '__self__')}")

    try:
        run_sig = inspect.signature(original_run)
        logger.error(f"  - _run signature: {run_sig}")
        logger.error(f"  - _run parameters: {list(run_sig.parameters.keys())}")
        logger.error(f"  - 'self' in _run signature: {'self' in run_sig.parameters}")
    except Exception as e:
        logger.error(f"  - Could not get _run signature: {e}")

    # CRITICAL DEBUGGING: Inspect the actual function signature
    logger.warning(f"Tool {tool.name} - hasattr(tool, 'func'): {hasattr(tool, 'func')}")
    if hasattr(tool, 'func'):
        logger.warning(f"Tool {tool.name} - tool.func: {tool.func}")
        logger.warning(f"Tool {tool.name} - func type: {type(tool.func)}")
        if tool.func:
            try:
                sig = inspect.signature(tool.func)
                logger.warning(f"Tool {tool.name} - func signature: {sig}")
                logger.warning(f"Tool {tool.name} - func parameters: {list(sig.parameters.keys())}")
            except Exception as e:
                logger.warning(f"Tool {tool.name} - Could not get func signature: {e}")
        else:
            logger.warning(f"Tool {tool.name} - func is None/False")
    else:
        logger.warning(f"Tool {tool.name} - NO func attribute")

    # FIX 1: Remove 'self' from args_schema if present
    # This prevents LangChain from trying to pass 'self' in the first place
    # CRITICAL DISCOVERY: MCP tools use JSON Schema (dict), not Pydantic models
    if hasattr(tool, 'args_schema') and tool.args_schema:
        logger.warning(f"Tool {tool.name} - HAS args_schema type: {type(tool.args_schema)}")

        # Handle JSON Schema (dict) - this is what MCP tools actually use!
        if isinstance(tool.args_schema, dict):
            logger.warning(f"Tool {tool.name} - Schema is JSON Schema (dict)")
            properties = tool.args_schema.get('properties', {})
            logger.warning(f"Tool {tool.name} - Properties: {list(properties.keys())}")

            if 'self' in properties:
                logger.error(f"Tool {tool.name} - 'self' found in JSON Schema properties, removing it!")

                # Create a copy of the schema without 'self'
                import copy
                new_schema = copy.deepcopy(tool.args_schema)
                del new_schema['properties']['self']

                # Also remove from required list if present
                if 'required' in new_schema and 'self' in new_schema['required']:
                    new_schema['required'].remove('self')

                tool.args_schema = new_schema
                logger.error(f"Tool {tool.name} - Successfully removed 'self' from JSON Schema")
            else:
                logger.info(f"Tool {tool.name} - No 'self' in JSON Schema properties (good!)")

        # Handle Pydantic models (for completeness)
        else:
            fields_dict = getattr(tool.args_schema, 'model_fields', None) or getattr(tool.args_schema, '__fields__', None)
            if fields_dict:
                logger.warning(f"Tool {tool.name} - Schema is Pydantic model")
                logger.warning(f"Tool {tool.name} - Pydantic fields: {list(fields_dict.keys())}")

                if 'self' in fields_dict:
                    logger.error(f"Tool {tool.name} - 'self' found in Pydantic schema, removing it")

                    # Create new schema without 'self' field
                    from pydantic import create_model

                    # Build new fields dict excluding 'self'
                    new_fields = {}
                    for name, field in fields_dict.items():
                        if name != 'self':
                            # Get field type and default
                            field_type = field.annotation if hasattr(field, 'annotation') else field.outer_type_
                            field_default = field.default if hasattr(field, 'default') else ...
                            new_fields[name] = (field_type, field_default)

                    # Create new schema model
                    if new_fields:
                        new_schema = create_model(
                            f"{tool.args_schema.__name__}_Fixed",
                            **new_fields
                        )
                        tool.args_schema = new_schema
                        logger.error(f"Tool {tool.name} - Successfully removed 'self' from Pydantic schema")
                    else:
                        # If no fields left after removing 'self', set schema to None
                        tool.args_schema = None
                        logger.error(f"Tool {tool.name} - Set args_schema to None (only had 'self' field)")
                else:
                    logger.info(f"Tool {tool.name} - No 'self' in Pydantic schema (good!)")

    # FIX 2: Monkey-patch _run and _arun as a safety net
    # Even though we removed 'self' from args_schema, we still patch the methods
    # in case 'self' gets passed through other code paths
    def patched_run(*args, **kwargs):
        """Patched _run that removes 'self' from kwargs."""
        logger.info(f"🔧 PATCHED_RUN called for {tool.name}")
        logger.debug(f"  - Received args: {args}")
        logger.debug(f"  - Received kwargs: {kwargs}")
        logger.debug(f"  - 'self' in kwargs: {'self' in kwargs}")

        # Don't pass *args because original_run is already a bound method
        # args[0] is the tool instance, which is already bound to original_run
        cleaned_kwargs = {k: v for k, v in kwargs.items() if k != 'self'}
        logger.debug(f"  - Cleaned kwargs: {cleaned_kwargs}")

        try:
            result = original_run(**cleaned_kwargs)
            logger.info(f"✅ PATCHED_RUN succeeded for {tool.name}")
            return result
        except Exception as e:
            logger.error(f"❌ PATCHED_RUN failed for {tool.name}: {type(e).__name__}: {e}")
            raise

    async def patched_arun(*args, **kwargs):
        """Patched _arun that removes 'self' from kwargs and ensures config is provided."""
        logger.info(f"🔧 PATCHED_ARUN called for {tool.name}")
        logger.info(f"  - Received kwargs keys: {list(kwargs.keys())}")
        logger.info(f"  - 'self' in kwargs: {'self' in kwargs}")
        logger.info(f"  - 'config' in kwargs: {'config' in kwargs}")

        # Filter out 'self', keep everything else
        cleaned_kwargs = {k: v for k, v in kwargs.items() if k != 'self'}

        # If config is not provided, add a default empty RunnableConfig
        # (StructuredTool._arun requires config as a keyword-only argument)
        if 'config' not in cleaned_kwargs:
            from langchain_core.runnables.config import RunnableConfig
            cleaned_kwargs['config'] = RunnableConfig()
            logger.info(f"  - Added default config to kwargs")

        logger.info(f"  - Final cleaned kwargs keys: {list(cleaned_kwargs.keys())}")

        try:
            if original_arun:
                result = await original_arun(**cleaned_kwargs)
            else:
                # If no async version, call sync version
                import asyncio
                result = await asyncio.to_thread(original_run, **cleaned_kwargs)
            logger.info(f"✅ PATCHED_ARUN succeeded for {tool.name}")
            return result
        except Exception as e:
            logger.error(f"❌ PATCHED_ARUN failed for {tool.name}: {type(e).__name__}: {e}")
            logger.error(f"  - Final cleaned_kwargs keys: {list(cleaned_kwargs.keys())}")
            raise

    # Monkey-patch the methods
    logger.debug(f"Tool {tool.name} - Before patch: _run = {tool._run}")
    tool._run = patched_run
    tool._arun = patched_arun
    logger.debug(f"Tool {tool.name} - After patch: _run = {tool._run}")
    logger.info(f"✅ Successfully patched tool: {tool.name}")

    return tool

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
        # Use asyncio.to_thread to run blocking OAuth calls in thread pool
        import asyncio
        gmail_toolkit = await asyncio.to_thread(GmailToolkit, credentials_file=credentials_path)

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
        # Use asyncio.to_thread to run blocking OAuth calls in thread pool
        import asyncio
        calendar_toolkit = await asyncio.to_thread(CalendarToolkit, credentials_file=credentials_path)

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

        # Create MCP client with corrected package and command-line arguments
        # Corrected package @supabase/mcp-server-postgrest verified to exist on npm registry
        # transport=stdio specifies that MCP server communicates via standard input/output streams
        # Note: This MCP server expects full PostgREST endpoint URL (not just base URL)
        # PostgREST endpoint is at /rest/v1 path on Supabase project URL
        postgrest_url = f"{supabase_url}/rest/v1" if not supabase_url.endswith("/rest/v1") else supabase_url

        supabase_client = MultiServerMCPClient(
            {
                "supabase": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@supabase/mcp-server-postgrest",
                        "--apiUrl",
                        postgrest_url,  # Use full PostgREST endpoint URL
                        "--apiKey",
                        service_key,
                        "--schema",
                        "public"  # Default to public schema for case management tables
                    ],
                    "transport": "stdio"
                }
            }
        )

        # MCP client initialization is async requiring await per LangChain MCP adapter pattern
        supabase_tools = await supabase_client.get_tools()

        # Confirm successful MCP server spawn and tool retrieval
        logger.info(f"Successfully initialized Supabase MCP with {len(supabase_tools)} tools")

        # Note: MCP tool signature issues are now handled by middleware (src/middleware/mcp_tool_fix.py)
        # rather than monkey-patching each tool individually. The middleware approach is superior
        # because it persists across subagent creation and is the proper LangChain pattern.

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
        import traceback
        logger.error(f"Supabase MCP initialization failed: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
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
        # transport=stdio specifies that MCP server communicates via standard input/output streams
        tavily_client = MultiServerMCPClient(
            {
                "tavily": {
                    "command": "npx",
                    "args": ["-y", "@mcptools/mcp-tavily"],
                    "transport": "stdio",
                    "env": {
                        "TAVILY_API_KEY": tavily_api_key
                    }
                }
            }
        )

        # MCP client initialization is async requiring await per LangChain MCP adapter pattern
        tavily_tools = await tavily_client.get_tools()

        # Confirm successful MCP server spawn and tool retrieval
        logger.info(f"Successfully initialized Tavily MCP with {len(tavily_tools)} tools")

        # Note: MCP tool signature issues are now handled by middleware (src/middleware/mcp_tool_fix.py)
        # rather than monkey-patching each tool individually. The middleware approach is superior
        # because it persists across subagent creation and is the proper LangChain pattern.

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
        import traceback
        logger.error(f"Tavily MCP initialization failed: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return []  # Prevent complete agent failure from single integration issue

    # Tavily provides AI-optimized search specifically designed for LLM applications with
    # relevance ranking and answer extraction.
    # MCP server communicates with Tavily API on behalf of agent avoiding need for Python SDK
    # dependency simplifying architecture.
    # Tavily MCP particularly useful for legal research enabling agent to search case law
    # statutes and legal databases with AI-enhanced relevance.
    # MCP client spawns subprocess so cleanup may be needed on agent shutdown to prevent
    # orphaned processes.


async def init_elevenlabs_tts() -> List[BaseTool]:
    """
    Initialize ElevenLabs text-to-speech tool with API key from ELEVENLABS_API_KEY environment variable.

    Returns:
        list[BaseTool]: List containing ElevenLabs text-to-speech tool or empty list if API key
        missing or initialization fails.

    Note:
        Requires ELEVENLABS_API_KEY environment variable for authenticating with ElevenLabs
        text-to-speech API per service requirements.
        Uses custom tool compatible with elevenlabs>=1.0.0 (generator-based API).

    Citation: https://python.langchain.com/docs/integrations/tools/eleven_labs_tts
    """
    try:
        # Read ELEVENLABS_API_KEY environment variable to get API key for authenticating TTS requests
        api_key = os.getenv("ELEVENLABS_API_KEY")

        # Check if API key missing and log warning, return empty list for graceful degradation
        if not api_key:
            logger.warning("ElevenLabs API key not configured, skipping text-to-speech initialization")
            return []

        # Log initialization attempt
        logger.info("Initializing ElevenLabs text-to-speech tool")

        # Import custom ElevenLabs tool compatible with elevenlabs>=1.0.0
        from src.tools.elevenlabs_tts import create_elevenlabs_tts_tool

        # Create tool instance - custom tool handles generator-based API properly
        # Use asyncio.to_thread to run potentially blocking initialization in thread pool
        import asyncio
        tts_tool = await asyncio.to_thread(create_elevenlabs_tts_tool)

        # Confirm successful initialization without exposing sensitive credentials
        logger.info("Successfully initialized ElevenLabs text-to-speech tool")

        # Return tool in list format to match other toolkit patterns
        return [tts_tool]

    except ImportError as e:
        # Catch missing package error for clearer error messaging
        logger.error(f"ElevenLabs package not installed (elevenlabs required): {e}")
        return []  # Graceful degradation: continue agent startup without TTS functionality

    except Exception as e:
        # Catch all other errors: API errors, network issues, invalid API key, etc.
        logger.error(f"ElevenLabs text-to-speech initialization failed: {str(e)}")
        return []  # Empty list ensures agent can start even if TTS initialization fails

    # ElevenLabs provides high-quality AI voice synthesis with natural-sounding speech generation
    # Custom tool compatible with elevenlabs>=1.0.0 which uses generator-based streaming API
    # Tool can generate audio from text input and save to temporary file
    # Particularly useful for legal agent to provide voice output for client communications
    # reading case summaries or legal documents aloud
    # Tool initialization reads API key from environment so no credentials need to be passed
    # explicitly per LangChain pattern
