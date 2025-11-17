# Render Deployment Guide - Telegram Webhook

This guide explains how to deploy the Telegram webhook service to Render for 24/7 cloud operation.

## Architecture

```
Telegram User → Telegram Bot API → Render Webhook → LangGraph Cloud → Response → Telegram User
                                           ↓
                                    ElevenLabs TTS (Audio)
```

**Key Benefits:**
- ✅ No local server needed
- ✅ Automatic HTTPS (required by Telegram)
- ✅ Auto-scaling and uptime
- ✅ Free tier available

## Prerequisites

1. **GitHub Repository**: Code must be pushed to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Telegram Bot**: Create via @BotFather (get bot token)
4. **LangGraph Deployment**: Have your LangGraph agent deployed (LangSmith/Cloud Run/etc.)

## Step-by-Step Deployment

### 1. Push Code to GitHub

```bash
# From the deepagents directory
git add telegram_webhook.py render.yaml requirements.txt
git commit -m "feat: Add Telegram webhook for Render deployment"
git push origin main
```

### 2. Create New Service on Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the `deepagents` repository

### 3. Configure Service

**Basic Settings:**
- **Name**: `roscoe-telegram-bot` (or your preferred name)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python telegram_webhook.py`

### 4. Set Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** for each:

#### Required Variables:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=8296515852:AAFqQM_eYxuDxgDaJfcU6I2uWVhnFYaXdIA
TELEGRAM_WEBHOOK_URL=https://roscoe-telegram-bot.onrender.com  # Your Render URL (add after first deploy)
TELEGRAM_ALLOWED_USER_IDS=123456789  # Your Telegram user ID (get from @userinfobot)

# LangGraph Configuration
LANGGRAPH_DEPLOYMENT_URL=https://your-langgraph-deployment.com  # Your LangGraph deployment
LANGGRAPH_GRAPH_ID=legal_agent

# ElevenLabs TTS
ELEVENLABS_API_KEY=sk_3c4e0d7a4bd1a3ff18812d19d684ac65a05f29263788f2d9
```

#### Optional Variables:

```bash
# ElevenLabs Voice Customization (defaults to professional voice)
ELEVENLABS_VOICE_ID=NNl6r8mD7vthiJatiJt1
```

**Important Notes:**
- **TELEGRAM_WEBHOOK_URL**: Use your Render service URL (e.g., `https://roscoe-telegram-bot.onrender.com`)
  - On first deploy, you won't have the URL yet
  - Deploy without it first, then add it and re-deploy
- **TELEGRAM_ALLOWED_USER_IDS**: Comma-separated list of user IDs allowed to use the bot
  - Get your ID from @userinfobot on Telegram
  - Example: `123456789,987654321` for multiple users

### 5. Deploy

1. Click **"Create Web Service"**
2. Wait for deployment to complete (5-10 minutes)
3. Copy your service URL: `https://your-service-name.onrender.com`

### 6. Update Webhook URL

After first deployment:

1. Go to **Environment** tab
2. Add/update `TELEGRAM_WEBHOOK_URL` with your Render URL
3. Click **"Save Changes"** (triggers re-deploy)

The webhook will be automatically configured on startup.

### 7. Verify Deployment

**Check Health:**
```bash
curl https://your-service-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "langgraph_url": "https://your-langgraph-deployment.com",
  "agent_id": "legal_agent",
  "elevenlabs_enabled": true
}
```

**Check Webhook:**
```bash
curl https://your-service-name.onrender.com/webhook
```

Expected response:
```json
{
  "status": "healthy",
  "service": "telegram-webhook"
}
```

### 8. Test on Telegram

1. Open Telegram
2. Search for your bot (from @BotFather creation)
3. Send `/start` command
4. Send a test message
5. You should receive:
   - Text response
   - Audio response (if ElevenLabs configured)

## Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ Yes | - | Bot token from @BotFather |
| `TELEGRAM_WEBHOOK_URL` | ✅ Yes | - | Your Render service URL (HTTPS) |
| `TELEGRAM_ALLOWED_USER_IDS` | ⚠️ Recommended | Empty (allows all) | Comma-separated user IDs |
| `LANGGRAPH_DEPLOYMENT_URL` | ✅ Yes | `http://127.0.0.1:2024` | Your LangGraph deployment URL |
| `LANGGRAPH_GRAPH_ID` | No | `legal_agent` | Agent ID in LangGraph |
| `ELEVENLABS_API_KEY` | ⚠️ Recommended | - | For audio responses |
| `ELEVENLABS_VOICE_ID` | No | Professional voice | Voice customization |

