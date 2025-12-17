"""
Google OAuth2 Authentication for Gmail and Calendar APIs

This module provides centralized OAuth2 credential management for Google services.
Follows the lazy initialization pattern used elsewhere in Roscoe to avoid pickle
issues with LangGraph checkpointing.

Usage:
    from roscoe.core.google_auth import get_google_credentials, get_gmail_service, get_calendar_service
    
    # Get credentials for custom API usage
    creds = get_google_credentials()
    
    # Get pre-built service clients
    gmail = get_gmail_service()
    calendar = get_calendar_service()

Environment Variables:
    GOOGLE_CREDENTIALS_FILE: Path to OAuth client credentials JSON (default: credentials.json)
    GOOGLE_TOKEN_FILE: Path to stored OAuth tokens (default: token.json)

Setup:
    1. Create a Google Cloud project
    2. Enable Gmail API and Google Calendar API
    3. Create OAuth 2.0 Desktop credentials
    4. Download credentials.json and set GOOGLE_CREDENTIALS_FILE
    5. Run first authentication (will open browser for consent)
"""

import os
from pathlib import Path
from typing import Optional

# OAuth scopes for Gmail and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',  # Read, compose, send, and modify emails
    'https://www.googleapis.com/auth/gmail.send',     # Send emails only
    'https://www.googleapis.com/auth/calendar',       # Full calendar access
    'https://www.googleapis.com/auth/calendar.events', # Create/modify events
]

# Default paths for credentials
DEFAULT_CREDENTIALS_FILE = "credentials.json"
DEFAULT_TOKEN_FILE = "token.json"


def _get_credentials_path() -> Path:
    """Get path to OAuth client credentials file."""
    path = os.environ.get("GOOGLE_CREDENTIALS_FILE", DEFAULT_CREDENTIALS_FILE)
    return Path(path)


def _get_token_path() -> Path:
    """Get path to stored OAuth tokens file."""
    path = os.environ.get("GOOGLE_TOKEN_FILE", DEFAULT_TOKEN_FILE)
    return Path(path)


def get_google_credentials():
    """
    Lazily initialize and return Google OAuth2 credentials.
    
    Handles:
    - Loading existing tokens from file
    - Refreshing expired tokens
    - Running OAuth flow for first-time authentication
    
    Returns:
        google.oauth2.credentials.Credentials or None if not configured
    """
    credentials_path = _get_credentials_path()
    token_path = _get_token_path()
    
    # Check if credentials file exists
    if not credentials_path.exists():
        print(f"Warning: Google credentials file not found at {credentials_path}")
        print("Set GOOGLE_CREDENTIALS_FILE environment variable or place credentials.json in project root")
        return None
    
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        
        creds = None
        
        # Load existing token if available
        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            except Exception as e:
                print(f"Warning: Could not load token file: {e}")
                creds = None
        
        # Check if credentials need refresh or re-auth
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed token
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Warning: Could not refresh token: {e}")
                creds = None
        
        # Run OAuth flow if no valid credentials
        if not creds or not creds.valid:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
                
                # Save token for future use
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                    
                print(f"Google OAuth credentials saved to {token_path}")
            except Exception as e:
                print(f"Error during Google OAuth flow: {e}")
                return None
        
        return creds
        
    except ImportError as e:
        print(f"Warning: Google auth libraries not installed: {e}")
        print("Run: pip install google-auth-oauthlib google-auth-httplib2")
        return None
    except Exception as e:
        print(f"Error initializing Google credentials: {e}")
        return None


def get_gmail_service():
    """
    Lazily initialize and return Gmail API service client.
    
    Returns:
        googleapiclient.discovery.Resource or None if not configured
    """
    creds = get_google_credentials()
    if not creds:
        return None
    
    try:
        from googleapiclient.discovery import build
        return build('gmail', 'v1', credentials=creds)
    except ImportError:
        print("Warning: google-api-python-client not installed")
        print("Run: pip install google-api-python-client")
        return None
    except Exception as e:
        print(f"Error creating Gmail service: {e}")
        return None


def get_calendar_service():
    """
    Lazily initialize and return Google Calendar API service client.
    
    Returns:
        googleapiclient.discovery.Resource or None if not configured
    """
    creds = get_google_credentials()
    if not creds:
        return None
    
    try:
        from googleapiclient.discovery import build
        return build('calendar', 'v3', credentials=creds)
    except ImportError:
        print("Warning: google-api-python-client not installed")
        print("Run: pip install google-api-python-client")
        return None
    except Exception as e:
        print(f"Error creating Calendar service: {e}")
        return None


def check_google_auth_configured() -> bool:
    """
    Check if Google OAuth is properly configured.
    
    Returns:
        True if credentials file exists, False otherwise
    """
    return _get_credentials_path().exists()


def get_auth_status() -> dict:
    """
    Get current Google authentication status.
    
    Returns:
        dict with status information
    """
    credentials_path = _get_credentials_path()
    token_path = _get_token_path()
    
    status = {
        "credentials_file_exists": credentials_path.exists(),
        "credentials_file_path": str(credentials_path),
        "token_file_exists": token_path.exists(),
        "token_file_path": str(token_path),
        "authenticated": False,
        "scopes": SCOPES,
    }
    
    if token_path.exists():
        try:
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            status["authenticated"] = creds.valid
            status["token_expired"] = creds.expired if creds else None
            status["has_refresh_token"] = bool(creds.refresh_token) if creds else False
        except Exception as e:
            status["token_error"] = str(e)
    
    return status



