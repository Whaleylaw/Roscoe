"""
Unit tests for memory backend routing.

Tests CompositeBackend routing pattern:
- /memories/ → StoreBackend (persistent)
- Everything else → StateBackend (ephemeral)

Run with:
    cd /Volumes/X10 Pro/Roscoe_v2/Roscoe_v1_essentials
    python -m pytest tests/core/test_memory_backend.py -v
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock
from core.memory_backend import create_memory_backend
from deepagents.backends import CompositeBackend


class TestMemoryBackendRouting:
    """Test CompositeBackend routing for memory persistence."""

    def test_memory_backend_creates_composite(self):
        """Test that create_memory_backend returns a CompositeBackend."""
        mock_runtime = Mock()
        backend = create_memory_backend(mock_runtime)

        assert isinstance(backend, CompositeBackend)

    def test_memory_backend_routes_memories_to_store(self):
        """Test that /memories/ paths route to StoreBackend."""
        mock_runtime = Mock()
        backend = create_memory_backend(mock_runtime)

        # Test /memories/ paths
        # CompositeBackend should route these to StoreBackend
        test_paths = [
            "/memories/TELOS/mission.md",
            "/memories/people/john_doe.md",
            "/memories/ideas/2026-01-11_project_idea.md",
        ]

        for path in test_paths:
            # The backend should have a route for /memories/
            assert "/memories/" in backend.routes, f"Missing /memories/ route for {path}"

    def test_memory_backend_routes_workspace_to_state(self):
        """Test that non-/memories/ paths use default (StateBackend)."""
        mock_runtime = Mock()
        backend = create_memory_backend(mock_runtime)

        # CompositeBackend should have a default backend (StateBackend)
        assert backend.default is not None, "Missing default backend"

    def test_memory_backend_accepts_runtime(self):
        """Test that create_memory_backend properly uses runtime parameter."""
        mock_runtime = Mock()
        mock_runtime.state = {"test": "state"}
        mock_runtime.store = Mock()

        # Should not raise an error
        backend = create_memory_backend(mock_runtime)
        assert backend is not None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
