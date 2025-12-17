# Slack Integration Setup for Roscoe

Complete guide to set up bidirectional chat with Roscoe from Slack.

---

## Overview

Once set up, you'll be able to:
- **@mention Roscoe** in channels: `@Roscoe what's the status of Wilson case?`
- **DM Roscoe directly**: Just message Roscoe like any team member
- **Use slash commands**: `/roscoe analyze the medical records`
- **Get notifications**: Roscoe can notify you when tasks complete or red flags are found

---

## Prerequisites

- Slack workspace admin permissions (to create apps)
- LangGraph server running (`langgraph dev`)
- Python environment with dependencies installed

---

## Part 1: Create Slack App (15 minutes)

### Step 1: Create New Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"**
3. Choose **"From scratch"**
4. App Name: `Roscoe` (or your preferred name)
5. Choose your workspace
6. Click **"Create App"**

### Step 2: Configure Bot Token Scopes

1. In the left sidebar, click **"OAuth & Permissions"**
2. Scroll to **"Scopes"** section
3. Under **"Bot Token Scopes"**, click **"Add an OAuth Scope"**
4. Add these scopes:
   - `app_mentions:read` - See @mentions in channels
   - `channels:history` - Read channel messages (for context)
   - `chat:write` - Send messages
   - `commands` - Use slash commands
   - `files:write` - Upload files
   - `im:history` - Read DM messages
   - `im:read` - See DM channel info
   - `im:write` - Send DMs

### Step 3: Enable Socket Mode

1. In the left sidebar, click **"Socket Mode"**
2. Toggle **"Enable Socket Mode"** to ON
3. Give it a token name: `Roscoe Socket Token`
4. Click **"Generate"**
5. **COPY THE TOKEN** (starts with `xapp-`) - you'll need this for `SLACK_APP_TOKEN`
6. Click **"Done"**

### Step 4: Subscribe to Events

1. In the left sidebar, click **"Event Subscriptions"**
2. Toggle **"Enable Events"** to ON
3. Under **"Subscribe to bot events"**, add:
   - `app_mention` - When someone @mentions the bot
   - `message.im` - Direct messages to bot
4. Click **"Save Changes"**

### Step 5: Create Slash Commands

1. In the left sidebar, click **"Slash Commands"**
2. Click **"Create New Command"**
3. Command: `/roscoe`
4. Request URL: (leave blank - Socket Mode handles this)
5. Short Description: `Ask Roscoe a question`
6. Usage Hint: `[your question or command]`
7. Click **"Save"**

8. Create another command:
   - Command: `/roscoe-reset`
   - Request URL: (leave blank)
   - Short Description: `Reset conversation with Roscoe`
   - Click **"Save"**

### Step 6: Install App to Workspace

1. In the left sidebar, click **"Install App"**
2. Click **"Install to Workspace"**
3. Review permissions
4. Click **"Allow"**
5. **COPY THE BOT TOKEN** (starts with `xoxb-`) - you'll need this for `SLACK_BOT_TOKEN`

### Step 7: Get App Token (if you didn't save it earlier)

1. In the left sidebar, click **"Basic Information"**
2. Scroll to **"App-Level Tokens"**
3. If you lost your token, generate a new one:
   - Click **"Generate Token and Scopes"**
   - Name: `Roscoe Socket Token`
   - Add scope: `connections:write`
   - Click **"Generate"**
   - **COPY THE TOKEN** (starts with `xapp-`)

---

## Part 2: Configure Environment Variables (5 minutes)

### Step 1: Update .env File

Open `../.env` (one directory up from Roscoe repo) and add:

```bash
# Slack Integration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_ASSISTANT_ID=roscoe_paralegal
SLACK_DEFAULT_CHANNEL=#legal-updates

# LangGraph connection (point to local dev or your VM)
LANGGRAPH_API_URL=http://127.0.0.1:2024
ROSCOE_ENABLE_SLACK_BRIDGE=true  # Auto-start Slack bridge inside the agent container
```

Set `LANGGRAPH_API_URL` to your deployed server (e.g., `http://34.63.223.97:8123`) when running the bot on the VM.
Set `ROSCOE_ENABLE_SLACK_BRIDGE=false` if you prefer to keep the Socket-Mode listener off inside the container and run it manually.

