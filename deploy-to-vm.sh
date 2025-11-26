#!/bin/bash
# Deploy Roscoe to Google Compute VM
# Official LangGraph Standalone Server deployment

set -e

echo "========================================="
echo "Deploying Roscoe to Google Cloud VM"
echo "========================================="
echo ""

# Step 1: Push image to Docker Hub
echo "📦 Pushing image to Docker Hub..."
docker push agwhaley/roscoe-agents:standalone

echo ""
echo "✅ Image pushed!"
echo ""

# Step 2: Stop existing services
echo "🛑 Stopping existing services on VM..."
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
cd /tmp && sudo docker compose down 2>/dev/null || true"

echo ""

# Step 3: Pull new image on VM
echo "📥 Pulling new image on VM..."
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
sudo docker pull agwhaley/roscoe-agents:standalone"

echo ""

# Step 4: Update docker-compose to use standalone image
echo "📝 Updating docker-compose configuration..."
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
cd /tmp && \
sudo sed -i 's|image: agwhaley/roscoe-agents:production.*|image: agwhaley/roscoe-agents:standalone|' docker-compose.yml"

echo ""

# Step 5: Start services
echo "🚀 Starting Agent Server with PostgreSQL and Redis..."
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
cd /tmp && \
sudo docker compose up -d"

echo ""
echo "⏳ Waiting for services to start..."
sleep 20

# Step 6: Check status
echo ""
echo "📊 Checking deployment status..."
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
cd /tmp && \
sudo docker compose ps && \
echo '' && \
echo '---AGENT SERVER LOGS---' && \
sudo docker compose logs roscoe 2>&1 | tail -30"

echo ""
echo "========================================="
echo "🎉 Deployment Complete!"
echo "========================================="
echo ""
echo "Agent Server URL: http://35.223.94.19:8123"
echo ""
echo "Test it:"
echo "  curl http://35.223.94.19:8123/ok"
echo ""
echo "View logs:"
echo "  gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command='sudo docker compose -f /tmp/docker-compose.yml logs -f roscoe'"
echo ""
echo "Next: Connect this URL to LangSmith for tracing and monitoring"
echo ""
