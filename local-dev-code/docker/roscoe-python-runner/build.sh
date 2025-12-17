#!/bin/bash
# Build script for Roscoe Python Runner Docker images

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Building Roscoe Python Runner Images"
echo "========================================"

# Build base image
echo ""
echo "Step 1: Building base image (roscoe-python-runner:latest)..."
docker build -t roscoe-python-runner:latest -f Dockerfile .

# Tag with version
VERSION="${1:-v1.0.0}"
docker tag roscoe-python-runner:latest "roscoe-python-runner:$VERSION"
echo "Tagged as roscoe-python-runner:$VERSION"

# Test base image
echo ""
echo "Step 2: Testing base image..."
docker run --rm roscoe-python-runner:latest python -c "
import pandas
import numpy
import pdfplumber
import requests
print('✓ All base dependencies OK')
"

# Build Playwright image
echo ""
echo "Step 3: Building Playwright image (roscoe-python-runner:playwright)..."
docker build -t roscoe-python-runner:playwright -f Dockerfile.playwright .

# Test Playwright image
echo ""
echo "Step 4: Testing Playwright image..."
docker run --rm roscoe-python-runner:playwright python -c "
from playwright.sync_api import sync_playwright
print('✓ Playwright dependencies OK')
"

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "Images created:"
echo "  - roscoe-python-runner:latest"
echo "  - roscoe-python-runner:$VERSION"
echo "  - roscoe-python-runner:playwright"
echo ""
echo "To test with workspace mount:"
echo "  docker run --rm -v /mnt/workspace:/workspace:rw roscoe-python-runner:latest python /workspace/Tools/test_script.py"

