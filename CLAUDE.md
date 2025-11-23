# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Context for Claude Code

**Training Data Cutoff:** January 2025
**Current Date:** November 2025

Significant changes have occurred in the LangChain/LangGraph ecosystem since the training cutoff. When working with LangChain or LangGraph code, **always reference the "langchain-docs" MCP server** for the most current documentation links and implementation patterns.

Given the knowledge cutoff mismatch, always check this reference for current APIs, best practices, and migration guides before making changes to LangChain/LangGraph code.

## Project Overview

**Roscoe** is a LangGraph-based paralegal AI agent specializing in personal injury litigation. The agent uses LangChain's DeepAgent framework with multiple specialized sub-agents to handle complex medical records analysis, legal research, and case management tasks.

**Core Technology Stack:**
- LangGraph for agent orchestration (deployed via LangGraph Cloud)
- LangChain DeepAgents framework for hierarchical agent architecture
- Claude Sonnet 4.5 (main agent) and Claude Haiku 4.5 (medical sub-agents)
- Google Gemini 3 Pro with native code execution (fact investigation with document processing)
- FilesystemBackend for sandboxed file operations
- Tavily for internet search
- Google Gemini multimodal capabilities for image/audio/video analysis

## Architecture

### Main Agent Structure

The main agent (`roscoe/agent.py`) is named `personal_assistant_agent` and is configured in `langgraph.json`:

```python
personal_assistant_agent = create_deep_agent(
    system_prompt=personal_assistant_prompt,
    subagents=[...],  # 9 specialized sub-agents
    model=agent_llm,  # Claude Sonnet 4.5
    backend=FilesystemBackend(root_dir=workspace_dir, virtual_mode=True),
    tools=[shell_tool]
).with_config({"recursion_limit": 1000})
```

**Key architectural principle:** The main agent orchestrates sub-agents but also synthesizes outputs (e.g., building medical chronologies from extraction reports).

### Sub-Agent Architecture

**Research Sub-Agent** (`roscoe/sub_agents.py`):
- General-purpose internet research using Tavily
- Uses Claude Sonnet 4.5
- Designed for focused, single-topic queries

**Medical Sub-Agents** (`roscoe/medical_sub_agents.py`) - 8 specialized agents:
1. **fact-investigator**: Analyzes litigation documents, photos, audio, video using Gemini 3 Pro with code execution
2. **organizer**: Inventories medical records and bills using Claude Haiku 4.5
3. **record-extractor**: Extracts structured data from 1-2 documents (batch parallel processing) using Claude Haiku 4.5
4. **inconsistency-detector**: Finds contradictions in medical documentation using Claude Haiku 4.5
5. **red-flag-identifier**: Identifies case weaknesses using Claude Haiku 4.5
6. **causation-analyzer**: Evaluates injury causation evidence using Claude Sonnet 4.5
7. **missing-records-detective**: Identifies gaps in records using Claude Haiku 4.5
8. **summary-writer**: Synthesizes comprehensive attorney-ready reports using Claude Sonnet 4.5

**Model selection rationale:**
- Sonnet 4.5: Complex analysis, synthesis, causation reasoning
- Haiku 4.5: Fast document processing, extraction, pattern detection
- Gemini 3 Pro: Native code execution for PDF processing and multimedia analysis

### Workflow Execution

Medical records analysis follows a **5-phase pipeline** defined in the `/medical-records-review` slash command:

1. **Phase 1**: Fact investigation (litigation documents, multimedia evidence)
2. **Phase 2**: Medical records organization (inventory creation)
3. **Phase 3**: Parallel extraction (spawn 3-4 record-extractors simultaneously)
4. **Phase 4**: Specialized analysis (inconsistencies, red flags, causation, missing records)
5. **Phase 5**: Final synthesis (comprehensive summary)

**Critical workflow note:** Main agent synthesizes extraction reports into chronology - it's not delegated to a sub-agent.

### FilesystemBackend Workspace

The agent operates in a sandboxed workspace with this structure:

