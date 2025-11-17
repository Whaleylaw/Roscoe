# Telegram Bot Integration

This document describes how to use the Telegram bot interface for Roscoe Legal Assistant.

## Overview

The Telegram bot provides a convenient way to interact with the legal agent through Telegram messaging. The bot:
- Receives messages from users
- Forwards them to the LangGraph agent
- Generates responses with ElevenLabs text-to-speech
- Sends back both text and audio to Telegram

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `python-telegram-bot>=21.0.0` and `elevenlabs>=1.0.0`.

### 2. Configure Environment Variables

Add the following to your `.env` file:

```bash
# Telegram bot token (from @BotFather)
TELEGRAM_BOT_TOKEN=your-bot-token-here

# ElevenLabs API key for text-to-speech
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Optional: Customize voice ID (defaults to professional voice)
ELEVENLABS_VOICE_ID=NNl6r8mD7vthiJatiJt1

# LangGraph deployment URL (defaults to local dev server)
LANGGRAPH_DEPLOYMENT_URL=http://127.0.0.1:2024

# Agent ID (defaults to legal_agent)
LANGGRAPH_GRAPH_ID=legal_agent
```

### 3. Start the Agent Server

First, start the LangGraph agent server:

```bash
langgraph dev --config langgraph.json
```

Or if using a deployed agent, set `LANGGRAPH_DEPLOYMENT_URL` to your deployment URL.

### 4. Start the Telegram Bot

In a separate terminal:

```bash
python telegram_bot.py
```

You should see:

```
INFO - Starting Roscoe Telegram Bot...
INFO - LangGraph API URL: http://127.0.0.1:2024
INFO - Agent ID: legal_agent
INFO - ElevenLabs TTS: Enabled
INFO - Bot started! Send /start to begin.
```

## Usage

### Commands

**`/start`** - Initialize conversation with the bot
- Creates a new thread for your user session
- Shows welcome message with available features

**`/reset`** - Reset conversation and start fresh
- Deletes current thread
- Creates new thread for clean slate

### Sending Messages

Simply send any text message to the bot, and it will:

1. Send "typing" indicator while processing
2. Forward your message to the legal agent
3. Get the agent's response
4. Send the text response back to you
5. Generate audio using ElevenLabs
6. Send the audio file as a voice message

### Example Conversation

```
You: /start

Bot: Welcome to Roscoe Legal Assistant, [Your Name]! 👋

I'm your AI legal assistant powered by Claude 4.5 Sonnet. I can help you with:
• Legal research and case law
• Document analysis and drafting
• Case management and organization
• Calendar and scheduling
• Email management

Send me a message and I'll respond with both text and audio.

Your conversation ID: 1a2b3c4d...

---

You: What's the statute of limitations for personal injury in California?

Bot: [typing...]

Bot: In California, the statute of limitations for personal injury cases is generally 2 years from the date of the injury (California Code of Civil Procedure § 335.1). However, there are important exceptions:

1. **Discovery Rule**: The clock may start when you discover (or should have discovered) the injury
2. **Minors**: Different rules apply for plaintiffs under 18
3. **Government Claims**: Only 6 months to file a claim against government entities

Would you like me to research specific exceptions that might apply to your case?

Bot: 🔊 Audio version
[Voice message with the same content]
```

## Features

### Session Management

- Each Telegram user gets their own conversation thread
- Threads persist across bot restarts (stored in LangGraph)
- Use `/reset` to start a new conversation

### Audio Responses

- Every text response automatically generates an audio version
- Uses ElevenLabs multilingual voice model
- Voice settings optimized for clarity and professionalism
- Audio sent as Telegram voice message for easy playback

### Error Handling

- Graceful degradation if ElevenLabs is not configured
- Timeout handling for long-running queries
- Error messages sent back to user
- Comprehensive logging for debugging

## Deployment

### Local Development

1. Run `langgraph dev` locally
2. Run `python telegram_bot.py`
3. Test with your Telegram bot

### Cloud Deployment

For production deployment, you need to run the Telegram bot as a service:

**Option 1: Deploy to same server as LangGraph**

```bash
# On your server
pip install -r requirements.txt
python telegram_bot.py &
```

**Option 2: Run as systemd service**

Create `/etc/systemd/system/roscoe-telegram-bot.service`:

```ini
[Unit]
Description=Roscoe Telegram Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/deepagents
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python telegram_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable roscoe-telegram-bot
sudo systemctl start roscoe-telegram-bot
```

**Option 3: Deploy to separate service (Render, Railway, etc.)**

1. Create a new web service
2. Set environment variables
3. Run `python telegram_bot.py`
4. Set `LANGGRAPH_DEPLOYMENT_URL` to your deployed agent

## Troubleshooting

### Bot not responding

1. Check bot is running: `ps aux | grep telegram_bot.py`
2. Check logs for errors
3. Verify `TELEGRAM_BOT_TOKEN` is correct
4. Test bot token with BotFather

### No audio responses

1. Check `ELEVENLABS_API_KEY` is set
2. Verify ElevenLabs API key is valid
3. Check logs for audio generation errors
4. Bot will still send text responses if audio fails

### Agent timeout errors

1. Increase timeout in `telegram_bot.py` (line 97: `timeout=120`)
2. Check LangGraph server is running
3. Verify `LANGGRAPH_DEPLOYMENT_URL` is correct
4. Check LangGraph server logs

### Connection errors to LangGraph

1. Verify LangGraph server is accessible
2. Check firewall rules if using remote server
3. Test with `curl http://your-server:2024/threads`
4. Verify `LANGGRAPH_API_URL` environment variable

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Telegram  │  HTTPS  │  telegram_bot.py │   HTTP  │  LangGraph API  │
│    User     ├────────►│  (Python bot)    ├────────►│  (Agent server) │
└─────────────┘         └──────────────────┘         └─────────────────┘
                                │
                                │  HTTPS
                                ▼
                        ┌──────────────────┐
                        │  ElevenLabs API  │
                        │  (Text-to-Speech)│
                        └──────────────────┘
```

## Configuration Reference

| Environment Variable | Required | Default | Description |
|---------------------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Bot token from @BotFather |
| `ELEVENLABS_API_KEY` | No | - | ElevenLabs API key (audio disabled if not set) |
| `ELEVENLABS_VOICE_ID` | No | `NNl6r8mD7vthiJatiJt1` | Voice ID for TTS |
| `LANGGRAPH_DEPLOYMENT_URL` | No | `http://127.0.0.1:2024` | LangGraph API URL |
| `LANGGRAPH_GRAPH_ID` | No | `legal_agent` | Agent/graph ID |

## Limitations

- Audio responses limited by ElevenLabs character limits (check your plan)
- Agent responses timeout after 120 seconds (configurable)
- One conversation thread per Telegram user ID
- Telegram message size limits apply (4096 characters for text)

## Support

For issues or questions:
1. Check logs: `python telegram_bot.py` will print logs to console
2. Enable debug logging: Set `level=logging.DEBUG` in `telegram_bot.py`
3. Check LangGraph server logs
4. Verify all environment variables are set correctly
