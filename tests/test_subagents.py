"""
Deep Agent Coder - Subagent Configuration Tests

Tests for the subagent configurations in subagents.py.
"""

import pytest

from deep_agent_coder.subagents import get_subagents


class TestGetSubagents:
    """Tests for get_subagents function."""

    def test_get_subagents_returns_list(self):
        """Test that get_subagents returns a list."""
        subagents = get_subagents()

        assert isinstance(subagents, list)

    def test_get_subagents_returns_four_subagents(self):
        """Test that get_subagents returns exactly 4 subagents."""
        subagents = get_subagents()

        assert len(subagents) == 4

    def test_get_subagents_accepts_model_parameter(self):
        """Test that get_subagents accepts custom model parameter."""
        custom_model = "claude-opus-4-20250514"
        subagents = get_subagents(model=custom_model)

        assert len(subagents) == 4
        for subagent in subagents:
            assert subagent["model"] == custom_model


class TestSubagentRequiredFields:
    """Tests for required fields in subagent configurations."""

    def test_all_subagents_have_name(self):
        """Test that all subagents have a 'name' field."""
        subagents = get_subagents()

        for subagent in subagents:
            assert "name" in subagent
            assert isinstance(subagent["name"], str)
            assert len(subagent["name"]) > 0

    def test_all_subagents_have_description(self):
        """Test that all subagents have a 'description' field."""
        subagents = get_subagents()

        for subagent in subagents:
            assert "description" in subagent
            assert isinstance(subagent["description"], str)
            assert len(subagent["description"]) > 0

    def test_all_subagents_have_system_prompt(self):
        """Test that all subagents have a 'system_prompt' field."""
        subagents = get_subagents()

        for subagent in subagents:
            assert "system_prompt" in subagent
            assert isinstance(subagent["system_prompt"], str)
            assert len(subagent["system_prompt"]) > 100  # Should be substantial

    def test_all_subagents_have_tools(self):
        """Test that all subagents have a 'tools' field."""
        subagents = get_subagents()

        for subagent in subagents:
            assert "tools" in subagent
            assert isinstance(subagent["tools"], list)

    def test_all_subagents_have_model(self):
        """Test that all subagents have a 'model' field."""
        subagents = get_subagents()

        for subagent in subagents:
            assert "model" in subagent
            assert isinstance(subagent["model"], str)


class TestSubagentNames:
    """Tests for subagent names."""

    def test_subagent_names_are_correct(self):
        """Test that subagent names are coder, tester, reviewer, fixer."""
        subagents = get_subagents()
        names = [s["name"] for s in subagents]

        expected_names = ["coder", "tester", "reviewer", "fixer"]
        assert names == expected_names

    def test_subagent_names_are_unique(self):
        """Test that all subagent names are unique."""
        subagents = get_subagents()
        names = [s["name"] for s in subagents]

        assert len(names) == len(set(names))

    def test_coder_subagent_exists(self):
        """Test that coder subagent exists with correct structure."""
        subagents = get_subagents()
        coder = next((s for s in subagents if s["name"] == "coder"), None)

        assert coder is not None
        assert "implement" in coder["description"].lower() or "code" in coder["description"].lower()

    def test_tester_subagent_exists(self):
        """Test that tester subagent exists with correct structure."""
        subagents = get_subagents()
        tester = next((s for s in subagents if s["name"] == "tester"), None)

        assert tester is not None
        assert "test" in tester["description"].lower() or "verif" in tester["description"].lower()

    def test_reviewer_subagent_exists(self):
        """Test that reviewer subagent exists with correct structure."""
        subagents = get_subagents()
        reviewer = next((s for s in subagents if s["name"] == "reviewer"), None)

        assert reviewer is not None
        assert "review" in reviewer["description"].lower() or "quality" in reviewer["description"].lower()

    def test_fixer_subagent_exists(self):
        """Test that fixer subagent exists with correct structure."""
        subagents = get_subagents()
        fixer = next((s for s in subagents if s["name"] == "fixer"), None)

        assert fixer is not None
        assert "fix" in fixer["description"].lower() or "bug" in fixer["description"].lower()


class TestSubagentDescriptions:
    """Tests for subagent descriptions quality."""

    def test_descriptions_are_meaningful(self):
        """Test that descriptions are meaningful (>50 chars)."""
        subagents = get_subagents()

        for subagent in subagents:
            assert len(subagent["description"]) > 50, \
                f"{subagent['name']} description is too short"

    def test_system_prompts_are_comprehensive(self):
        """Test that system prompts are comprehensive (>500 chars)."""
        subagents = get_subagents()

        for subagent in subagents:
            assert len(subagent["system_prompt"]) > 500, \
                f"{subagent['name']} system_prompt is too short"


class TestSubagentImports:
    """Tests for subagent module imports."""

    def test_import_get_subagents(self):
        """Test that get_subagents can be imported from package."""
        from deep_agent_coder import get_subagents as imported_func

        assert imported_func is not None
        assert callable(imported_func)

    def test_import_from_subagents_module(self):
        """Test direct import from subagents module."""
        from deep_agent_coder.subagents import get_subagents as direct_import

        assert direct_import is not None
        assert callable(direct_import)
