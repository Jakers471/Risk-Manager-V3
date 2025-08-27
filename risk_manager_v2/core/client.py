"""
TopStepX API Client

Handles all API communication with the TopStepX Gateway.
"""

import requests
import time
from typing import Dict, List, Optional
from .config import ConfigStore
from .auth import AuthManager
from .logger import get_logger
from risk_manager_v2.utils.rate_limiter import TopStepXRateLimiter

class ProjectXError(Exception):
    """Custom exception for ProjectX API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class ProjectXClient:
    """TopStepX API client with rate limiting and error handling."""
    
    def __init__(self, config: ConfigStore, auth: AuthManager):
        self.config = config
        self.auth = auth
        self.logger = get_logger(__name__)
        self.base_url = config.get_api_url()
        self.max_retries = config.get("api.max_retries", 3)
        self.timeout = config.get("api.timeout", 30)
        self.ratelimiter = TopStepXRateLimiter()
    
    def _make_request(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request with retry logic and error handling."""
        url = f"{self.base_url}{endpoint}"
        
        # Apply rate limiting based on endpoint
        bucket = "bars" if endpoint == "/api/History/retrieveBars" else "general"
        self.ratelimiter.consume(bucket)
        
        for attempt in range(self.max_retries + 1):
            try:
                session = self.auth.get_session()
                response = session.post(url, json=data, timeout=self.timeout)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    self.logger.warning("401 Unauthorized. Validating token...")
                    if self.auth.validate_token():
                        continue
                    self.logger.warning("Validate failed. Re-authenticating via API key...")
                    if self.auth.refresh_token():
                        continue
                    self.logger.error("Auth recovery failed")
                    raise ProjectXError("Authentication failed after retry attempts", 401)
                elif response.status_code == 429:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                elif response.status_code >= 500:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Server error {response.status_code}, retrying in {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    error_msg = f"API request failed: {response.status_code} - {response.text}"
                    self.logger.error(error_msg)
                    raise ProjectXError(error_msg, response.status_code, response.json() if response.text else None)
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise ProjectXError("Request timed out after all retries")
            except ProjectXError:
                raise
            except Exception as e:
                self.logger.error(f"Request error: {e}")
                raise ProjectXError(f"Request failed: {e}")
        
        raise ProjectXError("Request failed after all retry attempts")
    
    # Account Management
    def get_accounts(self, only_active: bool = True) -> List[Dict]:
        """Get list of trading accounts."""
        data = {"onlyActiveAccounts": only_active}
        response = self._make_request("/api/Account/search", data=data)
        if response and response.get("success"):
            return response.get("accounts", [])
        return []
    
    # Position Management
    def get_open_positions(self, account_id: str) -> List[Dict]:
        """Get open positions for account."""
        data = {"accountId": int(account_id)}
        response = self._make_request("/api/Position/search", data=data)
        if response and response.get("success"):
            return response.get("positions", [])
        return []
    
    def close_position(self, account_id: str, contract_id: str) -> Dict:
        """Close a specific position."""
        data = {"accountId": int(account_id), "contractId": contract_id}
        return self._make_request("/api/Position/closeContract", data=data)
    
    # Order Management
    def get_open_orders(self, account_id: str) -> List[Dict]:
        """Get pending orders for account."""
        data = {"accountId": int(account_id)}
        response = self._make_request("/api/Order/searchOpen", data=data)
        if response and response.get("success"):
            return response.get("orders", [])
        return []
    
    def place_order(self, account_id: str, contract_id: str, order_type: int, side: int, size: int,
                   limit_price: Optional[float] = None, stop_price: Optional[float] = None,
                   trail_price: Optional[float] = None, custom_tag: Optional[str] = None,
                   linked_order_id: Optional[int] = None) -> Dict:
        """Place a new order with proper parameters."""
        data = {
            "accountId": int(account_id), "contractId": contract_id, "type": order_type,
            "side": side, "size": size, "limitPrice": limit_price, "stopPrice": stop_price,
            "trailPrice": trail_price, "customTag": custom_tag, "linkedOrderId": linked_order_id
        }
        return self._make_request("/api/Order/place", data=data)
    
    def cancel_order(self, account_id: str, order_id: str) -> Dict:
        """Cancel a specific order."""
        data = {"accountId": int(account_id), "orderId": int(order_id)}
        return self._make_request("/api/Order/cancel", data=data)
    
    def get_trades(self, account_id: str, start_timestamp: str = None, end_timestamp: str = None) -> List[Dict]:
        """Get trade history for account."""
        data = {"accountId": int(account_id)}
        if start_timestamp:
            data["startTimestamp"] = start_timestamp
        if end_timestamp:
            data["endTimestamp"] = end_timestamp
        
        response = self._make_request("/api/Trade/search", data=data)
        if response and response.get("success"):
            return response.get("trades", [])
        return []
    
    # Market Data
    def get_market_data_bars(self, contract_id: str, start_time: str, end_time: str,
                            unit: int = 2, unit_number: int = 1, live: bool = False,
                            limit: Optional[int] = None, include_partial_bar: bool = False) -> List[Dict]:
        """Get market data bars for contract."""
        data = {
            "contractId": contract_id, "live": live, "startTime": start_time, "endTime": end_time,
            "unit": unit, "unitNumber": unit_number, "includePartialBar": include_partial_bar
        }
        if limit is not None:
            data["limit"] = int(limit)
        
        response = self._make_request("/api/History/retrieveBars", data=data)
        if response and response.get("success"):
            return response.get("bars", [])
        return []
    
    # System Status
    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            result = self.get_accounts()
            return len(result) >= 0
        except ProjectXError:
            return False
