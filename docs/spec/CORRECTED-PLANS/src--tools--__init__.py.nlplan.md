# Natural Language Plan: src/tools/__init__.py

**Status**: Planning Phase - No code written yet
**Purpose**: Python package initialization for tools module
**Approval Required**: "Approves, spec"

---

## File Purpose

This file makes `src/tools/` a proper Python package, allowing imports like `from src.tools.toolkits import gmail_tools`. It optionally exports key functions and objects for convenience but primarily serves as the package marker for Python's import system.

This file participates as the package initializer for the tools module, enabling `src.agents.legal_agent` to import toolkit initialization functions and tool lists.

---

## Imports We Will Need (and Why)

**No imports needed** - This is a minimal package initializer. We export symbols from submodules but don't need to import anything at this level.

---

## Objects We Will Define

### Module-level: `__all__`
**Purpose**: Explicitly declare public API of the tools package
**Type**: List[str]
**Contents**: Names of functions/objects exported from this package
**Side effects**: Controls what `from src.tools import *` would import (though we don't use star imports)

---

## Line-by-Line Natural Language Plan

[defines: package_init @ src/tools/__init__.py (planned lines 001-010)]

001: Create empty file as Python package marker allowing src dot tools to be imported as a module in the agent code.

002: Add docstring explaining this is the tools package containing toolkit initialization functions and code execution wrapper classes.

003: Define module-level dunder all list to declare the public API of this package for documentation and import control purposes.

004: Include string "init_gmail_toolkit" in dunder all list as a key export from toolkits submodule [uses: init_gmail_toolkit @ src/tools/toolkits.py (planned lines 015-045)].

005: Include string "init_calendar_toolkit" in dunder all list as key export from toolkits submodule [uses: init_calendar_toolkit @ src/tools/toolkits.py (planned lines 047-077)].

006: Include string "init_supabase_mcp" in dunder all list as key export from toolkits submodule [uses: init_supabase_mcp @ src/tools/toolkits.py (planned lines 079-109)].

007: Include string "init_tavily_mcp" in dunder all list as key export from toolkits submodule [uses: init_tavily_mcp @ src/tools/toolkits.py (planned lines 111-141)].

008: Include string "RunLoopExecutor" in dunder all list as key export from runloop executor submodule [uses: RunLoopExecutor @ src/tools/runloop_executor.py (planned lines 015-095)].

009: Add comment explaining that actual imports happen in dependent modules not in this init file to avoid circular dependencies.

010: Add comment with usage example showing how to import: "from src dot tools dot toolkits import init gmail toolkit".

---

## Cross-References

**Exports from this package:**
- [defines: __all__ @ src/tools/__init__.py (planned line 003)]

**References to submodules:**
- [uses: init_gmail_toolkit @ src/tools/toolkits.py (planned lines 015-045)]
- [uses: init_calendar_toolkit @ src/tools/toolkits.py (planned lines 047-077)]
- [uses: init_supabase_mcp @ src/tools/toolkits.py (planned lines 079-109)]
- [uses: init_tavily_mcp @ src/tools/toolkits.py (planned lines 111-141)]
- [uses: RunLoopExecutor @ src/tools/runloop_executor.py (planned lines 015-095)]

**Used by:**
- [used_by: src/agents/legal_agent.py @ import statement (planned line 009)]

---

## Notes & Assumptions

- **Minimal initialization**: This is deliberately kept minimal to avoid circular imports
- **No explicit re-exports**: We list symbols in `__all__` but don't actually import and re-export them here
- **Import pattern**: Dependent modules import directly from submodules (`from src.tools.toolkits import ...`)
- **Future extensibility**: Additional toolkit initialization functions can be added to `__all__` without breaking existing imports
- **No external dependencies**: Pure Python package initialization
- **File size**: Should be under 15 lines of actual code
