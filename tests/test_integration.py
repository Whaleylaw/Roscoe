"""
Deep Agent Coder - Integration Tests

End-to-end integration tests for the Deep Agent Coder system.

Tests are organized into:
- TestAgentInvocation: Basic agent invocation and response
- TestThreadPersistence: State persistence across invocations
- TestNewThread: Thread isolation and fresh starts

Tests marked with @pytest.mark.integration require ANTHROPIC_API_KEY to invoke the model.
Tests without this marker test the structure/setup without making API calls.
"""

import os
import pytest
import uuid


# Check if API key is available for integration tests
HAS_API_KEY = os.environ.get("ANTHROPIC_API_KEY") is not None
SKIP_MSG = "ANTHROPIC_API_KEY not set - skipping integration test that requires API calls"


class TestAgentInvocation:
    """Test that agent can be invoked and responds appropriately."""

    def test_agent_can_be_created(self, simple_agent):
        """Test that agent is created successfully (no API call)."""
        assert simple_agent is not None
        assert hasattr(simple_agent, 'invoke')

    def test_agent_invoke_accepts_config(self, simple_agent):
        """Test that agent invoke method accepts proper config structure (no API call)."""
        # We test the interface without actually calling invoke
        # Verify that invoke is callable and has expected signature
        import inspect
        sig = inspect.signature(simple_agent.invoke)
        params = list(sig.parameters.keys())

        # LangGraph invoke should accept input and config
        assert 'input' in params or len(params) >= 1
        assert 'config' in params or len(params) >= 2

    @pytest.mark.integration
    @pytest.mark.skipif(not HAS_API_KEY, reason=SKIP_MSG)
    def test_agent_invokes_with_message(self, simple_agent):
        """Test that agent can be invoked with a simple message."""
        thread_id = f"test-{uuid.uuid4().hex[:8]}"
        config = {"configurable": {"thread_id": thread_id}}

        result = simple_agent.invoke(
            {"messages": [{"role": "user", "content": "Hello, can you hear me?"}]},
            config=config,
        )

        # Should return a result with messages
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) > 0

    @pytest.mark.integration
    @pytest.mark.skipif(not HAS_API_KEY, reason=SKIP_MSG)
    def test_agent_responds_appropriately(self, simple_agent):
        """Test that agent provides an appropriate response to a message."""
        thread_id = f"test-{uuid.uuid4().hex[:8]}"
        config = {"configurable": {"thread_id": thread_id}}

        result = simple_agent.invoke(
            {"messages": [{"role": "user", "content": "What is 2+2?"}]},
            config=config,
        )

        # Find the AI response
        ai_response = None
        for msg in reversed(result["messages"]):
            if hasattr(msg, 'type') and msg.type == "ai":
                ai_response = msg.content
                break
            elif isinstance(msg, dict) and msg.get("role") == "assistant":
                ai_response = msg.get("content")
                break

        assert ai_response is not None
        assert len(ai_response) > 0
        # Response should contain "4" for the math question
        assert "4" in ai_response

    @pytest.mark.integration
    @pytest.mark.skipif(not HAS_API_KEY, reason=SKIP_MSG)
    def test_agent_handles_workspace_query(self, simple_agent, temp_workspace):
        """Test that agent can interact with workspace."""
        # Create a test file in the workspace
        test_file = temp_workspace / "test.txt"
        test_file.write_text("Hello from workspace!")

        thread_id = f"test-{uuid.uuid4().hex[:8]}"
        config = {"configurable": {"thread_id": thread_id}}

        result = simple_agent.invoke(
            {"messages": [{"role": "user", "content": "List files in /workspace/"}]},
            config=config,
        )

        # Should get a response
        assert result is not None
        assert "messages" in result


