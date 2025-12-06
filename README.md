# Deep Agent Coder

A multi-agent coding system built on [LangChain Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview).

## Overview

Deep Agent Coder orchestrates specialized AI agents to build software projects feature-by-feature:

- **Initializer Agent**: Orchestrates the workflow, creates plans, delegates to subagents
- **Coder Subagent**: Implements features one at a time
- **Tester Subagent**: Verifies implementations work correctly
- **Reviewer Subagent**: Reviews code for quality and security
- **Fixer Subagent**: Fixes bugs and addresses review feedback

## Features

All of these come from Deep Agents (no custom code needed):

| Feature | How It Works |
|---------|--------------|
| File System | Built-in `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` tools |
| Planning | Built-in `write_todos` tool for task tracking |
| Subagents | Built-in `task()` tool for spawning specialized agents |
| Context Management | Auto-summarizes at 170k tokens, evicts large results to files |
| Persistence | PostgresStore for cross-thread memory, PostgresSaver for checkpoints |

## Quick Start

### 1. Set up environment

```bash
# Clone and enter directory
cd deep-agent-coder

# Create .env file with your API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Set workspace path (where your code will live)
export WORKSPACE_PATH=/path/to/your/projects
```

### 2. Start with Docker

```bash
# Start Postgres
docker-compose up -d postgres

# Run interactive chat
docker-compose run agent chat

# Or start a new project
docker-compose run agent new my-app -i

# Continue an existing thread
docker-compose run agent continue my-app-a1b2c3d4 -i
```

### 3. Without Docker (development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run with in-memory storage (no Postgres)
python -m deep_agent_coder chat --simple --workspace ./workspace

# Or with Postgres
export DATABASE_URL=postgresql://user:pass@localhost:5432/deepagent
python -m deep_agent_coder chat --workspace ./workspace
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Deep Agent Coder                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Initializer Agent                       │    │
│  │  • Orchestrates workflow                            │    │
│  │  • Creates plans with write_todos                   │    │
│  │  • Delegates to subagents via task()               │    │
│  └──────────────┬──────────────────────────────────────┘    │
│                 │                                            │
│     ┌───────────┼───────────┬───────────┐                   │
│     ▼           ▼           ▼           ▼                   │
│  ┌──────┐  ┌──────┐  ┌──────────┐  ┌───────┐               │
│  │Coder │  │Tester│  │ Reviewer │  │ Fixer │               │
│  └──────┘  └──────┘  └──────────┘  └───────┘               │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                      Storage Layer                           │
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │   /workspace/       │  │      /memories/             │   │
│  │   FilesystemBackend │  │      StoreBackend           │   │
│  │   (local disk)      │  │      (Postgres)             │   │
│  └─────────────────────┘  └─────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              PostgresSaver (checkpoints)             │    │
│  │              Thread state persistence                │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## File System Layout

The agent sees two "directories":

```
/workspace/           ← Real files on your disk (code lives here)
  └── my-project/
      ├── src/
      ├── tests/
      └── ...

/memories/            ← Persistent in Postgres (survives across threads)
  └── projects/
      └── my-project/
          ├── features.json   ← Feature list and status
          ├── progress.json   ← Session history
          └── notes.md        ← Technical decisions
```

## Usage Examples

### Starting a new project

```
You: I want to build a REST API for a todo app using FastAPI

Agent: I'll create a plan for this project. Let me first set up the 
project structure and save our feature list.

[Creates /workspace/todo-api/ with basic structure]
[Saves features.json to /memories/projects/todo-api/]

Here's our feature list:
1. Project setup with FastAPI
2. Todo model and database
3. CRUD endpoints
4. Input validation
5. Error handling
6. Tests

Should I start with feature 1?
```

### Continuing work

```
You: Let's continue on the todo-api

Agent: [Reads /memories/projects/todo-api/features.json]

Current status:
- ✅ Feature 1: Project setup (complete)
- ✅ Feature 2: Todo model (complete)  
- 🔄 Feature 3: CRUD endpoints (in progress)
- ⏳ Features 4-6: Pending

Last session we were implementing the PUT endpoint. 
Should I continue with that?
```

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required |
| `DATABASE_URL` | Postgres connection string | `postgresql://coder:coder@localhost:5432/deepagent` |
| `WORKSPACE_PATH` | Local directory for code files | `./workspace` |

## CLI Commands

```bash
# Start new project with interactive chat
python -m deep_agent_coder new my-project -i

# Continue existing thread
python -m deep_agent_coder continue <thread-id> -i

# Send single message to thread
python -m deep_agent_coder continue <thread-id> -m "What's next?"

# Interactive chat (new thread)
python -m deep_agent_coder chat

# Use in-memory storage (no Postgres)
python -m deep_agent_coder chat --simple

# Custom workspace directory
python -m deep_agent_coder chat --workspace /path/to/projects
```

## How It Works

1. **Deep Agents Framework**: Provides the agent harness with built-in tools for file operations, planning, and subagent spawning.

2. **CompositeBackend**: Routes file operations to different storage:
   - `/workspace/*` → Local filesystem (your real code)
   - `/memories/*` → PostgresStore (persistent across threads)

3. **PostgresSaver**: Checkpoints thread state to Postgres, enabling:
   - Resume any conversation by thread ID
   - Multiple concurrent projects
   - Persistent history

4. **Subagents**: Specialized agents for different tasks:
   - Context isolation (subagent work doesn't clutter main agent)
   - Focused prompts for each role
   - Main agent receives only the final result

## Development

```bash
# Install in development mode
pip install -e .

# Run with simple storage for testing
python -m deep_agent_coder chat --simple --workspace ./test-workspace
```

## Credits

Built on [LangChain Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview), inspired by Anthropic's paper on effective harnesses for long-running agents.
