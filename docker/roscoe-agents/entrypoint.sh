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
if [ ! -d "/deps/Roscoe/src/roscoe" ]; then
    echo "WARNING: Source code not mounted at /deps/Roscoe/src/roscoe"
    echo "Make sure docker-compose.yml has the correct volume mount."
fi

# List available graphs from langgraph.json
if [ -f "/deps/Roscoe/langgraph.json" ]; then
    echo "LangGraph configuration found:"
    cat /deps/Roscoe/langgraph.json
else
    echo "WARNING: langgraph.json not found"
fi

echo ""
echo "=== Starting LangGraph API Server ==="
echo ""

# Start the LangGraph server
# The server reads langgraph.json and serves the configured graphs
exec langgraph up --host 0.0.0.0 --port 8000
