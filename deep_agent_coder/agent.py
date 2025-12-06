"""
Deep Agent Coder - Main Agent Factory

Creates the Initializer agent with:
- Local filesystem access (/workspace) for code files
- Postgres-backed persistent memory (/memories) across threads
- Postgres checkpointing for thread persistence
- Four specialized subagents (Coder, Tester, Reviewer, Fixer)
"""

import os
from typing import Optional

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, StoreBackend, StateBackend
from langchain.agents.middleware import ShellToolMiddleware, HostExecutionPolicy
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres import PostgresSaver

from .subagents import get_subagents
from .prompts import INITIALIZER_SYSTEM_PROMPT


def create_coder_agent(
    workspace_dir: str = "/workspace",
    postgres_url: Optional[str] = None,
    model: str = "claude-sonnet-4-5-20250929",
):
    """
    Create the Deep Agent Coder with full persistence.

    Args:
        workspace_dir: Local directory for code files (mounted in Docker)
        postgres_url: Postgres connection string for memory + checkpoints
        model: Model to use for all agents

    Returns:
        Compiled LangGraph agent ready to invoke
    """
    # Get Postgres URL from env if not provided
    postgres_url = postgres_url or os.environ.get(
        "DATABASE_URL",
        "postgresql://coder:coder@localhost:5432/deepagent"
    )

    # Postgres store for cross-thread persistent memory
    store = PostgresStore.from_conn_string(postgres_url)

    # Postgres checkpointer for thread state persistence
    checkpointer = PostgresSaver.from_conn_string(postgres_url)

    def make_backend(runtime):
        """
        CompositeBackend routes:
        - /workspace/* → Real local filesystem (code files)
        - /memories/* → Postgres store (persistent across threads)
        - Everything else → Ephemeral state (scratch space)
        """
        return CompositeBackend(
            default=StateBackend(runtime),  # Ephemeral scratch space by default
            routes={
                "/workspace/": FilesystemBackend(
                    root_dir=workspace_dir,
                    virtual_mode=True  # Sandbox paths under workspace_dir
                ),
                "/memories/": StoreBackend(runtime),
            }
        )

    # Get subagent configurations
    subagents = get_subagents(model=model)

    # Shell tool middleware for executing commands
    middleware = [
        ShellToolMiddleware(
            workspace_root="/workspace",
            execution_policy=HostExecutionPolicy(),
        ),
    ]

    # Create the main Initializer agent
    agent = create_deep_agent(
        model=model,
        system_prompt=INITIALIZER_SYSTEM_PROMPT,
        subagents=subagents,
        backend=make_backend,
        store=store,
        checkpointer=checkpointer,
        middleware=middleware,
        # Human-in-the-loop for destructive operations (optional)
        # interrupt_on={"edit_file": True},
    )

    return agent


def create_simple_agent(
    workspace_dir: str = ".",
    model: str = "claude-sonnet-4-5-20250929",
):
    """
    Create a simpler agent without Postgres (for testing/development).
    Uses in-memory store and local filesystem only.
    """
    from langgraph.store.memory import InMemoryStore
    from langgraph.checkpoint.memory import MemorySaver

    store = InMemoryStore()
    checkpointer = MemorySaver()

    def make_backend(runtime):
        return CompositeBackend(
            default=StateBackend(runtime),  # Ephemeral scratch space by default
            routes={
                "/workspace/": FilesystemBackend(
                    root_dir=workspace_dir,
                    virtual_mode=True
                ),
                "/memories/": StoreBackend(runtime),
            }
        )

    subagents = get_subagents(model=model)

    # Shell tool middleware for executing commands
    middleware = [
        ShellToolMiddleware(
            workspace_root="/workspace",
            execution_policy=HostExecutionPolicy(),
        ),
    ]

    agent = create_deep_agent(
        model=model,
        system_prompt=INITIALIZER_SYSTEM_PROMPT,
        subagents=subagents,
        backend=make_backend,
        store=store,
        checkpointer=checkpointer,
        middleware=middleware,
    )

    return agent


def create_agent_for_langgraph(config: dict):
    """
    Factory function for langgraph dev server.
    Takes a RunnableConfig and returns the compiled agent.
    """
    # Use absolute path to avoid os.getcwd() calls during async execution
    workspace_dir = config.get("configurable", {}).get("workspace_dir")
    if workspace_dir is None:
        workspace_dir = os.path.abspath(".")
    return create_simple_agent(workspace_dir=workspace_dir)
