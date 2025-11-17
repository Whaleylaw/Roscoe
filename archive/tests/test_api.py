#!/usr/bin/env python3
"""
Test script to verify Supabase tool execution with Fix Attempt 6.
"""
import requests
import json
import time
import uuid

def test_supabase_tool():
    """Send a test message that triggers Supabase postgrestRequest tool."""

    # Use stateless invocation endpoint
    url = "http://127.0.0.1:2024/assistants/legal_agent/invoke"

    payload = {
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": "Please query the doc_files table and return the count of documents. Use postgrestRequest with GET /doc_files?select=uuid&limit=5"
                }
            ]
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    print("=" * 80)
    print("TESTING FIX ATTEMPT 6: Missing 'config' parameter")
    print("=" * 80)
    print(f"\nSending request to: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nWaiting for response...\n")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("\n✅ Request successful! Response:\n")
            print("-" * 80)

            # Parse JSON response
            result = response.json()
            print(json.dumps(result, indent=2))

            print("-" * 80)
            print("\n✅ TEST COMPLETE - Check backend logs for detailed execution info")
            print("Look for:")
            print("  - '🔧 PATCHED_ARUN called for postgrestRequest'")
            print("  - 'Added default config to kwargs'")
            print("  - '✅ PATCHED_ARUN succeeded for postgrestRequest'")

        else:
            print(f"\n❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_supabase_tool()
