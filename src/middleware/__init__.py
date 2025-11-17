"""
Middleware for DeepAgents execution.

This module provides custom middleware for the legal agent, including
MCP tool signature fixes that apply to both main agent and all subagents.
"""

from .mcp_tool_fix import MCPToolFixMiddleware

__all__ = ["MCPToolFixMiddleware"]
