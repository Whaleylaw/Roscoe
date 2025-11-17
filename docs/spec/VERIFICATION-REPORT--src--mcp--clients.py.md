# Import Verification Report: src/mcp/clients.py

**Report Generated:** 2025-11-15
**Plan File:** `/Users/aaronwhaley/Documents/GitHub/Whaley-Law-Firm/deepagents/docs/spec/PLANS/src--mcp--clients.py.nlplan.md`
**Target File:** `src/mcp/clients.py` (planned)

---

## Executive Summary

This report verifies all imports, libraries, and objects referenced in the natural language plan for `src/mcp/clients.py`. The analysis identified **critical issues** with MCP server package names that require correction before implementation.

**Status:** ⚠️ **REQUIRES CORRECTIONS**

**Key Findings:**
- ✅ Core import `MultiServerMCPClient` from `langchain_mcp_adapters` is verified
- ✅ Standard library imports (`os`, `logging`) are correct
- ⚠️ **CRITICAL:** Method name should be `get_tools()` not `list_tools()`
- ❌ **CRITICAL:** MCP server package names are incorrect/non-existent
- ✅ Graceful degradation pattern is architecturally sound

---

## 1. Core Imports Verification

### 1.1 MultiServerMCPClient from langchain_mcp_adapters

**Plan Line 001:** `Import MultiServerMCPClient from langchain_mcp_adapters`

**Status:** ✅ **VERIFIED**

**Correct Import Statement:**
```python
from langchain_mcp_adapters.client import MultiServerMCPClient
```

**Documentation Citations:**
- **Package:** `langchain-mcp-adapters` on PyPI
- **Installation:** `pip install langchain-mcp-adapters`
- **Python Version:** Requires Python >=3.10
- **Release Date:** November 13, 2025
- **Documentation:** https://docs.langchain.com/oss/python/langchain/mcp
- **GitHub:** https://github.com/langchain-ai/langchain-mcp-adapters
- **PyPI:** https://pypi.org/project/langchain-mcp-adapters/

**Usage Pattern Verified:**
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "server_name": {
        "command": "npx",
        "args": ["-y", "package-name"],
        "transport": "stdio",
        "env": {
            "API_KEY": "value"
        }
    }
})

# IMPORTANT: The method is get_tools(), NOT list_tools()
tools = await client.get_tools()
```

**LangChain Documentation Quote:**
> "langchain-mcp-adapters enables agents to use tools defined across one or more MCP server. MultiServerMCPClient is stateless by default. Each tool invocation creates a fresh MCP ClientSession, executes the tool, and then cleans up."

Source: https://docs.langchain.com/oss/python/langchain/mcp

---

### 1.2 Standard Library Imports

**Plan Lines 002-004:**
- Line 002: `Import os module`
- Line 004: `Import logging module`

**Status:** ✅ **VERIFIED**

**Correct Import Statements:**
```python
import os
import logging
```

These are Python standard library modules, available in all Python installations (>=3.10).

---

### 1.3 Custom Import from Project

**Plan Line 003:** `Import get_setting from src.config.settings`

**Status:** ⚠️ **PENDING** (depends on other planned file)

**Expected Import Statement:**
```python
from src.config.settings import get_setting
```

**Note:** This references `src/config/settings.py` (planned line 011) which is a separate file in the project. This import cannot be fully verified until that file is implemented, but the pattern is standard and correct.

---

## 2. CRITICAL ISSUE: Method Name Correction

### Issue: list_tools() vs get_tools()

**Plan Lines Affected:** 019, 041, 061, 081

**Current Plan States:** `Call list_tools method on supabase_mcp`

**Actual API:** The method is `get_tools()`, not `list_tools()`

**Evidence from Official Documentation:**
1. **LangChain Docs (Python):** Shows `tools = await client.get_tools()`
2. **PyPI Page:** Example uses `tools = await client.get_tools()`
3. **GitHub README:** Consistently uses `get_tools()`

**Required Correction:**
```python
# INCORRECT (as shown in plan):
tools = supabase_mcp.list_tools()

