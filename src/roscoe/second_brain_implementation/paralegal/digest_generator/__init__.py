"""
Digest Generator Subagent

This subagent generates morning digests by querying the knowledge graph,
calendar, and memory files.
"""

from .agent import generate_morning_digest, get_digest_generator_subagent

__all__ = ['generate_morning_digest', 'get_digest_generator_subagent']
