from prompts import research_agent_prompt
from tools import internet_search
from models import sub_agent_llm

# Research Sub Agent Description
research_sub_agent_description = """Dedicated research assistant capable of investigating any topic. Conducts thorough web research on current events, products, how-to guides, locations, recommendations, and general information. Give focused queries on specific topics - for multiple topics, call multiple agents in parallel using the task tool."""

# Define the Research Sub Agent as a dictionary (per deepagents docs)
# Reference: https://docs.langchain.com/oss/python/deepagents/subagents.md
research_sub_agent = {
    "name": "research-agent",
    "description": research_sub_agent_description,
    "system_prompt": research_agent_prompt,
    "tools": [internet_search],
    "model": sub_agent_llm,
}
