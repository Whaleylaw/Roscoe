"""
Model configurations for the Coding Agent.

This agent uses OpenAI GPT-5.1 Thinking for all code-related tasks:
- GPT-5.1 with reasoning capabilities for complex problem-solving
- Deep analysis before generating code solutions
- Excellent for debugging, architecture decisions, and refactoring
- Provides thoughtful explanations and well-reasoned solutions
"""

from langchain_openai import ChatOpenAI

# Main agent model (GPT-5.1 Thinking)
# Using GPT-5.1 with reasoning capabilities for superior coding and problem-solving
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
