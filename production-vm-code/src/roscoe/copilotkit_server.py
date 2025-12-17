"""
CopilotKit FastAPI server for Roscoe.

This module wraps the Roscoe LangGraph agent with CopilotKit's SDK,
exposing an AG-UI endpoint that the React UI can connect to.

Uses the AG-UI protocol for LangGraph agent integration.

IMPORTANT: This file must set LANGGRAPH_DEPLOYMENT=true BEFORE importing
the agent module, otherwise the agent won't support checkpointing.
"""

import os
import sys
from pathlib import Path

# ============================================================================
# CRITICAL: Set environment variables BEFORE any other imports
# ============================================================================

# Load .env file
from dotenv import load_dotenv

env_paths = [
    Path("/Volumes/X10 Pro/Roscoe/.env"),
    Path.cwd() / ".env",
    Path(__file__).parent.parent.parent.parent / ".env",
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from {env_path}")
        break

# Set LANGGRAPH_DEPLOYMENT=true so agent allows checkpointing
# This MUST be set before importing the agent
os.environ["LANGGRAPH_DEPLOYMENT"] = "true"
print("✅ Set LANGGRAPH_DEPLOYMENT=true")

# ============================================================================
# Now safe to import other modules
# ============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.memory import MemorySaver

# Import AG-UI components
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import LangGraphAGUIAgent

# Import the Roscoe agent (will use checkpointer=None because LANGGRAPH_DEPLOYMENT=true)
from roscoe.agents.paralegal.agent import personal_assistant_agent

# ============================================================================
# Create FastAPI app
# ============================================================================

app = FastAPI(
    title="Roscoe CopilotKit Server",
    description="CopilotKit endpoint for the Roscoe AI Paralegal Assistant",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Create checkpointed graph for AG-UI
# ============================================================================

# Create in-memory checkpointer for local development
# (In production on GCE, PostgreSQL is used via langgraph.json config)
memory_checkpointer = MemorySaver()
print("✅ Created MemorySaver checkpointer")

# Recompile the agent graph with our checkpointer
# The agent was created with checkpointer=None, so we can add one
graph_with_checkpointer = personal_assistant_agent.builder.compile(
    checkpointer=memory_checkpointer
).with_config({"recursion_limit": 500})  # Allow complex graphs with many steps
print(f"✅ Recompiled graph with checkpointer and recursion_limit=500")

# ============================================================================
# Add AG-UI endpoint
# ============================================================================

add_langgraph_fastapi_endpoint(
    app=app,
    agent=LangGraphAGUIAgent(
        name="roscoe_paralegal",
        description="AI Paralegal Assistant - Roscoe helps with legal research, document drafting, case management, and paralegal tasks.",
        graph=graph_with_checkpointer,
    ),
    path="/copilotkit/agents/roscoe_paralegal",
)
print("✅ Added AG-UI endpoint at /copilotkit/agents/roscoe_paralegal")

# ============================================================================
# Additional endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "roscoe-copilotkit"}


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "roscoe-copilotkit",
        "version": "1.0.0",
        "endpoints": {
            "copilotkit": "/copilotkit/agents/roscoe_paralegal",
            "health": "/health",
        },
    }


# ============================================================================
# Main entry point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "roscoe.copilotkit_server:app",
        host="0.0.0.0",
        port=8124,
        reload=False,  # Disable reload to avoid module caching issues
    )