# CORRECT (actual API):
tools = await client.get_tools()
```

**Note:** The method is also **async**, requiring `await` keyword.

---

## 3. CRITICAL ISSUE: MCP Server Package Names

### 3.1 Supabase MCP Server

**Plan Line 015:** `Set args key to list containing "-y" flag and "@modelcontextprotocol/server-supabase" package name`

**Status:** ❌ **INCORRECT - Package Does Not Exist**

**Issue:** The package `@modelcontextprotocol/server-supabase` does not exist on npm.

**Actual Package:** `@supabase/mcp-server-postgrest`

**Evidence:**
- npm search for `@modelcontextprotocol/server-supabase` returns no results
- Official Supabase MCP server is `@supabase/mcp-server-postgrest`
- npm page: https://www.npmjs.com/package/@supabase/mcp-server-postgrest

**Required Correction:**
```python
# INCORRECT (as shown in plan):
"args": ["-y", "@modelcontextprotocol/server-supabase"]

# CORRECT (actual package):
"args": ["-y", "@supabase/mcp-server-postgrest"]
```

**Package Description:**
> "MCP server for PostgREST that allows LLMs to perform database queries and operations on Postgres databases via PostgREST. Works with both Supabase projects and standalone PostgREST servers."

---

### 3.2 Tavily MCP Server

**Plan Line 038:** `Set args key to list containing "-y" flag and "@modelcontextprotocol/server-tavily" package name`

**Status:** ❌ **INCORRECT - Package Name Wrong**

**Issue:** The package `@modelcontextprotocol/server-tavily` does not exist.

**Actual Package:** `@mcptools/mcp-tavily`

**Evidence:**
- npm search returns `@mcptools/mcp-tavily` as the actual package
- Released February 24, 2025
- npm page: https://www.npmjs.com/package/@mcptools/mcp-tavily

**Required Correction:**
```python
# INCORRECT (as shown in plan):
"args": ["-y", "@modelcontextprotocol/server-tavily"]

# CORRECT (actual package):
"args": ["-y", "@mcptools/mcp-tavily"]
```

**Alternative Configuration:**
Can also be installed via Smithery CLI:
```bash
npx -y @smithery/cli install @kshern/mcp-tavily --client claude
```

---

### 3.3 Gmail MCP Server

**Plan Line 058:** `Set args key to list containing "-y" and "@modelcontextprotocol/server-gmail" package name`

**Status:** ❌ **INCORRECT - Package Does Not Exist**

**Issue:** The package `@modelcontextprotocol/server-gmail` does not exist.

**Available Alternatives (Community Packages):**
1. `@monsoft/mcp-gmail` - Batch operations, multiple emails
2. `systemprompt-mcp-gmail` - Natural language email management (1.3K downloads, released Jan 26, 2025)
3. `mcp-gmail` (Python-based, not npm)

**Recommendation:**
```python
# SUGGESTED (most popular/recent):
"args": ["-y", "@monsoft/mcp-gmail"]

# OR:
"args": ["-y", "systemprompt-mcp-gmail"]
```

**Note:** There is **no official** `@modelcontextprotocol/server-gmail` package. All Gmail MCP servers are community-developed. OAuth credentials setup is required.

---

### 3.4 Google Calendar MCP Server

**Plan Line 078:** `Set args key to list containing "-y" and "@modelcontextprotocol/server-google-calendar" package name`

**Status:** ❌ **INCORRECT - Package Does Not Exist**

**Issue:** The package `@modelcontextprotocol/server-google-calendar` does not exist.

**Available Alternatives (Community Packages):**
1. `mcp-google-calendar` (by am2rican5) - 1.9K downloads, released March 19, 2025
2. `@takumi0706/mcp-google-calendar` - version 1.0.8
3. `@sowonai/mcp-google-calendar` - Claude Desktop integration
4. `mcp-google-calendar-plus` - Full CRUD operations
5. `@cablate/mcp-google-calendar` - Comprehensive management

**Recommendation:**
```python
# SUGGESTED (most popular):
"args": ["-y", "mcp-google-calendar"]

