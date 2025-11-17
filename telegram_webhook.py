"""
Telegram Webhook Integration for Roscoe Legal Assistant

Webhook-based Telegram bot that integrates with LangGraph agent, enabling:
- Text and voice message support
- Real-time streaming updates
- ElevenLabs text-to-speech responses
- Authorization whitelist

Architecture:
    Telegram → Webhook → FastAPI → LangGraph Agent → Stream Updates → Telegram
"""

import os
import asyncio
import logging
from typing import Dict, Optional
import tempfile
from pathlib import Path

from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import requests
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")  # e.g., https://your-app.onrender.com
TELEGRAM_ALLOWED_USER_IDS = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "NNl6r8mD7vthiJatiJt1")
LANGGRAPH_API_URL = os.getenv("LANGGRAPH_DEPLOYMENT_URL", "http://127.0.0.1:2024")
LANGGRAPH_API_KEY = os.getenv("LANGGRAPH_API_KEY")  # X-API-Key for authentication
AGENT_ID = os.getenv("LANGGRAPH_GRAPH_ID", "legal_agent")

# User session management: maps telegram_user_id -> langgraph_thread_id
user_threads: Dict[str, str] = {}

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else None

# Initialize FastAPI app
app = FastAPI(title="Roscoe Telegram Webhook")

# Telegram Bot API base URL
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def is_user_authorized(user_id: int) -> bool:
    """Check if user is in the authorization whitelist."""
    return str(user_id) in TELEGRAM_ALLOWED_USER_IDS or not TELEGRAM_ALLOWED_USER_IDS[0]


def send_telegram_message(chat_id: int, text: str, parse_mode: str = "Markdown") -> Optional[Dict]:
    """Send a text message to Telegram."""
    try:
        response = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return None


