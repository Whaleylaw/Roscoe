# Natural Language Plan: src/config/settings.py

## File Purpose

This file exists to centralize all environment variable access and configuration management for the backend DeepAgent system. It loads the `.env` file, constructs the PostgreSQL connection string from Supabase credentials, and provides safe access to all configuration values needed by other modules.

This file participates as a dependency for `src/agents/legal_agent.py` and `src/mcp/clients.py`, ensuring they have validated access to API keys and database credentials.

## Imports We Will Need (and Why)

001: Import `os` module to access environment variables via `os.getenv()` for reading API keys and credentials from system environment.

002: Import `dotenv` library's `load_dotenv` function to automatically load variables from `.env` file into environment, enabling local development without system-wide environment variable setup.

003: Import `typing.Optional` to type hint the `get_setting` function's return value, indicating it may return None if setting not found.

## Objects We Will Define

### Function: `load_dotenv()`
**Purpose**: Load environment variables from `.env` file into `os.environ`
**Inputs**: None (implicitly looks for `.env` in current directory or parents)
**Outputs**: None (side effect: populates `os.environ`)
**Side effects**: Modifies global `os.environ` dictionary with values from `.env` file

### Constant: `DB_URI`
**Purpose**: Provide ready-to-use PostgreSQL connection string for Supabase
**Inputs**: None (reads from environment via os.getenv)
**Outputs**: String in format `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`
**Side effects**: None (read-only)

### Function: `get_setting(key: str, default: Optional[str] = None) -> Optional[str]`
**Purpose**: Safely retrieve environment variable with optional default value
**Inputs**:
- `key`: Environment variable name (string)
- `default`: Optional default value if key not found (string or None)
**Outputs**: Environment variable value (string) or default value (string or None)
**Side effects**: None (read-only access to os.environ)

### Function: `validate_required_settings() -> None`
**Purpose**: Check that all required environment variables are present, raise error if missing
**Inputs**: None
**Outputs**: None (raises ValueError if validation fails)
**Side effects**: None if valid; raises exception if invalid

##

 Line-by-Line Natural Language Plan

[defines: load_dotenv @ src/config/settings.py (planned line 001)]
001: Call load_dotenv function from dotenv library to load environment variables from dot env file into OS environment for local development configuration access.

[defines: DB_URI @ src/config/settings.py (planned lines 002-010)]
002: Retrieve SUPABASE_URL environment variable and extract the host portion by removing the https protocol prefix to construct database connection string.

003: Retrieve SUPABASE_SERVICE_ROLE_KEY environment variable which contains the PostgreSQL password for service role access bypassing Row Level Security.

004: Retrieve database password from SUPABASE_SERVICE_ROLE_KEY using string parsing or direct use depending on format documentation specifies.

005: Extract Supabase project reference from URL to construct database host in format db dot project-ref dot supabase dot co.

006: Construct PostgreSQL connection string using format postgresql colon slash slash postgres colon password at host colon five-four-three-two slash postgres.

007: Assign constructed connection string to module-level constant DB_URI for import by other modules requiring database access.

008: Add inline comment explaining DB_URI format and its use for both checkpointer and store connections to single Supabase database.

009: Validate DB_URI is not empty string before export to prevent runtime connection errors in dependent modules.

010: Log successful database URI construction at debug level for troubleshooting connection issues during development.

[defines: get_setting @ src/config/settings.py (planned lines 011-016)]
011: Define function get_setting with parameters key as string and default as optional string defaulting to None for safe environment variable access.

012: Inside get_setting function call os dot getenv with key parameter to retrieve environment variable value from OS environment.

013: If os dot getenv returns None meaning environment variable not set then return the default parameter value to caller.

014: If os dot getenv returns a value then return that value directly to caller without modification.

015: Add docstring to get_setting function explaining purpose, parameters, return value, and usage example for API key retrieval.

016: Add type hints to function signature using typing module's Optional for return type indicating may return None if no default provided and key missing.

[defines: validate_required_settings @ src/config/settings.py (planned lines 017-035)]
017: Define function validate_required_settings with no parameters to verify all critical environment variables are present.

018: Create list of required setting names including ANTHROPIC_API_KEY for Claude model access as first required key.

019: Append SUPABASE_URL to required settings list as database connection requires valid Supabase project URL.

020: Append SUPABASE_SERVICE_ROLE_KEY to required settings list as service role key needed for backend database operations.

021: Append POSTGRES_CONNECTION_STRING to required settings list as alternative to constructed DB_URI if user prefers explicit connection string.

022: Create empty list called missing to accumulate names of required settings that are not present in environment.

023: Iterate over required settings list using for loop to check each setting individually.

024: For each setting name call get_setting function with that name and no default to check if it exists.

025: If get_setting returns None for a required setting then append that setting name to missing list.

026: After checking all required settings check if missing list has any elements indicating validation failure.

027: If missing list is not empty then construct error message listing all missing settings in human-readable format.

028: Raise ValueError with constructed error message to halt application startup and inform user of configuration problem.

029: If missing list is empty log success message at info level indicating all required settings validated successfully.

030: Add docstring to validate_required_settings function explaining it raises ValueError if any required settings missing.

031: Note in docstring that function should be called at application startup before any database or API connections attempted.

032: Document in comment that TAVILY_API_KEY, GMAIL_CREDENTIALS, and GOOGLE_CALENDAR_CREDENTIALS are optional for MVP functionality.

033: Add inline comment explaining that validation allows graceful degradation if optional services unavailable but enforces critical services.

034: Include example in docstring showing how to call validate_required_settings in main application entry point.

035: Ensure function returns None on success so it can be called for side effect of validation without needing to capture return value.

## Module Initialization

036: At module level after all function definitions call validate_required_settings to perform validation when module first imported.

037: Wrap validate_required_settings call in try-except block to provide more helpful error message if validation fails during import.

038: In except block catch ValueError and re-raise with additional context about checking dot env file and environment variable setup.

039: Log at info level the successful loading and validation of configuration settings module.

040: Export DB_URI, get_setting function, and validate_required_settings function for use by dependent modules via module namespace.

## Cross-References

[uses: os.getenv @ os (standard library)]
[uses: load_dotenv @ dotenv (external dependency)]
[uses: Optional @ typing (standard library)]

[defines: DB_URI @ src/config/settings.py (planned lines 002-010)]
[defines: get_setting @ src/config/settings.py (planned lines 011-016)]
[defines: validate_required_settings @ src/config/settings.py (planned lines 017-035)]

## Notes & Assumptions

- Assumes `.env` file exists in project root or parent directory for `load_dotenv()` to find
- Assumes Supabase URL format is `https://[project-ref].supabase.co`
- Assumes database host format is `db.[project-ref].supabase.co:5432`
- Service role key may be used directly as password or may need parsing depending on Supabase SDK version
- POSTGRES_CONNECTION_STRING can override constructed DB_URI if user prefers explicit configuration
- File has no external file dependencies beyond `.env` file
- Validation happens at module import time to fail fast if configuration invalid
- Optional settings (Tavily, Gmail, Calendar) allow graceful degradation per architecture error handling strategy
- Module is pure functions and constants, no classes or stateful objects
