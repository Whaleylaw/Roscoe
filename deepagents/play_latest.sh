#!/bin/bash
# Simple script to play the most recent TTS audio file

AUDIO_DIR="./audio_outputs"
LATEST_FILE="$AUDIO_DIR/latest.txt"

if [ -f "$LATEST_FILE" ]; then
    AUDIO_PATH=$(cat "$LATEST_FILE")
    if [ -f "$AUDIO_PATH" ]; then
        echo "Playing: $AUDIO_PATH"
        afplay "$AUDIO_PATH"
    else
        echo "Error: Audio file not found at $AUDIO_PATH"
        exit 1
    fi
else
    # Fallback: Find the most recent MP3 file
    LATEST_MP3=$(ls -t "$AUDIO_DIR"/*.mp3 2>/dev/null | head -1)
    if [ -n "$LATEST_MP3" ]; then
        echo "Playing: $LATEST_MP3"
        afplay "$LATEST_MP3"
    else
        echo "No audio files found in $AUDIO_DIR"
        exit 1
    fi
fi
