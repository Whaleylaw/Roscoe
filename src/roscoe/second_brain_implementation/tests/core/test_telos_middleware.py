"""
Unit tests for TELOS middleware.

Tests TELOSMiddleware loading attorney context at session start.
- Loads mission.md, goals.md, preferences.md from /memories/TELOS/
- Injects into system message once per session
- Skips template files with "[Attorney fills this in]"

Run with:
    cd /Volumes/X10 Pro/Roscoe_v2/Roscoe_v1_essentials
    python -m pytest tests/core/test_telos_middleware.py -v
"""

import sys
from pathlib import Path
import tempfile
import os

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock, MagicMock
from langchain_core.messages import SystemMessage, HumanMessage


class TestTELOSMiddleware:
    """Test TELOSMiddleware loading attorney context at session start."""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace with TELOS files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create /memories/TELOS/ structure
            telos_dir = Path(tmpdir) / 'memories' / 'TELOS'
            telos_dir.mkdir(parents=True)

            # Create test files
            (telos_dir / 'mission.md').write_text(
                "# Professional Mission\n\n"
                "Provide excellent legal representation with compassion and integrity."
            )
            (telos_dir / 'goals.md').write_text(
                "# Current Goals\n\n"
                "- Expand practice in medical malpractice\n"
                "- Improve client communication systems"
            )
            (telos_dir / 'preferences.md').write_text(
                "# Work Style Preferences\n\n"
                "- Prefer morning meetings\n"
                "- Communicate via email for non-urgent matters"
            )

            # Create a template file (should be skipped)
            (telos_dir / 'strategies.md').write_text(
                "# Legal Strategies\n\n"
                "[Attorney fills this in]"
            )

            yield tmpdir

    def test_telos_middleware_loads_on_startup(self, temp_workspace):
        """Test that TELOS files are loaded once per session."""
        from core.telos_middleware import TELOSMiddleware

        middleware = TELOSMiddleware(workspace_dir=str(temp_workspace))

        # Mock state and runtime
        state = {}
        runtime = Mock()

        # Call before_agent hook
        result = middleware.before_agent(state, runtime)

        # Verify TELOS content was loaded
        assert result is not None, "before_agent should return state update"
        assert result.get('telos_loaded') == True, "telos_loaded flag should be set"
        assert 'telos_content' in result, "telos_content should be in result"

        # Check that content includes the mission/goals/preferences
        content = result['telos_content']
        assert 'mission' in content.lower(), "Should include mission content"
        assert 'goals' in content.lower(), "Should include goals content"
        assert 'preferences' in content.lower(), "Should include preferences content"

        # Check that template file was skipped
        assert '[Attorney fills this in]' not in content, "Should skip template files"

    def test_telos_middleware_skips_if_already_loaded(self, temp_workspace):
        """Test that TELOS content is only loaded once per session."""
        from core.telos_middleware import TELOSMiddleware

        middleware = TELOSMiddleware(workspace_dir=str(temp_workspace))

        # State already has telos_loaded=True
        state = {'telos_loaded': True}
        runtime = Mock()

        # Call before_agent hook
        result = middleware.before_agent(state, runtime)

        # Should return None (no update needed)
        assert result is None, "Should skip loading if already loaded"

    def test_telos_middleware_injects_into_system_message(self, temp_workspace):
        """Test that TELOS content is injected into system message."""
        from core.telos_middleware import TELOSMiddleware

        middleware = TELOSMiddleware(workspace_dir=str(temp_workspace))

        # Create mock request with state containing TELOS content
        mock_request = Mock()
        mock_request.state = {
            'telos_loaded': True,
            'telos_content': '# Attorney Context (TELOS)\n\nMission: Excellence'
        }
        mock_request.system_message = SystemMessage(content="You are a helpful assistant.")

        # Mock the override method to return a modified request
        def override_impl(**kwargs):
            modified_request = Mock()
            modified_request.state = mock_request.state
            modified_request.system_message = kwargs.get('system_message', mock_request.system_message)
            return modified_request

        mock_request.override = override_impl

        # Create a handler that captures the modified request
        captured_request = None
        def mock_handler(req):
            nonlocal captured_request
            captured_request = req
            return "response"

        # Call wrap_model_call
        result = middleware.wrap_model_call(mock_request, mock_handler)

        # Verify system message was updated
        assert captured_request is not None, "Handler should have been called"
        assert captured_request.system_message is not None, "System message should exist"
        assert isinstance(captured_request.system_message, SystemMessage), \
            "System message should be a SystemMessage instance"
        assert 'Attorney Context (TELOS)' in captured_request.system_message.content, \
            "System message should include TELOS content"
        assert 'Mission: Excellence' in captured_request.system_message.content, \
            "System message should include TELOS details"

    def test_telos_middleware_handles_missing_files(self, temp_workspace):
        """Test that middleware gracefully handles missing TELOS files."""
        from core.telos_middleware import TELOSMiddleware

        # Point to non-existent directory
        middleware = TELOSMiddleware(workspace_dir=str(Path(temp_workspace) / 'nonexistent'))

        state = {}
        runtime = Mock()

        # Should not crash, should return None
        result = middleware.before_agent(state, runtime)

        # Should return None (no content to load)
        assert result is None, "Should return None when no files found"

    def test_telos_middleware_handles_empty_files(self):
        """Test that middleware skips empty TELOS files."""
        from core.telos_middleware import TELOSMiddleware

        # Create a separate temporary directory for empty files test
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory with empty files only
            telos_dir = Path(tmpdir) / 'memories' / 'TELOS'
            telos_dir.mkdir(parents=True, exist_ok=True)

            # Create empty files
            (telos_dir / 'mission.md').write_text('')
            (telos_dir / 'goals.md').write_text('   \n  \n')  # Whitespace only

            middleware = TELOSMiddleware(workspace_dir=str(tmpdir))

            state = {}
            runtime = Mock()

            result = middleware.before_agent(state, runtime)

            # Should return None (no meaningful content)
            assert result is None, "Should skip empty files"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
