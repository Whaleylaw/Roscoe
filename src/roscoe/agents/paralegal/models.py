"""
Model configurations for the Paralegal Agent.

This agent uses OpenAI GPT-5.1 Thinking for all capabilities:
- Main agent: GPT-5.1 with reasoning capabilities for complex legal analysis
- Sub-agents: GPT-5.1 for medical records extraction, causation analysis, and research
- Multimodal: GPT-5.1 for images/audio/video analysis

Switched from Gemini 3 Pro due to rate limits.
"""

from langchain_openai import ChatOpenAI

# Main agent model (GPT-5.1 Thinking)
# Using GPT-5.1 with reasoning capabilities for complex legal and medical analysis
agent_llm = ChatOpenAI(
    model="gpt-5.1",
    max_retries=3,
    temperature=0
)

# General-purpose sub-agent model (same as main agent)
sub_agent_llm = ChatOpenAI(
    model="gpt-5.1",
    max_retries=3,
    temperature=0
)

# Multimodal sub-agent model (same as main agent - GPT-5.1)
# Used for image/audio/video analysis and document processing tasks
multimodal_llm = ChatOpenAI(
    model="gpt-5.1",
    max_retries=3,
    temperature=0
)
