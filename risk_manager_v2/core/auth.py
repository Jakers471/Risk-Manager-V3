"""
Authentication Management

Handles TopStepX API authentication and token management.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from .config import ConfigStore
from .logger import get_logger

class AuthManager:
    """Manages TopStepX API authentication."""
    
    def __init__(self, config: ConfigStore):
        self.config = config
        self.logger = get_logger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.logger.info(f"Session headers: {dict(self.session.headers)}")
    
    def authenticate(self, username: str, api_key: str) -> bool:
        """Authenticate with TopStepX API."""
        try:
            self.logger.info(f"Authenticating user: {username}")
            self.logger.info(f"API URL: {self.config.get_api_url()}")
            
            # Prepare authentication payload
            auth_data = {
                "userName": username,
                "apiKey": api_key
            }
            self.logger.info(f"Auth payload: {auth_data}")
            
            # Make authentication request
            url = f"{self.config.get_api_url()}/api/Auth/loginKey"
            self.logger.info(f"Making POST request to: {url}")
            
            response = self.session.post(
                url,
                json=auth_data,
                timeout=self.config.get("api.timeout", 30)
            )
            
            self.logger.info(f"Response status: {response.status_code}")
            self.logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"Authentication response: {data}")
                
                # Check for success field
                if data.get("success"):
                    token = data.get("token")
                    
                    if token:
                        # Calculate token expiry (24 hours from now)
                        expiry = datetime.now() + timedelta(hours=24)
                        
                        # Save credentials and token
                        self.config.update_auth(username, api_key)
                        self.config.set("auth.token", token)
                        self.config.set("auth.token_expiry", expiry.isoformat())
                        
                        # Update session headers
                        self.session.headers.update({
                            'Authorization': f'Bearer {token}'
                        })
                        
                        self.logger.info("Authentication successful")
                        return True
                    else:
                        self.logger.error("No token received in response")
                        return False
                else:
                    error_msg = data.get("errorMessage", "Unknown error")
                    self.logger.error(f"Authentication failed: {error_msg}")
                    return False
            else:
                self.logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Authentication request failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        token = self.config.get("auth.token")
        token_expiry = self.config.get("auth.token_expiry")
        
        if not token or not token_expiry:
            return False
        
        try:
            expiry = datetime.fromisoformat(token_expiry)
            if datetime.now() >= expiry:
                self.logger.info("Token expired")
                return False
            
            # Update session headers
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
            
            return True
        except Exception as e:
            self.logger.error(f"Error checking authentication: {e}")
            return False
    
    def refresh_token(self) -> bool:
        """Refresh authentication token."""
        username = self.config.get("auth.userName")  # Updated field name
        api_key = self.config.get("auth.api_key")
        
        if not username or not api_key:
            self.logger.error("No credentials available for token refresh")
            return False
        
        return self.authenticate(username, api_key)
    
    def logout(self) -> None:
        """Clear authentication data."""
        self.config.set("auth.token", "")
        self.config.set("auth.token_expiry", "")
        self.session.headers.pop('Authorization', None)
        self.logger.info("Logged out")
    
    def get_session(self) -> requests.Session:
        """Get authenticated session."""
        if not self.is_authenticated():
            if not self.refresh_token():
                raise Exception("Not authenticated and refresh failed")
        
        return self.session
    
    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            if not self.is_authenticated():
                return False
            
            # Try to validate session
            response = self.session.post(
                f"{self.config.get_api_url()}/api/Auth/validate",
                timeout=self.config.get("api.timeout", 30)
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Update token if a new one is provided
                    new_token = data.get("newToken")
                    if new_token:
                        self.config.set("auth.token", new_token)
                        self.session.headers.update({
                            'Authorization': f'Bearer {new_token}'
                        })
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

if __name__ == "__main__":
    print("Testing AuthManager...")
    
    # Test basic initialization
    from core.config import ConfigStore
    config = ConfigStore()
    auth = AuthManager(config)
    print("✅ AuthManager created successfully!")
    
    # Test authentication check (should be False initially)
    is_auth = auth.is_authenticated()
    print(f"✅ Authentication status: {is_auth}")
    
    print("✅ AuthManager test completed!")
