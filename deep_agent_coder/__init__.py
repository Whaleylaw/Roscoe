"""
Deep Agent Coder

A multi-agent coding system built on LangChain Deep Agents.
"""

__version__ = "0.1.0"

from .agent import create_coder_agent, create_simple_agent
from .subagents import get_subagents

__all__ = [
    "create_coder_agent",
    "create_simple_agent", 
    "get_subagents",
]
