"""
Custom ElevenLabs text-to-speech tool compatible with elevenlabs>=1.0.0

This tool wraps the newer ElevenLabs SDK which returns audio as a generator
instead of direct bytes. The langchain-community ElevenLabsText2SpeechTool
was written for the older API and doesn't handle generators.
"""

import os
import tempfile
import logging
from typing import Optional
from datetime import datetime
from langchain_core.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)

# Directory for audio outputs
AUDIO_OUTPUT_DIR = os.path.join(os.getcwd(), "audio_outputs")
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)


class ElevenLabsTTSTool(BaseTool):
    """
    Custom tool for converting text to speech using ElevenLabs API.

    Compatible with elevenlabs>=1.0.0 which returns audio as a generator.
    """

    name: str = "eleven_labs_text2speech"
    description: str = """
    Convert text to speech using ElevenLabs AI voice synthesis.
    Input should be the text you want to convert to speech.
    Returns the path to the generated audio file (.wav format).
    """

    api_key: Optional[str] = Field(default=None, exclude=True)
    voice_id: Optional[str] = Field(default="NNl6r8mD7vthiJatiJt1", exclude=True)  # Default voice from KEYS

    def __init__(self, **kwargs):
        """Initialize with API key from environment if not provided."""
        if 'api_key' not in kwargs:
            kwargs['api_key'] = os.getenv("ELEVENLABS_API_KEY")
        super().__init__(**kwargs)

    def _run(self, text: str) -> str:
        """
        Convert text to speech and return the audio file path.

        Args:
            text: The text to convert to speech

        Returns:
            str: Path to the generated audio file

        Raises:
            RuntimeError: If API key is missing or conversion fails
        """
        if not self.api_key:
            raise RuntimeError(
                "ElevenLabs API key not found. Set ELEVENLABS_API_KEY environment variable."
            )

        try:
            # Import elevenlabs SDK
            from elevenlabs.client import ElevenLabs

            # Initialize client with API key
            client = ElevenLabs(api_key=self.api_key)

            logger.info(f"Generating speech for text: {text[:50]}...")

            # Generate speech using current API (elevenlabs>=1.0.0)
            # Returns audio as a generator of chunks
            audio_generator = client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )

            # Consume the generator and collect audio chunks
            logger.info("Consuming audio generator chunks...")
            audio_chunks = []
            for chunk in audio_generator:
                if chunk:
                    audio_chunks.append(chunk)

            # Combine chunks into single bytes object
            audio_bytes = b''.join(audio_chunks)
            logger.info(f"Collected {len(audio_chunks)} chunks, total size: {len(audio_bytes)} bytes")

            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tts_{timestamp}.mp3"
            file_path = os.path.join(AUDIO_OUTPUT_DIR, filename)

            # Save to audio outputs directory
            with open(file_path, 'wb') as f:
                f.write(audio_bytes)

            logger.info(f"Successfully generated speech audio at: {file_path}")

            # Also save path to "latest.txt" for easy access
            latest_file = os.path.join(AUDIO_OUTPUT_DIR, "latest.txt")
            with open(latest_file, 'w') as f:
                f.write(file_path)

            return file_path

        except ImportError as e:
            raise RuntimeError(
                f"ElevenLabs package not installed. Install with: pip install elevenlabs\nError: {e}"
            )
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            raise RuntimeError(f"Error while generating speech: {str(e)}")

    async def _arun(self, text: str) -> str:
        """
        Async version - runs sync implementation in thread pool.

        Args:
            text: The text to convert to speech

        Returns:
            str: Path to the generated audio file
        """
        import asyncio
        return await asyncio.to_thread(self._run, text)


def create_elevenlabs_tts_tool() -> ElevenLabsTTSTool:
    """
    Factory function to create ElevenLabs TTS tool instance.

    Returns:
        ElevenLabsTTSTool: Configured tool instance
    """
    return ElevenLabsTTSTool()
