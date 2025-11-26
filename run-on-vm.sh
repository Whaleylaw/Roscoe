#!/bin/bash
# Script to run Roscoe agent on Google Compute VM
# Run this after the AMD64 image pull completes

set -e

echo "========================================="
echo "Starting Roscoe Agent on VM"
echo "========================================="
echo ""

# Check if pull completed
echo "Checking if AMD64 image is available..."
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
sudo docker images | grep amd64"

echo ""
echo "Running container with GCS workspace mounted..."

gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
sudo docker run -d \
  --name roscoe-paralegal \
  -p 8080:8000 \
  -v /mnt/workspace:/app/workspace_paralegal \
  --restart unless-stopped \
  agwhaley/roscoe-agents:amd64
"

echo ""
echo "Waiting for container to start..."
sleep 5

echo ""
echo "Checking container status..."
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
sudo docker ps | grep roscoe-paralegal"

echo ""
echo "Checking container logs..."
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="
sudo docker logs roscoe-paralegal 2>&1 | tail -20"

echo ""
echo "========================================="
echo "✅ Agent should be running!"
echo "========================================="
echo ""
echo "Agent URL: http://35.223.94.19:8080"
echo ""
echo "Test it:"
echo "  curl http://35.223.94.19:8080/ok"
echo ""
