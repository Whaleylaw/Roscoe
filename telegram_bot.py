"""
Telegram Bot Integration for Roscoe Legal Assistant

This script provides a Telegram bot interface to the legal agent, allowing users to:
1. Send messages via Telegram
2. Receive AI-generated responses
3. Get audio versions of responses via ElevenLabs TTS

Workflow:
- User sends message → Bot receives → Agent processes → Generate audio → Send text + audio back

Usage:
    python telegram_bot.py
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional
import tempfile

# Telegram bot library
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Agent communication
import requests

# ElevenLabs for TTS
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# Environment variables
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
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "NNl6r8mD7vthiJatiJt1")  # Default to a professional voice
LANGGRAPH_API_URL = os.getenv("LANGGRAPH_DEPLOYMENT_URL", "http://127.0.0.1:2024")  # Default to local dev server
AGENT_ID = os.getenv("LANGGRAPH_GRAPH_ID", "legal_agent")

# User session management: maps telegram_user_id -> langgraph_thread_id
user_threads: Dict[int, str] = {}

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else None


def create_thread_for_user(user_id: int) -> str:
    """
    Create a new LangGraph thread for a Telegram user.

    Args:
        user_id: Telegram user ID

    Returns:
        str: Thread ID from LangGraph
    """
    try:
        response = requests.post(
            f"{LANGGRAPH_API_URL}/threads",
            json={"assistant_id": AGENT_ID},
            timeout=30
        )
        response.raise_for_status()
        thread_id = response.json()["thread_id"]

        logger.info(f"Created new thread {thread_id} for user {user_id}")
        return thread_id

    except Exception as e:
        logger.error(f"Failed to create thread for user {user_id}: {e}")
        raise


def get_or_create_thread(user_id: int) -> str:
    """
    Get existing thread ID or create new one for user.

    Args:
        user_id: Telegram user ID

    Returns:
        str: Thread ID
    """
    if user_id not in user_threads:
        user_threads[user_id] = create_thread_for_user(user_id)

    return user_threads[user_id]


async def send_message_to_agent(thread_id: str, message: str) -> str:
    """
    Send message to LangGraph agent and get response.

    Args:
        thread_id: LangGraph thread ID
        message: User's message

    Returns:
        str: Agent's response text
    """
    try:
        # Send message to agent
        response = requests.post(
            f"{LANGGRAPH_API_URL}/threads/{thread_id}/runs",
            json={
                "assistant_id": AGENT_ID,
                "input": {
                    "messages": [
                        {"role": "user", "content": message}
                    ]
                }
            },
            timeout=120  # Longer timeout for complex queries
        )
        response.raise_for_status()

        # Extract agent's response from the run result
        # The response structure depends on LangGraph API version
        result = response.json()

        # Try to extract the assistant's message from the response
        if "messages" in result:
            # Find the last assistant message
            for msg in reversed(result["messages"]):
                if msg.get("role") == "assistant":
                    return msg.get("content", "I processed your request but couldn't generate a response.")

        # Fallback: return a generic message if we can't find the response
        logger.warning(f"Couldn't extract response from result: {result}")
        return "I received your message and processed it, but encountered an issue generating the response."

    except requests.exceptions.Timeout:
        logger.error(f"Timeout while waiting for agent response for thread {thread_id}")
        return "I'm sorry, but processing your request took too long. Please try a simpler query."

    except Exception as e:
        logger.error(f"Failed to get response from agent for thread {thread_id}: {e}")
        return "I encountered an error while processing your request. Please try again later."


async def generate_audio(text: str) -> Optional[bytes]:
    """
    Generate audio from text using ElevenLabs TTS.

    Args:
        text: Text to convert to speech

    Returns:
        bytes: Audio file content (MP3), or None if generation fails
    """
    if not elevenlabs_client:
        logger.warning("ElevenLabs client not initialized, skipping audio generation")
        return None

    try:
        # Generate audio using ElevenLabs
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

        # Collect audio bytes from generator
        audio_bytes = b"".join(audio_generator)

        logger.info(f"Generated {len(audio_bytes)} bytes of audio")
        return audio_bytes

    except Exception as e:
        logger.error(f"Failed to generate audio: {e}")
        return None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command.
    """
    user = update.effective_user
    user_id = user.id

    # Create or get thread for user
    thread_id = get_or_create_thread(user_id)

    welcome_message = (
        f"Welcome to Roscoe Legal Assistant, {user.first_name}! 👋\n\n"
        f"I'm your AI legal assistant powered by Claude 4.5 Sonnet. I can help you with:\n"
        f"• Legal research and case law\n"
        f"• Document analysis and drafting\n"
        f"• Case management and organization\n"
        f"• Calendar and scheduling\n"
        f"• Email management\n\n"
        f"Send me a message and I'll respond with both text and audio.\n\n"
        f"Your conversation ID: {thread_id[:8]}..."
    )

    await update.message.reply_text(welcome_message)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /reset command to start a new conversation.
    """
    user_id = update.effective_user.id

    # Remove old thread and create new one
    if user_id in user_threads:
        old_thread_id = user_threads[user_id]
        logger.info(f"Resetting thread {old_thread_id} for user {user_id}")
        del user_threads[user_id]

    # Create new thread
    thread_id = get_or_create_thread(user_id)

    await update.message.reply_text(
        f"✅ Started a new conversation!\n\n"
        f"Your new conversation ID: {thread_id[:8]}..."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle incoming messages from Telegram users.

    Workflow:
    1. Get or create thread for user
    2. Send message to agent
    3. Generate audio from response
    4. Send back text and audio
    """
    user = update.effective_user
    user_id = user.id
    message_text = update.message.text

    logger.info(f"Received message from user {user_id} ({user.username}): {message_text[:50]}...")

    # Send "typing" indicator
    await update.message.chat.send_action(action="typing")

    try:
        # Get or create thread for this user
        thread_id = get_or_create_thread(user_id)

        # Send message to agent and get response
        response_text = await send_message_to_agent(thread_id, message_text)

        # Send text response first
        await update.message.reply_text(response_text)

        # Generate and send audio if ElevenLabs is configured
        if elevenlabs_client:
            # Send "uploading audio" indicator
            await update.message.chat.send_action(action="upload_voice")

            # Generate audio
            audio_bytes = await generate_audio(response_text)

            if audio_bytes:
                # Create temporary file for audio
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
                    temp_audio.write(audio_bytes)
                    temp_audio_path = temp_audio.name

                try:
                    # Send audio file
                    with open(temp_audio_path, 'rb') as audio_file:
                        await update.message.reply_voice(
                            voice=audio_file,
                            caption="🔊 Audio version"
                        )

                    logger.info(f"Sent audio response to user {user_id}")

                finally:
                    # Clean up temporary file
                    Path(temp_audio_path).unlink(missing_ok=True)
            else:
                logger.warning(f"Audio generation failed for user {user_id}")
        else:
            logger.info("ElevenLabs not configured, skipping audio generation")

    except Exception as e:
        logger.error(f"Error handling message from user {user_id}: {e}")
        await update.message.reply_text(
            "I encountered an error processing your message. Please try again or use /reset to start a new conversation."
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors in the bot.
    """
    logger.error(f"Exception while handling an update: {context.error}")


def main() -> None:
    """
    Start the Telegram bot.
    """
    # Check required configuration
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return

    if not ELEVENLABS_API_KEY:
        logger.warning("ELEVENLABS_API_KEY not found - audio responses will be disabled")

    logger.info(f"Starting Roscoe Telegram Bot...")
    logger.info(f"LangGraph API URL: {LANGGRAPH_API_URL}")
    logger.info(f"Agent ID: {AGENT_ID}")
    logger.info(f"ElevenLabs TTS: {'Enabled' if elevenlabs_client else 'Disabled'}")

    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("reset", reset_command))

    # Register message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Bot started! Send /start to begin.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
