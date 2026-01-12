"""
Memory backend for hybrid persistent/ephemeral storage.

Implements CompositeBackend routing pattern for Roscoe v2 Second Brain:
- /memories/ → Persistent storage (StoreBackend via PostgresStore)
- Everything else → Ephemeral storage (StateBackend)

Based on Deep Agents CompositeBackend pattern and PAI memory architecture.

Usage:
    from roscoe.core.memory_backend import create_memory_backend

    agent = create_deep_agent(
        system_prompt="...",
        backend=create_memory_backend,  # Pass as factory function
        ...
    )

Architecture:
    CompositeBackend routes file operations by path prefix:

    /memories/TELOS/mission.md → StoreBackend (survives across threads)
    /memories/people/john.md → StoreBackend (persistent)
    /workspace/case.pdf → StateBackend (ephemeral, per-thread)

    This enables:
    - Long-term memory (/memories/) persists across sessions
    - Working memory (everything else) stays ephemeral
    - No database migration needed - uses LangGraph Store
"""

from deepagents.backends import CompositeBackend, StateBackend, StoreBackend


def create_memory_backend(runtime):
    """
    Create hybrid filesystem routing backend.

    Routes:
    - /memories/ → Persistent (PostgresStore via StoreBackend)
    - Everything else → Ephemeral (StateBackend)

    Args:
        runtime: ToolRuntime object providing access to state and store

    Returns:
        CompositeBackend configured for memory persistence

    Example:
        # In agent.py
        agent = create_deep_agent(
            backend=create_memory_backend,  # Factory function
            ...
        )
    """
    return CompositeBackend(
        default=StateBackend(runtime),  # Ephemeral storage for workspace, etc.
        routes={
            "/memories/": StoreBackend(runtime),  # Persistent storage for memories
        }
    )
