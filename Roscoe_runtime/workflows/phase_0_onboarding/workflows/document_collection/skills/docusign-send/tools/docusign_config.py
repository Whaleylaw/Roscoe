#!/usr/bin/env python3
"""
DocuSign Configuration and Authentication

This module handles JWT authentication with DocuSign API.
Environment variables or config file can be used for credentials.
"""

import os
import time
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

# Try to import docusign_esign - will be installed on first use
try:
    from docusign_esign import ApiClient
    from docusign_esign.client.api_exception import ApiException
    DOCUSIGN_AVAILABLE = True
except ImportError:
    DOCUSIGN_AVAILABLE = False


class DocuSignConfig:
    """DocuSign configuration and authentication handler."""
    
    # Default paths
    CONFIG_DIR = Path(__file__).parent / "config"
    PRIVATE_KEY_PATH = CONFIG_DIR / "docusign_private.key"
    
    # DocuSign URLs
    DEMO_AUTH_SERVER = "account-d.docusign.com"
    DEMO_API_BASE = "https://demo.docusign.net/restapi"
    PROD_AUTH_SERVER = "account.docusign.com"
    PROD_API_BASE = "https://na.docusign.net/restapi"
    
    # Default credentials (from your DocuSign app)
    DEFAULT_INTEGRATION_KEY = "db757a98-c874-49cc-a158-d0d1c6107f41"
    DEFAULT_USER_ID = "0bac94dd-8bee-4042-b38c-6874da6755d2"
    DEFAULT_ACCOUNT_ID = "5046b601-8938-4639-92bd-2e202bbefc69"
    
    def __init__(self, use_production: bool = False):
        """
        Initialize DocuSign configuration.
        
        Args:
            use_production: If True, use production endpoints. Default is demo/sandbox.
        """
        self.use_production = use_production
        self.auth_server = self.PROD_AUTH_SERVER if use_production else self.DEMO_AUTH_SERVER
        self.api_base = self.PROD_API_BASE if use_production else self.DEMO_API_BASE
        
        # Load credentials (env vars override defaults)
        self.integration_key = os.environ.get("DOCUSIGN_INTEGRATION_KEY", self.DEFAULT_INTEGRATION_KEY)
        self.user_id = os.environ.get("DOCUSIGN_USER_ID", self.DEFAULT_USER_ID)
        self.account_id = os.environ.get("DOCUSIGN_ACCOUNT_ID", self.DEFAULT_ACCOUNT_ID)
        
        # Private key can be from env var or file
        self.private_key = self._load_private_key()
        
        # Token cache
        self._access_token = None
        self._token_expiry = None
    
    def _load_private_key(self) -> Optional[str]:
        """Load private key from environment or file."""
        # Try environment variable first
        key = os.environ.get("DOCUSIGN_PRIVATE_KEY")
        if key:
            return key
        
        # Try file
        key_path = os.environ.get("DOCUSIGN_PRIVATE_KEY_PATH", str(self.PRIVATE_KEY_PATH))
        key_path = Path(key_path)
        
        if key_path.exists():
            return key_path.read_text()
        
        return None
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate that all required configuration is present.
        
        Returns:
            Tuple of (is_valid, list_of_missing_items)
        """
        missing = []
        
        if not self.integration_key:
            missing.append("DOCUSIGN_INTEGRATION_KEY")
        if not self.user_id:
            missing.append("DOCUSIGN_USER_ID")
        if not self.account_id:
            missing.append("DOCUSIGN_ACCOUNT_ID")
        if not self.private_key:
            missing.append("DOCUSIGN_PRIVATE_KEY or DOCUSIGN_PRIVATE_KEY_PATH")
        
        return len(missing) == 0, missing
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Args:
            force_refresh: Force token refresh even if current token is valid
            
        Returns:
            Valid access token string
            
        Raises:
            ValueError: If configuration is invalid
            ApiException: If token request fails
        """
        if not DOCUSIGN_AVAILABLE:
            raise ImportError("docusign_esign package not installed. Run: pip install docusign-esign")
        
        # Check if we have a valid cached token
        if not force_refresh and self._access_token and self._token_expiry:
            if datetime.now() < self._token_expiry - timedelta(minutes=5):
                return self._access_token
        
        # Validate configuration
        is_valid, missing = self.validate()
        if not is_valid:
            raise ValueError(f"Missing DocuSign configuration: {', '.join(missing)}")
        
        # Request new token
        api_client = ApiClient()
        api_client.set_base_path(self.auth_server)
        
        # JWT scopes
        scopes = ["signature", "impersonation"]
        
        try:
            token_response = api_client.request_jwt_user_token(
                client_id=self.integration_key,
                user_id=self.user_id,
                oauth_host_name=self.auth_server,
                private_key_bytes=self.private_key.encode(),
                expires_in=3600,  # 1 hour
                scopes=scopes
            )
            
            self._access_token = token_response.access_token
            self._token_expiry = datetime.now() + timedelta(seconds=int(token_response.expires_in))
            
            return self._access_token
            
        except ApiException as e:
            if "consent_required" in str(e):
                consent_url = self._get_consent_url()
                raise ValueError(
                    f"User consent required. Please visit this URL and grant access:\n{consent_url}"
                )
            raise
    
    def _get_consent_url(self) -> str:
        """Generate the consent URL for granting JWT permission."""
        return (
            f"https://{self.auth_server}/oauth/auth?"
            f"response_type=code&"
            f"scope=signature%20impersonation&"
            f"client_id={self.integration_key}&"
            f"redirect_uri=https://localhost/callback"
        )
    
    def get_api_client(self) -> "ApiClient":
        """
        Get an authenticated API client.
        
        Returns:
            Configured ApiClient instance
        """
        if not DOCUSIGN_AVAILABLE:
            raise ImportError("docusign_esign package not installed. Run: pip install docusign-esign")
        
        access_token = self.get_access_token()
        
        api_client = ApiClient()
        api_client.host = self.api_base
        api_client.set_default_header("Authorization", f"Bearer {access_token}")
        
        return api_client
    
    def to_dict(self) -> dict:
        """Return configuration as dictionary (without sensitive data)."""
        return {
            "integration_key": self.integration_key,
            "user_id": self.user_id[:8] + "..." if self.user_id else None,
            "account_id": self.account_id[:8] + "..." if self.account_id else None,
            "private_key_configured": bool(self.private_key),
            "use_production": self.use_production,
            "api_base": self.api_base,
            "token_valid": bool(self._access_token and self._token_expiry and datetime.now() < self._token_expiry)
        }


# Singleton instance for reuse
_config_instance: Optional[DocuSignConfig] = None


def get_config(use_production: bool = False) -> DocuSignConfig:
    """Get or create the DocuSign configuration singleton."""
    global _config_instance
    if _config_instance is None or _config_instance.use_production != use_production:
        _config_instance = DocuSignConfig(use_production=use_production)
    return _config_instance


if __name__ == "__main__":
    # Test configuration
    config = get_config()
    is_valid, missing = config.validate()
    
    print("DocuSign Configuration Status:")
    print(json.dumps(config.to_dict(), indent=2))
    
    if not is_valid:
        print(f"\n⚠️  Missing: {', '.join(missing)}")
        print("\nTo configure, set these environment variables:")
        for item in missing:
            print(f"  export {item}=<value>")
    else:
        print("\n✅ Configuration complete!")
        
        # Try to get token
        try:
            token = config.get_access_token()
            print(f"✅ Successfully obtained access token")
        except Exception as e:
            print(f"❌ Token error: {e}")

