# Natural Language Plan: src/tools/runloop_executor.py

**Status**: Planning Phase - No code written yet
**Purpose**: Wrapper for RunLoop API to provide sandboxed Python code execution
**Approval Required**: "Approves, spec"

---

## File Purpose

This file creates a tool wrapper around the RunLoop API to execute Python code in isolated sandbox environments (devboxes). It replaces the deprecated PythonREPLTool with a secure, production-ready code execution solution that runs code in separate containers with resource limits, timeouts, and proper error handling.

This file participates as a critical tool provider for the agent's skills-first workflow, enabling safe execution of data processing code and skill scripts in isolated environments.

---

## Imports We Will Need (and Why)

001: Import Runloop class from runloop underscore api underscore client package to interact with RunLoop sandboxed execution API for creating devboxes and running code [Citation: https://github.com/runloopai/api-client-python].

002: Import os module from standard library to access RUNLOOP underscore API underscore KEY environment variable for API authentication.

003: Import logging module from standard library to log devbox creation, execution events, and errors for debugging and monitoring purposes.

004: Import Optional and Dict types from typing module to provide type hints for function parameters and return values ensuring type safety.

005: Import tool decorator from langchain underscore core dot tools to convert the executor class into a LangChain tool that the agent can invoke [Citation: https://python.langchain.com/docs/modules/tools/custom_tools].

---

## Objects We Will Define

### Class: `RunLoopExecutor`
**Purpose**: Wrapper class providing LangChain tool interface for RunLoop code execution
**Methods**:
- `__init__()` - Initialize RunLoop client
- `execute_code(code: str, timeout: int = 60) -> Dict` - Execute Python code in devbox
- `_create_devbox() -> str` - Create and return devbox ID
- `_cleanup_devbox(devbox_id: str)` - Clean up devbox after execution
**Side effects**: Creates/destroys devboxes via RunLoop API

### Function: `create_runloop_tool()`
**Purpose**: Factory function to create a LangChain-compatible tool from RunLoopExecutor
**Inputs**: None
**Outputs**: BaseTool (LangChain tool)
**Side effects**: None (creates tool instance)

---

## Line-by-Line Natural Language Plan

[defines: imports @ src/tools/runloop_executor.py (planned lines 001-010)]

001: Import Runloop class from runloop underscore api underscore client package as the main client for interacting with RunLoop sandbox API per official SDK documentation.

002: Import os module to read RUNLOOP underscore API underscore KEY environment variable which is automatically loaded by Runloop client for authentication without explicit passing.

003: Import logging module to create logger instance for recording devbox lifecycle events code execution results and any errors that occur during execution.

004: Import Optional and Dict from typing module to provide type annotations for nullable return values and dictionary structures used in execution results.

005: Import tool decorator from langchain underscore core dot tools to mark execute underscore code method as a LangChain tool making it discoverable by the agent.

006: Import BaseException from standard library to catch all possible exceptions during code execution including timeouts and API errors for comprehensive error handling.

007: Get logger instance by calling logging dot getLogger with dunder name to create module-specific logger for RunLoop executor operations.

008: Add module-level docstring explaining this file provides RunLoop-based sandboxed Python code execution replacing PythonREPLTool with production-ready isolation.

009: Add comment with citation to RunLoop API client GitHub repository for reference: https colon slash slash github dot com slash runloopai slash api-client-python.

010: Add comment explaining that Runloop client automatically loads API key from RUNLOOP underscore API underscore KEY environment variable per SDK behavior.

[defines: RunLoopExecutor @ src/tools/runloop_executor.py (planned lines 011-095)]

011: Define class named RunLoopExecutor to encapsulate all RunLoop code execution logic providing clean interface for agent tool usage.

012: Add class docstring explaining RunLoopExecutor provides sandboxed Python code execution via RunLoop API with automatic devbox management and error handling.

013: Define dunder init method with self parameter to initialize RunLoop client and set up execution environment when executor instance created.

014: Inside dunder init call Runloop constructor to create client instance which automatically loads RUNLOOP underscore API underscore KEY from environment per SDK design.

015: Assign Runloop client instance to self dot client for use in execute underscore code and helper methods throughout class lifecycle.

016: Log info message stating RunLoop executor initialized successfully to confirm client creation without errors.

017: Add instance variable self dot current underscore devbox underscore id initialized to None to track active devbox for cleanup if execution fails midway.

018: Add try-except block around client initialization to catch authentication errors if RUNLOOP underscore API underscore KEY missing or invalid.

019: In except block log error with details and raise RuntimeError with message RunLoop API key not configured or invalid to fail fast on misconfiguration.

020: Close dunder init method ensuring RunLoopExecutor instance fully initialized with working client before any code execution attempted.

[defines: execute_code method @ src/tools/runloop_executor.py (planned lines 021-065)]

021: Define execute underscore code method with self parameter code parameter as string and timeout parameter as integer defaulting to 60 seconds.

022: Add tool decorator above method signature with name parameter set to runloop underscore execute underscore code and description explaining sandboxed Python execution.

023: Add method docstring explaining execute underscore code runs Python code in isolated RunLoop devbox returns dictionary with stdout stderr and exit status.

024: Add docstring parameters section documenting code parameter as Python code string to execute and timeout parameter as maximum seconds before termination.

025: Add docstring returns section specifying dictionary with keys stdout stderr exit underscore status and success for execution result parsing by agent.

026: Start try block to wrap all execution logic ensuring errors caught and returned as structured results rather than raising exceptions to agent.

027: Log info message with code preview first 100 characters to record what code is being executed for debugging and audit trail purposes.

028: Call self dot underscore create underscore devbox method to provision isolated execution environment and assign returned devbox ID to variable.

029: Assign devbox ID to self dot current underscore devbox underscore id for cleanup tracking in case of errors or interruptions during execution.

030: Log info message with devbox ID to record which sandbox environment was created for this execution correlating with RunLoop dashboard logs.

031: Call self dot client dot devboxes dot write underscore file underscore contents passing devbox ID file underscore path equals execute dot py and contents equals code parameter.

032: This writes the Python code to a file named execute dot py inside the devbox filesystem preparing it for command line execution via python command.

033: Log debug message stating code written to devbox file system to confirm file write operation succeeded before attempting execution step.

034: Call self dot client dot devboxes dot execute passing devbox ID and command equals python execute dot py to run the written Python code.

035: Assign execution result to variable named result which contains exit underscore status stdout stderr attributes per RunLoop API response structure.

036: Check if result dot exit underscore status equals zero indicating successful execution with no errors or non-zero return code from Python script.

037: If exit status zero log info message Code executed successfully with output length to record successful execution without logging full potentially large output.

038: Construct return dictionary with success equals True stdout equals result dot stdout stderr equals result dot stderr exit underscore status equals 0.

039: If exit status non-zero log warning message Code execution failed with exit status and error preview to alert of execution failure.

040: Construct return dictionary with success equals False stdout equals result dot stdout stderr equals result dot stderr exit underscore status equals result dot exit underscore status.

041: After execution block call self dot underscore cleanup underscore devbox passing devbox ID to destroy sandbox freeing resources and preventing orphaned devboxes.

042: Set self dot current underscore devbox underscore id back to None after cleanup to clear tracking variable indicating no active devbox.

043: Return the constructed result dictionary to agent allowing it to see execution output and success status for next step decision making.

044: Define except TimeoutError block to catch execution timeout if code runs longer than specified timeout parameter value in seconds.

045: In timeout except block log error message Code execution timeout after timeout seconds to record that execution was terminated due to time limit.

046: Return dictionary with success equals False error equals Execution timeout message stdout equals empty stderr equals timeout error for agent to understand timeout occurred.

047: Define except Exception as e block to catch all other errors API failures network issues invalid code syntax errors et cetera.

048: In general except block log error message Code execution error with exception details using str e for error message recording.

049: If self dot current underscore devbox underscore id is not None attempt cleanup even after error to avoid orphaned devboxes consuming resources.

050: Return dictionary with success equals False error equals str e message stdout equals empty stderr equals exception details for agent error handling.

051: Add finally block to ensure cleanup always attempted even if exception occurs during return statement construction or other unexpected failures.

052: In finally block if self dot current underscore devbox underscore id not None call cleanup method to guarantee devbox destruction in all code paths.

053: Add inline comment that finally cleanup is safety net as normal flow already cleans up but ensures no devbox left running on errors.

054: Close execute underscore code method returning structured result dictionary in all cases never raising exceptions that would crash agent execution loop.

055: Add method-level comment explaining that returning error dictionary instead of raising exception allows agent to retry with modified code or different approach.

[defines: _create_devbox helper @ src/tools/runloop_executor.py (planned lines 056-070)]

056: Define private helper method underscore create underscore devbox with self parameter to encapsulate devbox creation logic for cleaner execute underscore code method.

057: Add method docstring explaining underscore create underscore devbox creates new RunLoop devbox waits for running state and returns devbox ID string.

058: Call self dot client dot devboxes dot create underscore and underscore await underscore running to create devbox and block until fully initialized per RunLoop API.

059: Assign returned devbox object to variable named devbox which contains id attribute and other metadata about created sandbox environment.

060: Log info message Created devbox with ID devbox dot id to record successful devbox creation with unique identifier for tracking.

061: Add validation check if devbox dot id is None or empty string raise RuntimeError Failed to create devbox no ID returned for error handling.

062: Return devbox dot id string value to caller execute underscore code method which will use ID for file writing and execution commands.

063: Define except block to catch devbox creation failures such as API errors quota exceeded or service unavailable conditions.

064: Log error message Devbox creation failed with exception details to record why creation failed for debugging RunLoop API issues.

065: Raise RuntimeError with message Failed to create RunLoop devbox and exception details to propagate error to execute underscore code except handler.

066: Add comment explaining that create underscore and underscore await underscore running blocks until devbox ready so no additional polling needed unlike async devbox dot wait underscore until.

067: Add comment that devbox remains running until explicitly destroyed via cleanup method so must ensure cleanup always called to avoid resource leaks.

068: Note in comment that devbox has default resource limits CPU memory disk set by RunLoop account configuration not controllable per-devbox currently.

069: Close underscore create underscore devbox method returning string devbox ID for use in subsequent write and execute operations.

070: Add inline comment that method name prefixed with underscore to indicate private helper not intended for direct external calls.

[defines: _cleanup_devbox helper @ src/tools/runloop_executor.py (planned lines 071-085)]

071: Define private helper method underscore cleanup underscore devbox with self and devbox underscore id string parameter to encapsulate cleanup logic.

072: Add method docstring explaining underscore cleanup underscore devbox destroys RunLoop devbox freeing resources with optional graceful failure if devbox already gone.

073: Start try block to wrap cleanup operations allowing graceful handling if devbox already destroyed or API unavailable.

074: Call self dot client dot devboxes dot stop passing devbox underscore id to shutdown devbox gracefully before destruction per RunLoop best practices.

075: Log debug message Stopped devbox devbox underscore id to record shutdown operation completed successfully.

076: Call self dot client dot devboxes dot delete passing devbox underscore id to permanently remove devbox and free all associated resources.

077: Log info message Cleaned up devbox devbox underscore id to confirm successful deletion and resource reclamation.

078: Define except Exception as e block to catch cleanup failures such as devbox already deleted network error or API unavailable.

079: Log warning message Failed to cleanup devbox but continuing with exception details since cleanup failure non-critical if devbox already gone.

080: Do not raise exception from cleanup method as cleanup is best-effort operation that should not crash main execution flow.

081: Add comment explaining that cleanup failures are logged but not raised because devbox may have auto-terminated or been deleted externally.

082: Add comment that RunLoop has automatic garbage collection of old devboxes so manual cleanup failure does not leak resources permanently.

083: Close underscore cleanup underscore devbox method returning None in all cases whether cleanup succeeded or failed.

084: Add inline comment that method name prefixed with underscore to indicate private helper not part of public tool interface.

085: Note that cleanup is idempotent can be safely called multiple times on same devbox ID without errors due to exception handling.

[defines: create_runloop_tool factory @ src/tools/runloop_executor.py (planned lines 086-095)]

086: Define module-level function create underscore runloop underscore tool with no parameters to serve as factory for creating tool instance.

087: Add function docstring explaining create underscore runloop underscore tool instantiates RunLoopExecutor and returns it as LangChain-compatible tool for agent use.

088: Inside function create instance of RunLoopExecutor class by calling RunLoopExecutor constructor which initializes RunLoop client.

089: Assign executor instance to variable named executor for wrapping in tool decorator or returning directly depending on tool integration pattern.

090: Return executor instance directly as the tool decorator on execute underscore code method already makes it LangChain-compatible tool.

091: Add comment explaining that tool decorator on execute underscore code method provides LangChain tool interface so no additional wrapping needed.

092: Add usage example in comment showing how to import and use: from src dot tools dot runloop underscore executor import create underscore runloop underscore tool.

093: Add comment that function allows lazy initialization of RunLoop client only when tool actually added to agent avoiding startup cost if not used.

094: Close create underscore runloop underscore tool function returning configured executor instance ready for agent tools list.

095: Add module-level comment at end noting that executor can be reused across multiple code execution calls as devboxes created per execution not per instance.

---

## Cross-References

**Imports:**
- [uses: Runloop @ runloop_api_client (external package)]
- [uses: tool decorator @ langchain_core.tools (external package)]
- [uses: os @ Python stdlib]
- [uses: logging @ Python stdlib]
- [uses: typing.Optional, typing.Dict @ Python stdlib]

**Exports:**
- [defines: RunLoopExecutor @ src/tools/runloop_executor.py (planned lines 011-095)]
- [defines: execute_code @ src/tools/runloop_executor.py (planned lines 021-054)]
- [defines: create_runloop_tool @ src/tools/runloop_executor.py (planned lines 086-095)]

**Used by:**
- [used_by: src/tools/toolkits.py @ initialization (planned lines 143-150)]
- [used_by: src/agents/legal_agent.py @ tools list (planned line 186)]

**References:**
- [uses: RUNLOOP_API_KEY @ environment variable]

---

## Notes & Assumptions

- **RunLoop SDK**: Uses official Python client from https://github.com/runloopai/api-client-python
- **API Key**: Automatically loaded from `RUNLOOP_API_KEY` environment variable per SDK design
- **Devbox lifecycle**: Create → Write → Execute → Cleanup (always)
- **Timeout handling**: RunLoop API handles timeout internally; we catch TimeoutError
- **Resource limits**: Set at account level, not per-devbox (CPU, memory, disk)
- **Automatic cleanup**: RunLoop has garbage collection, but we cleanup explicitly for faster resource reclamation
- **Error handling**: Never raise exceptions to agent; always return structured error dictionary
- **Idempotent cleanup**: Can safely call cleanup multiple times on same devbox ID
- **Tool decorator**: `@tool` from langchain_core makes execute_code method a LangChain tool
- **Code isolation**: Each execution gets fresh devbox; no state sharing between executions
- **File system**: Code written to `execute.py` in devbox root directory
- **Execution command**: Always `python execute.py` (could be parameterized if needed)
- **Result structure**: `{success: bool, stdout: str, stderr: str, exit_status: int, error?: str}`
- **Logging**: Info for lifecycle events, debug for details, warning for non-critical failures, error for critical failures
- **Future enhancements**: Could add custom devbox configuration, multiple file support, pip install support
- **Testing**: Should have unit tests mocking RunLoop API, integration tests with real API
- **Security**: Devbox is isolated; code cannot access host system or network (depends on RunLoop sandbox config)

---

## Validation

- [x] All imports from official RunLoop SDK and LangChain
- [x] No circular dependencies
- [x] Error handling for all API calls
- [x] Cleanup guaranteed in all code paths (try/finally)
- [x] Structured error returns (no exceptions to agent)
- [x] Logging for all operations
- [x] Type hints for all parameters and returns
- [x] Docstrings for class and all methods
- [x] Private methods prefixed with underscore
- [x] Tool decorator for LangChain integration

**Citations:**
- **RunLoop Python SDK**: https://github.com/runloopai/api-client-python
- **LangChain Custom Tools**: https://python.langchain.com/docs/modules/tools/custom_tools
- **RunLoop Documentation**: https://runloop.ai/docs

---

**Status**: ✅ Plan Complete - Ready for validation
**Estimated LOC**: ~100 lines
**Next**: Create toolkits.py plan
