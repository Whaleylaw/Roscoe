# Quick Start Guide - Legal Agent

Get the Whaley Law Firm legal agent running in 10 minutes.

## Prerequisites

- Python 3.11+
- Node.js 18+
- API keys (see below)

## 1. Clone and Setup

```bash
# Navigate to project
cd deepagents

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install DeepAgents library
pip install -e ./libs/deepagents

# Install legal agent dependencies
pip install -r requirements.txt
```

## 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Minimum required variables:**
```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
POSTGRES_CONNECTION_STRING=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
RUNLOOP_API_KEY=rl_...
TAVILY_API_KEY=tvly-...
```

**Get API Keys:**
- Anthropic: https://console.anthropic.com (required)
- OpenAI: https://platform.openai.com (required)
- Supabase: https://supabase.com (required - create free project)
- RunLoop: https://runloop.ai (required)
- Tavily: https://tavily.com (required for legal research)

## 3. Initialize Database

```bash
python -c "
from src.config.settings import DB_URI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string(DB_URI)
checkpointer = PostgresSaver.from_conn_string(DB_URI)

store.setup()
checkpointer.setup()
print('✅ Database initialized!')
"
```

## 4. Test Backend

```bash
# Test toolkit initialization
python -c "
import asyncio
from src.tools.toolkits import init_supabase_mcp, init_tavily_mcp

async def test():
    supabase = await init_supabase_mcp()
    tavily = await init_tavily_mcp()
    print(f'✅ Supabase tools: {len(supabase)}')
    print(f'✅ Tavily tools: {len(tavily)}')

asyncio.run(test())
"

# Test agent compilation
python -c "
import asyncio
from src.agents.legal_agent import initialize_agent

async def test():
    graph = await initialize_agent()
    print('✅ Agent compiled successfully!')

asyncio.run(test())
"
```

## 5. Run Backend

```bash
# Option A: LangGraph dev server (recommended for local dev)
langgraph dev --config langgraph.json --port 8000

# Option B: Direct Python invocation
python -c "
import asyncio
from src.agents.legal_agent import initialize_agent

async def main():
    graph = await initialize_agent()
    result = await graph.ainvoke(
        {'messages': [{'role': 'user', 'content': 'List your available tools'}]},
        config={'configurable': {'thread_id': 'quickstart-test'}}
    )
    print(result)

asyncio.run(main())
"
```

## 6. Setup Frontend

```bash
# Navigate to frontend
cd deep-agents-ui-main

# Install dependencies
yarn install  # or npm install

# Configure environment
cat > .env.local << EOF
NEXT_PUBLIC_LANGGRAPH_URL=http://localhost:8000
NEXT_PUBLIC_ASSISTANT_ID=legal_agent
EOF

# Start dev server
yarn dev
```

Open browser to http://localhost:3000

## 7. Test the System

In the frontend chat interface, try these commands:

1. **List tools**: "What tools do you have access to?"
2. **Check skills**: "What skills are available in /memories/skills/?"
3. **Test code execution**: "Write a Python script to calculate 2+2"
4. **Test database**: "Query the doc_files table in Supabase"
5. **Test search**: "Search for recent Supreme Court cases about contracts"

## Common Issues

### Import Errors

```bash
# Make sure DeepAgents library is installed
pip install -e ./libs/deepagents

# Verify installation
python -c "import deepagents; print(deepagents.__version__)"
```

### MCP Server Fails

```bash
# Verify Node.js installed
node --version  # Should be 18+

# Test MCP servers manually
npx -y @supabase/mcp-server-postgrest
npx -y @mcptools/mcp-tavily
```

### Database Connection

```bash
# Test connection
python -c "
import psycopg
from src.config.settings import DB_URI
conn = psycopg.connect(DB_URI)
print('✅ Database connected!')
conn.close()
"
```

### RunLoop Errors

```bash
# Verify API key
python -c "
from runloop_api_client import Runloop
client = Runloop()
print('✅ RunLoop client initialized!')
"
```

## Optional: Gmail and Calendar

If you want email and calendar features:

1. Create Google Cloud project: https://console.cloud.google.com
2. Enable Gmail API and Google Calendar API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials.json
5. Set in .env:

```bash
GMAIL_CREDENTIALS=/path/to/gmail-credentials.json
GOOGLE_CALENDAR_CREDENTIALS=/path/to/calendar-credentials.json
```

First use will trigger OAuth consent flow.

## Next Steps

1. **Create skills**: Ask agent to create workflows and save to `/memories/skills/`
2. **Monitor usage**: Enable LangSmith tracing for debugging
3. **Customize prompts**: Edit `src/agents/legal_agent.py` system_prompt
4. **Add subagents**: Create specialized agents for specific tasks
5. **Deploy**: See DEPLOYMENT.md for production deployment

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│                   http://localhost:3000                      │
└──────────────────────────┬──────────────────────────────────┘
                           │ LangGraph SDK
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (LangGraph Agent)                   │
│                   http://localhost:8000                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Legal Agent (Claude Sonnet 4.5)                       │  │
│  │  - TodoListMiddleware (write_todos)                   │  │
│  │  - FilesystemMiddleware (ls, read, write, edit)      │  │
│  │  - SubAgentMiddleware (task delegation)              │  │
│  │  - RunLoop Code Executor (runloop_execute_code)      │  │
│  │  - MCP Tools (Supabase, Tavily, Gmail, Calendar)     │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────┬────────────────────────────┘
               │                  │
               ▼                  ▼
      ┌────────────────┐  ┌──────────────────┐
      │ Supabase       │  │ External APIs     │
      │ PostgreSQL     │  │ - RunLoop        │
      │ - Checkpoints  │  │ - Tavily         │
      │ - Memory Store │  │ - Gmail          │
      │ - Case Data    │  │ - Calendar       │
      └────────────────┘  └──────────────────┘
```

## Skills-First Workflow

The agent is optimized for token efficiency using a skills library:

1. **Check for skill**: Agent looks in `/memories/skills/` first
2. **Execute skill**: If match found, execute directly (4K tokens instead of 32K)
3. **Create new skill**: For complex tasks, save successful workflow as skill
4. **Reuse**: Next time, 88-98% token savings

Example skill execution:
```python
# Agent automatically runs:
exec(open('/memories/skills/batch_document_processor.py').read())
result = await run_skill(case_id='MVA-2024-001', limit=100)
```

## Token Efficiency Tips

- Always use code execution for data processing
- Return summaries, not full datasets
- Save frequently-used workflows as skills
- Filter and aggregate in Python, not LLM context

**Example**:
```python
# ❌ Bad: Returns 150K tokens to LLM
docs = supabase_query("SELECT * FROM doc_files")
return docs  # Full array in LLM context

# ✅ Good: Returns 2K tokens
docs = supabase_query("SELECT * FROM doc_files")
unconverted = [d for d in docs if not d['markdown_path']]
return {"total": len(docs), "unconverted": len(unconverted)}
```

## Resource Links

- **Full Deployment**: DEPLOYMENT.md
- **Architecture**: COMPLETE-ARCHITECTURE.md
- **Implementation Plans**: docs/spec/CORRECTED-PLANS/
- **DeepAgents Docs**: https://docs.langchain.com/oss/python/deepagents/overview
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/

## Support

For issues or questions, see:
- GitHub Issues: https://github.com/langchain-ai/deepagents/issues
- LangChain Discord: https://www.langchain.com/join-community

---

**Status**: ✅ Phase 2 Implementation Complete - Ready for deployment

**Version**: 1.0.0

**Last Updated**: November 2024