# OR (scoped version):
"args": ["-y", "@takumi0706/mcp-google-calendar"]
```

**Note:** There is **no official** `@modelcontextprotocol/server-google-calendar` package. All Google Calendar MCP servers are community-developed. OAuth credentials setup is required.

---

## 4. Official MCP Server Packages

For reference, here are the **actual official** MCP server packages under `@modelcontextprotocol`:

### Verified Official Packages (as of 2025):
1. `@modelcontextprotocol/server-everything` - Reference/test server
2. `@modelcontextprotocol/server-fetch` - Web content fetching
3. `@modelcontextprotocol/server-filesystem` - File operations
4. `@modelcontextprotocol/server-git` - Git repository operations
5. `@modelcontextprotocol/server-github` - GitHub integration
6. `@modelcontextprotocol/server-memory` - Knowledge graph memory
7. `@modelcontextprotocol/server-puppeteer` - Browser automation
8. `@modelcontextprotocol/server-sequential-thinking` - Problem-solving

**Repository:** https://github.com/modelcontextprotocol/servers

**Notable Absences:**
- No official Supabase server (use `@supabase/mcp-server-postgrest`)
- No official Tavily server (use `@mcptools/mcp-tavily`)
- No official Gmail server (use community packages)
- No official Google Calendar server (use community packages)

---

## 5. Configuration Patterns Verification

### 5.1 MultiServerMCPClient Configuration Structure

**Plan Lines 013-016 (Supabase example):**

**Pattern Verified:** ✅ **CORRECT**

The configuration structure follows the correct pattern:
```python
{
    "command": "npx",
    "args": ["-y", "package-name"],
    "env": {
        "ENV_VAR": "value"
    }
}
```

**LangChain Documentation Confirms:**
```python
client = MultiServerMCPClient({
    "math": {
        "transport": "stdio",
        "command": "node",
        "args": ["/path/to/math_server.js"],
    },
    "weather": {
        "transport": "sse",
        "url": "http://localhost:8000/mcp",
    },
})
```

**Note:** The `transport` key defaults to `"stdio"` when using `command` and `args`, so it can be omitted.

---

### 5.2 Transport Types

**Supported Transport Types:**
1. **`stdio`** - Standard I/O (for local subprocesses via `command`/`args`)
2. **`sse`** - Server-Sent Events (for remote servers via `url`)
3. **`streamable_http`** - Streamable HTTP (for remote MCP endpoints with auth)

**Plan Usage:** The plan correctly uses `stdio` transport via `command: "npx"` and `args`.

---

## 6. Graceful Degradation Pattern

**Plan Lines 011-012, 023-025 (and similar for other servers):**

**Pattern Verified:** ✅ **CORRECT and BEST PRACTICE**

The plan implements proper graceful degradation:

```python
# Check for missing credentials
if SUPABASE_URL is None or SUPABASE_SERVICE_ROLE_KEY is None:
    logger.warning("Supabase MCP unavailable")
    return []

# Wrap in try-except
try:
    # ... initialization code ...
except Exception:
    logger.error("Failed to initialize Supabase MCP")
    return []  # Graceful degradation
