# Deep Agent Coder - Dockerfile
#
# Build: docker build -t deep-agent-coder .
# Run:   docker-compose up
#
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY deep_agent_coder/ deep_agent_coder/

# Create workspace directory
RUN mkdir -p /workspace

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV WORKSPACE_DIR=/workspace

# Default command: interactive chat
CMD ["python", "-m", "deep_agent_coder", "chat", "--workspace", "/workspace"]
