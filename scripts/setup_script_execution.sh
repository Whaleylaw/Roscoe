#!/bin/bash
# Setup Script Execution Environment
# Run this on the GCE VM after deploying the code

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "========================================"
echo "Script Execution Environment Setup"
echo "========================================"
echo "Repository: $REPO_ROOT"
echo ""

# 1. Verify Docker is installed and running
echo "Step 1: Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Install with: sudo apt-get install docker.io"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "ERROR: Docker daemon not running or permission denied"
    echo "Try: sudo systemctl start docker"
    echo "Or add user to docker group: sudo usermod -aG docker $USER"
    exit 1
fi
echo "✓ Docker is available"

# 2. Verify gcsfuse mount
echo ""
echo "Step 2: Checking GCS mount..."
if mount | grep -q "gcsfuse"; then
    WORKSPACE_MOUNT=$(mount | grep gcsfuse | awk '{print $3}')
    echo "✓ GCS mounted at: $WORKSPACE_MOUNT"
else
    echo "WARNING: gcsfuse mount not detected"
    echo "Scripts may not have access to workspace files"
    echo "Expected mount: /mnt/workspace"
fi

# 3. Build Docker images
echo ""
echo "Step 3: Building Docker images..."
cd "$REPO_ROOT/docker/roscoe-python-runner"

if [ ! -f "Dockerfile" ]; then
    echo "ERROR: Dockerfile not found at $REPO_ROOT/docker/roscoe-python-runner/"
    exit 1
fi

chmod +x build.sh 2>/dev/null || true
./build.sh

# 4. Verify images
echo ""
echo "Step 4: Verifying images..."
if docker images | grep -q "roscoe-python-runner.*latest"; then
    echo "✓ Base image: roscoe-python-runner:latest"
else
    echo "ERROR: Base image not found"
    exit 1
fi

if docker images | grep -q "roscoe-python-runner.*playwright"; then
    echo "✓ Playwright image: roscoe-python-runner:playwright"
else
    echo "WARNING: Playwright image not built (optional)"
fi

# 5. Install Python dependencies
echo ""
echo "Step 5: Installing Python dependencies..."
cd "$REPO_ROOT"

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Python dependencies installed"
else
    echo "WARNING: requirements.txt not found"
fi

# Specifically ensure docker SDK is installed
pip install docker==7.0.0

# 6. Create execution logs directory
echo ""
echo "Step 6: Creating logs directory..."
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/workspace}"
LOGS_DIR="$WORKSPACE_ROOT/Database/script_execution_logs"
mkdir -p "$LOGS_DIR" 2>/dev/null || true
echo "✓ Logs directory: $LOGS_DIR"

# 7. Run quick test
echo ""
echo "Step 7: Running quick test..."

# Create a simple test script
TEST_SCRIPT="$WORKSPACE_ROOT/Tools/tests/test_basic.py"
if [ -f "$TEST_SCRIPT" ]; then
    docker run --rm \
        -v "$WORKSPACE_ROOT:/workspace:rw" \
        -w /workspace \
        roscoe-python-runner:latest \
        python /workspace/Tools/tests/test_basic.py
    echo "✓ Quick test passed"
else
    # Create inline test
    docker run --rm \
        -v "$WORKSPACE_ROOT:/workspace:rw" \
        -w /workspace \
        roscoe-python-runner:latest \
        python -c "import pandas; import numpy; print('Dependencies OK')"
    echo "✓ Quick dependency test passed"
fi

# 8. Summary
echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Docker images ready:"
echo "  - roscoe-python-runner:latest (base Python)"
echo "  - roscoe-python-runner:playwright (with browser)"
echo ""
echo "The agent can now use:"
echo "  - execute_python_script() for /Tools/ scripts"
echo "  - execute_python_script_with_browser() for web automation"
echo ""
echo "Test the full suite with:"
echo "  python $WORKSPACE_ROOT/Tools/tests/run_all_tests.py --direct"
echo ""
echo "View documentation:"
echo "  cat $REPO_ROOT/docs/SCRIPT_EXECUTION.md"