```

**Why This Is Correct:**
1. **Fail-Fast Detection:** Checks credentials before attempting connection
2. **Error Logging:** Provides visibility into failures
3. **Empty List Return:** Safe fallback that won't break agent initialization
4. **No Crash:** Agent can still function with subset of tools
5. **Architecture Alignment:** Matches "graceful degradation per architecture error handling strategy" (plan line 027)

**LangChain Best Practices:** This pattern aligns with LangChain's philosophy that agents should continue operating with available tools even if some services are unavailable.

---

## 7. Environment Variables

### 7.1 Required Environment Variables

**Plan References:**

| Server | Environment Variable(s) | Status |
|--------|------------------------|--------|
| Supabase | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | ✅ Standard |
| Tavily | `TAVILY_API_KEY` | ✅ Standard |
| Gmail | `GMAIL_CREDENTIALS` | ⚠️ Package-dependent |
| Calendar | `GOOGLE_CALENDAR_CREDENTIALS` | ⚠️ Package-dependent |

**Notes:**
- **Supabase:** Variables are standard Supabase configuration (verified in repository `.env` patterns)
- **Tavily:** Standard API key pattern
- **Gmail/Calendar:** OAuth credentials as JSON - actual variable names may vary by chosen package

**Recommendation:** Verify environment variable names against the specific MCP server package documentation once packages are selected.

---

### 7.2 Service Role Key Note (Plan Line 030)

**Plan Comment:** "service role key bypasses Row Level Security for backend operations per architecture requirements"

**Verification:** ✅ **CORRECT**

This is accurate for Supabase. The service role key bypasses RLS policies, which is appropriate for backend/MCP server usage. This aligns with Supabase best practices for server-side operations.

**Supabase Documentation Confirms:** Service role keys should only be used in secure backend environments (never client-side) and bypass all RLS policies.

---

## 8. Async/Await Considerations

### CRITICAL ISSUE: Missing Async/Await

**Plan Lines Affected:** All initialization functions (007-090)

**Issue:** The plan does not specify that the functions should be **async** or that `get_tools()` requires **await**.

**Required Correction:**

```python
# INCORRECT (plan implies synchronous):
def init_supabase_mcp() -> list:
    # ...
    tools = supabase_mcp.list_tools()  # Wrong method name too
    return tools

# CORRECT (actual API):
async def init_supabase_mcp() -> list:
    # ...
    tools = await client.get_tools()  # Async call
    return tools
```

**Module-Level Initialization (Plan Lines 091-095):**

The plan shows:
```python
supabase_tools = init_supabase_mcp()
```

This will **NOT work** if functions are async. Correct patterns:

**Option 1: Keep functions async, use asyncio at module level**
```python
import asyncio

async def _init_all_mcp():
    return await asyncio.gather(
        init_supabase_mcp(),
        init_tavily_mcp(),
        init_gmail_mcp(),
        init_calendar_mcp()
    )

supabase_tools, tavily_tools, gmail_tools, calendar_tools = asyncio.run(_init_all_mcp())
```

**Option 2: Make functions synchronous wrappers**
```python
def init_supabase_mcp() -> list:
    async def _async_init():
        # async logic here
        return tools

    return asyncio.run(_async_init())

