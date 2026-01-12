"""
Test Digest Generator Subagent

This test verifies that the digest generator subagent can be initialized
and that the integration with ProactiveSurfacingMiddleware works correctly.

NOTE: This is a basic import/structure test. Full functionality testing
requires:
- Neo4j/FalkorDB running with test data
- Google Calendar API credentials configured
- Mock data for realistic digest generation

Run with: pytest tests/test_digest_generator.py -v
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime


def test_digest_generator_imports():
    """Test that digest generator modules can be imported."""
    from paralegal.digest_generator import generate_morning_digest, get_digest_generator_subagent
    from paralegal.digest_generator.agent import format_digest_markdown
    from paralegal.digest_generator.prompts import DIGEST_GENERATOR_PROMPT

    # Verify imports successful
    assert callable(generate_morning_digest)
    assert callable(get_digest_generator_subagent)
    assert callable(format_digest_markdown)
    assert isinstance(DIGEST_GENERATOR_PROMPT, str)
    assert "top_3_actions" in DIGEST_GENERATOR_PROMPT
    assert "calendar" in DIGEST_GENERATOR_PROMPT


def test_format_digest_markdown():
    """Test digest markdown formatting."""
    from paralegal.digest_generator.agent import format_digest_markdown

    # Test with full digest
    digest = {
        "top_3_actions": [
            "Draft motion to compel for Wilson MVA",
            "Call McCay to confirm deposition",
            "Finish medical chronology for Rodriguez"
        ],
        "calendar": [
            "9:00 AM: Client meeting @ Office",
            "2:00 PM: Deposition prep @ Virtual"
        ],
        "stuck_or_avoiding": "Rodriguez deposition prep - overdue 5 days",
        "small_win": "Completed Wilson discovery responses - 47 pages"
    }

    markdown = format_digest_markdown(digest)

    # Verify structure
    assert "## 🎯 TOP 3 ACTIONS" in markdown
    assert "## 📅 TODAY'S CALENDAR" in markdown
    assert "## 🚧 STUCK/AVOIDING" in markdown
    assert "## 🎉 SMALL WIN" in markdown

    # Verify content
    assert "Draft motion to compel for Wilson MVA" in markdown
    assert "9:00 AM: Client meeting @ Office" in markdown
    assert "Rodriguez deposition prep - overdue 5 days" in markdown
    assert "Completed Wilson discovery responses - 47 pages" in markdown


def test_format_digest_markdown_empty():
    """Test digest formatting with empty sections."""
    from paralegal.digest_generator.agent import format_digest_markdown

    # Test with empty digest
    digest = {
        "top_3_actions": [],
        "calendar": [],
        "stuck_or_avoiding": "",
        "small_win": ""
    }

    markdown = format_digest_markdown(digest)

    # Should return empty string or minimal content
    assert isinstance(markdown, str)
    # Empty sections should not appear
    assert "## 🎯 TOP 3 ACTIONS" not in markdown or "1." not in markdown


def test_proactive_surfacing_middleware_integration():
    """Test that ProactiveSurfacingMiddleware calls digest generator."""
    from core.proactive_surfacing_middleware import ProactiveSurfacingMiddleware

    # Create mock graph and slack clients
    mock_graph = Mock()
    mock_slack = Mock()

    # Initialize middleware
    middleware = ProactiveSurfacingMiddleware(
        graph_client=mock_graph,
        slack_client=mock_slack
    )

    # Verify initialization
    assert middleware.graph_client == mock_graph
    assert middleware.slack_client == mock_slack
    assert hasattr(middleware, '_generate_morning_digest')

    # Test that _generate_morning_digest can be called
    # (Mock the subagent to avoid actual LLM calls)
    with patch('paralegal.digest_generator.agent.generate_morning_digest') as mock_gen:
        mock_gen.return_value = {
            "top_3_actions": ["Action 1", "Action 2", "Action 3"],
            "calendar": ["9:00 AM: Meeting"],
            "stuck_or_avoiding": "Something stuck",
            "small_win": "Something completed"
        }

        result = middleware._generate_morning_digest("test_user", "test_thread")

        # Verify subagent was called
        mock_gen.assert_called_once()

        # Verify result is markdown string
        assert isinstance(result, str)
        assert "TOP 3 ACTIONS" in result
        assert "Action 1" in result


def test_generate_morning_digest_error_handling():
    """Test error handling in generate_morning_digest."""
    from paralegal.digest_generator.agent import generate_morning_digest

    # Mock the subagent to raise an exception
    with patch('paralegal.digest_generator.agent.get_digest_generator_subagent') as mock_get:
        mock_subagent = Mock()
        mock_subagent.invoke.side_effect = Exception("Test error")
        mock_get.return_value = mock_subagent

        # Should return None on error
        result = generate_morning_digest("test_user", "test_thread", "2024-12-15")
        assert result is None


def test_generate_morning_digest_json_parsing():
    """Test JSON parsing from subagent response."""
    from paralegal.digest_generator.agent import generate_morning_digest

    # Mock subagent that returns JSON in code block
    with patch('paralegal.digest_generator.agent.get_digest_generator_subagent') as mock_get:
        mock_subagent = Mock()
        mock_message = Mock()
        mock_message.content = '''```json
{
  "top_3_actions": ["Action 1", "Action 2", "Action 3"],
  "calendar": ["Event 1"],
  "stuck_or_avoiding": "Something stuck",
  "small_win": "Something done"
}
```'''
        mock_subagent.invoke.return_value = {'messages': [mock_message]}
        mock_get.return_value = mock_subagent

        result = generate_morning_digest("test_user", "test_thread", "2024-12-15")

        # Verify JSON was parsed correctly
        assert result is not None
        assert "top_3_actions" in result
        assert len(result["top_3_actions"]) == 3
        assert result["top_3_actions"][0] == "Action 1"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
