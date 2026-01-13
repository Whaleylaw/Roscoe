#!/bin/bash
# Build script for Roscoe Python Runner Docker images
#
# This script builds both the base Python runner image and the Playwright-enabled image.
# Run from the repository root: ./docker/python-runner/build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

echo "Building roscoe-python-runner:latest (base image)..."
docker build -t roscoe-python-runner:latest -f docker/python-runner/Dockerfile .

echo ""
echo "Building roscoe-python-runner:playwright (Playwright-enabled image)..."
docker build -t roscoe-python-runner:playwright -f docker/python-runner/Dockerfile.playwright .

echo ""
echo "✓ Both images built successfully!"
echo ""
echo "Images:"
docker images | grep roscoe-python-runner

