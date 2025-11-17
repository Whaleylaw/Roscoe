#!/usr/bin/env python3
"""
Quick test script to verify the agent works with MCP tools.
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:2024"

# Create a thread
print("Creating thread...")
response = requests.post(f"{BASE_URL}/threads", json={"assistant_id": "legal_agent"})
thread_id = response.json()["thread_id"]
print(f"Thread ID: {thread_id}")

# Send a message
print("\nSending query...")
query = "Show me the first 3 files in the doc_files table"
payload = {
    "assistant_id": "legal_agent",
    "input": {
        "messages": [
            {"role": "user", "content": query}
        ]
    },
    "stream_mode": ["values"]
}

response = requests.post(
    f"{BASE_URL}/threads/{thread_id}/runs/stream",
    json=payload,
    stream=True
)

print(f"\nQuery: {query}")
print("\nAgent response stream:")
print("=" * 80)

for line in response.iter_lines():
    if line:
        try:
            # Parse the SSE event
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = json.loads(line_str[6:])  # Skip 'data: '

                # Print relevant parts
                if isinstance(data, list) and len(data) > 0:
                    for item in data:
                        if 'messages' in item:
                            for msg in item['messages']:
                                if hasattr(msg, 'content') and msg.content:
                                    print(f"\nMessage: {msg.content}")
                        elif 'error' in item:
                            print(f"\n❌ ERROR: {item['error']}")
        except Exception as e:
            print(f"Parse error: {e}")

print("\n" + "=" * 80)
print("\nTest complete. Check server logs for middleware invocation messages.")