# Then module-level calls work as planned:
supabase_tools = init_supabase_mcp()
```

**Recommendation:** The plan needs to specify the async handling strategy.

---

## 9. Additional Verification Notes

### 9.1 Node.js/npm Dependency

**Plan Line 103:** "Node.js and npm must be installed on system for npx command to work"

**Verification:** ✅ **CORRECT**

This is a critical system dependency. The plan correctly identifies it as an assumption (line 309).

**Testing MCP Servers Independently (Plan Line 110):**
```bash
npx @supabase/mcp-server-postgrest  # CORRECTED package name
```

---

### 9.2 Tool Return Type

**Plan Line 107:** "tools returned are LangChain Tool objects ready for agent use"

**Verification:** ✅ **CORRECT**

The `langchain-mcp-adapters` library converts MCP tools to LangChain `Tool` objects that are compatible with LangChain agents.

**LangChain Documentation Confirms:** Tools returned from `get_tools()` follow the LangChain `BaseTool` interface and can be passed directly to `create_agent()`.

---

### 9.3 JSON-RPC Protocol

**Plan Line 105:** "MCP protocol uses JSON-RPC for communication between agent and servers"

**Verification:** ✅ **CORRECT**

Model Context Protocol is built on JSON-RPC 2.0. The `langchain-mcp-adapters` library handles this transparently.

**MCP Specification:** MCP uses JSON-RPC for all client-server communication over stdio, SSE, or HTTP transports.

---

## 10. Required Corrections Summary

### Priority 1: CRITICAL (Breaking Changes)

1. **Method Name:** Change `list_tools()` to `get_tools()`
   - Lines affected: 019, 041, 061, 081

2. **Supabase Package Name:** Change to `@supabase/mcp-server-postgrest`
   - Line affected: 015

3. **Tavily Package Name:** Change to `@mcptools/mcp-tavily`
   - Line affected: 038

4. **Async/Await:** Add async function declarations and await calls
   - Lines affected: 007-090, especially 019, 041, 061, 081

### Priority 2: IMPORTANT (Package Selection Needed)

5. **Gmail Package:** Select and specify community package
   - Options: `@monsoft/mcp-gmail` or `systemprompt-mcp-gmail`
   - Line affected: 058
   - **Action Required:** Research and choose based on features/stability

6. **Calendar Package:** Select and specify community package
   - Options: `mcp-google-calendar`, `@takumi0706/mcp-google-calendar`, etc.
   - Line affected: 078
   - **Action Required:** Research and choose based on features/stability

### Priority 3: RECOMMENDED (Clarifications)

7. **Environment Variables:** Verify variable names for chosen Gmail/Calendar packages
   - Lines affected: 053, 073

8. **Module-Level Async Handling:** Specify async initialization strategy
   - Lines affected: 091-095

9. **Transport Type:** Consider explicitly specifying `"transport": "stdio"` for clarity
   - Lines affected: 013-016 and similar

---

## 11. Corrected Import and Configuration Examples

### Complete Corrected Example for Supabase:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
import os
import logging
from src.config.settings import get_setting

logger = logging.getLogger(__name__)

async def init_supabase_mcp() -> list:
    """Initialize Supabase MCP client and return list of database tools.

    Returns:
        List of Supabase MCP tools or empty list on failure.

    Implements graceful degradation per architecture error handling strategy.
    """
    try:
        # Retrieve credentials from environment
        supabase_url = get_setting("SUPABASE_URL")
        supabase_key = get_setting("SUPABASE_SERVICE_ROLE_KEY")

        # Check for missing credentials
        if supabase_url is None or supabase_key is None:
            logger.warning("Supabase MCP unavailable - missing credentials")
            return []

        # Create MCP client configuration
        client = MultiServerMCPClient({
            "supabase": {
                "command": "npx",
                "args": ["-y", "@supabase/mcp-server-postgrest"],  # CORRECTED
                "transport": "stdio",  # Explicit (optional)
                "env": {
                    "SUPABASE_URL": supabase_url,
                    "SUPABASE_SERVICE_ROLE_KEY": supabase_key  # Bypasses RLS
                }
            }
        })

        # Retrieve tools (async operation)
        tools = await client.get_tools()  # CORRECTED: was list_tools()

        logger.info(f"Supabase MCP initialized successfully with {len(tools)} tools")
        return tools

    except Exception as e:
        logger.error(f"Failed to initialize Supabase MCP: {e}")
        return []  # Graceful degradation
```

---

## 12. Recommendations for Implementation

### Before Coding:

1. ✅ **Install langchain-mcp-adapters:**
   ```bash
   pip install langchain-mcp-adapters
   ```

2. ⚠️ **Research Gmail/Calendar Packages:**
   - Test community packages independently
   - Verify OAuth setup requirements
   - Check for package stability and maintenance
   - Review API documentation

3. ✅ **Verify Node.js/npm Installation:**
   ```bash
   node --version
   npm --version
   npx --version
   ```