## Monitoring

### View Logs

1. Go to your service on Render dashboard
2. Click **"Logs"** tab
3. Monitor real-time logs

**What to look for:**
```
INFO - ✅ Webhook configured: https://your-service.onrender.com/webhook
INFO - LangGraph API: https://your-langgraph-deployment.com
INFO - Agent ID: legal_agent
INFO - ElevenLabs TTS: Enabled
```

### Check Metrics

- **Metrics** tab shows:
  - CPU usage
  - Memory usage
  - Request count
  - Response times

## Troubleshooting

### Bot Not Responding

**Check webhook status:**
```bash
# Test if webhook is set correctly
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

**Reset webhook:**
```bash
# Delete webhook
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook

# Service will auto-configure on next request
```

### Unauthorized Access Error

1. Get your Telegram user ID from @userinfobot
2. Add to `TELEGRAM_ALLOWED_USER_IDS` environment variable
3. Save and redeploy

### LangGraph Connection Errors

1. Verify `LANGGRAPH_DEPLOYMENT_URL` is correct (include https://)
2. Check LangGraph deployment is running
3. Test connection:
   ```bash
   curl https://your-langgraph-deployment.com/threads
   ```

### Audio Not Working

1. Check `ELEVENLABS_API_KEY` is set correctly
2. Verify API key is valid at elevenlabs.io
3. Check logs for TTS errors
4. Text responses will still work if audio fails

### Logs Show Errors

**Common errors:**

| Error | Solution |
|-------|----------|
| `TELEGRAM_BOT_TOKEN not set!` | Add environment variable |
| `TELEGRAM_WEBHOOK_URL not set!` | Add your Render URL |
| `Failed to create thread` | Check LangGraph deployment URL |
| `Failed to generate audio` | Check ElevenLabs API key |

## Cost Estimation

**Render Free Tier:**
- 750 hours/month of free compute
- Automatic sleep after 15 min inactivity
- Wakes on first request (cold start ~30s)

**Paid Plan ($7/month):**
- Always-on (no cold starts)
- Better performance
- More compute resources

**Recommended:** Start with free tier, upgrade if cold starts are annoying.

## Updating Your Deployment

When you make changes to the code:

```bash
# 1. Commit changes
git add .
git commit -m "Update telegram webhook"
git push origin main

# 2. Render auto-deploys on push (if auto-deploy enabled)
# OR manually deploy from Render dashboard
```

## Security Best Practices

1. **Whitelist Users**: Always set `TELEGRAM_ALLOWED_USER_IDS`
2. **Keep Tokens Secret**: Never commit tokens to GitHub
3. **Use HTTPS**: Render provides this automatically
4. **Monitor Logs**: Watch for suspicious activity
5. **Rotate Tokens**: Periodically regenerate bot token via @BotFather

## Advanced Configuration

### Custom Domain

1. Go to service **Settings** → **Custom Domain**
2. Add your domain (e.g., `bot.yourdomain.com`)
3. Update `TELEGRAM_WEBHOOK_URL` to use custom domain

### Auto-Deploy

Enable automatic deployments on GitHub push:

1. Service **Settings** → **Auto-Deploy**
2. Select branch (e.g., `main`)
3. Save

### Health Check Endpoint

Render can ping your service to keep it warm:

1. **Settings** → **Health Check Path**
2. Set to: `/health`
3. Save

## Support

**Render Support:**
- Docs: [render.com/docs](https://render.com/docs)
- Community: [community.render.com](https://community.render.com)

**Telegram Bot Issues:**
- Check logs on Render dashboard
- Test webhook with curl commands above
- Verify environment variables are set correctly

## Next Steps After Deployment

1. **Test thoroughly**: Send various messages to ensure everything works
2. **Set up monitoring**: Configure alerts for errors
3. **Document for users**: Share bot username and instructions
4. **Backup configuration**: Save environment variables somewhere safe
