"""
Configuration Management

Handles loading, saving, and managing application configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigStore:
    """Manages application configuration and settings."""
    
    def __init__(self, config_file: str = "config/settings.json"):
        """Initialize configuration store."""
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
                self.create_default_config()
        else:
            self.create_default_config()
    
    def create_default_config(self) -> None:
        """Create default configuration."""
        self.config = {
            "api": {
                "base_url": "https://gateway-api-demo.s2f.projectx.com",
                "user_hub": "https://gateway-rtc-demo.s2f.projectx.com/hubs/user",
                "market_hub": "https://gateway-rtc-demo.s2f.projectx.com/hubs/market",
                "timeout": 30,
                "max_retries": 3
            },
            "auth": {
                "userName": "",  # Changed to match API field name
                "api_key": "",
                "token": "",
                "token_expiry": ""
            },
            "logging": {
                "level": "INFO",
                "file": "logs/risk_manager.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "risk": {
                "max_daily_loss": 1000.0,
                "daily_profit_target": 2000.0,
                "max_daily_trades": 10,
                "max_daily_volume": 100000.0,
                "max_position_size": 10,
                "max_open_positions": 5,
                "max_risk_per_trade": 500.0,
                "auto_flatten": True,
                "stop_on_loss": True,
                "stop_on_profit": True,
                "end_of_day_flatten": True,
                "session_timeout": 30
            },
            "trading_hours": {
                "start": "09:30",
                "end": "16:00",
                "timezone": "America/New_York",
                "pre_market_start": "04:00",
                "pre_market_end": "09:30",
                "after_hours_start": "16:00",
                "after_hours_end": "20:00",
                "enable_pre_market": False,
                "enable_after_hours": False,
                "allow_regular": True,
                "allow_pre_market": False,
                "allow_after_hours": False
            }
        }
        self.save_config()
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        self.save_config()
    
    def update_auth(self, username: str, api_key: str) -> None:
        """Update authentication credentials."""
        self.set("auth.userName", username)  # Changed to match API field name
        self.set("auth.api_key", api_key)
    
    def get_api_url(self) -> str:
        """Get the API base URL."""
        return self.get("api.base_url", "https://gateway-api-demo.s2f.projectx.com")
    
    def get_user_hub_url(self) -> str:
        """Get the WebSocket user hub URL."""
        return self.get("api.user_hub", "https://gateway-rtc-demo.s2f.projectx.com/hubs/user")
    
    def get_market_hub_url(self) -> str:
        """Get the WebSocket market hub URL."""
        return self.get("api.market_hub", "https://gateway-rtc-demo.s2f.projectx.com/hubs/market")

if __name__ == "__main__":
    print("Testing ConfigStore...")
    config = ConfigStore()
    print("✅ ConfigStore created successfully!")
    api_url = config.get("api.base_url")
    print(f"✅ API URL: {api_url}")
