#!/usr/bin/env python3
"""
Healthcheck script for roscoe-uploads container.
Expected to be placed at /api/healthcheck.py in the container.
"""

import sys
import urllib.request

try:
    # Check if service is responding on port 8125
    response = urllib.request.urlopen("http://localhost:8125/health", timeout=2)
    data = response.read().decode('utf-8')

    if "healthy" in data:
        sys.exit(0)  # Healthy
    else:
        sys.exit(1)  # Unhealthy

except Exception as e:
    sys.exit(1)  # Unhealthy
