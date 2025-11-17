"""
Configuration settings for Whaley Law Firm Legal Agent.
Loads environment variables and constructs database connection strings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_setting(key: str, default: str | None = None) -> str:
    """
    Safely retrieve environment variable with optional default.

    Args:
        key: Environment variable name
        default: Default value if variable not set

    Returns:
        Environment variable value or default

    Raises:
        ValueError: If variable not set and no default provided
    """
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Required environment variable {key} not set")
    return value

# Database connection string for PostgreSQL (Supabase)
# Used by PostgresSaver (checkpointer) and PostgresStore (memory storage)
DB_URI = get_setting(
    "POSTGRES_CONNECTION_STRING",
    default=None  # Will raise ValueError if not set
)
