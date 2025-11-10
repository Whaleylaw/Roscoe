---
name: supabase-edge-functions-specialist
description: Use when creating, debugging, or deploying Supabase Edge Functions, experiencing 504 timeouts, external service calls failing, or needing to trace edge function execution flow - provides systematic approach to edge function lifecycle management including debugging with logs, testing external integrations, and deployment verification
---

# Supabase Edge Functions Specialist

## Overview

Supabase Edge Functions are serverless TypeScript/Deno functions with a **hard 150-second timeout limit**. This skill provides systematic workflows for creating, debugging, and deploying edge functions, with focus on timeout management and external service integration.

## When to Use

**Use this skill when:**
- Creating new Supabase Edge Functions
- Debugging 504 Gateway Timeout errors
- External service calls from edge functions failing or hanging
- Edge function logs show execution but external service has no logs
- Need to verify edge function → external service connection
- Deploying edge functions with secrets/environment variables
- Optimizing batch operations to fit within 150s timeout

**Symptoms that trigger this skill:**
- "504 Gateway Timeout" after ~150 seconds
- Edge function says "calling service X" but service X never receives request
- Database updates not executing (edge function times out before reaching them)
- Infinite loops due to operations not completing
- External API parameters causing silent failures

## Core Constraints

**CRITICAL LIMITS:**
- **150-second hard timeout** - Edge function MUST complete within this limit
- **Deno runtime** - Not Node.js (different APIs, import patterns)
- **No file system access** - Use Supabase Storage for files
- **Limited memory** - Optimize for efficiency

## 🚨 CRITICAL: Supabase MCP Requirement

**ALL Supabase operations when debugging/managing edge functions MUST use Supabase MCP Server:**

❌ **NEVER use `supabase` CLI commands directly:**
- `supabase functions logs` - Use MCP `get_logs` instead
- `supabase functions deploy` - Edge functions deploy via MCP when available
- `supabase secrets set/list` - Use MCP tools for secrets management

✅ **ALWAYS use Supabase MCP tools:**
- `mcp__supabase__get_logs(service="edge-function")` - View edge function logs
- `mcp__supabase__execute_sql` - Query database
- `mcp__supabase__search_docs` - Look up edge function documentation
- `mcp__supabase__list_edge_functions` - List all edge functions
- `mcp__supabase__get_edge_function(function_slug="...")` - Get edge function code

**Why:** MCP server provides proper authentication, error handling, and audit trail. CLI commands will fail with authentication errors.

**Exception:** Code examples in this skill may show CLI commands for reference, but you MUST use MCP equivalents when actually executing.

## Systematic Debugging Workflow

When edge function fails or times out, follow this **exact sequence**:

### Step 1: Verify Edge Function Execution
```bash
# View edge function logs
supabase functions logs <function-name> --limit 50
```

**Look for:**
- Function start marker (timestamp when invoked)
- Console.log markers showing execution flow
- Error messages or stack traces
- Timeout indicator (exactly 150 seconds between start and 504)

### Step 2: Check External Service Separately

**CRITICAL:** Edge function logs ≠ external service logs

If edge function says "calling DoclingService" but times out:
```bash
# Check external service logs (e.g., Google Cloud Run)
gcloud logging read "resource.type=cloud_run_revision" --limit=50 --format=json

# Or use MCP tool
mcp__cloud-run__get_service_log(project="...", service="...")
```

**Root cause analysis:**
- **Edge function logs show call, service logs empty** → Request never reached service (API parameter issue, URL wrong, auth failing)
- **Both show activity** → Service is slow, need to optimize or reduce batch size
- **Edge function logs show timeout at exactly 150s** → Operation taking too long

### Step 3: Trace Execution Flow with Markers

Add console.log markers at EVERY significant step:

```typescript
console.log('[handler] Edge Function invoked');
console.log('[step1] Validating authorization');
console.log('[step2] Initializing Supabase client');
console.log('[step3] Parsing request parameters');
console.log('[step4] Querying documents');
console.log(`[step5] Found ${documents.length} documents`);
console.log('[step6] Processing documents');
console.log(`[docling] Calling external service with file: ${filename}`);
console.log('[docling] External service responded');
console.log('[database] Updating doc_files table');
console.log('[complete] Batch processing complete');
```

**Why this matters:** Logs show WHERE execution stops

### Step 4: Verify External API Parameters

**Common failure:** Adding unsupported parameters to external API calls

**Example of what goes wrong:**
```typescript
// ❌ BAD: Added parameter that service doesn't recognize
formData.append('skip_ai_metadata', 'true'); // Service silently rejects request
```

**How to verify:**
1. Check external service API documentation
2. Test API call with minimal required parameters first
3. Add optional parameters ONE AT A TIME
4. Verify each parameter in service logs

### Step 5: Calculate Timeout Budget

**150 seconds total budget. Calculate:**
- Query time: ~1-5 seconds
- Download from storage: ~2-10 seconds per file
- External service call: ~10-60 seconds per document
- Upload to storage: ~2-5 seconds
- Database update: ~1-2 seconds

**Formula:** `batch_size × (download + service + upload) < 140 seconds`

**Example:**
- Service processes 1 document in 30 seconds
- Download + upload = 10 seconds
- Total per document = 40 seconds
- Safe batch_size = 3 (120 seconds + 20s buffer)

## Common Mistake Patterns

