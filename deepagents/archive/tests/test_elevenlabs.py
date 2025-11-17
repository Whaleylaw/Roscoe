#!/usr/bin/env python3
"""
Quick test script to understand ElevenLabs API behavior
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = "NNl6r8mD7vthiJatiJt1"

print(f"API Key: {api_key[:20]}...")
print(f"Voice ID: {voice_id}")
print()

# Import and test ElevenLabs
try:
    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=api_key)

    print("Calling text_to_speech.convert()...")
    result = client.text_to_speech.convert(
        text="Hello, this is a test of the ElevenLabs API.",
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )

    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    print()

    # Check if it's a generator
    import types
    if isinstance(result, types.GeneratorType):
        print("✓ It's a generator!")
        print("Consuming generator chunks...")
        chunks = []
        for i, chunk in enumerate(result):
            print(f"  Chunk {i}: type={type(chunk)}, len={len(chunk) if chunk else 0}")
            if chunk:
                chunks.append(chunk)

        audio_bytes = b''.join(chunks)
        print(f"\nTotal chunks: {len(chunks)}")
        print(f"Total bytes: {len(audio_bytes)}")

        # Save to test file
        with open('/tmp/elevenlabs_test.mp3', 'wb') as f:
            f.write(audio_bytes)
        print(f"✓ Saved to /tmp/elevenlabs_test.mp3")

    elif isinstance(result, bytes):
        print("✓ It's already bytes!")
        print(f"Length: {len(result)} bytes")

        # Save to test file
        with open('/tmp/elevenlabs_test.mp3', 'wb') as f:
            f.write(result)
        print(f"✓ Saved to /tmp/elevenlabs_test.mp3")

    else:
        print(f"⚠ Unexpected type: {type(result)}")
        print(f"Has __iter__: {hasattr(result, '__iter__')}")
        print(f"Has __next__: {hasattr(result, '__next__')}")

        # Try to iterate anyway
        print("\nTrying to iterate...")
        try:
            chunks = []
            for i, chunk in enumerate(result):
                print(f"  Chunk {i}: type={type(chunk)}, len={len(chunk) if hasattr(chunk, '__len__') else '?'}")
                chunks.append(chunk)

            audio_bytes = b''.join(chunks)
            print(f"\nTotal chunks: {len(chunks)}")
            print(f"Total bytes: {len(audio_bytes)}")

            with open('/tmp/elevenlabs_test.mp3', 'wb') as f:
                f.write(audio_bytes)
            print(f"✓ Saved to /tmp/elevenlabs_test.mp3")
        except Exception as e:
            print(f"✗ Failed to iterate: {e}")

except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
