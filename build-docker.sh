#!/bin/bash
set -e

# Roscoe Docker Build and Push Script
# Usage: ./build-docker.sh [version]

VERSION=${1:-latest}
DOCKER_USERNAME=${DOCKER_USERNAME:-}
IMAGE_NAME="roscoe-agents"

echo "========================================="
echo "Roscoe Docker Build Script"
echo "========================================="
echo ""

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Prompt for Docker Hub username if not set
if [ -z "$DOCKER_USERNAME" ]; then
    read -p "Enter your Docker Hub username: " DOCKER_USERNAME
    if [ -z "$DOCKER_USERNAME" ]; then
        echo "❌ Error: Docker Hub username is required"
        exit 1
    fi
fi

FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"

echo "Building Docker image: $FULL_IMAGE_NAME"
echo ""

# Build the image
docker build -t "$FULL_IMAGE_NAME" .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "Image: $FULL_IMAGE_NAME"
    echo ""

    # Also tag as latest if version is specified
    if [ "$VERSION" != "latest" ]; then
        LATEST_TAG="${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
        docker tag "$FULL_IMAGE_NAME" "$LATEST_TAG"
        echo "Also tagged as: $LATEST_TAG"
        echo ""
    fi

    # Ask if user wants to push
    read -p "Push to Docker Hub? (y/N) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Logging in to Docker Hub..."
        docker login

        echo ""
        echo "Pushing $FULL_IMAGE_NAME..."
        docker push "$FULL_IMAGE_NAME"

        if [ "$VERSION" != "latest" ]; then
            echo "Pushing $LATEST_TAG..."
            docker push "$LATEST_TAG"
        fi

        echo ""
        echo "✅ Push successful!"
        echo ""
        echo "Your image is now available at:"
        echo "  docker pull $FULL_IMAGE_NAME"
        echo ""
    else
        echo "Skipping push to Docker Hub"
        echo ""
        echo "To push later, run:"
        echo "  docker push $FULL_IMAGE_NAME"
        echo ""
    fi

    echo "To test locally:"
    echo "  docker run -p 8123:8000 --env-file .env $FULL_IMAGE_NAME"
    echo ""
else
    echo "❌ Build failed"
    exit 1
fi
