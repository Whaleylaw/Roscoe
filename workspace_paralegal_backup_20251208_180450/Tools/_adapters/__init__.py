"""
Case Data Adapters

Unified interface for reading/writing to existing JSON data structures.
"""

from .case_data import CaseData, get_workspace_path, get_database_path

__all__ = ["CaseData", "get_workspace_path", "get_database_path"]

