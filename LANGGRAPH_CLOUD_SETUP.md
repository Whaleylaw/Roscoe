# LangGraph Cloud Deployment Setup

## Issue: Missing Tools in Deployment

If your deployed agent only has text-to-speech and native filesystem tools, but is missing Gmail, Calendar, Supabase, Tavily, and code execution tools, this is because **required environment variables are not set** in the LangGraph Cloud deployment.

## Root Cause

The toolkit initialization functions in `src/tools/toolkits.py` use graceful degradation:
- If environment variables are missing, they return empty tool lists instead of failing
- This means the agent starts successfully but without the tools

## Required Environment Variables

Set these in your LangGraph Cloud deployment settings (Dashboard → Deployments → Your Deployment → Settings → Environment Variables):

### ✅ Core Required Variables

```bash
# Anthropic API (for Claude models)
ANTHROPIC_API_KEY=sk-ant-...

# PostgreSQL Database Connection
POSTGRES_CONNECTION_STRING=postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres

# Supabase MCP Server
SUPABASE_URL=https://PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# RunLoop Code Execution
RUNLOOP_API_KEY=your_runloop_api_key

# Tavily Search API
TAVILY_API_KEY=tvly-...
```

### ⚠️ Optional Variables (Tools will be skipped if not provided)

```bash
# ElevenLabs Text-to-Speech
ELEVENLABS_API_KEY=sk_...

# Gmail (requires OAuth setup)
GMAIL_CREDENTIALS={"installed":{...}}
GMAIL_TOKEN={"token":"...","refresh_token":"..."}

# Google Calendar (requires OAuth setup)
GOOGLE_CALENDAR_CREDENTIALS={"installed":{...}}
GOOGLE_CALENDAR_TOKEN={"token":"...","refresh_token":"..."}
```

## Environment Variable Details

### 1. RUNLOOP_API_KEY (CRITICAL - Code Execution)

**What it's for:** Sandboxed Python code execution via RunLoop API

**How to get it:**
1. Sign up at https://runloop.ai
2. Navigate to API Keys section
3. Create a new API key
4. Copy the key (starts with `rl-...`)

**Why it's missing:** Most common oversight - new requirement for code execution

### 2. SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (CRITICAL - Database)

**What it's for:** Supabase MCP server for PostgREST database queries

**How to get it:**
1. Go to your Supabase project: https://supabase.com/dashboard/project/YOUR_PROJECT
2. Navigate to Settings → API
3. Copy:
   - `SUPABASE_URL`: Project URL (e.g., `https://abc123.supabase.co`)
   - `SUPABASE_SERVICE_ROLE_KEY`: Service role key (secret, starts with `eyJ...`)

**Why it's missing:** Need both URL and service role key for RLS bypass

### 3. TAVILY_API_KEY (CRITICAL - Search)

**What it's for:** Tavily MCP server for AI-powered web search

**How to get it:**
1. Sign up at https://tavily.com
2. Navigate to API Keys
3. Create a new API key
4. Copy the key (starts with `tvly-...`)

**Why it's missing:** Required for legal research and web search capabilities

### 4. ELEVENLABS_API_KEY (WORKING - Already Set)

**What it's for:** Text-to-speech voice synthesis

**Status:** ✅ This one is working, which confirms environment variables CAN be set correctly

### 5. Gmail and Calendar (Optional)

**What they're for:** Email and calendar management

**How to get them:**
1. Create OAuth credentials at https://console.cloud.google.com
2. Enable Gmail API and Google Calendar API
3. Download credentials JSON
4. For cloud deployment, you need BOTH:
   - `GMAIL_CREDENTIALS`: The OAuth client credentials JSON
   - `GMAIL_TOKEN`: The token.json after completing OAuth flow locally

**Why they might be missing:** OAuth setup is complex for cloud deployments

## System Dependencies

The `apt.txt` file in the repository root ensures Node.js is installed:

```txt
nodejs
npm
```

This is required for MCP servers (Supabase and Tavily) which run as Node.js subprocesses using `npx`.

## How to Fix

### Option 1: Set All Required Variables

1. Go to LangGraph Cloud Dashboard
2. Navigate to your deployment
3. Click **Settings** → **Environment Variables**
4. Add each required variable from the list above
5. Click **Save** and **Redeploy**

### Option 2: Verify Environment Variables

Test if environment variables are being loaded:

```python
# Add this temporarily to src/agents/legal_agent.py init_tools()
import os
import logging

logger = logging.getLogger(__name__)

async def init_tools():
    logger.error("🔍 Environment Variable Check:")
    logger.error(f"  RUNLOOP_API_KEY: {'✅ Set' if os.getenv('RUNLOOP_API_KEY') else '❌ Missing'}")
    logger.error(f"  SUPABASE_URL: {'✅ Set' if os.getenv('SUPABASE_URL') else '❌ Missing'}")
    logger.error(f"  SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else '❌ Missing'}")
    logger.error(f"  TAVILY_API_KEY: {'✅ Set' if os.getenv('TAVILY_API_KEY') else '❌ Missing'}")
    logger.error(f"  ELEVENLABS_API_KEY: {'✅ Set' if os.getenv('ELEVENLABS_API_KEY') else '❌ Missing'}")

    # ... rest of init_tools() code
```

