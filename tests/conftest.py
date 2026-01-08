"""
Pytest configuration for Roscoe tests.

Loads environment variables from .env file for tests.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def pytest_configure(config):
    """Load environment variables before running tests."""
    # Look for .env file in project root
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"

    if env_file.exists():
        load_dotenv(env_file)
    else:
        # Try .env.example if .env doesn't exist
        env_example = project_root / ".env.example"
        if env_example.exists():
            # For testing, we can use placeholder values if real .env doesn't exist
            # In production, tests should use real credentials
            pass
