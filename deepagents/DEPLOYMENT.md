# Legal Agent Deployment Guide

This guide covers deploying the Whaley Law Firm legal case management agent to production.

## Overview

The system consists of:
- **Backend**: Python LangGraph agent (`src/agents/legal_agent.py`)
- **Frontend**: Next.js UI (`deep-agents-ui-main/`)
- **Database**: Supabase PostgreSQL (shared by both)

## Prerequisites

### System Requirements

- Python 3.11+ (backend)
- Node.js 18+ and npm/yarn (frontend and MCP servers)
- PostgreSQL database (Supabase provides this)
- Git (for deployment)

### Required API Keys and Credentials

Before deployment, obtain these credentials:

1. **Anthropic API Key** (required)
   - Sign up at https://console.anthropic.com
   - Create API key from dashboard
   - Set as `ANTHROPIC_API_KEY`

2. **OpenAI API Key** (required for GPT-4o subagents)
   - Sign up at https://platform.openai.com
   - Create API key from dashboard
   - Set as `OPENAI_API_KEY`

3. **Supabase Project** (required)
   - Create project at https://supabase.com
   - Get project URL from Settings > API
   - Get service role key from Settings > API (secret!)
   - Set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
   - Get PostgreSQL connection string from Settings > Database
   - Set `POSTGRES_CONNECTION_STRING`

4. **RunLoop API Key** (required)
   - Sign up at https://runloop.ai
   - Create API key from dashboard
   - Set as `RUNLOOP_API_KEY`

5. **Tavily API Key** (required for legal research)
   - Sign up at https://tavily.com
   - Create API key from dashboard
   - Set as `TAVILY_API_KEY`

6. **Google OAuth Credentials** (optional, for Gmail/Calendar)
   - Create project at https://console.cloud.google.com
   - Enable Gmail API and Google Calendar API
   - Create OAuth 2.0 credentials (Desktop app type)
   - Download credentials JSON file
   - Set `GMAIL_CREDENTIALS` and `GOOGLE_CALENDAR_CREDENTIALS` to file paths

7. **LangSmith** (optional, for observability)
   - Sign up at https://smith.langchain.com
   - Create API key from Settings
   - Set `LANGSMITH_API_KEY`, `LANGSMITH_TRACING=true`, `LANGSMITH_PROJECT=whaley-legal-agent`

## Backend Deployment

### Step 1: Install Dependencies

```bash
# Navigate to project root
cd deepagents

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install DeepAgents library (local development)
pip install -e ./libs/deepagents

# Install legal agent dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Fill in all required variables. See `.env.example` for detailed descriptions.

### Step 3: Database Setup

The agent uses PostgreSQL for state checkpointing and memory storage. Initialize the database tables:

```python
# Run this ONCE on first deployment to create tables
python -c "
from src.config.settings import DB_URI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string(DB_URI)
checkpointer = PostgresSaver.from_conn_string(DB_URI)

store.setup()
checkpointer.setup()
print('Database tables created successfully!')
"
```

**Important**: Only run `setup()` once. Comment it out in `src/agents/legal_agent.py` after initial deployment.

### Step 4: Test Backend Locally

```bash
# Test toolkit initialization
python -c "
import asyncio
from src.tools.toolkits import init_gmail_toolkit, init_calendar_toolkit, init_supabase_mcp, init_tavily_mcp

async def test():
    gmail = await init_gmail_toolkit()
    calendar = await init_calendar_toolkit()
    supabase = await init_supabase_mcp()
    tavily = await init_tavily_mcp()
    print(f'Gmail tools: {len(gmail)}')
    print(f'Calendar tools: {len(calendar)}')
    print(f'Supabase tools: {len(supabase)}')
    print(f'Tavily tools: {len(tavily)}')

asyncio.run(test())
"
```

Expected output (with all credentials configured):
```
Gmail tools: 5
Calendar tools: 7
Supabase tools: [varies by server]
Tavily tools: [varies by server]
```

If a toolkit returns 0 tools, check:
- Environment variables are set correctly
- Credentials files exist at specified paths (Gmail/Calendar)
- Node.js is installed (required for MCP servers)

### Step 5: Test Agent Compilation

```bash
python -c "
import asyncio
from src.agents.legal_agent import initialize_agent

async def test():
    graph = await initialize_agent()
    print('Agent compiled successfully!')
    print(f'Graph nodes: {list(graph.nodes.keys())}')

asyncio.run(test())
"
```

### Step 6: Deploy to Production

**Option A: LangGraph Cloud (Recommended)**

1. Create `langgraph.json` in project root:

```json
{
  "graphs": {
    "legal_agent": {
      "path": "src/agents/legal_agent.py:initialize_agent",
      "config": {
        "checkpointer": true
      }
    }
  },
  "python_version": "3.11"
}
```

2. Deploy via LangSmith UI:
   - Go to https://smith.langchain.com
   - Navigate to Deployments
   - Click "New Deployment"
   - Connect GitHub repository
   - Configure environment variables
   - Deploy

3. Get deployment URL from LangSmith dashboard

**Option B: Self-Hosted Docker**

```bash
# Install LangGraph CLI
pip install langgraph-cli