```
/                           # Workspace root (virtual_mode=True)
├── Reports/                # ALL analysis reports (centralized)
│   ├── extractions/        # Individual document extractions
│   ├── frames/             # Video frame extracts
│   ├── case_facts.md
│   ├── chronology.md
│   ├── causation.md
│   └── FINAL_SUMMARY.md
├── Tools/                  # Python scripts generated during analysis
├── [case_name]/            # Case-specific folders
│   ├── medical_records/
│   ├── medical_bills/
│   └── litigation/
│       ├── discovery/
│       └── investigation/
```

**Path conventions:**
- Use workspace-relative paths starting with `/` (e.g., `/Reports/case_facts.md`)
- NEVER use absolute system paths in sub-agent prompts
- All reports MUST go to `/Reports/` directory
- All generated Python scripts go to `/Tools/`

## Development Commands

### Local Development

The agent is designed for LangGraph Cloud deployment. For local testing:

```bash
# Install dependencies (if using uv)
uv sync

# Run LangGraph development server
langgraph dev

# The agent is accessible at the LangGraph API endpoint
# defined in langgraph.json
```

### Deployment

```bash
# Deploy to LangGraph Cloud
langgraph deploy

# The deployment configuration is in langgraph.json
```

### Environment Setup

Required environment variables (in `../.env`):
- `ANTHROPIC_API_KEY` - For Claude models
- `GOOGLE_API_KEY` - For Gemini models
- `TAVILY_API_KEY` - For internet search

## Model Configuration (`roscoe/models.py`)

```python
# Main agent and complex analysis
agent_llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")

# Fast medical sub-agents (extraction, organization)
medical_sub_agent_llm = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0)

# Fact investigation with code execution
fact_investigator_llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    temperature=0
).bind_tools([{"code_execution": {}}])

# Fallback for fact investigator
fact_investigator_fallback_llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", ...)

# Multimodal analysis (images, audio, video)
multimodal_llm = ChatGoogleGenerativeAI(model="gemini-3-pro-preview", ...)
```

**Model Fallback Middleware:**
Fact investigator uses `ModelFallbackMiddleware` to fall back from Gemini 3 Pro → Gemini 2.5 Pro on server errors.

## Tools and Capabilities

### Core Tools (`roscoe/tools.py`)

1. **internet_search**: Tavily-powered web search
   - Supports general/news/finance topics
   - Optional raw content extraction

2. **analyze_image**: Multimodal image analysis (accident photos, scene documentation)
   - Uses Gemini 3 Pro with vision
   - Provides legal evidence analysis

3. **analyze_audio**: Audio transcription and analysis (911 calls, depositions)
   - Uses Gemini 3 Pro with audio
   - Speaker identification, timestamps, emotional state

4. **analyze_video**: Video analysis with timeline (body camera, dashcam)
   - Uses Gemini 3 Pro with video
   - Audio transcription + visual timeline
   - Optional key frame timestamp extraction

### Shell Tool (`roscoe/middleware.py`)

The bash/shell tool enables:
- Python script execution
- Package installation (`pip install`)
- PDF processing (`pdftotext`, `pdfplumber`)
- Video frame extraction (`ffmpeg`)
- Data analysis and manipulation

**Working directory:** Commands execute from workspace root

## Critical Citation Requirements

**Every factual claim in sub-agent outputs must include precise citations:**

- Document citations: `"per Complaint ¶12, page 3"`
- Audio citations: `"per 911 Call Audio at 00:01:23, caller states..."`
- Video citations: `"per Body Camera Video at 00:15:30 (frame: /Reports/frames/bodycam_00-15-30.jpg)"`
- Medical record citations: `"per Dr. Smith note 03/25/2024, page 2"`

**Video frame extraction protocol:**
When citing video evidence, extract frames using ffmpeg:
```bash
ffmpeg -i /path/to/video.mp4 -ss 00:01:30 -frames:v 1 /Reports/frames/description_HH-MM-SS.jpg
```

## Common Patterns

### Spawning Multiple Sub-Agents in Parallel

```python
# Main agent spawns 3-4 record-extractors simultaneously
# Each processes 1-2 documents
# Main agent then synthesizes extraction reports into chronology
```

### Research Task Delegation

```python
# Assign ONE topic per research agent
# For multiple topics, spawn multiple agents in parallel
# Provide focused queries with context
```

