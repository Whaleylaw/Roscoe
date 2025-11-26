# Roscoe Docker Deployment Guide

This guide covers building, testing, and deploying Roscoe agents using Docker containers.

## Quick Start

### 1. Local Development with Docker Compose

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env

# Start all services (Roscoe + PostgreSQL)
docker-compose up -d

# View logs
docker-compose logs -f roscoe

# Test the API
curl http://localhost:8123/ok

# Stop services
docker-compose down
```

The agent will be available at: `http://localhost:8123`

### 2. Build and Push to Docker Hub

```bash
# Build and optionally push to Docker Hub
./build-docker.sh v0.1.0

# Or set your Docker Hub username as environment variable
DOCKER_USERNAME=yourusername ./build-docker.sh v0.1.0
```

### 3. Pull and Run from Docker Hub

```bash
# Pull the image
docker pull yourusername/roscoe-agents:latest

# Run with environment file
docker run -p 8123:8000 --env-file .env yourusername/roscoe-agents:latest

# Run with individual environment variables
docker run -p 8123:8000 \
  -e ANTHROPIC_API_KEY=your_key \
  -e GOOGLE_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  yourusername/roscoe-agents:latest
```

## Architecture

The Docker setup includes:

- **Dockerfile**: Multi-stage build optimized for LangGraph Cloud
- **docker-compose.yml**: Local development environment with PostgreSQL
- **build-docker.sh**: Automated build and push script
- **.dockerignore**: Optimized for minimal image size

## Image Details

### What's Included

- Python 3.11 base image
- All Roscoe dependencies (LangGraph, LangChain, etc.)
- Source code (`src/roscoe/`)
- Skills templates (`workspace_paralegal/Skills/`)
- Tools templates (`workspace_paralegal/Tools/`)

### What's NOT Included

- Runtime-generated reports (`workspace_*/Reports/`)
- Agent-generated scripts (`workspace_*/Tools/_generated/`)
- Case files (mount as volumes if needed)
- `.env` file (provide via environment variables)

### Image Size

Approximately 2-3 GB (includes ML dependencies like sentence-transformers)

## Environment Variables

### Required

```bash
ANTHROPIC_API_KEY=sk-ant-...      # Claude models
GOOGLE_API_KEY=...                 # Gemini models
```

### Optional

```bash
TAVILY_API_KEY=...                 # Web search
LANGCHAIN_TRACING_V2=true          # Enable LangSmith tracing
LANGCHAIN_API_KEY=...              # LangSmith API key
LANGCHAIN_PROJECT=roscoe-prod      # LangSmith project name
DATABASE_URI=postgres://...        # PostgreSQL for checkpointing
```

### Research Tools (Optional)

```bash
NCBI_EMAIL=you@example.com         # PubMed searches
NCBI_API_KEY=...                   # PubMed (higher rate limits)
COURTLISTENER_API_KEY=...          # Legal research
```

## Deployment Options

### Option 1: Docker Compose (Local Development)

Best for local testing and development.

```bash
docker-compose up -d
```

Includes:
- Roscoe agent (port 8123)
- PostgreSQL database (port 5432)
- Persistent volumes for data

### Option 2: Standalone Container

Best for simple deployments without database persistence.

```bash
docker run -d \
  --name roscoe \
  -p 8123:8000 \
  --env-file .env \
  yourusername/roscoe-agents:latest
```

### Option 3: Docker Hub + External PostgreSQL

Best for production deployments.

```bash
docker run -d \
  --name roscoe \
  -p 8123:8000 \
  -e ANTHROPIC_API_KEY=... \
  -e GOOGLE_API_KEY=... \
  -e DATABASE_URI=postgres://user:pass@host:5432/db \
  yourusername/roscoe-agents:latest
```

### Option 4: LangGraph Cloud

Best for production at scale with managed infrastructure.

1. Push your image to Docker Hub
2. Deploy via LangGraph Cloud UI
3. Reference your image: `yourusername/roscoe-agents:latest`

See: https://langchain-ai.github.io/langgraph/cloud/

## Workspace Volumes (Optional)

To persist agent-generated files (reports, tools, etc.):

```bash
docker run -d \
  --name roscoe \
  -p 8123:8000 \
  --env-file .env \
  -v $(pwd)/workspace_paralegal:/app/workspace_paralegal \
  -v $(pwd)/workspace_coding:/app/workspace_coding \
  yourusername/roscoe-agents:latest
```

This mounts your local workspace directories into the container, allowing you to:
- Access generated reports on your host machine
- Provide case files to the agent
- Inspect agent-generated tools

## Testing the Deployment

### Health Check

```bash
curl http://localhost:8123/ok
# Expected: {"status":"ok"}
```

### List Available Graphs

```bash
curl http://localhost:8123/graphs
# Expected: {"graphs": ["roscoe_paralegal", "roscoe_coding"]}
```

### Invoke Paralegal Agent

```bash
curl -X POST http://localhost:8123/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "roscoe_paralegal",
    "input": {
      "messages": [{"role": "user", "content": "Hello, who are you?"}]
    }
  }'
```

## Updating the Image

### Build New Version

```bash
# Build new version
./build-docker.sh v0.2.0

# Push to Docker Hub (prompted during build)
# Or manually:
docker push yourusername/roscoe-agents:v0.2.0
docker push yourusername/roscoe-agents:latest
```

### Pull and Restart

```bash
# Pull latest
docker pull yourusername/roscoe-agents:latest

# Stop old container
docker stop roscoe
docker rm roscoe

# Start new container
docker run -d --name roscoe -p 8123:8000 --env-file .env yourusername/roscoe-agents:latest
```

Or with docker-compose:

```bash
docker-compose pull
docker-compose up -d
```

## Troubleshooting

### Check Logs

```bash
# Docker Compose
docker-compose logs -f roscoe

# Standalone container
docker logs -f roscoe
```

### Common Issues

**Port already in use:**
```bash
# Use a different port
docker run -p 8124:8000 ...
```

**Missing API keys:**
```bash
# Check environment variables
docker exec roscoe env | grep API_KEY
```

**Database connection failed:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check DATABASE_URI is correct
docker exec roscoe env | grep DATABASE_URI
```

### Enter Container for Debugging

```bash
docker exec -it roscoe bash

# Check Python packages
pip list | grep langchain

# Test imports
python -c "from roscoe.agents.paralegal.agent import personal_assistant_agent; print('OK')"
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Image

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/roscoe-agents:${{ github.ref_name }}
            ${{ secrets.DOCKER_USERNAME }}/roscoe-agents:latest
```

## Security Considerations

1. **Never commit .env file** - Contains sensitive API keys
2. **Use secrets management** - For production, use Docker secrets or environment injection
3. **Scan images** - Use `docker scan yourusername/roscoe-agents:latest`
4. **Update base image** - Regularly rebuild to get security patches
5. **Restrict network access** - Use firewalls and network policies in production

## Multi-Platform Builds (Optional)

To build for multiple architectures (AMD64, ARM64):

```bash
# Create builder
docker buildx create --use

# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 \
  -t yourusername/roscoe-agents:latest \
  --push .
```

## Next Steps

- **Production Deployment**: See LangGraph Cloud documentation
- **Monitoring**: Set up LangSmith tracing with `LANGCHAIN_TRACING_V2=true`
- **Scaling**: Use Kubernetes or Docker Swarm for multi-container orchestration
- **Custom Skills**: Mount custom skills directory as volume

## Support

- **Issues**: https://github.com/yourusername/roscoe/issues
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Docker Docs**: https://docs.docker.com/
