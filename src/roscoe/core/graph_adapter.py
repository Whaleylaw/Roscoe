"""
Graph client adapter for Second Brain middleware compatibility.

The ContinuityMiddleware and ProactiveSurfacingMiddleware expect a
graph_client object with a .run(query, params) method. This adapter
wraps the existing run_cypher_query function to provide that interface.
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GraphClientAdapter:
    """
    Adapter to provide graph_client.run() interface.

    Wraps roscoe.core.graphiti_client.run_cypher_query.
    """

    async def run(self, query: str, params: Optional[Dict[str, Any]] = None):
        """
        Execute Cypher query against FalkorDB.

        Args:
            query: Cypher query string
            params: Query parameters

        Returns:
            Query results
        """
        from roscoe.core.graphiti_client import run_cypher_query

        try:
            return await run_cypher_query(query, params or {})
        except Exception as e:
            logger.error(f"[GRAPH ADAPTER] Query failed: {e}")
            raise


# Singleton instance for middleware
graph_client = GraphClientAdapter()
