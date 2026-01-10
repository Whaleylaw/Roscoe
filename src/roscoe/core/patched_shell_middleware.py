"""
Patched ShellToolMiddleware that stores session resources externally
to avoid pickle errors with LangGraph checkpointing.

The original middleware stores _SessionResources in the graph state,
but _SessionResources contains threading.Lock objects that cannot be pickled.

This version stores resources in a module-level dictionary keyed by
a combination of thread_id and checkpoint_ns, keeping them out of 
the checkpointed state entirely.
"""

import logging
from typing import Any
from pathlib import Path

LOGGER = logging.getLogger(__name__)

# External storage for session resources - keyed by thread context
_EXTERNAL_SHELL_RESOURCES: dict[str, Any] = {}


def _get_resource_key(state: dict, runtime: Any = None) -> str:
    """Get a unique key for the current execution context."""
    # Try multiple sources for identification
    configurable = state.get("configurable", {})
    thread_id = configurable.get("thread_id", "")
    checkpoint_ns = configurable.get("checkpoint_ns", "")
    
    # Also try runtime config if available
    if runtime is not None and hasattr(runtime, 'config'):
        config = runtime.config or {}
        configurable = config.get("configurable", configurable)
        thread_id = configurable.get("thread_id", thread_id)
        checkpoint_ns = configurable.get("checkpoint_ns", checkpoint_ns)
    
    if thread_id:
        return f"shell:{thread_id}:{checkpoint_ns}"
    
    # Fallback: use id of state
    return f"shell:state:{id(state)}"


def get_patched_shell_middleware(*args, **kwargs):
    """Factory function to create a patched shell middleware.
    
    Instead of wrapping the middleware, we monkey-patch the original
    to not store resources in the graph state.
    """
    from langchain.agents.middleware.shell_tool import (
        ShellToolMiddleware,
        _SessionResources,
    )
    
    # Create the original middleware
    middleware = ShellToolMiddleware(*args, **kwargs)
    
    # Store reference to _SessionResources class
    _session_resources_class = _SessionResources
    
    # Monkey-patch the before_agent method to not return resources
    original_before_agent = middleware.before_agent
    
    def patched_before_agent(state, runtime):
        """Start shell session without storing resources in state."""
        key = _get_resource_key(state, runtime)
        
        # Check if resources already exist externally
        if key not in _EXTERNAL_SHELL_RESOURCES:
            # Create resources
            resources = middleware._create_resources()
            _EXTERNAL_SHELL_RESOURCES[key] = resources
            # Run startup commands
            middleware._run_startup_commands(resources.session)
            LOGGER.debug(f"Created shell resources for {key}")
        
        # Return None - don't add anything to checkpointed state
        return None
    
    async def patched_abefore_agent(state, runtime):
        return patched_before_agent(state, runtime)
    
    # Monkey-patch the after_agent method
    original_after_agent = middleware.after_agent
    
    def patched_after_agent(state, runtime):
        """Clean up resources from external storage."""
        key = _get_resource_key(state, runtime)
        resources = _EXTERNAL_SHELL_RESOURCES.pop(key, None)
        
        if resources is None:
            return
            
        if not isinstance(resources, _session_resources_class):
            return
        
        try:
            middleware._run_shutdown_commands(resources.session)
        finally:
            resources.finalizer()
        LOGGER.debug(f"Cleaned up shell resources for {key}")
    
    async def patched_aafter_agent(state, runtime):
        return patched_after_agent(state, runtime)
    
    # Monkey-patch _get_or_create_resources
    original_get_or_create = middleware._get_or_create_resources
    
    def patched_get_or_create_resources(state):
        """Get or create resources using external storage."""
        # Try to get runtime from the call stack if not passed
        runtime = None
        key = _get_resource_key(state, runtime)
        
        # Check external storage
        if key in _EXTERNAL_SHELL_RESOURCES:
            resources = _EXTERNAL_SHELL_RESOURCES[key]
            if isinstance(resources, _session_resources_class):
                return resources
        
        # Create new resources
        new_resources = middleware._create_resources()
        _EXTERNAL_SHELL_RESOURCES[key] = new_resources
        middleware._run_startup_commands(new_resources.session)
        LOGGER.debug(f"Created shell resources for {key}")
        return new_resources
    
    # Apply monkey patches
    middleware.before_agent = patched_before_agent
    middleware.abefore_agent = patched_abefore_agent
    middleware.after_agent = patched_after_agent
    middleware.aafter_agent = patched_aafter_agent
    middleware._get_or_create_resources = patched_get_or_create_resources
    
    print("🔧 Patched ShellToolMiddleware with external resource storage")
    return middleware


# Convenience export
__all__ = ['get_patched_shell_middleware']
