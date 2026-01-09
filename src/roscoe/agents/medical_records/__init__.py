"""
Medical Records Analysis Agent.

A standalone LangGraph agent for comprehensive medical records analysis
in personal injury cases. Designed to be invoked via fire-and-forget
pattern from the paralegal DeepAgent.

Architecture:
- Uses LangGraph's create_react_agent for the agent loop
- ShellToolMiddleware for file operations (glob, grep, shell)
- Progress tracking via progress.json (from "Effective Harnesses for Long-Running Agents")
- Task list with passes: true/false to prevent premature completion

Phases:
1. Fact Investigation - Extract incident details from litigation docs
2. Medical Organization & Extraction - Inventory + batch extract records
3. Parallel Analysis - Inconsistencies, red flags, causation, missing records
4. Final Synthesis - Attorney-ready FINAL_SUMMARY.md
"""

from roscoe.agents.medical_records.agent import medical_records_agent

__all__ = ["medical_records_agent"]
