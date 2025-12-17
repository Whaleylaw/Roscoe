# Roscoe - Paralegal AI Agent

Production LangGraph-based paralegal AI agent for personal injury litigation.

## Repository Structure

This repository contains:

### 📦 production-vm-code/ (1.1MB)
**VM Code Snapshot** - Exact copy of code running on production VM

- Complete Python source (25 files)
- Production configuration (docker-compose.yml)
- Documentation (CLAUDE.md, bug fixes)
- **Use this to**: Compare with local dev, reference production settings

**Production VM**: `34.63.223.97` (roscoe-paralegal-vm, us-central1-a)

### 💻 local-dev-code/ (764KB)
**Local Development** - Clean working version for development

- Source code (src/roscoe/)
- Configuration (pyproject.toml, langgraph.json)
- Documentation (CLAUDE.md, SLACK_SETUP.md)
- Build scripts (build-docker.sh, deploy-to-vm.sh)

**Use this to**: Develop and test locally before deploying

### 📚 archive-20251208.tar.gz (775MB)
**Archived Clutter** - Everything else compressed

Contents:
- roscoe-ui/ (1.4GB) - Next.js UI project
- workspace_paralegal/ (75MB) - Runtime workspace (gitignored)
- Roscoe_workflows/ (65MB) - Old workflow materials
- Document_templates/ (39MB)
- forms/ (16MB)
- PDF case files (123MB)
- Misc loose files

## Development Workflow

### Local Development

```bash
cd "/Volumes/X10 Pro/Roscoe/local-dev-code"

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run locally
langgraph dev
```

### Deploy to Production

```bash
# 1. Test locally first
cd local-dev-code
langgraph dev

# 2. Copy changes to VM
gcloud compute scp --recurse --zone us-central1-a \
  src/roscoe/agents/paralegal/ \
  roscoe-paralegal-vm:~/roscoe/src/roscoe/agents/paralegal/

# 3. Restart on VM
gcloud compute ssh roscoe-paralegal-vm --zone us-central1-a \
  --command "cd ~ && docker compose restart roscoe"
```

### Compare Production vs Local

```bash
# See what's different
diff production-vm-code/src/roscoe/agents/paralegal/agent.py \
     local-dev-code/src/roscoe/agents/paralegal/agent.py
```

## Production Environment

**VM**: roscoe-paralegal-vm (us-central1-a)  
**IP**: 34.63.223.97  
**Workspace**: GCS bucket (whaley_law_firm) at `/mnt/workspace`  
**Services**: Docker Compose (postgres, redis, roscoe, ui)

**Ports**:
- 8123: LangGraph API
- 8124: CopilotKit
- 3000: UI
- 5432: PostgreSQL
- 6379: Redis

## Documentation

- **local-dev-code/CLAUDE.md** - Complete architecture & development guide
- **production-vm-code/CLAUDE.md** - Production deployment guide
- **local-dev-code/SLACK_SETUP.md** - Slack integration setup
- **production-vm-code/BUGFIX_CASE_MATCHING.md** - Recent bug fixes

## Archive Contents

To extract archived files if needed:

```bash
# List contents
tar -tzf archive-20251208.tar.gz | head -20

# Extract specific file
tar -xzf archive-20251208.tar.gz path/to/file

# Extract everything
tar -xzf archive-20251208.tar.gz
```

## Support

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangSmith**: https://smith.langchain.com/projects/roscoe-local
- **Production VM**: `gcloud compute ssh roscoe-paralegal-vm --zone us-central1-a`
