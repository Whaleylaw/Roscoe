# Roscoe - Dynamic Skills-Based Paralegal AI Agent

Roscoe is an AI paralegal agent built with LangGraph that uses a dynamic skills architecture to handle legal research, medical records analysis, and case management.

## Features

- **Dynamic Skills Loading**: Skills are loaded automatically based on semantic matching to user requests
- **Adaptive Model Selection**: Switches between Claude Sonnet, Claude Haiku, and Gemini 3 Pro based on task requirements
- **Workflow Checkpointing**: Resume complex workflows after errors without starting over
- **Large Filesystem Support**: Access to 68GB+ of case files, medical records, and legal documents
- **HIPAA-Ready**: Self-hosted deployment keeps all data on your local machine

## Architecture

```
User Request
    ↓
SkillSelectorMiddleware (semantic search for relevant skills)
    ↓
Model Selector (choose optimal LLM: Gemini/Sonnet/Haiku)
    ↓
Agent Execution (with checkpointing)
    ↓
General-Purpose Sub-agents (inherit current model)
```

## Quick Start

### 1. Deploy Locally with Docker

```bash
./deploy.sh
```

This will:
- Start PostgreSQL for checkpointing
- Start Redis for caching
- Start LangGraph API server
- Mount your local filesystem
- Connect to LangSmith for monitoring

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
# Edit .env and add your keys
```

Required keys:
- `LANGSMITH_API_KEY` - For tracing and checkpointing
- `ANTHROPIC_API_KEY` - For Claude models
- `GOOGLE_API_KEY` - For Gemini models
- `TAVILY_API_KEY` - For web search (optional)

### 3. Access the API

```bash
curl http://localhost:8123/ok
```

## Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide with checkpointing setup
- **[workspace/Skills/](workspace/Skills/)** - Available skills and how to add new ones

## Skills

Skills are defined in `workspace/Skills/skills_manifest.json`:

- **Medical Records Analysis**: Parse, analyze, and summarize medical records with timeline extraction
- **Legal Research**: Research case law, statutes, and regulations

New skills can be added without code changes - just add a skill definition and markdown file.

## Models

- **Claude Sonnet 4.5**: Complex reasoning, medical analysis (default)
- **Claude Haiku 4.5**: Simple tasks, categorization
- **Gemini 3 Pro**: Multimodal analysis (images, PDFs), code execution

Models are selected automatically based on skill requirements.

## Checkpointing

Every workflow is automatically checkpointed to PostgreSQL. If an error occurs:

1. Fix the issue (code, data, or configuration)
2. Resume from the checkpoint
3. Continue where you left off

View all checkpoints in LangSmith: https://smith.langchain.com

## Cost

- **Infrastructure**: FREE (self-hosted on your machine)
- **LangSmith**: FREE (self-hosted tier)
- **API Calls**: ~$20-200/month depending on usage

## Support

For deployment issues, see [DEPLOYMENT.md](DEPLOYMENT.md).

For LangGraph documentation: https://langchain-ai.github.io/langgraph/
