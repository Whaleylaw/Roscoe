"""Tests for directory browser functionality."""
import pytest
from pathlib import Path
from roscoe.agents.paralegal.directory_browser_helpers import (
    build_directory_tree,
    count_items,
    should_skip_item,
)


def test_build_directory_tree_single_level(tmp_path):
    """Test building tree for flat directory."""
    # Create test structure
    (tmp_path / "file1.txt").write_text("test")
    (tmp_path / "file2.pdf").write_text("test")
    (tmp_path / "folder1").mkdir()

    tree = build_directory_tree(tmp_path, max_depth=1, current_depth=0)

    assert tree['type'] == 'folder'
    assert tree['name'] == tmp_path.name
    assert 'children' in tree
    assert len(tree['children']) == 3


def test_build_directory_tree_respects_depth(tmp_path):
    """Test max_depth limit."""
    # Create nested structure
    level1 = tmp_path / "level1"
    level1.mkdir()
    level2 = level1 / "level2"
    level2.mkdir()
    (level2 / "deep_file.txt").write_text("test")

    tree = build_directory_tree(tmp_path, max_depth=1, current_depth=0)

    # Should have level1 but not level2
    assert len(tree['children']) == 1
    level1_node = tree['children'][0]
    assert level1_node['name'] == 'level1'
    assert 'children' not in level1_node or len(level1_node.get('children', [])) == 0


def test_should_skip_hidden_files():
    """Test hidden file filtering."""
    assert should_skip_item(Path(".hidden"), show_hidden=False) == True
    assert should_skip_item(Path(".hidden"), show_hidden=True) == False
    assert should_skip_item(Path("visible.txt"), show_hidden=False) == False


def test_should_skip_by_extension():
    """Test extension filtering."""
    assert should_skip_item(
        Path("file.pdf"),
        file_extensions=["txt", "md"],
        show_hidden=False
    ) == True
    assert should_skip_item(
        Path("file.txt"),
        file_extensions=["txt", "md"],
        show_hidden=False
    ) == False


def test_count_items():
    """Test counting files and folders."""
    tree = {
        'type': 'folder',
        'children': [
            {'type': 'file', 'name': 'f1.txt'},
            {'type': 'file', 'name': 'f2.txt'},
            {
                'type': 'folder',
                'name': 'sub',
                'children': [
                    {'type': 'file', 'name': 'f3.txt'}
                ]
            }
        ]
    }

    files, folders = count_items(tree)
    assert files == 3
    assert folders == 2  # root + sub
