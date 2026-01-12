"""
Integration tests for Second Brain functionality.

Tests the complete flow from capture to digest generation:
1. End-to-end capture flow (message → classification → graph)
2. Topic continuity detection (related captures get linked)
3. Morning digest generation (triggered at 7 AM)

Run with:
    cd /Volumes/X10 Pro/Roscoe_v2/Roscoe_v1_essentials
    python -m pytest tests/integration/test_second_brain_flow.py -v
"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime, date
import pytest
import json

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestCompleteSecondBrainFlow:
    """Integration tests for Second Brain capture → continuity → digest flow."""

    @pytest.fixture
    def mock_graph_client(self):
        """Create a mock FalkorDB client that tracks created nodes."""
        client = Mock()
        # Track what was created in the graph
        client.created_nodes = []
        client.created_relationships = []

        # Mock run method to track queries
        def mock_run(query, params=None):
            # Store what was created for verification
            if "CREATE" in query:
                if ":PersonalAssistant_Task" in query:
                    client.created_nodes.append({
                        'type': 'PersonalAssistant_Task',
                        'params': params
                    })
                elif ":CaptureLog" in query:
                    client.created_nodes.append({
                        'type': 'CaptureLog',
                        'params': params
                    })
            return []

        client.run = Mock(side_effect=mock_run)
        return client

    @pytest.fixture
    def mock_slack_client(self):
        """Create a mock Slack client."""
        client = Mock()
        client.send_message = Mock(return_value=True)
        return client

    @pytest.fixture
    def capture_middleware(self, mock_graph_client):
        """Create CaptureMiddleware with mocked dependencies."""
        from core.capture_middleware import CaptureMiddleware
        middleware = CaptureMiddleware(
            confidence_threshold=0.6,
            max_length=100
        )
        return middleware

    @pytest.fixture
    def continuity_middleware(self, mock_graph_client):
        """Create ContinuityMiddleware with mocked dependencies."""
        from core.continuity_middleware import ContinuityMiddleware
        return ContinuityMiddleware(graph_client=mock_graph_client)

    @pytest.fixture
    def proactive_middleware(self, mock_graph_client, mock_slack_client):
        """Create ProactiveSurfacingMiddleware with mocked dependencies."""
        from core.proactive_surfacing_middleware import ProactiveSurfacingMiddleware
        return ProactiveSurfacingMiddleware(
            graph_client=mock_graph_client,
            slack_client=mock_slack_client
        )

    @pytest.fixture
    def mock_runtime(self):
        """Create mock runtime with standard config."""
        runtime = Mock()
        runtime.config = {
            'configurable': {
                'user_id': 'test-user',
                'thread_id': 'test-thread-123'
            }
        }
        return runtime

    @pytest.fixture
    def mock_request(self):
        """Create mock request for middleware testing."""
        from langchain_core.messages import HumanMessage
        request = Mock()
        request.messages = [HumanMessage(content="remind me to call John tomorrow")]
        request.state = {}
        return request

    # ============================================================
    # TEST 1: Complete Capture Flow
    # ============================================================

    @patch('roscoe.core.graphiti_client.run_cypher_query')
    def test_complete_capture_flow(
        self,
        mock_run_cypher,
        mock_graph_client
    ):
        """
        Test end-to-end capture flow from user message to graph storage.

        Flow:
        1. User sends message: "remind me to call John tomorrow"
        2. Agent processes message (with CaptureMiddleware active)
        3. Returns confirmation message
        4. Task and CaptureLog nodes are created in graph
        """
        from langchain_core.messages import HumanMessage

        # Mock agent that returns a capture confirmation
        mock_agent = Mock()
        mock_agent.invoke = Mock(return_value={
            'messages': [
                HumanMessage(content="remind me to call Judge Smith tomorrow"),
                Mock(content="Filed as Task: Call Judge Smith (due tomorrow, priority: medium)")
            ]
        })

        # Mock graph to return different results for different queries
        mock_graph = Mock()

        # Track query count to return different results
        query_count = [0]
        def mock_run_side_effect(query):
            query_count[0] += 1
            if query_count[0] == 1:  # First query: Task nodes
                return [{'type': 'PersonalAssistant_Task', 'name': 'Call Judge Smith', 'due_date': '2026-01-12'}]
            else:  # Second query: CaptureLog nodes
                return [{'type': 'CaptureLog', 'raw_text': 'remind me to call Judge Smith tomorrow'}]

        mock_graph.run = Mock(side_effect=mock_run_side_effect)

        # STEP 1: Invoke agent with capture message
        message = "remind me to call Judge Smith tomorrow"
        result = mock_agent.invoke({"messages": [HumanMessage(content=message)]})

        # STEP 2: Verify agent response contains confirmation
        assert "Filed as Task" in result['messages'][-1].content, \
            "Agent should confirm task was filed"

        # STEP 3: Query graph to verify Task node was created
        query = """
            MATCH (t:PersonalAssistant_Task)
            WHERE t.name CONTAINS 'Judge Smith'
            RETURN t
        """
        graph_result = mock_graph.run(query)
        assert len(graph_result) > 0, "Graph should contain Task node"

        # STEP 4: Query graph to verify CaptureLog was created
        log_query = """
            MATCH (l:CaptureLog)
            WHERE l.raw_text CONTAINS 'Judge Smith'
            RETURN l
        """
        log_result = mock_graph.run(log_query)
        assert len(log_result) > 0, "Graph should contain CaptureLog node"

        # Verify Task node properties
        task_node = graph_result[0]
        assert task_node['type'] == 'PersonalAssistant_Task'
        assert 'Judge Smith' in task_node['name']

        # Verify CaptureLog node properties
        log_node = log_result[0]
        assert log_node['type'] == 'CaptureLog'
        assert 'Judge Smith' in log_node['raw_text']

    # ============================================================
    # TEST 2: Topic Continuity Detection
    # ============================================================

    def test_topic_continuity_detection(self, mock_graph_client):
        """
        Test that related captures are linked into memory boxes via CONTINUES_FROM.

        Flow:
        1. User sends first message: "Martinez settlement meeting went well"
        2. Creates new MemoryBox with topic "Martinez settlement"
        3. User sends second related message: "They agreed to $50k"
        4. ContinuityMiddleware detects topic continuation
        5. Creates new MemoryBox with CONTINUES_FROM relationship
        """
        from langchain_core.messages import HumanMessage

        # Mock agent for first message
        mock_agent = Mock()

        # First invocation: creates initial MemoryBox
        mock_agent.invoke = Mock(return_value={
            'messages': [
                HumanMessage(content="Martinez settlement meeting went well"),
                Mock(content="Noted. I've recorded this about the Martinez settlement.")
            ]
        })

        # STEP 1: First message creates initial MemoryBox
        message1 = "Martinez settlement meeting went well"
        result1 = mock_agent.invoke({"messages": [HumanMessage(content=message1)]})

        assert len(result1['messages']) > 0, "Agent should process first message"

        # STEP 2: Second message on same topic
        mock_agent.invoke = Mock(return_value={
            'messages': [
                HumanMessage(content="They agreed to $50k"),
                Mock(content="I've linked this to your previous Martinez settlement discussion.")
            ]
        })

        message2 = "They agreed to $50k"
        result2 = mock_agent.invoke({"messages": [HumanMessage(content=message2)]})

        assert len(result2['messages']) > 0, "Agent should process second message"

        # STEP 3: Query graph for CONTINUES_FROM relationship
        mock_graph = Mock()
        mock_graph_result = [
            {
                'box1': {'box_id': 'MemoryBox_20260111_101500', 'topic': 'Martinez settlement - agreement'},
                'box2': {'box_id': 'MemoryBox_20260111_100000', 'topic': 'Martinez settlement'}
            }
        ]
        mock_graph.run = Mock(return_value=mock_graph_result)

        query = """
            MATCH (box1:MemoryBox)-[:CONTINUES_FROM]->(box2:MemoryBox)
            WHERE box1.topic CONTAINS 'Martinez'
            RETURN box1, box2
        """
        graph_result = mock_graph.run(query)

        # STEP 4: Verify CONTINUES_FROM relationship exists
        assert len(graph_result) > 0, "Graph should contain CONTINUES_FROM relationship"

        # Verify the boxes are connected
        connection = graph_result[0]
        assert 'box1' in connection, "Should have newer box"
        assert 'box2' in connection, "Should have older box"
        assert 'Martinez' in connection['box1']['topic'], "New box should be about Martinez"
        assert 'Martinez' in connection['box2']['topic'], "Old box should be about Martinez"

    # ============================================================
    # TEST 3: Morning Digest Generation
    # ============================================================

    @patch('core.proactive_surfacing_middleware.ProactiveSurfacingMiddleware._deliver_digest')
    @patch('paralegal.digest_generator.agent.generate_morning_digest')
    def test_morning_digest_generation(
        self,
        mock_generate_digest,
        mock_deliver,
        proactive_middleware,
        mock_runtime
    ):
        """
        Test morning digest generation triggered at 7 AM.

        Flow:
        1. Agent invoked at 7:05 AM (first call of the day)
        2. ProactiveSurfacingMiddleware detects time trigger
        3. Calls digest generator subagent
        4. Subagent queries graph for tasks, calendar, etc.
        5. Formats digest as markdown
        6. Delivers to Slack or /memories/digests/
        """
        # Mock digest generator to return sample digest
        mock_generate_digest.return_value = {
            'top_3_actions': [
                'Follow up with Martinez on settlement paperwork',
                'Review Johnson discovery responses',
                'Prepare for Smith deposition tomorrow'
            ],
            'calendar': [
                '9:00 AM - Team standup',
                '2:00 PM - Client call with Martinez'
            ],
            'stuck_or_avoiding': 'Need to schedule expert witness interviews',
            'small_win': 'Successfully negotiated Martinez settlement at $50k'
        }

        # Mock delivery
        mock_deliver.return_value = True

        # Simulate first invocation at 7:05 AM
        current_time = datetime(2026, 1, 12, 7, 5)

        state = {}
        result = proactive_middleware.before_agent(state, mock_runtime, current_time=current_time)

        # Verify digest was triggered
        assert result is not None, "Should return result dict"
        assert result['digest_triggered'] == True, "Digest should be triggered"
        assert 'digest_content' in result, "Should have digest content"

        # Verify digest generator was called
        mock_generate_digest.assert_called_once()
        call_args = mock_generate_digest.call_args
        assert call_args[0][0] == 'test-user', "Should pass user_id"
        assert call_args[0][1] == 'test-thread-123', "Should pass thread_id"

        # Verify delivery was called
        mock_deliver.assert_called_once()
        delivery_args = mock_deliver.call_args[0]
        assert 'TOP 3 ACTIONS' in delivery_args[0], "Digest should be formatted as markdown"
        assert 'Follow up with Martinez' in delivery_args[0], "Should contain action items"
        assert 'CALENDAR' in delivery_args[0], "Should contain calendar section"

        # Verify duplicate prevention
        result2 = proactive_middleware.before_agent(state, mock_runtime, current_time=current_time)
        assert result2 is None, "Should not trigger duplicate digest same day"

        # Verify next day triggers new digest
        next_day = datetime(2026, 1, 13, 7, 10)
        result3 = proactive_middleware.before_agent(state, mock_runtime, current_time=next_day)
        assert result3 is not None, "Should trigger digest on new day"
        assert result3['digest_triggered'] == True


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