**Replace**:
- `xoxb-your-bot-token-here` with the Bot Token from Step 6
- `xapp-your-app-token-here` with the App Token from Step 3 or 7
- `#legal-updates` with your preferred default channel

---

## Part 3: Install Dependencies (2 minutes)

```bash
cd "/Volumes/X10 Pro/Roscoe"

# Install Slack dependencies
uv sync

# Or if using pip directly:
pip install slack-sdk slack-bolt
```

---

## Part 4: Start Everything (5 minutes)

You need TWO processes running:

### Terminal 1: LangGraph Server

```bash
cd "/Volumes/X10 Pro/Roscoe"
langgraph dev --allow-blocking
```

Wait until you see:
```
Server started in XX.XXs
🎨 Opening Studio in your browser...
```

### Terminal 2: Slack Bot

```bash
cd "/Volumes/X10 Pro/Roscoe"
./scripts/run_slack_bot.sh
```

You should see log output similar to:
```
Roscoe Slack Bot - Starting...
LangGraph API: http://127.0.0.1:2024
Assistant ID : roscoe_paralegal
✅ Successfully connected to LangGraph API
Starting Socket Mode handler...
⚡️ Bolt app is running!
```
Leave this process running; it maintains a persistent WebSocket to Slack’s Socket Mode gateway.

---

## Part 5: Test Integration (5 minutes)

### Test 1: DM Roscoe

1. Open Slack
2. Find "Roscoe" in Apps section
3. Send a direct message: `Hello Roscoe!`
4. You should get a response

### Test 2: @mention in Channel

1. Invite Roscoe to a channel:
   - In channel, type `/invite @Roscoe`
2. @mention Roscoe: `@Roscoe what can you help me with?`
3. You should get a response

### Test 3: Slash Command

1. In any channel or DM, type:
   `/roscoe what's your purpose?`
2. You should get a response

### Test 4: Have a Conversation

```
You: @Roscoe I'm working on the Wilson case
Roscoe: I'd be happy to help with the Wilson case. What would you like me to do?

You: Can you check if we have the medical records organized?
Roscoe: I can check the case folder structure. What's the full case folder name?
(e.g., "Wilson-MVA-03-15-2024")

You: Wilson-MVA-03-15-2024
Roscoe: [checks folder, provides status]
```

---

## Common Issues & Solutions

### Issue: "Cannot connect to LangGraph API"

**Solution**: Make sure LangGraph server is running:
```bash
cd "/Volumes/X10 Pro/Roscoe"
langgraph dev --allow-blocking
```

### Issue: "Slack integration not configured"

**Solution**: Check environment variables:
```bash
echo $SLACK_BOT_TOKEN
echo $SLACK_APP_TOKEN
```

If empty, add to `../.env` and restart both processes.

### Issue: Bot doesn't respond to @mentions

**Solutions**:
1. Check Event Subscriptions are enabled in Slack App settings
2. Make sure bot is invited to the channel: `/invite @Roscoe`
3. Check slack_bot.py terminal for errors

### Issue: "slack-sdk not installed"

**Solution**:
```bash
cd "/Volumes/X10 Pro/Roscoe"
uv sync
# or
pip install slack-sdk slack-bolt
```

Restart LangGraph server after installing.

---

## Advanced Features

### Notifications from Roscoe

The agent can proactively send notifications:

```python
# When agent completes a task
send_slack_message(
    "✅ Medical analysis complete for Wilson case",
    channel="#wilson-case"
)

# When red flag detected
send_slack_message(
    "⚠️ Red flag: 6-month treatment gap in Martinez case",
    urgency="high"
)
```

### File Uploads

The agent can upload reports:

```python
upload_file_to_slack(
    "/Reports/FINAL_SUMMARY_Wilson.md",
    channel="#wilson-case",
    title="Final Medical Analysis",
    comment="Analysis complete with strong causation"
)
```

### Conversation Reset

If conversation gets confused, reset it:
```
/roscoe-reset
```

This clears the conversation history and starts fresh.

---

## Using Roscoe from Slack

### Ask Questions

```
@Roscoe what's the status of the Martinez case?
@Roscoe summarize the causation analysis for Wilson
@Roscoe what are the key red flags in the Johnson records?
```

