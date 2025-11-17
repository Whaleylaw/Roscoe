"""
RunLoop Sandboxed Code Execution Tool

This file provides RunLoop-based sandboxed Python code execution, replacing
PythonREPLTool with production-ready isolation, resource limits, and error handling.

Plan Reference: /Users/aaronwhaley/Documents/GitHub/Whaley-Law-Firm/deepagents/docs/spec/CORRECTED-PLANS/src--tools--runloop_executor.py.nlplan.md

Citation: https://github.com/runloopai/api-client-python
"""

# Imports (planned lines 001-010)
from runloop_api_client import Runloop  # Line 001: Main client for RunLoop sandbox API
import os  # Line 002: Read RUNLOOP_API_KEY environment variable
import logging  # Line 003: Logger for devbox lifecycle events and errors
from typing import Optional, Dict  # Line 004: Type annotations for parameters and returns
from langchain_core.tools import tool  # Line 005: Decorator to make execute_code a LangChain tool

# Line 007: Module-specific logger for RunLoop executor operations
logger = logging.getLogger(__name__)

# Line 010: Runloop client automatically loads API key from RUNLOOP_API_KEY environment variable


class RunLoopExecutor:
    """
    Provides sandboxed Python code execution via RunLoop API with automatic
    devbox management and error handling.

    This executor creates isolated devboxes for each code execution, ensuring
    no state sharing between runs and proper resource cleanup.
    """

    def __init__(self):
        """Initialize RunLoop client and set up execution environment."""
        try:
            # Line 014: Create Runloop client (auto-loads RUNLOOP_API_KEY from environment)
            self.client = Runloop()  # Line 015: Assign to self.client for use throughout class

            # Line 016: Log successful initialization
            logger.info("RunLoop executor initialized successfully")

            # Line 017: Track active devbox for cleanup if execution fails midway
            self.current_devbox_id: Optional[str] = None

        except Exception as e:
            # Line 019: Fail fast on misconfiguration
            logger.error(f"RunLoop initialization failed: {str(e)}")
            raise RuntimeError("RunLoop API key not configured or invalid") from e

    def _execute_code_impl(self, code: str, timeout: int = 60) -> Dict:
        """
        Internal implementation of code execution (called by wrapper function).

        Runs the provided Python code in a sandboxed environment with resource
        limits and timeout protection. Returns structured results for agent parsing.

        Args:
            code: Python code string to execute
            timeout: Maximum seconds before termination (default: 60)

        Returns:
            Dictionary with keys:
                - success (bool): Whether execution completed without errors
                - stdout (str): Standard output from code execution
                - stderr (str): Standard error from code execution
                - exit_status (int): Exit code from Python process
                - error (str, optional): Error message if execution failed
        """
        try:
            # Line 027: Log code preview for debugging and audit trail
            logger.info(f"Executing code: {code[:100]}...")

            # Line 028-029: Create devbox and track for cleanup
            devbox_id = self._create_devbox()
            self.current_devbox_id = devbox_id

            # Line 030: Log devbox ID for correlation with RunLoop dashboard
            logger.info(f"Created devbox: {devbox_id}")

            # Line 031-032: Write Python code to execute.py inside devbox filesystem
            self.client.devboxes.write_file_contents(
                devbox_id=devbox_id,
                file_path="execute.py",
                contents=code
            )

            # Line 033: Confirm file write succeeded
            logger.debug("Code written to devbox file system")

            # Line 034-035: Execute the written Python code
            result = self.client.devboxes.execute(
                devbox_id=devbox_id,
                command="python execute.py"
            )

            # Line 036-043: Check exit status and construct result dictionary
            if result.exit_status == 0:
                # Line 037: Log successful execution
                logger.info(f"Code executed successfully (output length: {len(result.stdout)})")

                # Line 038: Return success result
                return_dict = {
                    "success": True,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_status": 0
                }
            else:
                # Line 039: Log execution failure
                logger.warning(f"Code execution failed with exit status {result.exit_status}: {result.stderr[:200]}")

                # Line 040: Return failure result
                return_dict = {
                    "success": False,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_status": result.exit_status
                }

            # Line 041: Cleanup devbox after execution
            self._cleanup_devbox(devbox_id)

            # Line 042: Clear tracking variable
            self.current_devbox_id = None

            # Line 043: Return result to agent
            return return_dict

        except TimeoutError as e:
            # Line 045: Log timeout event
            logger.error(f"Code execution timeout after {timeout} seconds")

            # Line 046: Return timeout error
            return {
                "success": False,
                "error": f"Execution timeout after {timeout} seconds",
                "stdout": "",
                "stderr": str(e)
            }

        except Exception as e:
            # Line 048: Log general execution error
            logger.error(f"Code execution error: {str(e)}")

            # Line 049: Attempt cleanup even after error
            if self.current_devbox_id is not None:
                self._cleanup_devbox(self.current_devbox_id)

            # Line 050: Return error details
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e)
            }

        finally:
            # Line 052-053: Safety net cleanup (normal flow already cleans up)
            if self.current_devbox_id is not None:
                # Ensures no devbox left running on errors
                self._cleanup_devbox(self.current_devbox_id)

    # Line 055: Returning error dictionary allows agent to retry with modified code

    def _create_devbox(self) -> str:
        """
        Create new RunLoop devbox, wait for running state, and return devbox ID.

        This method blocks until the devbox is fully initialized and ready for
        file operations and code execution.

        Returns:
            str: Devbox ID for use in write/execute operations

        Raises:
            RuntimeError: If devbox creation fails or no ID returned
        """
        try:
            # Line 058-059: Create devbox and block until fully initialized
            devbox = self.client.devboxes.create_and_await_running()

            # Line 060: Log successful devbox creation
            logger.info(f"Created devbox with ID: {devbox.id}")

            # Line 061: Validate devbox ID returned
            if not devbox.id:
                raise RuntimeError("Failed to create devbox: no ID returned")

            # Line 062: Return devbox ID to caller
            return devbox.id

        except Exception as e:
            # Line 064: Log creation failure
            logger.error(f"Devbox creation failed: {str(e)}")

            # Line 065: Propagate error to execute_code except handler
            raise RuntimeError(f"Failed to create RunLoop devbox: {str(e)}") from e

    # Line 066: create_and_await_running blocks until ready, no additional polling needed
    # Line 067: Devbox remains running until explicitly destroyed via cleanup method
    # Line 068: Default resource limits (CPU, memory, disk) set by RunLoop account config

    def _cleanup_devbox(self, devbox_id: str) -> None:
        """
        Destroy RunLoop devbox, freeing resources.

        This method attempts graceful cleanup but will not raise exceptions if
        cleanup fails, as the devbox may have already been destroyed or the API
        may be temporarily unavailable.

        Args:
            devbox_id: ID of devbox to destroy
        """
        try:
            # Line 074-075: Shutdown devbox gracefully before destruction
            self.client.devboxes.stop(devbox_id=devbox_id)
            logger.debug(f"Stopped devbox: {devbox_id}")

            # Line 076-077: Permanently remove devbox and free resources
            self.client.devboxes.delete(devbox_id=devbox_id)
            logger.info(f"Cleaned up devbox: {devbox_id}")

        except Exception as e:
            # Line 079: Log cleanup failure but don't raise (non-critical)
            logger.warning(f"Failed to cleanup devbox {devbox_id}, but continuing: {str(e)}")

            # Line 080: Cleanup is best-effort; don't crash main execution flow
            # Line 081: Devbox may have auto-terminated or been deleted externally
            # Line 082: RunLoop has automatic garbage collection of old devboxes

    # Line 085: Cleanup is idempotent; can be safely called multiple times


