from pathlib import Path
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from models import agent_llm
from sub_agents import research_sub_agent
from medical_sub_agents import (
    fact_investigator_agent,
    organizer_agent,
    record_extractor_agent,
    inconsistency_detector_agent,
    red_flag_identifier_agent,
    causation_analyzer_agent,
    missing_records_detective_agent,
    summary_writer_agent,
)
from prompts import personal_assistant_prompt
from middleware import shell_tool

# Get absolute path to workspace directory
# FilesystemBackend requires absolute paths per docs
workspace_dir = str(Path(__file__).parent / "workspace")

# Compile the Personal Assistant Agent
# Per deepagents docs: subagents are passed directly to create_deep_agent()
# FilesystemBackend with virtual_mode=True for sandboxing
# ShellTool added for bash/command execution capabilities
# Reference: https://docs.langchain.com/oss/python/deepagents/backends.md
# Reference: https://docs.langchain.com/oss/python/integrations/tools/bash
personal_assistant_agent = create_deep_agent(
    system_prompt=personal_assistant_prompt,
    subagents=[
        research_sub_agent,
        fact_investigator_agent,
        organizer_agent,
        record_extractor_agent,
        inconsistency_detector_agent,
        red_flag_identifier_agent,
        causation_analyzer_agent,
        missing_records_detective_agent,
        summary_writer_agent,
    ],
    model=agent_llm,
    backend=FilesystemBackend(root_dir=workspace_dir, virtual_mode=True),
    tools=[shell_tool]
).with_config({"recursion_limit": 1000})