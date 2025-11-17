# Archive Directory

This directory contains historical documentation and test files from the development process.

## Contents

### `debugging/`
Historical troubleshooting and debugging documentation from the development process:

- **FIX_ATTEMPT_*.md** - Step-by-step troubleshooting attempts for various issues
- **MCP_TOOL_SIGNATURE_ERROR.md** - Documentation of MCP tool signature resolution
- **POSTGREST_QUERY_ERROR.md** - PostgREST query formatting issues
- **RESOLUTION_SUMMARY.md** - Summary of resolved issues
- **INVESTIGATION_FINDINGS.md** - Investigation notes and findings
- **FINAL_RESOLUTION.md** - Final resolution documentation
- **STATUS.md** - Development status snapshots
- **IMPLEMENTATION-COMPLETE.md** - Implementation completion documentation
- **MIGRATION_ANALYSIS.md** - Frontend migration analysis

These files are preserved for:
- Historical reference of problem-solving approaches
- Understanding design decisions and trade-offs
- Future troubleshooting of similar issues

### `tests/`
Test scripts used during development:

- **test_agent.py** - Agent functionality tests
- **test_api.py** - API endpoint tests
- **test_elevenlabs.py** - ElevenLabs TTS integration tests
- **test_supabase_api.py** - Supabase API tests
- **test_tool_invocation.py** - Tool invocation tests

These scripts were used to verify functionality during development and may be useful for:
- Understanding how components were tested
- Creating new test cases
- Debugging regressions

## Why Archive?

These files were moved from the root directory to keep the repository clean and focused on production code. They are preserved (not deleted) because:

1. They document the development journey and problem-solving process
2. They may be useful for future debugging or understanding design decisions
3. They provide context for why certain implementation choices were made
4. They can serve as templates for future troubleshooting documentation

## Organization

This archive was created on 2025-11-16 as part of preparing the repository for GitHub publication.
