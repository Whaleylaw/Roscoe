# Deployment Configuration Guide

## Environment Variables for LangSmith Deployment

Your `.env` file is now configured for deployment! Here's what to copy to LangSmith:

### Required Variables (Core Functionality)

```bash
ANTHROPIC_API_KEY=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
OPENAI_API_KEY=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
SUPABASE_URL=https://pdhrmsoydwvoafunalez.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBkaHJtc295ZHd2b2FmdW5hbGV6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzkwMjQ1NCwiZXhwIjoyMDY5NDc4NDU0fQ.sK89R5rqq5ScGt_qHYcN_57mikg5716rdxhHkq_YhUY
POSTGRES_CONNECTION_STRING=postgresql://postgres:Beekerks50$@db.pdhrmsoydwvoafunalez.supabase.co:5432/postgres
TAVILY_API_KEY=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
```

### Optional Variables (Enhanced Functionality)

```bash
# Gmail Integration (✅ NOW READY!)
GMAIL_CREDENTIALS={"web":{...}}
GMAIL_TOKEN={"token":"ya29..."}

# Calendar Integration (✅ NOW READY!)
GOOGLE_CALENDAR_CREDENTIALS={"web":{...}}
GOOGLE_CALENDAR_TOKEN={"token":"ya29..."}

# Text-to-Speech
ELEVENLABS_API_KEY=sk_3c4e0d7a4bd1a3ff18812d19d684ac65a05f29263788f2d9

# Observability
LANGSMITH_API_KEY=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
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=Roscoe_deepagent
```

## Deployment Steps

1. **Go to LangSmith** → Deployments → Create Deployment
2. **Connect GitHub Repository**: `https://github.com/Whaleylaw/Roscoe`
3. **Add Environment Variables**: Copy all REQUIRED variables above
4. **Optional**: Add ELEVENLABS_API_KEY and LANGSMITH_* variables
5. **Optional**: Add Gmail/Calendar credentials and tokens (OAuth support now implemented!)
6. **Deploy** and wait for build to complete

## What Will Work

✅ Claude 4.5 Sonnet AI responses
✅ GPT-4o subagents
✅ Supabase database operations (doc_files, case_projects, etc.)
✅ Tavily web search for legal research
✅ PostgresStore persistent memory (`/memories/*`)
✅ PostgresSaver conversation checkpoints
✅ Skills library workflow
✅ Text-to-speech (if ELEVENLABS_API_KEY added)
✅ LangSmith tracing (if LANGSMITH_* added)
✅ Gmail integration (if GMAIL_CREDENTIALS and GMAIL_TOKEN added) - **NOW READY!**
✅ Google Calendar integration (if GOOGLE_CALENDAR_CREDENTIALS and GOOGLE_CALENDAR_TOKEN added) - **NOW READY!**

## Implementation Notes

**OAuth Token Support (Gmail & Calendar):**
- OAuth token support has been implemented in `src/tools/toolkits.py`
- Both Gmail and Calendar toolkits now support environment variable credentials
- Temporary directory approach ensures credentials are written securely
- Automatic cleanup of temporary files after toolkit initialization
- Works in both local development (file paths) and cloud deployment (JSON strings)

## Next Steps After Deployment

1. Test the deployment with a simple query
2. Verify Supabase database connectivity
3. Check LangSmith traces for debugging
4. Test Gmail/Calendar integration if credentials were added