# Build Docker image
langgraph build -t whaley-legal-agent:v1

# Run container
docker run -p 8000:8000 --env-file .env whaley-legal-agent:v1
```

**Option C: Direct Python Server**

```bash
# Run LangGraph server directly
langgraph dev --config langgraph.json --port 8000
```

## Frontend Deployment

### Step 1: Configure Frontend

```bash
cd deep-agents-ui-main

# Install dependencies
yarn install  # or npm install
```

### Step 2: Environment Variables

Create `.env.local`:

```bash
# LangGraph backend URL (from backend deployment)
NEXT_PUBLIC_LANGGRAPH_URL=https://your-deployment.langchain.com

# Or for local development:
# NEXT_PUBLIC_LANGGRAPH_URL=http://localhost:8000

# Assistant/Graph ID
NEXT_PUBLIC_ASSISTANT_ID=legal_agent
```

### Step 3: Test Locally

```bash
# Start development server
yarn dev

# Open browser to http://localhost:3000
```

Verify:
- Chat interface loads
- Can send messages to agent
- Tools are called and displayed
- Thread/conversation state persists

### Step 4: Deploy Frontend

**Vercel (Recommended):**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Follow prompts to:
# - Connect GitHub repository
# - Configure environment variables
# - Deploy to production
```

**Or via Vercel Dashboard:**
1. Go to https://vercel.com
2. Import GitHub repository
3. Configure environment variables in Settings
4. Deploy

**Alternative: Netlify, AWS Amplify, etc.**

The frontend is a standard Next.js app and can be deployed to any hosting platform that supports Node.js.

## Post-Deployment Verification

### Backend Health Check

```bash
# Test agent invocation
curl -X POST https://your-deployment.langchain.com/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [{"role": "user", "content": "List available skills"}]
    },
    "config": {
      "configurable": {"thread_id": "test-thread-1"}
    }
  }'
```

### Frontend Health Check

1. Open frontend URL in browser
2. Start new conversation
3. Send test message: "What tools do you have access to?"
4. Verify agent responds with list of tools
5. Check that tool calls are displayed with correct badges

### Skills Library Verification

```bash
# The agent should automatically check /memories/skills/ on first use
# Test by asking: "What skills are available?"

# Or verify directly in database
python -c "
from src.config.settings import DB_URI
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string(DB_URI)
# Query store for skills
print('Skills directory initialized')
"
```

## Monitoring and Observability

### LangSmith Tracing

If `LANGSMITH_TRACING=true`, all agent executions will be traced to LangSmith:

1. Go to https://smith.langchain.com
2. Select your project (`whaley-legal-agent`)
3. View traces for debugging

### Logs

**Backend logs:**
- LangGraph Cloud: View in LangSmith UI > Deployments > Logs
- Self-hosted: Check stdout/stderr or Docker logs

**Frontend logs:**
- Vercel: View in Vercel dashboard > Deployments > Function Logs
- Self-hosted: Check browser console and server logs

## Troubleshooting

### Gmail/Calendar OAuth Flow

On first toolkit initialization, OAuth consent flow is triggered:

1. Open the URL printed to logs
2. Authorize the application
3. `token.json` is created for future authentication
4. Subsequent requests use refresh token automatically

### MCP Server Issues

If Supabase or Tavily MCP servers fail to initialize:

**Check Node.js:**
```bash
node --version  # Should be 18+
npx --version
```

**Test MCP server manually:**
```bash
# Test Supabase MCP
npx -y @supabase/mcp-server-postgrest

# Test Tavily MCP
npx -y @mcptools/mcp-tavily
```

**Check environment variables:**
```bash
env | grep -E "(SUPABASE|TAVILY)"
```

### Database Connection Issues

**Test PostgreSQL connection:**
```bash
python -c "
import psycopg
from src.config.settings import DB_URI
conn = psycopg.connect(DB_URI)
print('Database connected successfully!')
conn.close()
"
```

**Common issues:**
- Firewall blocking port 5432
- Incorrect password in connection string
- Database not accepting connections from deployment IP

### RunLoop Sandbox Issues

**Test RunLoop connectivity:**
```bash
python -c "
from runloop_api_client import Runloop
client = Runloop()  # Auto-loads RUNLOOP_API_KEY
print('RunLoop client initialized successfully!')
"
```

**Common issues:**
- Invalid API key
- Network connectivity
- Rate limiting (check RunLoop dashboard)

## Security Best Practices

### Environment Variables

- **Never commit `.env` to version control** (already in `.gitignore`)
- Use secrets management for production (Vercel secrets, Docker secrets, etc.)
- Rotate API keys regularly
- Use separate keys for development and production

### Database Access