| Mistake | Symptom | Fix |
|---------|---------|-----|
| **Unsupported API parameter** | Edge function says "calling service", service logs empty, 150s timeout | Remove parameter, check API docs |
| **Batch size too large** | Processing starts, times out at 150s | Reduce batch_size (calculate: total_time ÷ per-item-time) |
| **Missing await** | Function completes instantly, database not updated | Add `await` to async operations |
| **Database update after timeout** | Edge function times out, database never updates | Move database update BEFORE expensive operations OR reduce batch size |
| **Not checking service logs** | Assume edge function sent request, but service never received it | ALWAYS check service logs separately |
| **Silent API rejection** | API call "succeeds" but does nothing | Verify all parameters are supported |

## Deployment Quick Reference

```bash
# Deploy edge function
supabase functions deploy <function-name>

# Deploy with environment verification
supabase secrets list  # Verify secrets exist
supabase functions deploy <function-name>
supabase functions logs <function-name> --limit 5  # Verify deployment

# Set secrets
supabase secrets set DOCLING_SERVICE_URL=https://...
supabase secrets set API_KEY=...

# Test locally (uses local Supabase)
supabase functions serve <function-name>

# Invoke for testing
curl -i --location --request POST 'https://PROJECT_REF.supabase.co/functions/v1/<function-name>' \
  --header 'Authorization: Bearer ANON_KEY' \
  --header 'Content-Type: application/json' \
  --data '{"batch_size": 1}'
```

## Edge Function Structure Template

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req: Request) => {
  console.log('[handler] Function invoked');

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: corsHeaders });
  }

  try {
    // 1. Validate authorization
    console.log('[step1] Validating auth');
    const authHeader = req.headers.get('Authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      throw new Error('Invalid authorization');
    }

    // 2. Initialize Supabase
    console.log('[step2] Init Supabase');
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    );

    // 3. Parse request
    console.log('[step3] Parsing request');
    const body = await req.json().catch(() => ({}));
    const batchSize = body.batch_size || 1;

    // 4. Process (with timeout awareness)
    console.log('[step4] Processing');
    const results = [];

    for (const item of items) {
      const result = await processItem(item);
      results.push(result);
    }

    // 5. Return response
    console.log('[complete] Returning results');
    return new Response(JSON.stringify({
      success: true,
      results,
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json', ...corsHeaders },
    });

  } catch (error: any) {
    console.error('[error]', error);
    return new Response(JSON.stringify({
      success: false,
      error: error.message,
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders },
    });
  }
});
```

## External Service Integration Pattern

```typescript
async function callExternalService(data: Blob, filename: string): Promise<Response> {
  const serviceUrl = Deno.env.get('EXTERNAL_SERVICE_URL');

  console.log(`[external] Calling ${serviceUrl}`);
  console.log(`[external] File: ${filename}, Size: ${data.size} bytes`);

  // Create FormData with ONLY supported parameters
  const formData = new FormData();
  formData.append('file', data, filename);
  formData.append('output_format', 'json'); // Verify in API docs
  // DO NOT add parameters without verifying API supports them

  const response = await fetch(serviceUrl, {
    method: 'POST',
    body: formData,
    // Add timeout if supported by Deno version
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`[external] HTTP ${response.status}: ${errorText}`);
    throw new Error(`Service error: ${response.status}`);
  }

  console.log('[external] Success');
  return response;
}
```

## Red Flags - STOP and Debug Systematically

- Edge function logs show "calling service" but service has no logs
- Timeout happens at exactly 150 seconds
- Database updates not executing
- Same operation processes repeatedly (infinite loop)
- Added new API parameter and now nothing works
- "It worked 20 minutes ago" (recent code change broke it)

**All of these mean: Follow the Systematic Debugging Workflow above**

## Timeout Optimization Strategies

**Strategy 1: Reduce Batch Size**
```typescript
// From: batch_size = 10 (10 × 40s = 400s > 150s TIMEOUT)
// To:   batch_size = 1  (1 × 40s = 40s < 150s OK)
const batchSize = body.batch_size || 1; // Safe default
```

**Strategy 2: Use Temporal Workflows**
```typescript
// Edge function calls Temporal workflow
// Workflow retries on timeout, processes incrementally
// Eliminates 150s limit for long-running operations
```

**Strategy 3: Async Processing**
```typescript
// Edge function queues task, returns immediately
// Background worker processes queue
// Database trigger or scheduled function
```

## Testing Checklist

Before deploying edge function:

- [ ] Test locally with `supabase functions serve`
- [ ] Verify all required secrets are set
- [ ] Test with batch_size=1 first
- [ ] Check edge function logs after deployment
- [ ] **Check external service logs separately**
- [ ] Verify database updates execute
- [ ] Calculate timeout budget (batch_size × per-item-time < 140s)
- [ ] Add console.log markers for debugging
- [ ] Test error handling (invalid auth, missing data, service down)

## Real-World Example: Fixing 504 Timeout

**Problem:** Edge function times out calling Docling service

**Investigation:**
1. Check edge function logs → Shows "calling Docling" at 10:11
2. Check Docling logs → Last entry at 10:06 (service never received request!)
3. Review recent code changes → Added `skip_ai_metadata` parameter
4. Check Docling API docs → Parameter not supported
5. Remove parameter, redeploy
6. Test → Request reaches Docling, completes in 25s

**Root cause:** Unsupported API parameter caused silent rejection

**Fix:** Remove unsupported parameter, verify API docs first
