#!/usr/bin/env python3
"""
Test 5: Internet Access
Verifies that scripts can make HTTP requests when internet is enabled.
"""

import sys

print("=" * 50)
print("Test: Internet Access")
print("=" * 50)

try:
    import requests
except ImportError:
    print("requests library not available")
    print("Installing with pip would be needed in production")
    sys.exit(1)

# Test basic HTTP GET
print("Testing HTTP GET to httpbin.org/ip...")
try:
    response = requests.get("https://httpbin.org/ip", timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✓ Internet access test passed!")
    else:
        print(f"\n✗ Unexpected status code: {response.status_code}")
        sys.exit(1)
        
except requests.exceptions.Timeout:
    print("\n✗ Request timed out - network may be restricted")
    sys.exit(1)
except requests.exceptions.ConnectionError as e:
    print(f"\n✗ Connection error - internet may be disabled: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Unexpected error: {e}")
    sys.exit(1)

