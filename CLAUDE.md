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

## Architecture: Dynamic Skills-Based System

Roscoe uses a **dynamic skills architecture** with semantic skill selection and automatic model switching. This eliminates hardcoded sub-agents and enables unlimited skill expansion without code changes.

### Main Agent Structure

The main agent (`roscoe/agent.py`) uses middleware for dynamic behavior:

```python
personal_assistant_agent = create_deep_agent(
    system_prompt=minimal_personal_assistant_prompt,  # Minimal prompt
    subagents=[],  # EMPTY - uses only built-in general-purpose sub-agent
    model=agent_llm,  # Default: Claude Sonnet 4.5 (switches dynamically)
    backend=FilesystemBackend(root_dir=workspace_dir, virtual_mode=True),
    tools=[shell_tool],
    middleware=[
        SkillSelectorMiddleware(...),  # Semantic skill selection
        model_selector_middleware,      # Dynamic model switching
    ]
).with_config({"recursion_limit": 1000})
```

**Key Innovation:** No hardcoded sub-agents. Behavior is controlled entirely by dynamically loaded skills.

### Middleware Architecture

**1. SkillSelectorMiddleware** (`roscoe/skill_middleware.py`):
- Embeds all skill descriptions using sentence-transformers
- On each request, computes cosine similarity between user query and skills
- Loads top-matching skill(s) into system prompt
- Sets skill metadata in request state for model selector
- **Token Efficient**: Only relevant skills loaded per conversation

**2. model_selector_middleware** (`roscoe/skill_middleware.py`):
- Reads skill metadata from request state
- Dynamically switches agent model based on skill requirements:
  - `gemini-3-pro`: Multimodal analysis, code execution
  - `sonnet`: Complex reasoning, analysis (DEFAULT)
  - `haiku`: Simple high-volume tasks only
- General-purpose sub-agent inherits the current model

### Skills System

**Skills Location:** `/workspace/Skills/`

**Skills Manifest:** `skills_manifest.json` - Registry of all available skills with:
- Semantic descriptions for matching
- Trigger keywords for search optimization
- Model requirements
- Sub-skill definitions
- Tool requirements

**Main Skills:**
1. **medical-records-analysis** - 5-phase medical analysis pipeline
2. **legal-research** - Internet research using Tavily

**Sub-Skills** (`/workspace/Skills/sub-agents/`):
- **fact-investigation.md** - Gemini 3 Pro (multimodal + code execution)
- **medical-organization.md** - Haiku (simple inventory)
- **record-extraction.md** - Sonnet (accurate medical data extraction)
- **inconsistency-detection.md** - Sonnet (reasoning about contradictions)
- **red-flag-identification.md** - Sonnet (legal/medical judgment)
- **causation-analysis.md** - Sonnet (complex medical-legal reasoning)
- **missing-records-detection.md** - Sonnet (pattern recognition)
- **summary-writing.md** - Sonnet (synthesis)

### Model Strategy (Accuracy > Cost for POC)

**Gemini 3 Pro Preview:**
- Fact investigation (multimodal + code execution required)
- PDF-heavy document processing
- Image/audio/video analysis

**Claude Sonnet 4.5** (DEFAULT):
- Medical records extraction (needs accuracy)
- Inconsistency detection (requires reasoning)
- Red flag identification (legal/medical judgment)
- Causation analysis (complex reasoning)
- Missing records detection (pattern recognition)
- Summary writing (synthesis)

**Claude Haiku 4.5** (Minimal Use):
- Medical organization only (simple listing/categorizing)
- High-volume parallel tasks where speed matters and complexity is low

**Rationale:** For proof of concept, prioritize accuracy. Use Haiku only for genuinely simple tasks.

### Workflow Execution

Medical records analysis follows a **5-phase pipeline** via the medical-records-analysis skill:

1. **Phase 1**: Fact investigation (litigation documents, multimedia evidence) - Gemini 3 Pro
2. **Phase 2**: Medical organization (inventory creation) - Haiku
3. **Phase 3**: Parallel extraction (spawn 3-4 general-purpose sub-agents) - Sonnet
4. **Phase 4**: Specialized analysis (inconsistencies, red flags, causation, missing records) - Sonnet
5. **Phase 5**: Final synthesis (comprehensive summary) - Sonnet

**How It Works:**
- Main agent's skill selector loads medical-records-analysis skill
- Skill instructs which sub-skills to use for each phase
- Main agent spawns general-purpose sub-agent with sub-skill instructions
- Model selector switches model based on sub-skill requirements
- General-purpose sub-agent inherits the appropriate model
- Main agent synthesizes results (e.g., chronology from extraction reports)

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

## Adding New Skills

The dynamic skills architecture makes it easy to add new capabilities without touching agent code:

### 1. Create Skill File

Create `/workspace/Skills/skill-name/skill.md` with skill instructions:
```markdown
# Skill Name

## When to Use
[Describe when this skill applies]

## Workflow
[Step-by-step instructions for executing the skill]

## Tools Required
[List any tools from /Tools/ directory]

## Sub-Skills
[If this skill uses sub-agents, list sub-skills to load]

## Model Required
sonnet | haiku | gemini-3-pro

## Output Format
[Expected output format and location]
```

### 2. Update Skills Manifest

Add entry to `/workspace/Skills/skills_manifest.json`:
```json
{
  "name": "skill-name",
  "description": "Use when [triggers/use cases] - [what it does]",
  "file": "skill-name/skill.md",
  "triggers": ["keyword1", "keyword2", "keyword3"],
  "model_required": "sonnet",
  "tools_required": ["/Tools/tool_name.py"],
  "sub_skills": {
    "sub-skill-name": {
      "file": "sub-agents/sub-skill.md",
      "model": "sonnet",
      "description": "What this sub-skill does"
    }
  }
}
```

### 3. Create Sub-Skills (If Needed)

If skill requires specialized sub-agents, create `/workspace/Skills/sub-agents/sub-skill-name.md`:
```markdown
# Sub-Skill Name Sub-Skill

[Instructions for the general-purpose sub-agent when using this sub-skill]

## Your Task
[Detailed task description]

## Tools Available
[File system tools, bash, code execution]

## Output Location
[Where to save results]
```

### 4. No Code Changes Required!

The skill is immediately available:
- SkillSelectorMiddleware will find it via semantic search
- ModelSelectorMiddleware will switch to the appropriate model
- Main agent will load and follow the skill instructions

## Key Design Principles

1. **Dynamic Skill Loading**: Skills loaded semantically based on user request, not hardcoded
2. **Automatic Model Optimization**: Right model selected per task automatically
3. **Zero-Code Skill Addition**: Add unlimited skills by editing files, no deployment needed
4. **Parallel Processing**: Spawn multiple general-purpose sub-agents for batch work
5. **Centralized Reporting**: All outputs go to `/Reports/` directory
6. **Citation Integrity**: Every factual claim must cite source document + page/timestamp
7. **Workspace Sandboxing**: All operations scoped to workspace root with virtual paths
8. **Token Efficiency**: Only relevant skills loaded per conversation
9. **Multimedia Evidence**: Native support for images, audio, video with AI analysis (Gemini 3 Pro)