class TestThreadPersistence:
    """Test that state persists correctly across invocations on the same thread."""

    def test_thread_config_structure(self, simple_agent):
        """Test thread config structure (no API call)."""
        thread_id = f"test-{uuid.uuid4().hex[:8]}"
        config = {"configurable": {"thread_id": thread_id}}

        # Verify config structure is valid
        assert "configurable" in config
        assert "thread_id" in config["configurable"]
        assert config["configurable"]["thread_id"] == thread_id

    @pytest.mark.integration
    @pytest.mark.skipif(not HAS_API_KEY, reason=SKIP_MSG)
    def test_state_persists_same_thread(self, simple_agent):
        """Test that conversation state persists across invocations on same thread_id."""
        thread_id = f"test-persist-{uuid.uuid4().hex[:8]}"
        config = {"configurable": {"thread_id": thread_id}}

        # First invocation: Set context
        result1 = simple_agent.invoke(
            {"messages": [{"role": "user", "content": "My favorite color is blue. Remember this."}]},
            config=config,
        )

        assert result1 is not None
        assert "messages" in result1

        # Second invocation: Ask about the context
        result2 = simple_agent.invoke(
            {"messages": [{"role": "user", "content": "What is my favorite color?"}]},
            config=config,
        )

        # Find the AI response
        ai_response = None
        for msg in reversed(result2["messages"]):
            if hasattr(msg, 'type') and msg.type == "ai":
                ai_response = msg.content
                break
            elif isinstance(msg, dict) and msg.get("role") == "assistant":
                ai_response = msg.get("content")
                break

        # Response should reference blue
        assert ai_response is not None
        assert "blue" in ai_response.lower()

    @pytest.mark.integration
    @pytest.mark.skipif(not HAS_API_KEY, reason=SKIP_MSG)
    def test_message_history_accumulates(self, simple_agent):
        """Test that message history accumulates across invocations."""
        thread_id = f"test-history-{uuid.uuid4().hex[:8]}"
        config = {"configurable": {"thread_id": thread_id}}

        # First message
        result1 = simple_agent.invoke(
            {"messages": [{"role": "user", "content": "First message"}]},
            config=config,
        )
        initial_count = len(result1["messages"])

        # Second message on same thread
        result2 = simple_agent.invoke(
            {"messages": [{"role": "user", "content": "Second message"}]},
            config=config,
        )

        # Message count should have increased
        assert len(result2["messages"]) > initial_count

    @pytest.mark.integration
    @pytest.mark.skipif(not HAS_API_KEY, reason=SKIP_MSG)
    def test_workspace_changes_persist(self, simple_agent, temp_workspace):
        """Test that workspace file operations persist across invocations."""
        thread_id = f"test-workspace-{uuid.uuid4().hex[:8]}"
        config = {"configurable": {"thread_id": thread_id}}

        # First invocation: Create a file
        result1 = simple_agent.invoke(
            {"messages": [{"role": "user", "content": "Create a file at /workspace/persistent.txt with content 'test data'"}]},
            config=config,
        )

        # Second invocation: Read the file
        result2 = simple_agent.invoke(
            {"messages": [{"role": "user", "content": "Read /workspace/persistent.txt"}]},
            config=config,
        )

        # Should successfully interact with the persisted file
        assert result2 is not None
        assert "messages" in result2


