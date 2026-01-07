"""
Core shared infrastructure for all Roscoe agents.

This module provides:
- Model configurations (Claude, Gemini)
- Middleware (shell tool, skill selector, case context)
- Multimodal tools and sub-agents
- Graphiti knowledge graph client
"""

# Graphiti client exports (lazy import to avoid startup overhead)
__all__ = [
    "get_graphiti",
    "close_graphiti",
    "add_case_episode",
    "search_case",
    "get_case_context",
    "format_context_for_prompt",
]


def __getattr__(name):
    """Lazy import graphiti client components."""
    if name in __all__:
        from roscoe.core.graphiti_client import (
            get_graphiti,
            close_graphiti,
            add_case_episode,
            search_case,
            get_case_context,
            format_context_for_prompt,
        )
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
