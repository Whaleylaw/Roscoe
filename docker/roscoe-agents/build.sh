#!/bin/bash
# Build script for roscoe-agents Docker image
#
# Usage:
#   ./build.sh           # Build locally
#   ./build.sh --push    # Build and push to registry (if configured)
#
# The image should be built on the VM where it will run, or pushed to a registry.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

IMAGE_NAME="roscoe-agents"
IMAGE_TAG="local"

echo "=== Building Roscoe Agents Docker Image ==="
echo "Project root: $PROJECT_ROOT"
echo "Image: $IMAGE_NAME:$IMAGE_TAG"
echo ""

cd "$PROJECT_ROOT"

# Build the image
docker build \
    -t "$IMAGE_NAME:$IMAGE_TAG" \
    -f docker/roscoe-agents/Dockerfile \
    .

echo ""
echo "=== Build Complete ==="
echo "Image: $IMAGE_NAME:$IMAGE_TAG"
echo ""
echo "To deploy:"
echo "  1. Copy this to the VM: scp -r docker/roscoe-agents aaronwhaley@roscoe-paralegal-vm:/home/aaronwhaley/roscoe/docker/"
echo "  2. SSH to VM: gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a"
echo "  3. Build on VM: cd /home/aaronwhaley/roscoe && ./docker/roscoe-agents/build.sh"
echo "  4. Restart: docker compose restart roscoe"
echo ""

# Push if requested
if [ "$1" == "--push" ]; then
    echo "Pushing to registry..."
    docker push "$IMAGE_NAME:$IMAGE_TAG"
fi
