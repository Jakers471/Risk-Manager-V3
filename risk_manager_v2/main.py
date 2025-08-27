#!/usr/bin/env python3
"""
Risk Manager V2 - Main Entry Point
"""

from risk_manager_v2.core.config import ConfigStore
from risk_manager_v2.core.logger import setup_logging
from risk_manager_v2.core.auth import AuthManager
from risk_manager_v2.core.client import ProjectXClient

def main():
    """Main application entry point."""
    print("Risk Manager V2 starting up...")
    
    # Setup logging
    logger = setup_logging()
    logger.info("Risk Manager V2 starting up...")
    
    # Load configuration
    config = ConfigStore()
    logger.info("Configuration loaded successfully")
    
    # Initialize authentication
    auth = AuthManager(config)
    logger.info("Authentication manager initialized")
    
    # Initialize API client
    client = ProjectXClient(config, auth)
    logger.info("API client initialized")
    
    # Test config
    api_url = config.get("api.base_url")
    logger.info(f"API URL: {api_url}")
    
    # Test authentication status
    is_auth = auth.is_authenticated()
    logger.info(f"Authentication status: {is_auth}")
    
    # Test client connection
    try:
        connection_test = client.test_connection()
        logger.info(f"API connection test: {connection_test}")
    except Exception as e:
        logger.warning(f"API connection test failed (expected without auth): {e}")
    
    print("âœ… Main entry point loaded successfully!")
    logger.info("Main entry point loaded successfully")

if __name__ == "__main__":
    main()

