# Roscoe Python Runner - Base Image
#
# Lightweight Python image for executing scripts from the workspace.
# This image provides a clean Python environment with common dependencies.
#
# Build: docker build -t roscoe-python-runner:latest -f docker/python-runner/Dockerfile .

FROM python:3.11-slim

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools for Python packages
    build-essential \
    # Git for pip installs from git repos
    git \
    # Common utilities
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install common Python packages that scripts might need
RUN pip install --no-cache-dir \
    requests \
    pandas \
    numpy \
    pyyaml \
    python-dotenv

# Default command (can be overridden)
CMD ["python"]

