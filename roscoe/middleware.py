"""
Tools configuration for Roscoe agent.

This module provides additional tools for enhanced agent capabilities including
shell/bash execution for running commands, scripts, and utilities.
"""

from langchain_community.tools import ShellTool

# Get absolute path to workspace directory for shell tool
workspace_root = "/Volumes/X10 Pro/whaley law firm"

# Configure Shell Tool for command execution
# Reference: https://docs.langchain.com/oss/python/integrations/tools/bash
# Note: ShellTool provides command execution capabilities but should be used carefully
# The tool has limited sandboxing - commands run on the host system
shell_tool = ShellTool()

# Set the shell tool to work from the workspace directory
# This is done by setting the working directory when executing commands
shell_tool.name = "bash"
shell_tool.description = """Execute shell commands in the workspace environment.
Use this to run Python scripts, install packages, git operations, data processing, etc.
Commands execute from the workspace directory.
Examples: 'pip install pandas', 'python script.py', 'ls -la'
WARNING: Commands run on the host system - use responsibly."""
