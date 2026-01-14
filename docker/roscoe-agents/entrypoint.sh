#!/bin/bash
# Roscoe Agents Entrypoint Script
#
# This script:
# 1. Sets up environment variables
# 2. Waits for dependent services (postgres, redis)
# 3. Starts the LangGraph API server

set -e

echo "=== Roscoe Agents Container Starting ==="
echo "Timestamp: $(date)"
echo "Python: $(python --version)"
echo "PYTHONPATH: $PYTHONPATH"

# Wait for postgres to be ready
if [ -n "$DATABASE_URI" ]; then
    echo "Waiting for PostgreSQL..."
    # Extract host from DATABASE_URI
    PG_HOST=$(echo $DATABASE_URI | sed -n 's/.*@\([^:\/]*\).*/\1/p')
    PG_PORT=$(echo $DATABASE_URI | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    PG_PORT=${PG_PORT:-5432}

    for i in {1..30}; do
        if pg_isready -h "$PG_HOST" -p "$PG_PORT" > /dev/null 2>&1; then
            echo "PostgreSQL is ready!"
            break
        fi
        echo "Waiting for PostgreSQL... ($i/30)"
        sleep 2
    done
fi

# Wait for Redis to be ready
if [ -n "$REDIS_URI" ]; then
    echo "Waiting for Redis..."
    REDIS_HOST=$(echo $REDIS_URI | sed -n 's/redis:\/\/\([^:]*\).*/\1/p')
    REDIS_PORT=$(echo $REDIS_URI | sed -n 's/.*:\([0-9]*\)$/\1/p')
    REDIS_PORT=${REDIS_PORT:-6379}

    for i in {1..30}; do
        if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; then
            echo "Redis is ready!"
            break
        fi
        echo "Waiting for Redis... ($i/30)"
        sleep 2
    done
fi

# Verify source code is mounted
if [ ! -d "/deps/roscoe/src/roscoe" ]; then
    echo "WARNING: Source code not mounted at /deps/roscoe/src/roscoe"
    echo "Make sure docker-compose.yml has the correct volume mount."
fi

# List available graphs from langgraph.json
if [ -f "/deps/roscoe/langgraph.json" ]; then
    echo "LangGraph configuration found:"
    cat /deps/roscoe/langgraph.json
else
    echo "WARNING: langgraph.json not found"
fi

echo ""
echo "=== Starting LangGraph API Server ==="
echo ""

# CRITICAL: Unset LANGSERVE_GRAPHS so LangGraph reads from langgraph.json file
# The base image bakes LANGSERVE_GRAPHS during build, which becomes stale.
# By unsetting it, LangGraph will read the mounted langgraph.json instead.
unset LANGSERVE_GRAPHS
echo "Cleared LANGSERVE_GRAPHS - will read from langgraph.json"

# Set server config
export LANGGRAPH_SERVER_HOST=${LANGGRAPH_SERVER_HOST:-0.0.0.0}
export PORT=${PORT:-8000}
export UVICORN_TIMEOUT_KEEP_ALIVE=${UVICORN_TIMEOUT_KEEP_ALIVE:-75}

# Start the LangGraph API server using uvicorn (same as base image)
echo "Starting API server on $LANGGRAPH_SERVER_HOST:$PORT"
exec uvicorn langgraph_api.server:app \
    --log-config /api/logging.json \
    --host $LANGGRAPH_SERVER_HOST \
    --port $PORT \
    --no-access-log \
    --timeout-graceful-shutdown 3600 \
    --timeout-keep-alive $UVICORN_TIMEOUT_KEEP_ALIVE