Check the deployment logs to see which variables are missing.

## Expected Tool Counts

When all environment variables are set correctly, you should see:

```
Successfully initialized Gmail toolkit with 5 tools
Successfully initialized Calendar toolkit with 7 tools
Successfully initialized Supabase MCP with X tools (varies)
Successfully initialized Tavily MCP with X tools (varies)
Successfully initialized ElevenLabs text-to-speech tool
RunLoop executor initialized successfully
```

If any return 0 tools or show warnings, check:
1. Environment variable is set
2. Value is correct (no typos, whitespace, or encoding issues)
3. API key is valid and not expired

## Testing After Deployment

Send this message to your agent:

```
What tools do you have access to?
```

You should see:
- ✅ runloop_execute_code (code execution)
- ✅ postgrestRequest, sqlToRest (Supabase database)
- ✅ tavily_search (web search)
- ✅ text_to_speech (ElevenLabs)
- ✅ Gmail tools (if configured)
- ✅ Calendar tools (if configured)

## Common Mistakes

### 1. Missing Quotes in JSON Environment Variables

❌ Wrong:
```
GMAIL_CREDENTIALS={"installed":{"client_id":"123"}}
```

✅ Correct (in LangGraph Cloud UI, paste JSON as-is):
```json
{"installed":{"client_id":"123"}}
```

### 2. Using Anon Key Instead of Service Role Key

❌ Wrong: `SUPABASE_SERVICE_ROLE_KEY=eyJh...` (anon key)
✅ Correct: `SUPABASE_SERVICE_ROLE_KEY=eyJh...` (service_role key)

Service role key is longer and has more permissions (RLS bypass).

### 3. Forgetting the /rest/v1 Endpoint

The toolkit automatically adds `/rest/v1` to `SUPABASE_URL`, so use:
- ✅ `https://PROJECT.supabase.co`
- ❌ `https://PROJECT.supabase.co/rest/v1` (will become `/rest/v1/rest/v1`)

### 4. Not Redeploying After Setting Variables

Environment variables only take effect after redeployment:
1. Set variables
2. Click **Deploy** or **Redeploy**
3. Wait for build to complete

## Troubleshooting Logs

Enable debug logging to see toolkit initialization:

In deployment settings, add:
```bash
LANGCHAIN_VERBOSE=true
LANGCHAIN_TRACING_V2=true  # Optional: if using LangSmith
```

Then check logs for messages like:
```
INFO - Initializing Gmail toolkit with credentials from...
INFO - Successfully initialized Gmail toolkit with 5 tools
WARNING - Gmail credentials not configured, skipping Gmail toolkit initialization
ERROR - Supabase MCP initialization failed: npx command not found
```

## Still Having Issues?

If tools are still missing after setting all environment variables:

1. **Check Node.js availability**
   - MCP servers require Node.js/npm
   - The `apt.txt` file should install this
   - Verify in logs: Look for "npx command not found" errors

2. **Check API key validity**
   - Test keys locally first
   - Ensure keys have required permissions
   - Check for rate limits or expiration

3. **Check deployment logs**
   - Look for initialization errors
   - MCP server startup failures
   - Network connectivity issues

4. **Verify graceful degradation**
   - System should log warnings for missing tools
   - Agent should start even if some tools fail
   - Only TTS working means others are silently failing

## Quick Checklist

- [ ] `RUNLOOP_API_KEY` set (code execution)
- [ ] `SUPABASE_URL` set (database)
- [ ] `SUPABASE_SERVICE_ROLE_KEY` set (database)
- [ ] `TAVILY_API_KEY` set (search)
- [ ] `POSTGRES_CONNECTION_STRING` set (checkpointer)
- [ ] `ELEVENLABS_API_KEY` set (TTS) - ✅ Already working
- [ ] `apt.txt` file exists in repository root
- [ ] Redeployed after setting variables
- [ ] Checked deployment logs for errors
- [ ] Tested agent with "What tools do you have access to?"

## Summary

**The problem:** Environment variables for tool credentials are not set in LangGraph Cloud deployment.

**The solution:** Set all required environment variables in the deployment settings and redeploy.

**The evidence:** Only TTS works because only `ELEVENLABS_API_KEY` is set. All other tools return empty lists due to missing credentials.

---

**Need help?** Share your deployment logs showing the toolkit initialization output, and I can help identify which specific variables are missing.
