# Troubleshooting

## "'NoneType' object has no attribute 'bind_tools'"

Use getter functions for models:
```python
# WRONG
from roscoe.agents.paralegal.models import agent_llm

# CORRECT
from roscoe.agents.paralegal.models import get_agent_llm
```

## UI Connection Issues

```bash
# Test API
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="curl -s http://localhost:8123/ok"

# Test UI
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="curl -s http://localhost:3000 | head -1"

# Restart UI
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
  pkill -f 'next dev'; cd /home/aaronwhaley/roscoe-ui && nohup npm run dev > /tmp/ui-dev.log 2>&1 &"
```

## LangSmith Not Showing Traces

Check docker-compose.yml has:
```yaml
LANGCHAIN_TRACING_V2: 'true'
LANGSMITH_API_KEY: lsv2_pt_...
LANGCHAIN_PROJECT: roscoe
```

Then: `sudo docker compose restart roscoe-agents`

## Knowledge Graph Issues

```bash
# Test connection
docker exec roscoe-falkordb redis-cli -p 6379 PING

# View logs
sudo docker logs roscoe-falkordb --tail 50

# Check agent graph errors
sudo docker logs roscoe-agents 2>&1 | grep -i "falkor\|graph\|cypher"
```

## Debugging Agent Runs

```bash
# Get run ID
sudo docker logs roscoe-agents | grep run_id | tail -1

# Find events
sudo docker logs roscoe-agents 2>&1 | grep '<run_id>' | grep -E '(tool|ERROR)'

# LangSmith URL
https://smith.langchain.com/o/{org}/projects/{project}/r?trace={run_id}
```

## Common Issues

| Issue | Check |
|-------|-------|
| Agent slow (20+ min) | Model inference time, check LangSmith |
| Tool returns empty | Tool inputs in logs, Cypher syntax |
| Middleware errors | "Event loop is closed" in logs |
| Graph timeouts | FalkorDB connection, index status |