- **Service role key bypasses RLS** - only use in backend, never expose to frontend
- Use anon key for frontend if needed (not in current architecture)
- Enable Row Level Security (RLS) policies in Supabase
- Monitor database access logs

### Code Execution

- RunLoop provides isolated sandboxes - no additional security needed
- Review user-provided code before execution if accepting external input
- Set reasonable timeout limits (default: 60 seconds)
- Monitor execution metrics and costs

## Maintenance

### Database Maintenance

```bash
# Backup database regularly (Supabase provides automatic backups)
# Check backup status in Supabase dashboard > Settings > Database

# Clean up old checkpoints periodically
python -c "
from src.config.settings import DB_URI
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(DB_URI)
# Implement cleanup logic based on thread age
"
```

### Dependency Updates

```bash
# Update Python dependencies
pip install --upgrade -r requirements.txt

# Update frontend dependencies
cd deep-agents-ui-main
yarn upgrade

# Test thoroughly after updates
```

### Skills Library Management

The `/memories/skills/` directory grows over time. Monitor and maintain:

1. Review skills periodically for accuracy
2. Remove obsolete or broken skills
3. Optimize frequently-used skills
4. Document skills with clear usage examples

## Cost Estimation

Estimated monthly costs for production deployment:

| Service | Cost | Notes |
|---------|------|-------|
| Anthropic API | $100-500 | Varies by usage, ~$3 per 1M input tokens |
| OpenAI API | $50-200 | GPT-4o subagents, ~$2.50 per 1M input tokens |
| RunLoop | $50-200 | Sandboxed execution, pay-per-use |
| Supabase | $25 | Pro plan with PostgreSQL + storage |
| Tavily | $50-100 | Search API, varies by query volume |
| Vercel | $20 | Pro plan for frontend hosting |
| LangSmith | $0-100 | Free tier available, pay for high volume |
| **Total** | **$295-1,175/month** | Actual costs vary significantly by usage |

To reduce costs:
- Use Claude Haiku for simple tasks (80% cheaper)
- Implement aggressive skills library to reduce token usage (88-98% savings)
- Cache common queries
- Monitor usage with LangSmith and optimize expensive calls

## Support and Resources

- **DeepAgents Docs**: https://docs.langchain.com/oss/python/deepagents/overview
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangChain MCP**: https://docs.langchain.com/oss/python/langchain/mcp
- **Supabase Docs**: https://supabase.com/docs
- **RunLoop Docs**: https://docs.runloop.ai

For issues specific to this implementation, see:
- `COMPLETE-ARCHITECTURE.md` - Full system architecture
- `docs/spec/CORRECTED-PLANS/` - Implementation plans
- `README.md` - DeepAgents library overview

## Breaking Changes from Previous Implementation

This implementation includes breaking changes from the original architecture:

### Environment Variable Changes

**Gmail Toolkit:**
- **Old**: `GMAIL_CREDENTIALS` was JSON string
- **New**: `GMAIL_CREDENTIALS` is file path to `credentials.json`

**Calendar Toolkit:**
- **Old**: `GOOGLE_CALENDAR_CREDENTIALS` was JSON string
- **New**: `GOOGLE_CALENDAR_CREDENTIALS` is file path to `credentials.json`

### New Environment Variables

- `RUNLOOP_API_KEY` - Required for code execution (replaces PythonREPLTool)

### Package Changes

**Removed:**
- PythonREPLTool (insecure, no sandboxing)

**Added:**
- `runloop-api-client>=0.66.1` - Sandboxed code execution
- `langchain-google-community>=2.0.0` - Native Gmail/Calendar toolkits
- `langchain-mcp-adapters>=0.1.0` - MCP protocol support

### MCP Server Packages

**Corrected packages (verify npm):**
- Supabase: `@supabase/mcp-server-postgrest` (corrected from incorrect package)
- Tavily: `@mcptools/mcp-tavily` (corrected from incorrect package)

### Migration Checklist

If migrating from previous implementation:

- [ ] Update environment variables (Gmail/Calendar to file paths)
- [ ] Add `RUNLOOP_API_KEY` environment variable
- [ ] Install new dependencies: `pip install -r requirements.txt`
- [ ] Update MCP server package names if configured externally
- [ ] Test toolkit initialization (should return non-zero tool counts)
- [ ] Verify code execution works (test with simple Python script)
- [ ] Update system prompts to reference `runloop_execute_code` instead of `python_repl`

## Next Steps

After successful deployment:

1. **Create Initial Skills**: Ask agent to create common workflows and save as skills
2. **Monitor Token Usage**: Track token efficiency improvements over time
3. **Train Users**: Educate law firm staff on how to interact with agent
4. **Iterate on Prompts**: Refine system prompts based on real-world usage
5. **Add Custom Toolkits**: Integrate additional legal research APIs as needed

---

**Deployment Status**: ✅ Implementation complete, ready for deployment

**Last Updated**: November 2024

**Version**: 1.0.0 (Phase 2 Implementation Complete)
