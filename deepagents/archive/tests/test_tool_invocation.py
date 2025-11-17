"""
Test script to understand MCP tool invocation and the 'self' error.

This script will help us understand how LangGraph invokes StructuredTool._run
and why we're getting "multiple values for 'self'" error.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the MCP client
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import StructuredTool

async def main():
    print("=" * 80)
    print("MCP Tool Invocation Test")
    print("=" * 80)

    # Initialize Supabase MCP
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_key:
        print("❌ Supabase credentials missing")
        return

    print("\n1. Creating MCP client...")
    supabase_client = MultiServerMCPClient(
        {
            "supabase": {
                "command": "npx",
                "args": [
                    "-y",
                    "@supabase/mcp-server-postgrest",
                    "--apiUrl",
                    supabase_url,
                    "--apiKey",
                    service_key,
                    "--schema",
                    "public"
                ],
                "transport": "stdio"
            }
        }
    )

    print("2. Getting tools...")
    tools = await supabase_client.get_tools()
    print(f"   Found {len(tools)} tools")

    if not tools:
        print("❌ No tools retrieved")
        return

    # Test the first tool
    tool = tools[0]
    print(f"\n3. Testing tool: {tool.name}")
    print(f"   Type: {type(tool)}")
    print(f"   Is StructuredTool: {isinstance(tool, StructuredTool)}")

    # Inspect the tool's internal structure
    print(f"\n4. Tool structure:")
    print(f"   tool.func: {tool.func}")
    print(f"   tool._run: {tool._run}")
    print(f"   type(tool._run): {type(tool._run)}")
    print(f"   Is bound method: {hasattr(tool._run, '__self__')}")

    # Inspect signature
    import inspect
    sig = inspect.signature(tool._run)
    print(f"   _run signature: {sig}")
    print(f"   _run parameters: {list(sig.parameters.keys())}")

    # Try to invoke the tool directly
    print(f"\n5. Attempting direct invocation...")
    try:
        # Simulate what LangGraph might do
        kwargs = {"method": "GET", "path": "/doc_files?select=uuid&limit=1"}
        print(f"   Calling tool._run(**{kwargs})")

        # Direct call
        from langchain_core.runnables.config import RunnableConfig
        result = await tool._arun(config=RunnableConfig(), **kwargs)
        print(f"   ✅ Direct call succeeded: {result}")
    except Exception as e:
        print(f"   ❌ Direct call failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    # Try to invoke through LangChain's invoke method
    print(f"\n6. Attempting invoke method...")
    try:
        result = await tool.ainvoke({"method": "GET", "path": "/doc_files?select=uuid&limit=1"})
        print(f"   ✅ ainvoke succeeded: {result}")
    except Exception as e:
        print(f"   ❌ ainvoke failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("Test complete")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