### Request Analysis

```
@Roscoe analyze the 911 call for Smith case at /projects/Smith-MVA/Investigation/911_call.mp3
@Roscoe run medical records analysis for Wilson case
@Roscoe research Kentucky comparative negligence statute
```

### Get File Information

```
@Roscoe what files are in the Wilson case folder?
@Roscoe show me the medical bills total for Martinez
@Roscoe list all reports for Johnson case
```

### Multi-turn Conversations

Roscoe remembers context in the conversation:

```
You: @Roscoe I need to analyze the Harris case medical records
Roscoe: I can help with that. What's the case folder name?

You: Harris-MVA-07-15-2024
Roscoe: Found the case folder. I see 15 medical records. Should I start the full 5-phase analysis?

You: Yes, start the analysis
Roscoe: Starting medical records analysis...
[analysis runs]
Roscoe: ✅ Analysis complete! Key findings: [summary]
```

---

## Production Tips

### Running as Background Service

For production, you'll want the Slack bot to run continuously:

**Option 1: Using nohup**
```bash
nohup ./scripts/run_slack_bot.sh > slack_bot.log 2>&1 &
```

**Option 2: Using systemd (Linux)**
1. Copy the provided template and update paths/users:
   ```bash
   sudo cp ops/roscoe-slack.service /etc/systemd/system/roscoe-slack.service
   sudo nano /etc/systemd/system/roscoe-slack.service
   ```
2. Reload and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable roscoe-slack
   sudo systemctl start roscoe-slack
   ```

The template already calls `scripts/run_slack_bot.sh`, so it uses the same startup logic as local dev.

**Option 3: Using Docker**
Include both LangGraph server and Slack bot in Docker Compose so they share the same image/code.

---

## Architecture Diagram

```
Slack Workspace
    ↓
    ├── User sends: "@Roscoe what's the status?"
    ↓
[Socket Mode WebSocket]
    ↓
slack_bot.py (receives message)
    ↓
    ├── Extracts user message
    ├── Gets/creates thread ID for user
    ↓
POST to LangGraph API
    ↓
    http://127.0.0.1:2024/threads/{thread_id}/runs/stream
    ↓
Roscoe Agent (LangGraph)
    ↓
    ├── Skill selector middleware
    ├── Execute tools (shell, Slack, filesystem)
    ├── Spawn sub-agents if needed
    ↓
Response streamed back
    ↓
slack_bot.py (collects response)
    ↓
Send to Slack (chat.postMessage)
    ↓
User sees response in Slack
```

---

## Monitoring

### Check Slack Bot Status

```bash
# Check if slack_bot.py is running
ps aux | grep slack_bot.py

# View logs
tail -f slack_bot.log
```

### Check LangGraph Server Status

```bash
# Test API endpoint
curl http://127.0.0.1:2024/ok

# Check if server is running
ps aux | grep langgraph
```

### View Conversation Threads

In slack_bot.py, conversation threads are stored in memory. For production, consider using Redis or a database to persist threads across restarts.

---

## Security Considerations

1. **Keep tokens secret**: Never commit SLACK_BOT_TOKEN or SLACK_APP_TOKEN to git
2. **Use .env files**: Store tokens in `../.env` (which is gitignored)
3. **Workspace permissions**: Only install to your workspace, not public
4. **Rate limiting**: Slack has rate limits - Roscoe respects these automatically
5. **Private data**: Be mindful of case information shared in Slack (use private channels)

---

## Next Steps

Once Slack integration is working:

1. **Create channels per case**: e.g., `#wilson-case-2024` for case-specific discussions
2. **Set up notifications**: Configure agent to notify on task completions
3. **Train team**: Show attorneys and staff how to interact with Roscoe
4. **Monitor usage**: Track which features are most valuable
5. **Iterate**: Add more tools or capabilities based on usage patterns

---

## Support

If you encounter issues:

1. Check the logs in both terminals
2. Verify environment variables are set
3. Test LangGraph API directly: `curl http://127.0.0.1:2024/ok`
4. Check Slack App settings (scopes, event subscriptions)
5. Try `/roscoe-reset` to clear conversation state

---

**You're all set!** Start chatting with Roscoe from Slack. 🎉
