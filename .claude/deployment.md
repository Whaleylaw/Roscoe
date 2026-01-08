# Deployment

## VM: roscoe-paralegal-vm (us-central1-a)

```
/home/aaronwhaley/
├── roscoe/src/roscoe/     # Agent source (mounted into container)
├── roscoe-ui/             # UI source (npm run dev directly on VM)
├── docker-compose.yml
└── .env

/mnt/workspace/            # GCS mount (whaley_law_firm bucket)
```

## Containers

| Container | Port | Purpose |
|-----------|------|---------|
| roscoe-agents | 8123→8000 | LangGraph API |
| roscoe-postgres | 5432 | Checkpointing |
| roscoe-redis | 6379 | Caching |
| roscoe-falkordb | 6380→6379 | Knowledge graph |

## UI

Runs in dev mode directly on VM (not Docker):
```bash
# .env.local
NEXT_PUBLIC_LANGGRAPH_API_URL=http://localhost:8123
```

## Sync Commands

```bash
# Sync agent code
gcloud compute scp --recurse "/Volumes/X10 Pro/Roscoe/src/roscoe" \
  aaronwhaley@roscoe-paralegal-vm:/home/aaronwhaley/roscoe/src/ \
  --zone=us-central1-a

# Sync UI (hot-reloads automatically)
gcloud compute scp --recurse "/Volumes/X10 Pro/Roscoe/ui/src" \
  aaronwhaley@roscoe-paralegal-vm:/home/aaronwhaley/roscoe-ui/ \
  --zone=us-central1-a

# Sync single file
gcloud compute scp "/Volumes/X10 Pro/Roscoe/src/roscoe/agents/paralegal/tools.py" \
  aaronwhaley@roscoe-paralegal-vm:/home/aaronwhaley/roscoe/src/roscoe/agents/paralegal/ \
  --zone=us-central1-a
```

## Restart Commands

```bash
# Restart agent
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  cd /home/aaronwhaley && sudo docker compose restart roscoe-agents"

# Restart UI
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  pkill -f 'next dev'; cd /home/aaronwhaley/roscoe-ui && nohup npm run dev > /tmp/ui-dev.log 2>&1 &"

# Full restart
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  cd /home/aaronwhaley && sudo docker compose down && sudo docker compose up -d"

# Check status
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  sudo docker ps --format 'table {{.Names}}\t{{.Status}}' && curl -s http://localhost:8123/ok"
```

## Environment Variables

```bash
# Core APIs
ANTHROPIC_API_KEY, GOOGLE_API_KEY, OPENAI_API_KEY
TAVILY_API_KEY, COURTLISTENER_API_KEY

# LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY, LANGCHAIN_PROJECT=roscoe

# Graph
FALKORDB_HOST=roscoe-graphdb
FALKORDB_PORT=6379

# Workspace
WORKSPACE_DIR=/mnt/workspace
LANGGRAPH_DEPLOYMENT=true
```