def edit_telegram_message(chat_id: int, message_id: int, text: str, parse_mode: str = "Markdown") -> Optional[Dict]:
    """Edit an existing Telegram message."""
    try:
        response = requests.post(
            f"{TELEGRAM_API}/editMessageText",
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": parse_mode
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to edit Telegram message: {e}")
        return None


def send_telegram_voice(chat_id: int, voice_data: bytes, caption: str = None) -> Optional[Dict]:
    """Send a voice message to Telegram."""
    try:
        files = {"voice": ("voice.mp3", voice_data, "audio/mpeg")}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption

        response = requests.post(
            f"{TELEGRAM_API}/sendVoice",
            files=files,
            data=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send Telegram voice: {e}")
        return None


def send_chat_action(chat_id: int, action: str = "typing"):
    """Send chat action (typing indicator)."""
    try:
        requests.post(
            f"{TELEGRAM_API}/sendChatAction",
            json={"chat_id": chat_id, "action": action},
            timeout=5
        )
    except Exception as e:
        logger.error(f"Failed to send chat action: {e}")


def create_thread_for_user(user_id: int) -> str:
    """Create a new LangGraph thread for a Telegram user."""
    try:
        headers = {}
        if LANGGRAPH_API_KEY:
            headers["X-API-Key"] = LANGGRAPH_API_KEY

        response = requests.post(
            f"{LANGGRAPH_API_URL}/threads",
            json={"assistant_id": AGENT_ID},
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        thread_id = response.json()["thread_id"]
        logger.info(f"Created thread {thread_id} for user {user_id}")
        return thread_id
    except Exception as e:
        logger.error(f"Failed to create thread: {e}")
        raise


def get_or_create_thread(user_id: int) -> str:
    """Get existing thread or create new one for user."""
    user_key = str(user_id)
    if user_key not in user_threads:
        user_threads[user_key] = create_thread_for_user(user_id)
    return user_threads[user_key]


async def stream_agent_response(thread_id: str, message: str, chat_id: int):
    """
    Stream agent response with real-time updates to Telegram.

    This sends the message to LangGraph and streams the response back,
    editing the Telegram message every 2 seconds with new content.
    """
    try:
        # Send initial "processing" message
        sent_message = send_telegram_message(chat_id, "🤔 Processing your request...")
        if not sent_message:
            return None

        message_id = sent_message["result"]["message_id"]

        # Prepare headers with authentication
        headers = {}
        if LANGGRAPH_API_KEY:
            headers["X-API-Key"] = LANGGRAPH_API_KEY

        # Stream the agent response
        response = requests.post(
            f"{LANGGRAPH_API_URL}/threads/{thread_id}/runs/stream",
            json={
                "assistant_id": AGENT_ID,
                "input": {
                    "messages": [{"role": "user", "content": message}]
                },
                "stream_mode": "messages"
            },
            headers=headers,
            stream=True,
            timeout=300
        )
        response.raise_for_status()

        accumulated_text = ""
        last_update_time = asyncio.get_event_loop().time()

        # Process streaming response
        for line in response.iter_lines():
            if not line:
                continue

            try:
                # Parse SSE format
                if line.startswith(b"data: "):
                    import json
                    data = json.loads(line[6:])

                    # Extract message content
                    if isinstance(data, list) and len(data) > 0:
                        for item in data:
                            if isinstance(item, dict) and item.get("type") == "ai":
                                content = item.get("content", "")
                                if content:
                                    accumulated_text = content

                    # Update message every 2 seconds
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_update_time >= 2.0 and accumulated_text:
                        edit_telegram_message(chat_id, message_id, accumulated_text)
                        last_update_time = current_time

            except Exception as e:
                logger.error(f"Error processing stream line: {e}")
                continue

        # Final update with complete response
        if accumulated_text:
            edit_telegram_message(chat_id, message_id, accumulated_text)
            return accumulated_text
        else:
            fallback = "I processed your request but couldn't generate a response."
            edit_telegram_message(chat_id, message_id, fallback)
            return fallback

    except Exception as e:
        logger.error(f"Error streaming agent response: {e}")
        error_msg = "Sorry, I encountered an error processing your request."
        send_telegram_message(chat_id, error_msg)
        return None


async def generate_audio(text: str) -> Optional[bytes]:
    """Generate audio from text using ElevenLabs TTS."""
    if not elevenlabs_client:
        logger.warning("ElevenLabs client not initialized")
        return None

    try:
        audio_generator = elevenlabs_client.generate(
            text=text,
            voice=ELEVENLABS_VOICE_ID,
            model="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True
            )
        )

        audio_bytes = b"".join(audio_generator)
        logger.info(f"Generated {len(audio_bytes)} bytes of audio")
        return audio_bytes

    except Exception as e:
        logger.error(f"Failed to generate audio: {e}")
        return None


async def process_message(chat_id: int, user_id: int, message_text: str):
    """Process incoming text message from Telegram."""
    try:
        # Check authorization
        if not is_user_authorized(user_id):
            send_telegram_message(chat_id, "🚫 Unauthorized access. Please contact your administrator.")
            return

        # Send typing indicator
        send_chat_action(chat_id, "typing")

        # Get or create thread
        thread_id = get_or_create_thread(user_id)

        # Stream agent response
        response_text = await stream_agent_response(thread_id, message_text, chat_id)

        if not response_text:
            return

        # Generate and send audio
        if elevenlabs_client:
            send_chat_action(chat_id, "upload_voice")
            audio_bytes = await generate_audio(response_text)

            if audio_bytes:
                send_telegram_voice(chat_id, audio_bytes, "🔊 Audio version")
                logger.info(f"Sent audio response to chat {chat_id}")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        send_telegram_message(chat_id, "❌ Error processing your message. Please try again.")


async def handle_start_command(chat_id: int, user_id: int, first_name: str):
    """Handle /start command."""
    try:
        if not is_user_authorized(user_id):
            send_telegram_message(chat_id, "🚫 Unauthorized access.")
            return

        thread_id = get_or_create_thread(user_id)

        welcome_message = (
            f"Welcome to Roscoe Legal Assistant, {first_name}! 👋\n\n"
            f"I'm your AI legal assistant powered by Claude 4.5 Sonnet. I can help you with:\n"
            f"• Legal research and case law\n"
            f"• Document analysis and drafting\n"
            f"• Case management and organization\n"
            f"• Calendar and scheduling\n"
            f"• Email management\n\n"
            f"Send me a message and I'll respond with both text and audio.\n\n"
            f"Your conversation ID: `{thread_id[:8]}...`"
        )

        send_telegram_message(chat_id, welcome_message)

    except Exception as e:
        logger.error(f"Error handling /start: {e}")
        send_telegram_message(chat_id, "Error initializing conversation.")


async def handle_reset_command(chat_id: int, user_id: int):
    """Handle /reset command."""
    try:
        user_key = str(user_id)

        if user_key in user_threads:
            old_thread = user_threads[user_key]
            logger.info(f"Resetting thread {old_thread} for user {user_id}")
            del user_threads[user_key]

        thread_id = get_or_create_thread(user_id)

        send_telegram_message(
            chat_id,
            f"✅ Started a new conversation!\n\nYour new conversation ID: `{thread_id[:8]}...`"
        )

    except Exception as e:
        logger.error(f"Error handling /reset: {e}")
        send_telegram_message(chat_id, "Error resetting conversation.")


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Telegram webhook endpoint.

    Receives updates from Telegram and processes them asynchronously.
    Returns 200 OK immediately to comply with Telegram's timeout requirements.
    """
    try:
        update = await request.json()
        logger.info(f"Received webhook update: {update.get('update_id')}")

        # Extract message data
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        user_id = message.get("from", {}).get("id")
        first_name = message.get("from", {}).get("first_name", "User")

        if not chat_id or not user_id:
            return JSONResponse({"status": "ok"})

        # Handle commands
        text = message.get("text", "")

        if text == "/start":
            background_tasks.add_task(handle_start_command, chat_id, user_id, first_name)
        elif text == "/reset":
            background_tasks.add_task(handle_reset_command, chat_id, user_id)
        elif text:
            background_tasks.add_task(process_message, chat_id, user_id, text)

        return JSONResponse({"status": "ok"})

    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.get("/webhook")
async def webhook_health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "telegram-webhook"}


@app.get("/health")
async def health():
    """General health check."""
    return {
        "status": "healthy",
        "langgraph_url": LANGGRAPH_API_URL,
        "agent_id": AGENT_ID,
        "elevenlabs_enabled": elevenlabs_client is not None
    }


@app.on_event("startup")
async def setup_webhook():
    """Set up Telegram webhook on startup."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    if not TELEGRAM_WEBHOOK_URL:
        logger.error("TELEGRAM_WEBHOOK_URL not set!")
        return

    try:
        webhook_url = f"{TELEGRAM_WEBHOOK_URL}/webhook"

        response = requests.post(
            f"{TELEGRAM_API}/setWebhook",
            json={"url": webhook_url},
            timeout=10
        )
        response.raise_for_status()

        logger.info(f"✅ Webhook configured: {webhook_url}")
        logger.info(f"LangGraph API: {LANGGRAPH_API_URL}")
        logger.info(f"Agent ID: {AGENT_ID}")
        logger.info(f"ElevenLabs TTS: {'Enabled' if elevenlabs_client else 'Disabled'}")

    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")


if __name__ == "__main__":
    import uvicorn

    # Get port from environment (Render uses PORT)
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        "telegram_webhook:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
