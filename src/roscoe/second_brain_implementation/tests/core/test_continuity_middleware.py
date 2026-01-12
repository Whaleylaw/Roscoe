"""
Unit tests for ContinuityMiddleware.

Tests topic continuity detection for Membox-inspired memory formation.
- Loads recent memory boxes from graph
- Detects topic continuation in current message
- Links related captures into event traces

Run with:
    cd /Volumes/X10 Pro/Roscoe_v2/Roscoe_v1_essentials
    python -m pytest tests/core/test_continuity_middleware.py -v
"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import pytest

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestContinuityMiddleware:
    """Test ContinuityMiddleware topic continuity detection."""

    @pytest.fixture
    def mock_graph_client(self):
        """Create a mock FalkorDB client."""
        client = Mock()
        client.run = Mock(return_value=[])
        return client

    @pytest.fixture
    def middleware(self, mock_graph_client):
        """Create ContinuityMiddleware instance with mock graph client."""
        from core.continuity_middleware import ContinuityMiddleware
        return ContinuityMiddleware(graph_client=mock_graph_client)

    @patch('langchain_anthropic.ChatAnthropic')
    def test_detects_topic_continuation(self, mock_chat_anthropic, middleware, mock_graph_client):
        """
        Test that middleware detects topic continuation.
        """
        # Mock LLM responses
        mock_llm = Mock()
        mock_chat_anthropic.return_value = mock_llm

        # Mock continuity check response (Yes)
        continuity_response = Mock()
        continuity_response.content = "Yes"

        # Mock extraction response
        extraction_response = Mock()
        extraction_response.content = '''```json
{
  "topic": "Martinez settlement discussion",
  "events": ["Adjuster agreed to $50K"]
}
```'''

        # Set up mock to return different responses for each call
        mock_llm.invoke.side_effect = [continuity_response, extraction_response]

        # Simulate recent box about "Martinez settlement"
        recent_box = {
            "box_id": "box1",
            "topic": "Martinez settlement",
            "content_summary": "Discussing settlement offer for Martinez case",
            "started_at": "2026-01-10T10:00:00",
            "last_updated": "2026-01-10T11:00:00"
        }

        # New message also about Martinez settlement
        message = "Talked to adjuster, they agreed to $50K"

        # Check continuity
        result = middleware._check_continuity(recent_box, message)

        # Should detect continuation
        assert result['continues'] == True, \
            "Should detect continuation of Martinez settlement topic"
        assert 'events' in result, "Result should include events"
        assert 'new_topic' in result, "Result should include new_topic"
        assert result['new_topic'] is None, "new_topic should be None when continuing"

    @patch('langchain_anthropic.ChatAnthropic')
    def test_detects_new_topic(self, mock_chat_anthropic, middleware):
        """Test that middleware detects when topic changes."""
        # Mock LLM responses
        mock_llm = Mock()
        mock_chat_anthropic.return_value = mock_llm

        # Mock continuity check response (No)
        continuity_response = Mock()
        continuity_response.content = "No"

        # Mock extraction response
        extraction_response = Mock()
        extraction_response.content = '''```json
{
  "topic": "Weather inquiry",
  "events": []
}
```'''

        # Set up mock to return different responses for each call
        mock_llm.invoke.side_effect = [continuity_response, extraction_response]

        # Simulate recent box about "Martinez settlement"
        recent_box = {
            "box_id": "box1",
            "topic": "Martinez settlement",
            "content_summary": "Discussed settlement offer with adjuster",
            "started_at": "2026-01-10T10:00:00",
            "last_updated": "2026-01-10T11:00:00"
        }

        # New message about completely different topic
        message = "What's the weather like today?"

        # Check continuity
        result = middleware._check_continuity(recent_box, message)

        # Should return False (new topic)
        assert result['continues'] == False, \
            "Should detect new topic (not continuation)"
        assert result['new_topic'] is not None, \
            "Should extract new topic when not continuing"
        assert 'events' in result, "Result should include events"

    def test_loads_recent_boxes(self, middleware, mock_graph_client):
        """Test that before_agent loads recent boxes from graph."""
        # Mock graph client to return sample boxes
        mock_graph_client.run.return_value = [
            {
                "box_id": "box1",
                "topic": "Martinez settlement",
                "started_at": "2026-01-10T10:00:00",
                "last_updated": "2026-01-10T11:00:00"
            },
            {
                "box_id": "box2",
                "topic": "Wilson discovery",
                "started_at": "2026-01-09T14:00:00",
                "last_updated": "2026-01-09T15:30:00"
            }
        ]

        # Mock state and runtime
        state = {}
        runtime = Mock()
        runtime.config = {
            'configurable': {
                'thread_id': 'test-thread-123'
            }
        }

        # Call before_agent hook
        result = middleware.before_agent(state, runtime)

        # Verify graph was queried
        assert mock_graph_client.run.called, "Should query graph for recent boxes"

        # Verify result contains boxes
        assert result is not None, "Should return state update"
        assert 'recent_memory_boxes' in result, "Should include recent boxes"
        assert 'current_thread_id' in result, "Should include thread ID"
        assert len(result['recent_memory_boxes']) == 2, "Should return 2 boxes"
        assert result['current_thread_id'] == 'test-thread-123', "Should return correct thread ID"

    def test_handles_no_thread_id(self, middleware):
        """Test that middleware handles missing thread_id gracefully."""
        # Mock runtime without thread_id
        state = {}
        runtime = Mock()
        runtime.config = {}  # No thread_id

        # Call before_agent hook
        result = middleware.before_agent(state, runtime)

        # Should return None (no thread_id)
        assert result is None, "Should return None when no thread_id"

    def test_handles_empty_graph_result(self, middleware, mock_graph_client):
        """Test that middleware handles empty graph results gracefully."""
        # Mock graph client to return empty result
        mock_graph_client.run.return_value = []

        # Mock state and runtime
        state = {}
        runtime = Mock()
        runtime.config = {
            'configurable': {
                'thread_id': 'test-thread-123'
            }
        }

        # Call before_agent hook
        result = middleware.before_agent(state, runtime)

        # Should return empty boxes list
        assert result is not None, "Should return state update"
        assert result['recent_memory_boxes'] == [], "Should return empty list"

    @patch('langchain_anthropic.ChatAnthropic')
    def test_check_continuity_returns_structured_result(self, mock_chat_anthropic, middleware):
        """Test that _check_continuity returns properly structured result."""
        # Mock LLM responses
        mock_llm = Mock()
        mock_chat_anthropic.return_value = mock_llm

        # Mock continuity check response
        continuity_response = Mock()
        continuity_response.content = "Yes"

        # Mock extraction response
        extraction_response = Mock()
        extraction_response.content = '''```json
{
  "topic": "Test topic",
  "events": ["Test event"]
}
```'''

        # Set up mock to return different responses for each call
        mock_llm.invoke.side_effect = [continuity_response, extraction_response]

        recent_box = {
            "box_id": "box1",
            "topic": "Test topic",
            "content_summary": "Test summary",
            "started_at": "2026-01-10T10:00:00",
            "last_updated": "2026-01-10T11:00:00"
        }

        message = "Test message about the same topic"

        result = middleware._check_continuity(recent_box, message)

        # Verify structure
        assert 'continues' in result, "Result should have 'continues' key"
        assert 'new_topic' in result, "Result should have 'new_topic' key"
        assert 'events' in result, "Result should have 'events' key"

        # Verify types
        assert isinstance(result['continues'], bool), "'continues' should be bool"
        assert isinstance(result['events'], list), "'events' should be list"
        # new_topic can be None or string
        assert result['new_topic'] is None or isinstance(result['new_topic'], str), \
            "'new_topic' should be None or string"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
