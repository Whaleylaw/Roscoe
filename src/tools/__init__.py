"""
Tools package for legal AI agent system.

This package contains toolkit initialization functions and code execution wrapper classes.
For implementation details, see: docs/spec/CORRECTED-PLANS/src--tools--__init__.py.nlplan.md
"""

__all__ = [
    "init_gmail_toolkit",
    "init_calendar_toolkit",
    "init_supabase_mcp",
    "init_tavily_mcp",
    "RunLoopExecutor",
]

# Actual imports happen in dependent modules, not in this __init__.py file
# to avoid circular dependencies.
# Usage example: from src.tools.toolkits import init_gmail_toolkit
