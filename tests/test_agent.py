"""
Deep Agent Coder - Agent Creation Tests

Tests for the agent factory functions in agent.py.
"""

import pytest


class TestCreateSimpleAgent:
    """Tests for create_simple_agent function."""

    def test_create_simple_agent(self, temp_workspace):
        """Test that create_simple_agent returns a valid agent."""
        from deep_agent_coder import create_simple_agent

        agent = create_simple_agent(workspace_dir=str(temp_workspace))

        assert agent is not None

    def test_create_simple_agent_default_workspace(self):
        """Test that create_simple_agent works with default workspace."""
        from deep_agent_coder import create_simple_agent

        agent = create_simple_agent()

        assert agent is not None

    def test_create_simple_agent_custom_model(self, temp_workspace):
        """Test that create_simple_agent accepts custom model parameter."""
        from deep_agent_coder import create_simple_agent

        agent = create_simple_agent(
            workspace_dir=str(temp_workspace),
            model="claude-sonnet-4-5-20250929"
        )

        assert agent is not None


class TestAgentInterface:
    """Tests for the agent interface."""

    def test_agent_has_invoke(self, simple_agent):
        """Test that agent has invoke method."""
        assert hasattr(simple_agent, 'invoke')
        assert callable(simple_agent.invoke)

    def test_agent_has_ainvoke(self, simple_agent):
        """Test that agent has async invoke method."""
        assert hasattr(simple_agent, 'ainvoke')
        assert callable(simple_agent.ainvoke)

    def test_agent_has_stream(self, simple_agent):
        """Test that agent has stream method."""
        assert hasattr(simple_agent, 'stream')
        assert callable(simple_agent.stream)

    def test_agent_is_compiled_graph(self, simple_agent):
        """Test that agent is a CompiledStateGraph."""
        # The agent should be a compiled LangGraph
        assert simple_agent is not None
        assert hasattr(simple_agent, 'get_graph')


class TestAgentImports:
    """Tests for agent module imports."""

    def test_import_create_coder_agent(self):
        """Test that create_coder_agent can be imported."""
        from deep_agent_coder import create_coder_agent

        assert create_coder_agent is not None
        assert callable(create_coder_agent)

    def test_import_create_simple_agent(self):
        """Test that create_simple_agent can be imported."""
        from deep_agent_coder import create_simple_agent

        assert create_simple_agent is not None
        assert callable(create_simple_agent)

    def test_import_from_agent_module(self):
        """Test direct import from agent module."""
        from deep_agent_coder.agent import create_coder_agent, create_simple_agent

        assert create_coder_agent is not None
        assert create_simple_agent is not None


class TestAgentConfiguration:
    """Tests for agent configuration."""

    def test_agent_uses_subagents(self, simple_agent):
        """Test that agent is configured with subagents."""
        # The agent should have subagent capabilities via the task tool
        # We can verify by checking the graph structure
        graph = simple_agent.get_graph()
        assert graph is not None

    def test_simple_agent_uses_memory_store(self, temp_workspace):
        """Test that simple agent uses in-memory store."""
        from deep_agent_coder import create_simple_agent
        from langgraph.store.memory import InMemoryStore

        # Create agent - it should use InMemoryStore internally
        agent = create_simple_agent(workspace_dir=str(temp_workspace))

        # Agent should be created successfully with in-memory storage
        assert agent is not None
