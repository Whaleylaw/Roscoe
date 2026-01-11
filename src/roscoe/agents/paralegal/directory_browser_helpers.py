"""
Helper functions for directory browser tool.
Handles directory traversal, filtering, sorting.
"""
from pathlib import Path
from typing import Dict, List, Optional, Literal, Tuple


def should_skip_item(
    path: Path,
    show_hidden: bool = False,
    file_extensions: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
) -> bool:
    """
    Determine if an item should be skipped during traversal.

    Args:
        path: Path to check
        show_hidden: Whether to include hidden files (starting with .)
        file_extensions: If provided, only include files with these extensions (folders always included)
        exclude_patterns: Patterns to exclude (e.g., ["__pycache__", "*.pyc"])

    Returns:
        True if item should be skipped
    """
    name = path.name

    # Skip hidden files unless explicitly requested
    if not show_hidden and name.startswith('.'):
        return True

    # Check exclude patterns
    if exclude_patterns:
        for pattern in exclude_patterns:
            if pattern in name or (pattern.startswith('*') and name.endswith(pattern[1:])):
                return True

    # For files, check extension filter
    # Note: We check if path has extension or is actually a file
    # to handle both real paths and test paths
    if file_extensions:
        # Only apply extension filter if this appears to be a file
        # (has an extension or exists as a file on disk)
        has_extension = bool(path.suffix)
        is_actual_file = path.exists() and path.is_file()
        is_actual_dir = path.exists() and path.is_dir()

        # Skip if it's a file (or looks like one) with wrong extension
        # But never skip directories
        if not is_actual_dir and (has_extension or is_actual_file):
            ext = path.suffix[1:].lower() if path.suffix else ''
            if ext not in file_extensions:
                return True

    return False


def build_directory_tree(
    path: Path,
    max_depth: int,
    current_depth: int = 0,
    show_hidden: bool = False,
    file_extensions: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    sort_by: Literal["name", "modified", "size"] = "name",
) -> Dict:
    """
    Recursively build directory tree structure.

    Args:
        path: Root path to traverse
        max_depth: Maximum depth to traverse
        current_depth: Current depth (internal)
        show_hidden: Include hidden files
        file_extensions: Filter by extensions
        exclude_patterns: Patterns to exclude
        sort_by: Sort criterion

    Returns:
        Dict representing tree node
    """
    node = {
        'path': str(path),
        'name': path.name,
        'type': 'folder' if path.is_dir() else 'file',
    }

    if path.is_file():
        # Add file metadata
        stat = path.stat()
        node['size'] = stat.st_size
        node['modified'] = stat.st_mtime
        ext = path.suffix[1:].lower() if path.suffix else ''
        if ext:
            node['extension'] = ext
        return node

    # For directories, recurse if within depth limit
    if current_depth >= max_depth:
        return node

    children = []
    try:
        for item in path.iterdir():
            if should_skip_item(item, show_hidden, file_extensions, exclude_patterns):
                continue

            child = build_directory_tree(
                item,
                max_depth,
                current_depth + 1,
                show_hidden,
                file_extensions,
                exclude_patterns,
                sort_by,
            )
            children.append(child)
    except PermissionError:
        # Skip directories without read permission
        pass

    # Sort children
    if sort_by == "name":
        children.sort(key=lambda x: (x['type'] == 'file', x['name'].lower()))
    elif sort_by == "modified":
        children.sort(key=lambda x: (x['type'] == 'file', -x.get('modified', 0)))
    elif sort_by == "size":
        children.sort(key=lambda x: (x['type'] == 'file', -x.get('size', 0)))

    if children:
        node['children'] = children

    return node


def count_items(tree: Dict) -> Tuple[int, int]:
    """
    Count total files and folders in tree.

    Args:
        tree: Tree structure from build_directory_tree

    Returns:
        Tuple of (file_count, folder_count)
    """
    if tree['type'] == 'file':
        return (1, 0)

    file_count = 0
    folder_count = 1  # Count this folder

    for child in tree.get('children', []):
        f, d = count_items(child)
        file_count += f
        folder_count += d

    return (file_count, folder_count)
