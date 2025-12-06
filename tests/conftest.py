"""
Deep Agent Coder - Pytest Fixtures

Shared fixtures for all test modules.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver


@pytest.fixture
def mock_store():
    """
    In-memory store for testing cross-thread persistent memory.

    Use this instead of PostgresStore in tests to avoid database dependencies.
    """
    return InMemoryStore()


@pytest.fixture
def mock_checkpointer():
    """
    In-memory checkpointer for testing thread state persistence.

    Use this instead of PostgresSaver in tests to avoid database dependencies.
    """
    return MemorySaver()


@pytest.fixture
def temp_workspace():
    """
    Temporary directory for workspace files during tests.

    Creates a temp directory before the test and cleans it up after.
    Yields the Path object to the temp directory.
    """
    temp_dir = tempfile.mkdtemp(prefix="deep_agent_coder_test_")
    temp_path = Path(temp_dir)

    yield temp_path

    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_workspace_with_files(temp_workspace):
    """
    Temporary workspace pre-populated with a basic project structure.

    Creates:
    - src/ directory
    - tests/ directory
    - README.md file
    """
    # Create basic structure
    (temp_workspace / "src").mkdir()
    (temp_workspace / "tests").mkdir()
    (temp_workspace / "README.md").write_text("# Test Project\n")

    yield temp_workspace


@pytest.fixture
def simple_agent(temp_workspace):
    """
    Create a simple agent with in-memory storage for testing.

    Uses the temp_workspace fixture for the workspace directory.
    """
    from deep_agent_coder import create_simple_agent

    return create_simple_agent(workspace_dir=str(temp_workspace))
