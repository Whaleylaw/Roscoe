"""
DeepAgents middleware to fix MCP tool signature issues.

This middleware intercepts ALL tool calls (main agent + all subagents including
general-purpose subagent) and filters 'self' from tool call arguments to prevent
"got multiple values for argument 'self'" error.

The middleware approach is superior to monkey-patching because:
1. It's part of agent configuration, not tool object state
2. It persists across subagent creation (subagents get the middleware too)
3. It's the proper DeepAgents pattern per official documentation
4. It applies to ALL tools uniformly without individual patching

Citations:
- DeepAgents Middleware: https://docs.langchain.com/oss/python/deepagents/middleware
- Custom Middleware: https://docs.langchain.com/oss/python/releases/langchain-v1
"""

import logging
from typing import Any, Callable

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage
from langgraph.types import Command

logger = logging.getLogger(__name__)


class MCPToolFixMiddleware(AgentMiddleware):
    """
    Middleware that fixes MCP tool signature issues by filtering 'self' from arguments.

    This middleware intercepts every tool call and removes 'self' from the arguments
    dictionary before passing to the handler. This prevents the "multiple values for
    argument 'self'" error that occurs when MCP tools incorrectly include 'self' in
    their tool call arguments.

    The middleware applies to:
    - Main agent tool calls
    - All specialized subagent tool calls (legal-researcher, email-manager, etc.)
    - General-purpose subagent tool calls (copy of main agent)

    Example tool call structure:
        request.tool_call = {
            'name': 'postgrestRequest',
            'args': {'method': 'GET', 'path': '/doc_files?limit=10', 'self': <instance>},
            'id': 'call_abc123'
        }

    After this middleware:
        request.tool_call['args'] = {'method': 'GET', 'path': '/doc_files?limit=10'}
    """

    async def awrap_tool_call(
        self,
        request: Any,
        handler: Callable[[Any], ToolMessage | Command],
    ) -> ToolMessage | Command:
        """
        Intercept tool calls and filter 'self' from arguments (async version).

        This is the async implementation required for LangGraph's async invocation
        (astream, ainvoke). The method name MUST be 'awrap_tool_call' not 'wrap_tool_call'.

        Args:
            request: ToolCallRequest containing tool_call dict with 'name', 'args', 'id'
            handler: Async function to call after modifying request

        Returns:
            ToolMessage or Command from handler execution
        """
        # DEBUG: Log that middleware is being invoked
        logger.info(f"🔍 MCPToolFixMiddleware.awrap_tool_call INVOKED for tool: {request.tool_call.get('name', 'UNKNOWN')}")

        # Get tool call arguments dictionary
        args = request.tool_call.get('args', {})

        # Check if 'self' present in arguments (MCP tool signature bug)
        if 'self' in args:
            # Log the fix for debugging and monitoring
            logger.info(
                f"🔧 MCP Tool Fix: Filtering 'self' from {request.tool_call['name']} arguments"
            )
            logger.debug(f"  - Original args keys: {list(args.keys())}")

            # Create new arguments dict without 'self'
            cleaned_args = {k: v for k, v in args.items() if k != 'self'}

            # Update request with cleaned arguments
            request.tool_call['args'] = cleaned_args

            logger.debug(f"  - Cleaned args keys: {list(cleaned_args.keys())}")
            logger.info(f"✅ MCP Tool Fix: Successfully cleaned {request.tool_call['name']}")

        # Call the handler with the (possibly modified) request
        # Wrap in try-except to catch errors and return as messages instead of crashing
        try:
            return await handler(request)
        except Exception as e:
            # Catch all tool errors and return as ToolMessage so agent can see and retry
            error_type = type(e).__name__
            error_msg = str(e)

            logger.error(
                f"❌ Tool Error: {request.tool_call['name']} failed with {error_type}: {error_msg}"
            )

            # Return error as ToolMessage so agent can see it and try a different approach
            return ToolMessage(
                content=f"Error executing {request.tool_call['name']}: {error_type}: {error_msg}\n\nPlease try a different approach or check your syntax.",
                tool_call_id=request.tool_call.get('id', ''),
                status="error"
            )