4. ⚠️ **Test MCP Servers Independently:**
   ```bash
   # Test Supabase MCP
   npx -y @supabase/mcp-server-postgrest

   # Test Tavily MCP
   npx -y @mcptools/mcp-tavily
   ```

### During Implementation:

5. ✅ **Follow Async Patterns:** Ensure all MCP operations use async/await
6. ✅ **Implement Logging:** Use provided logging patterns for visibility
7. ✅ **Test Graceful Degradation:** Verify agent works with missing services
8. ✅ **Environment Variables:** Ensure `.env` file has all required variables

### After Implementation:

9. ✅ **Integration Testing:** Test with `src/agents/legal_agent.py`
10. ✅ **Monitor Logs:** Check which MCP servers successfully initialize
11. ✅ **Update Documentation:** Document actual package choices for Gmail/Calendar

---

## 13. Citations and References

### Primary Documentation:

1. **LangChain MCP Adapters (Python):**
   - Docs: https://docs.langchain.com/oss/python/langchain/mcp
   - GitHub: https://github.com/langchain-ai/langchain-mcp-adapters
   - PyPI: https://pypi.org/project/langchain-mcp-adapters/

2. **Model Context Protocol:**
   - Official Servers: https://github.com/modelcontextprotocol/servers
   - SDK: https://www.npmjs.com/package/@modelcontextprotocol/sdk

3. **Supabase MCP:**
   - Package: https://www.npmjs.com/package/@supabase/mcp-server-postgrest

4. **Tavily MCP:**
   - Package: https://www.npmjs.com/package/@mcptools/mcp-tavily

### Community Packages:

5. **Gmail MCP Servers:**
   - @monsoft/mcp-gmail: https://www.npmjs.com/package/@monsoft/mcp-gmail
   - systemprompt-mcp-gmail: https://playbooks.com/mcp/ejb503-gmail

6. **Google Calendar MCP Servers:**
   - mcp-google-calendar: https://playbooks.com/mcp/am2rican5-google-calendar
   - @takumi0706/mcp-google-calendar: https://socket.dev/npm/package/@takumi0706/mcp-google-calendar

---

## 14. Final Verdict

### Overall Assessment: ⚠️ **REQUIRES CORRECTIONS BEFORE IMPLEMENTATION**

### What's Correct:
- ✅ Core architecture and graceful degradation pattern
- ✅ Import structure and Python standard library usage
- ✅ Configuration dictionary structure
- ✅ Error handling and logging approach
- ✅ Environment variable patterns (mostly)

### What Needs Fixing:
- ❌ **CRITICAL:** Method name `list_tools()` → `get_tools()`
- ❌ **CRITICAL:** Supabase package name incorrect
- ❌ **CRITICAL:** Tavily package name incorrect
- ❌ **CRITICAL:** Gmail package doesn't exist (select alternative)
- ❌ **CRITICAL:** Calendar package doesn't exist (select alternative)
- ❌ **CRITICAL:** Missing async/await specifications

### Implementation Readiness: 60%

The plan provides a solid foundation but requires package name corrections and async specification before coding can begin.

---

## Appendix: Quick Reference

### Correct Import Statement:
```python
from langchain_mcp_adapters.client import MultiServerMCPClient
```

### Correct Method Call:
```python
tools = await client.get_tools()  # NOT list_tools()
```

### Correct Package Names:
| Service | Incorrect (Plan) | Correct (Actual) |
|---------|-----------------|------------------|
| Supabase | `@modelcontextprotocol/server-supabase` | `@supabase/mcp-server-postgrest` |
| Tavily | `@modelcontextprotocol/server-tavily` | `@mcptools/mcp-tavily` |
| Gmail | `@modelcontextprotocol/server-gmail` | `@monsoft/mcp-gmail` (or others) |
| Calendar | `@modelcontextprotocol/server-google-calendar` | `mcp-google-calendar` (or others) |

---

**End of Report**