### Medical Records Workflow

The main agent follows this pattern:
1. Spawn fact-investigator → reads litigation folder
2. Spawn organizer → scans medical_records/ and medical_bills/
3. Spawn 3-4 record-extractors in parallel → each reads 1-2 files
4. Main agent synthesizes extractions into chronology
5. Spawn analysis agents (inconsistency, red-flag, causation, missing-records)
6. Spawn summary-writer → reads all reports, creates FINAL_SUMMARY.md

### Path Handling in Code

Always use workspace-relative paths in file system operations:

```python
# ✅ CORRECT
read_file("/Reports/case_facts.md")
ls("/mo_alif/medical_records/")

# ❌ WRONG
read_file("/Volumes/X10 Pro/Roscoe/workspace/case_facts.md")
read_file("../workspace/Reports/case_facts.md")
```

## File Organization

```
/Volumes/X10 Pro/Roscoe/
├── roscoe/                 # Main agent code
│   ├── agent.py            # Main agent entry point
│   ├── models.py           # LLM configurations
│   ├── prompts.py          # System prompts
│   ├── sub_agents.py       # Research sub-agent
│   ├── medical_sub_agents.py  # 8 medical sub-agents
│   ├── tools.py            # Tool definitions
│   └── middleware.py       # Shell tool configuration
├── workspace/              # Sandboxed workspace (gitignored)
│   ├── Reports/
│   ├── Tools/
│   └── [case_folders]/
├── langgraph.json          # LangGraph Cloud config
├── roscoe_prompt.md        # Original agent description
└── QUICK_START.txt         # Web scraping tools analysis
```

## Important Notes

### DeepAgents Sub-Agent Format

Sub-agents are defined as dictionaries per LangChain DeepAgents documentation:

```python
{
    "name": "agent-name",
    "description": "Description for when to invoke",
    "system_prompt": "Detailed system prompt",
    "tools": [list_of_tools],
    "model": llm_instance,
    "middleware": [optional_middleware]  # e.g., ModelFallbackMiddleware
}
```

### Workspace Sandboxing

- `FilesystemBackend` with `virtual_mode=True` provides sandboxing
- All file paths are scoped to workspace root
- Sub-agents inherit file system tools from backend automatically
- Bash tool is explicitly added to main agent and certain sub-agents

### Model Cost Optimization

The codebase uses a tiered model strategy:
- **Haiku 4.5**: High-volume, straightforward extraction/processing tasks
- **Sonnet 4.5**: Complex reasoning, synthesis, causation analysis
- **Gemini 3 Pro**: Document-heavy tasks with native code execution, multimedia analysis

### Multimedia Evidence Processing

The fact-investigator agent can:
1. Analyze images (accident photos, scene documentation)
2. Transcribe and analyze audio (911 calls, witness statements)
3. Analyze video with timeline (body camera, dashcam, surveillance)
4. Extract video frames at specific timestamps using ffmpeg

### Slash Commands

The repository uses a `/medical-records-review` slash command (in `.claude/commands/`) that orchestrates the 5-phase medical analysis pipeline.

## Testing and Debugging

When modifying sub-agents:
1. Test individual sub-agent prompts for clarity and completeness
2. Verify citation requirements are explicit in prompts
3. Ensure file paths use workspace-relative format
4. Test fallback mechanisms (e.g., ModelFallbackMiddleware)
5. Verify parallel processing works for record-extractor batch operations

When adding new tools:
1. Define in `roscoe/tools.py`
2. Import and add to relevant sub-agent `tools` list
3. Document in sub-agent system prompt
4. Test with workspace-relative paths

## Key Design Principles

1. **Hierarchical Agent Architecture**: Main agent delegates to specialists but also synthesizes
2. **Parallel Processing**: Spawn multiple extractors for batch document processing
3. **Centralized Reporting**: All outputs go to `/Reports/` directory
4. **Citation Integrity**: Every factual claim must cite source document + page/timestamp
5. **Workspace Sandboxing**: All operations scoped to workspace root with virtual paths
6. **Cost-Optimized Models**: Use fastest/cheapest model that can handle the task
7. **Multimedia Evidence**: Native support for images, audio, video with AI analysis
