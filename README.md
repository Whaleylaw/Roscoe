# Roscoe - AI Paralegal Agent

An AI-powered paralegal assistant built on LangGraph with a custom React UI.

## Architecture

```
roscoe/
├── src/roscoe/           # Backend (Python/LangGraph)
│   ├── agents/
│   │   ├── paralegal/    # Main paralegal agent
│   │   └── coding/       # Coding agent
│   ├── core/             # Middleware (case context, skills)
│   └── workflow_engine/  # State machine
│
├── ui/                   # Frontend (Next.js)
│   └── src/
│       ├── app/          # Pages & API routes
│       ├── components/   # React components
│       └── hooks/        # Custom hooks
│
├── slack_bot.py          # Slack integration
└── langgraph.json        # Agent configuration
```

## Quick Start

### 1. Environment Setup

```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys (Anthropic, OpenAI, Tavily, etc.)
```

### 2. Backend (LangGraph Agent)

```bash
# Install Python dependencies
uv sync  # or pip install -e .

# Run development server
langgraph dev
```

The agent will be available at `http://localhost:8123`

### 3. Frontend (Next.js UI)

```bash
cd ui
npm install
npm run dev
```

The UI will be available at `http://localhost:3000`

### 4. Slack Bot (Optional)

```bash
# Set Slack tokens in .env
# SLACK_BOT_TOKEN=xoxb-...
# SLACK_APP_TOKEN=xapp-...

python slack_bot.py
```

## Google OAuth Setup (Gmail/Calendar)

1. Create OAuth credentials in Google Cloud Console
2. Download as `client_secret_*.json` 
3. Run the agent - it will prompt for OAuth on first use
4. Token saved to `token.json`

## Production Deployment

The VM deployment uses Docker Compose with mounted source code:

```bash
# Sync code to VM
gcloud compute scp --recurse src/roscoe VM:/home/user/roscoe/src/
gcloud compute scp --recurse ui/src VM:/home/user/roscoe-ui/

# Restart services
ssh VM "cd /home/user && docker compose restart roscoe-agents"
```

## Key Files

| File | Purpose |
|------|---------|
| `langgraph.json` | Agent entry points |
| `pyproject.toml` | Python dependencies |
| `.env` | API keys (not in git) |
| `slack_bot.py` | Slack integration |
| `CLAUDE.md` | AI context documentation |

## License

Private - Whaley Law Firm
