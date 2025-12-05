#!/bin/bash
# Deploy Roscoe CopilotKit Server to Google Compute VM
# This adds the CopilotKit wrapper service alongside the existing LangGraph server

set -e

echo "========================================="
echo "Deploying CopilotKit Server to GCE VM"
echo "========================================="
echo ""

# Configuration
VM_NAME="roscoe-paralegal-vm"
ZONE="us-central1-a"
IMAGE_TAG="copilotkit"
COPILOTKIT_PORT=8124

# Step 1: Build new Docker image with CopilotKit dependencies
echo "📦 Building Docker image with CopilotKit support..."
if [ -f "Dockerfile" ]; then
    docker build -t agwhaley/roscoe-agents:${IMAGE_TAG} .
else
    # Use langgraph CLI to build
    langgraph build -t agwhaley/roscoe-agents:${IMAGE_TAG}
fi

echo ""
echo "✅ Build complete!"

# Step 2: Push to Docker Hub
echo ""
echo "📤 Pushing image to Docker Hub..."
docker push agwhaley/roscoe-agents:${IMAGE_TAG}

echo ""
echo "✅ Image pushed!"

# Step 3: Create the CopilotKit docker-compose override file
echo ""
echo "📝 Creating CopilotKit service configuration..."

cat << 'COMPOSE_OVERRIDE' > /tmp/docker-compose.copilotkit.yml
version: '3.8'
services:
  roscoe-copilotkit:
    image: agwhaley/roscoe-agents:copilotkit
    container_name: roscoe-copilotkit
    ports:
      - "8124:8124"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY:-}
      - THESYS_API_KEY=${THESYS_API_KEY}
      - LANGCHAIN_TRACING_V2=true
      - LANGSMITH_API_KEY=${LANGSMITH_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
      - SLACK_APP_TOKEN=${SLACK_APP_TOKEN}
      - SLACK_DEFAULT_CHANNEL=${SLACK_DEFAULT_CHANNEL:-#legal-updates}
      - LANGCHAIN_PROJECT=${LANGCHAIN_PROJECT:-roscoe-local}
      - DATABASE_URI=postgres://postgres:postgres@postgres:5432/postgres?sslmode=disable
      - REDIS_URI=redis://redis:6379
      - WORKSPACE_DIR=/app/workspace_paralegal
      - WORKSPACE_ROOT=/mnt/workspace
      - LANGGRAPH_DEPLOYMENT=true
      - PYTHONUNBUFFERED=1
      - COPILOTKIT_PORT=8124
    volumes:
      - /mnt/workspace:/app/workspace_paralegal
      - /mnt/workspace:/mnt/workspace
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - roscoe-network
    restart: unless-stopped
    command: ["python", "-m", "roscoe.copilotkit_server"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8124/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

networks:
  roscoe-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
COMPOSE_OVERRIDE

echo "✅ Configuration created"

# Step 4: Copy configuration to VM
echo ""
echo "📤 Copying configuration to VM..."
gcloud compute scp /tmp/docker-compose.copilotkit.yml ${VM_NAME}:/tmp/docker-compose.copilotkit.yml --zone=${ZONE}

echo ""
echo "✅ Configuration copied"

# Step 5: Pull new image and start CopilotKit service on VM
echo ""
echo "📥 Pulling new image on VM..."
gcloud compute ssh ${VM_NAME} --zone=${ZONE} --command="
sudo docker pull agwhaley/roscoe-agents:${IMAGE_TAG}"

echo ""
echo "🚀 Starting CopilotKit server..."
gcloud compute ssh ${VM_NAME} --zone=${ZONE} --command="
cd /tmp && \
sudo docker compose -f docker-compose.yml -f docker-compose.copilotkit.yml up -d roscoe-copilotkit"

echo ""
echo "⏳ Waiting for service to start..."
sleep 15

# Step 6: Check status
echo ""
echo "📊 Checking deployment status..."
gcloud compute ssh ${VM_NAME} --zone=${ZONE} --command="
cd /tmp && \
sudo docker compose -f docker-compose.yml -f docker-compose.copilotkit.yml ps && \
echo '' && \
echo '---COPILOTKIT SERVER LOGS---' && \
sudo docker logs roscoe-copilotkit 2>&1 | tail -20"

# Get external IP
EXTERNAL_IP=$(gcloud compute instances describe ${VM_NAME} --zone=${ZONE} --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo ""
echo "========================================="
echo "🎉 CopilotKit Deployment Complete!"
echo "========================================="
echo ""
echo "CopilotKit Server URL: http://${EXTERNAL_IP}:${COPILOTKIT_PORT}/copilotkit"
echo "Health Check: http://${EXTERNAL_IP}:${COPILOTKIT_PORT}/health"
echo ""
echo "Test it:"
echo "  curl http://${EXTERNAL_IP}:${COPILOTKIT_PORT}/health"
echo ""
echo "IMPORTANT: Don't forget to open port ${COPILOTKIT_PORT} in the GCE firewall:"
echo ""
echo "  gcloud compute firewall-rules create allow-roscoe-copilotkit \\"
echo "    --allow tcp:${COPILOTKIT_PORT} \\"
echo "    --source-ranges 0.0.0.0/0 \\"
echo "    --description 'Allow access to Roscoe CopilotKit Server'"
echo ""
echo "Update your .env.local in roscoe-ui:"
echo "  ROSCOE_COPILOTKIT_URL=http://${EXTERNAL_IP}:${COPILOTKIT_PORT}/copilotkit"
echo ""

