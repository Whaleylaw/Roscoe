# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Context for Claude Code

**Training Data Cutoff:** January 2025
**Current Date:** November 2025

Significant changes have occurred in the LangChain/LangGraph ecosystem since the training cutoff. When working with LangChain or LangGraph code, **always reference the "langchain-docs" MCP server** for the most current documentation links and implementation patterns.

Given the knowledge cutoff mismatch, always check this reference for current APIs, best practices, and migration guides before making changes to LangChain/LangGraph code.

## Project Overview

**Roscoe** is a multi-agent platform built on LangGraph with shared infrastructure supporting multiple specialized AI agents. The platform currently includes a paralegal agent for personal injury litigation, with plans for a personal assistant agent and a coding agent for agent development.

**Current Agents:**
1. **Paralegal Agent** (`paralegal_agent`) - Personal injury litigation specialist
   - Medical records analysis
   - Legal research
   - Case management
   - Document processing
2. **Personal Assistant** (planned) - Personal task management
3. **Coding Agent** (planned) - Agent development and maintenance

**Architecture:**
- **src/roscoe/core/** - Shared infrastructure (models, middleware, skill system)
- **src/roscoe/agents/** - Individual agent implementations (each with own workspace, skills, tools, prompts)
- **Isolation:** Each agent has completely separate workspace, skills, and tools

**Core Technology Stack:**
- LangGraph for agent orchestration (deployed via LangGraph Cloud)
- LangChain DeepAgents framework for hierarchical agent architecture
- Claude Sonnet 4.5 (main agent) and Claude Haiku 4.5 (medical sub-agents)
- Google Gemini 3 Pro with native code execution (fact investigation with document processing)
- FilesystemBackend for sandboxed file operations
- Tavily for internet search
- Google Gemini multimodal capabilities for image/audio/video analysis

## Architecture: Dynamic Skills-Based System

Roscoe uses a **dynamic skills architecture** with semantic skill selection. This eliminates hardcoded sub-agents and enables unlimited skill expansion without code changes.

### Main Agent Structure

The main agent (`src/roscoe/agents/paralegal/agent.py`) uses middleware for dynamic behavior:

```python
personal_assistant_agent = create_deep_agent(
    system_prompt=minimal_personal_assistant_prompt,  # Minimal prompt
    subagents=[],  # EMPTY - uses only built-in general-purpose sub-agent
    model=agent_llm,  # Default: Claude Sonnet 4.5 (switches dynamically)
    backend=FilesystemBackend(root_dir=workspace_dir, virtual_mode=True),
    tools=[shell_tool],
    middleware=[
        SkillSelectorMiddleware(...),  # Semantic skill selection
    ]
).with_config({"recursion_limit": 1000})
```

**Key Innovation:** No hardcoded sub-agents. Behavior is controlled entirely by dynamically loaded skills.

### Middleware Architecture

**SkillSelectorMiddleware** (`src/roscoe/core/skill_middleware.py`):
- Embeds all skill descriptions using sentence-transformers
- On each request, computes cosine similarity between user query and skills
- Loads top-matching skill(s) into system prompt
- Sets skill metadata in request state
- **Token Efficient**: Only relevant skills loaded per conversation

### Skills System

**Skills Location:** `/workspace_paralegal/Skills/` (paralegal agent)

**Skills Manifest:** `skills_manifest.json` - Registry of all available skills with:
- Semantic descriptions for matching
- Trigger keywords for search optimization
- Model requirements
- Sub-skill definitions
- Tool requirements

**Main Skills:**
1. **medical-records-analysis** - 5-phase medical analysis pipeline
2. **legal-research** - Internet research using Tavily

**Sub-Skills** (`/workspace_paralegal/Skills/sub-agents/`):
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
- General-purpose sub-agent uses the main agent's model (Sonnet)
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
├── Tools/                  # Standalone executable tools (permanent)
│   ├── research/           # General research tools
│   ├── medical_research/   # Medical/academic research tools
│   ├── legal_research/     # Legal research tools
│   ├── document_processing/ # PDF extraction tools
│   └── _generated/         # Agent-generated scripts (temporary, case-specific)
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
- All **permanent tools** go to `/Tools/[category]/` (e.g., `/Tools/legal_research/`)
- All **temporary agent-generated scripts** go to `/Tools/_generated/` (e.g., reorganize scripts, case-specific automation)

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

## Model Configuration (`src/roscoe/core/models.py`)

```python
# Main agent model (Claude Sonnet 4.5)
agent_llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", max_retries=3)

# General-purpose sub-agent model (same as main agent)
sub_agent_llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", max_retries=3)

# Multimodal sub-agent model (Gemini 3 Pro with code execution)
# Used for image/audio/video analysis and document processing tasks
multimodal_llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    max_retries=3,
    temperature=0
).bind_tools([{"code_execution": {}}])
```

## Tools Architecture: Standalone Executable Scripts

**IMPORTANT:** Roscoe uses a **unique tools architecture** that differs from typical LangChain agents. Tools are NOT added to the agent's context window. Instead, they are standalone Python scripts that the agent executes via the shell tool.

### Why Standalone Scripts?

**Problems with traditional tool loading:**
- Tool descriptions consume 500-1300 tokens per tool per message
- Agent context bloated with tool signatures for rarely-used capabilities
- Adding new tools requires redeploying the agent
- Large tool outputs fill context window

**Our solution:**
1. Tools are executable Python scripts in `/Tools/` directory
2. Agent discovers tools by reading `/Tools/tools_manifest.json`
3. Agent executes tools via shell: `python /Tools/tool_name.py "query"`
4. Results output to stdout (JSON or text)
5. Agent processes results with grep/jq/awk or reads directly

**Benefits:**
- ✅ **Zero context bloat** - Tools not loaded until needed
- ✅ **Terminal output processing** - Agent can grep/filter large results
- ✅ **Dynamic discovery** - Add tools without redeploying agent
- ✅ **Token efficiency** - Saves 500-1300 tokens per tool per message
- ✅ **Composable** - Tools work with Unix pipes and standard tools
- ✅ **Scalable** - Add unlimited tools without performance degradation

### Tools Directory Structure

```
/workspace_paralegal/Tools/
├── tools_manifest.json       # Master registry of all permanent tools
├── README.md                 # Tools documentation
│
├── research/                 # General research (2 tools)
│   ├── manifest.json         # Category-specific manifest
│   ├── internet_search.py
│   └── expert_witness_lookup.py
│
├── medical_research/         # Medical/academic research (2 tools)
│   ├── manifest.json
│   ├── pubmed_search.py
│   └── semantic_scholar_search.py
│
├── legal_research/           # Legal research (7 tools)
│   ├── manifest.json
│   ├── search_case_law.py
│   ├── explore_citations.py
│   ├── get_opinion_full_text.py
│   ├── find_my_cases.py
│   ├── get_docket_details.py
│   ├── monitor_upcoming_dates.py
│   └── oral_arguments_search.py
│
├── document_processing/      # PDF extraction (2 tools)
│   ├── manifest.json
│   ├── read_pdf.py
│   └── import_documents.py
│
├── _generated/               # Agent-generated scripts (temporary)
│   └── README.md             # Guidelines for generated scripts
│
└── _archive/                 # Deprecated tools (replaced/obsolete)
```

**IMPORTANT: Permanent vs. Generated Scripts**

- **Permanent tools** (reusable, tested, general-purpose) → `/Tools/[category]/tool_name.py`
  - Example: `/Tools/legal_research/search_case_law.py`
  - Listed in `tools_manifest.json`
  - Discovered via manifest by agent

- **Generated scripts** (temporary, case-specific, one-off) → `/Tools/_generated/script_name.sh`
  - Example: `/Tools/_generated/reorganize_Amy-Mills-Premise-04-26-2019.sh`
  - NOT in manifest
  - Cleanup policy: Delete after 90 days or when case closes

### Tool Pattern (All Tools Follow This)

Every tool in `/Tools/` follows this standardized pattern:

```python
#!/usr/bin/env python3
"""
Tool Name and Description

Comprehensive docstring with usage examples.
"""

import argparse
import json
import sys

def tool_function(query: str, **kwargs) -> dict:
    """Core function that does the work."""
    try:
        # Perform the task
        results = do_something(query)

        return {
            "success": True,
            "query": query,
            "results": results
        }
    except Exception as e:
        return {
            "error": f"Tool failed: {str(e)}",
            "query": query
        }

def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(description="Tool description")
    parser.add_argument("query", help="Query string")
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--pretty", action="store_true")

    args = parser.parse_args()

    result = tool_function(args.query, max_results=args.max_results)

    # Output JSON to stdout
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))

    # Exit code
    sys.exit(0 if "success" in result else 1)

if __name__ == "__main__":
    main()
```

**Key requirements:**
1. ✅ Shebang: `#!/usr/bin/env python3`
2. ✅ Comprehensive docstring with examples
3. ✅ argparse CLI with `--help` support
4. ✅ JSON output to stdout (or text for documents)
5. ✅ Status messages to stderr (keeps stdout clean)
6. ✅ Exit codes: 0 = success, 1 = error
7. ✅ Environment variables for API keys
8. ✅ Graceful error handling
9. ✅ `--pretty` flag for human-readable output

### Tools Manifest System

The agent discovers tools by reading `/Tools/tools_manifest.json`:

```json
{
  "version": "1.0.0",
  "description": "Tool registry for dynamic discovery",
  "tools": [
    {
      "name": "tool_name",
      "file": "tool_name.py",
      "description": "What the tool does",
      "category": "research|document_processing|...",
      "usage": "python /Tools/tool_name.py \"query\" [--flags]",
      "examples": ["example command 1", "example command 2"],
      "when_to_use": ["Use case 1", "Use case 2"],
      "output_format": "JSON to stdout",
      "dependencies": ["package1", "package2"],
      "environment_requirements": ["ENV_VAR_NAME"],
      "cost": "FREE | paid"
    }
  ]
}
```

**Agent workflow:**
1. Agent reads manifest when it needs a tool
2. Finds appropriate tool via `when_to_use` descriptions
3. Checks `usage` and `examples` for syntax
4. Executes: `python /Tools/tool_name.py "query"`
5. Processes JSON output or pipes through grep/jq

### Current Tools Inventory

**Research Tools (All FREE):**

1. **internet_search.py** - General web search
   - Tavily API for news, general research, fact-finding
   - Env: `TAVILY_API_KEY` (required)
   - Package: `tavily-python`

2. **pubmed_search.py** - Medical research
   - 39M+ peer-reviewed medical citations
   - Essential for causation research, standards of care
   - Env: `NCBI_EMAIL` (required), `NCBI_API_KEY` (optional)
   - Package: `biopython`

3. **semantic_scholar_search.py** - Academic research
   - 230M+ papers with citation tracking
   - Expert witness publication verification
   - No API key required, 100% FREE

4. **court_case_search.py** - Legal precedent
   - Millions of court opinions via CourtListener
   - Kentucky 6th Circuit coverage
   - Env: `COURTLISTENER_API_KEY` (optional)
   - No packages needed

5. **expert_witness_lookup.py** - Expert verification
   - Publication records, h-index, citation counts
   - Credential checking for cross-examination
   - No API key required, 100% FREE

**Document Processing Tools:**

6. **read_pdf.py** - PDF text extraction
   - Multi-page support, error recovery
   - Medical records, bills, reports
   - Package: `pypdf`

### Agent-Facing Tools (Loaded in Context)

These tools ARE loaded into the agent context (in `src/roscoe/agents/paralegal/tools.py`) because they require multimodal models:

1. **analyze_image** - Gemini 3 Pro vision for accident photos
2. **analyze_audio** - Gemini 3 Pro audio for 911 calls, depositions
3. **analyze_video** - Gemini 3 Pro video for dashcam, body camera

### Shell Tool

The bash/shell tool (via `FilesystemBackend`) enables:
- Executing `/Tools/*.py` scripts
- Package installation (`pip install`)
- PDF processing (`pdftotext`, `pdfplumber`)
- Video frame extraction (`ffmpeg`)
- Data analysis with piping: `python /Tools/tool.py "query" | jq '.results[0]'`

**Working directory:** Workspace root

### How to Add New Tools

1. **Create the Python script** in `/Tools/tool_name.py`:
   - Follow the standardized pattern above
   - Include comprehensive docstring
   - Add argparse CLI with `--help`
   - Output JSON to stdout
   - Make it executable: `chmod +x /Tools/tool_name.py`

2. **Update tools_manifest.json**:
   - Add entry with name, description, usage, examples
   - Specify `when_to_use` cases clearly
   - List dependencies and environment variables
   - Document output format

3. **Test the tool**:
   ```bash
   python /Tools/tool_name.py --help  # Check help works
   python /Tools/tool_name.py "test query" --pretty  # Test output
   ```

4. **No agent changes needed!**
   - Agent discovers tool via manifest
   - Tool immediately usable in next conversation

### Tool Usage Examples

**Agent executing a tool:**
```python
# Agent runs via shell tool:
python /Tools/pubmed_search.py "whiplash cervical spine" --max-results 10
```

**Agent processing large output:**
```bash
# Filter results with jq:
python /Tools/semantic_scholar_search.py "brain injury" | jq '.results[] | select(.citation_count > 100)'

# Search for keywords:
python /Tools/court_case_search.py "personal injury" | grep -i "kentucky"

# Count results:
python /Tools/expert_witness_lookup.py "John Smith" | jq '.primary_match.total_papers'
```

### Environment Variables for Tools

Required in `../.env`:
```bash
# Research APIs
TAVILY_API_KEY=sk-...           # Required for internet_search
NCBI_EMAIL=user@example.com     # Required for pubmed_search
NCBI_API_KEY=...                # Optional for pubmed_search (10 req/sec vs 3)
COURTLISTENER_API_KEY=...       # Optional for court_case_search (higher limits)

# Core agent (already configured)
ANTHROPIC_API_KEY=sk-...
GOOGLE_API_KEY=...
```

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
├── src/                           # Source code (src/ layout)
│   └── roscoe/                    # Main package
│       ├── __init__.py
│       ├── core/                  # Shared infrastructure (all agents)
│       │   ├── __init__.py
│       │   ├── models.py          # LLM configurations (Claude, Gemini)
│       │   ├── middleware.py      # Shell tool configuration
│       │   └── skill_middleware.py # Skill selector middleware
│       │
│       └── agents/                # Individual agent implementations
│           ├── __init__.py
│           └── paralegal/         # Paralegal agent (law office)
│               ├── __init__.py
│               ├── agent.py       # Main agent entry point
│               ├── prompts.py     # Agent-specific system prompts
│               ├── sub_agents.py  # Multimodal sub-agent definition
│               └── tools.py       # Multimodal tool definitions
│
├── workspace_paralegal/           # Paralegal agent workspace (gitignored)
│   ├── Reports/                   # Analysis reports
│   ├── Tools/                     # Paralegal-specific tools
│   ├── Skills/                    # Paralegal-specific skills
│   └── [case_folders]/            # Case-specific folders
│
├── langgraph.json                 # LangGraph Cloud config (multi-agent)
├── pyproject.toml                 # Python project configuration
├── CLAUDE.md                      # This file
└── README.md                      # Project README

Future agent structure (when added):
├── workspace_personal_assistant/  # Personal assistant workspace
│   ├── Reports/
│   ├── Tools/
│   └── Skills/
│
└── workspace_coding/              # Coding agent workspace
    ├── Reports/
    ├── Tools/
    └── Skills/
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
    "model": llm_instance
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
4. Verify parallel processing works for batch operations

When adding new standalone tools (in `/Tools/`):
1. Create executable Python script following the standardized pattern
2. Update `/Tools/tools_manifest.json` with tool metadata
3. Test: `python /Tools/tool_name.py --help` and with sample queries
4. No agent code changes or redeployment needed!

When adding multimodal tools (requires agent context):
1. Define in `src/roscoe/agents/paralegal/tools.py` (for analyze_image, analyze_audio, analyze_video)
2. Import and add to relevant sub-agent `tools` list in `sub_agents.py`
3. Document in sub-agent system prompt
4. Test with workspace-relative paths

## Adding New Skills

The dynamic skills architecture makes it easy to add new capabilities without touching agent code:

### 1. Create Skill File

Create `/workspace_paralegal/Skills/skill-name/skill.md` with skill instructions (for paralegal agent):
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

Add entry to `/workspace_paralegal/Skills/skills_manifest.json` (for paralegal agent):
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

If skill requires specialized sub-agents, create `/workspace_paralegal/Skills/sub-agents/sub-skill-name.md` (for paralegal agent):
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
- Main agent will load and follow the skill instructions

## Key Design Principles

1. **Dynamic Skill Loading**: Skills loaded semantically based on user request, not hardcoded
2. **Zero-Code Skill Addition**: Add unlimited skills by editing files, no deployment needed
3. **Parallel Processing**: Spawn multiple general-purpose sub-agents for batch work
4. **Centralized Reporting**: All outputs go to `/Reports/` directory
5. **Citation Integrity**: Every factual claim must cite source document + page/timestamp
6. **Workspace Sandboxing**: All operations scoped to workspace root with virtual paths
7. **Token Efficiency**: Only relevant skills loaded per conversation
8. **Multimedia Evidence**: Native support for images, audio, video with AI analysis (Gemini 3 Pro)