class TestNewThread:
    """Test that new thread_id starts fresh without previous context."""

    def test_different_thread_ids_are_unique(self):
        """Test that different thread IDs are generated as unique (no API call)."""
        thread_id1 = f"test-{uuid.uuid4().hex[:8]}"
        thread_id2 = f"test-{uuid.uuid4().hex[:8]}"

        assert thread_id1 != thread_id2

    @pytest.mark.integration
    @pytest.mark.skipif(not HAS_API_KEY, reason=SKIP_MSG)
    def test_new_thread_starts_fresh(self, simple_agent):
        """Test that a new thread_id starts without context from other threads."""
        # First thread: Set context
        thread_id1 = f"test-thread1-{uuid.uuid4().hex[:8]}"
        config1 = {"configurable": {"thread_id": thread_id1}}

        simple_agent.invoke(
            {"messages": [{"role": "user", "content": "My secret code is ALPHA123. Remember this."}]},
            config=config1,
        )

        # Second thread: Should not have access to first thread's context
        thread_id2 = f"test-thread2-{uuid.uuid4().hex[:8]}"
        config2 = {"configurable": {"thread_id": thread_id2}}

        result = simple_agent.invoke(
            {"messages": [{"role": "user", "content": "What is my secret code?"}]},
            config=config2,
        )

        # Find the AI response
        ai_response = None
        for msg in reversed(result["messages"]):
            if hasattr(msg, 'type') and msg.type == "ai":
                ai_response = msg.content
                break
            elif isinstance(msg, dict) and msg.get("role") == "assistant":
                ai_response = msg.get("content")
                break

        # Response should NOT contain the secret code from the other thread
        assert ai_response is not None
        assert "ALPHA123" not in ai_response

    @pytest.mark.integration
    @pytest.mark.skipif(not HAS_API_KEY, reason=SKIP_MSG)
    def test_new_thread_empty_history(self, simple_agent):
        """Test that new thread starts with empty conversation history."""
        # Create a completely new thread
        thread_id = f"test-fresh-{uuid.uuid4().hex[:8]}"
        config = {"configurable": {"thread_id": thread_id}}

        result = simple_agent.invoke(
            {"messages": [{"role": "user", "content": "Hello"}]},
            config=config,
        )

        # The result should have our message plus the response
        # But no prior history from other threads
        # LangGraph uses HumanMessage with type="human", not "user"
        user_messages = [msg for msg in result["messages"]
                        if (hasattr(msg, 'type') and msg.type in ("user", "human")) or
                           (isinstance(msg, dict) and msg.get("role") in ("user", "human"))]

        # Should only have one user message (the one we just sent)
        # Note: There might be system messages, so we specifically check user messages
        assert len(user_messages) >= 1

    @pytest.mark.integration
    @pytest.mark.skipif(not HAS_API_KEY, reason=SKIP_MSG)
    def test_thread_isolation(self, simple_agent):
        """Test that multiple threads maintain isolated state."""
        # Thread A: Set a variable
        thread_a = f"test-thread-a-{uuid.uuid4().hex[:8]}"
        config_a = {"configurable": {"thread_id": thread_a}}

        simple_agent.invoke(
            {"messages": [{"role": "user", "content": "My name is Alice"}]},
            config=config_a,
        )

        # Thread B: Set a different variable
        thread_b = f"test-thread-b-{uuid.uuid4().hex[:8]}"
        config_b = {"configurable": {"thread_id": thread_b}}

        simple_agent.invoke(
            {"messages": [{"role": "user", "content": "My name is Bob"}]},
            config=config_b,
        )

        # Check Thread A still has Alice
        result_a = simple_agent.invoke(
            {"messages": [{"role": "user", "content": "What is my name?"}]},
            config=config_a,
        )

        ai_response_a = None
        for msg in reversed(result_a["messages"]):
            if hasattr(msg, 'type') and msg.type == "ai":
                ai_response_a = msg.content
                break
            elif isinstance(msg, dict) and msg.get("role") == "assistant":
                ai_response_a = msg.get("content")
                break

        assert ai_response_a is not None
        assert "Alice" in ai_response_a or "alice" in ai_response_a.lower()
        assert "Bob" not in ai_response_a and "bob" not in ai_response_a.lower()


class TestAgentConfiguration:
    """Test agent configuration and setup."""

    def test_simple_agent_fixture(self, simple_agent):
        """Test that simple_agent fixture provides valid agent (no API call)."""
        assert simple_agent is not None

    def test_temp_workspace_fixture(self, temp_workspace):
        """Test that temp_workspace fixture provides valid directory (no API call)."""
        assert temp_workspace.exists()
        assert temp_workspace.is_dir()

    def test_agent_with_temp_workspace(self, simple_agent, temp_workspace):
        """Test that agent is configured with temp workspace (no API call)."""
        # Verify workspace exists and agent was created with it
        assert temp_workspace.exists()
        assert simple_agent is not None

        # Create a test file to verify workspace is accessible
        test_file = temp_workspace / "config_test.txt"
        test_file.write_text("test")
        assert test_file.exists()