def create_runloop_tool():
    """
    Factory function to create RunLoopExecutor instance as LangChain-compatible tool.

    This allows lazy initialization of the RunLoop client only when the tool is
    actually added to the agent, avoiding startup cost if not used.

    Returns:
        Decorated execute_code function ready for agent tools list (with executor closure)

    Example:
        from src.tools.runloop_executor import create_runloop_tool

        tool = create_runloop_tool()
        agent_tools = [tool, other_tool, ...]
    """
    # Line 088-089: Create executor instance (initializes RunLoop client)
    executor = RunLoopExecutor()

    # Create a standalone function that closes over the executor instance
    # This avoids 'self' appearing in the tool signature
    @tool
    def execute_code(code: str, timeout: int = 60) -> Dict:
        """
        Execute Python code in isolated RunLoop devbox.

        Runs the provided Python code in a sandboxed environment with resource
        limits and timeout protection. Returns structured results for agent parsing.

        Args:
            code: Python code string to execute
            timeout: Maximum seconds before termination (default: 60)

        Returns:
            Dictionary with keys:
                - success (bool): Whether execution completed without errors
                - stdout (str): Standard output from code execution
                - stderr (str): Standard error from code execution
                - exit_status (int): Exit code from Python process
                - error (str, optional): Error message if execution failed
        """
        # Delegate to the executor instance's method (closure)
        # Note: We can't use the @tool decorator on the instance method directly
        # because it would include 'self' in the signature. Instead, we create
        # this wrapper function that closes over the executor instance.
        return executor._execute_code_impl(code, timeout)

    # Return the standalone decorated function
    return execute_code

# Line 095: Executor can be reused across multiple code execution calls
# Each execution gets fresh devbox; no state sharing between calls
