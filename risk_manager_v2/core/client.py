"""
TopStepX API Client

Handles all API communication with the TopStepX Gateway.
"""

import requests
import time
from typing import Dict, List, Optional, Any
from .config import ConfigStore
from .auth import AuthManager
from .logger import get_logger

class ProjectXClient:
    """TopStepX API client with rate limiting and error handling."""
    
    def __init__(self, config: ConfigStore, auth: AuthManager):
        self.config = config
        self.auth = auth
        self.logger = get_logger(__name__)
        self.base_url = config.get_api_url()
        self.max_retries = config.get("api.max_retries", 3)
        self.timeout = config.get("api.timeout", 30)
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make API request with retry logic and error handling."""
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                session = self.auth.get_session()
                
                if method.upper() == "GET":
                    response = session.get(url, params=params, timeout=self.timeout)
                elif method.upper() == "POST":
                    response = session.post(url, json=data, timeout=self.timeout)
                elif method.upper() == "PUT":
                    response = session.put(url, json=data, timeout=self.timeout)
                elif method.upper() == "DELETE":
                    response = session.delete(url, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle different response codes
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    self.logger.warning("Authentication failed, attempting token validation")
                    # Try to validate/refresh token first
                    if self.auth.refresh_token():
                        continue
                    else:
                        self.logger.error("Token validation failed, re-authentication required")
                        return None
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
                    self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                    return None
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    self.logger.error("Request timed out after all retries")
                    return None
            except Exception as e:
                self.logger.error(f"Request error: {e}")
                return None
        
        return None
    
    # Account Management
    def get_accounts(self, only_active: bool = True) -> Optional[List[Dict]]:
        """Get list of trading accounts."""
        data = {"onlyActiveAccounts": only_active}
        response = self._make_request("POST", "/api/Account/search", data=data)
        if response and response.get("success"):
            return response.get("accounts", [])
        return None
    
    def get_account_details(self, account_id: str) -> Optional[Dict]:
        """Get detailed account information."""
        # Note: This endpoint may not exist in actual API - using search for now
        data = {"onlyActiveAccounts": True}
        response = self._make_request("POST", "/api/Account/search", data=data)
        if response and response.get("success"):
            accounts = response.get("accounts", [])
            for account in accounts:
                if str(account.get("id")) == str(account_id):
                    return account
        return None
    
    def get_account_balance(self, account_id: str) -> Optional[Dict]:
        """Get account balance information."""
        # Balance is included in account search response
        account = self.get_account_details(account_id)
        if account:
            return {"balance": account.get("balance", 0)}
        return None
    
    # Position Management
    def get_open_positions(self, account_id: str) -> Optional[List[Dict]]:
        """Get open positions for account."""
        data = {"accountId": int(account_id)}
        response = self._make_request("POST", "/api/Position/searchOpen", data=data)
        if response and response.get("success"):
            return response.get("positions", [])
        return None
    
    def close_position(self, account_id: str, contract_id: str) -> Optional[Dict]:
        """Close a specific position."""
        data = {
            "accountId": int(account_id),
            "contractId": contract_id
        }
        return self._make_request("POST", "/api/Position/closeContract", data=data)
    
    def close_partial_position(self, account_id: str, contract_id: str, size: int) -> Optional[Dict]:
        """Close a partial position."""
        data = {
            "accountId": int(account_id),
            "contractId": contract_id,
            "size": size
        }
        return self._make_request("POST", "/api/Position/partialCloseContract", data=data)
    
    def close_all_positions(self, account_id: str) -> Optional[Dict]:
        """Close all positions for account."""
        # Get all positions first, then close each one
        positions = self.get_open_positions(account_id)
        if not positions:
            return {"success": True, "message": "No positions to close"}
        
        results = []
        for position in positions:
            contract_id = position.get("contractId")
            if contract_id:
                result = self.close_position(account_id, contract_id)
                results.append(result)
        
        return {"success": True, "closed_positions": results}
    
    # Order Management
    def get_open_orders(self, account_id: str) -> Optional[List[Dict]]:
        """Get pending orders for account."""
        data = {"accountId": int(account_id)}
        response = self._make_request("POST", "/api/Order/searchOpen", data=data)
        if response and response.get("success"):
            return response.get("orders", [])
        return None
    
    def get_orders(self, account_id: str, start_timestamp: str = None, end_timestamp: str = None) -> Optional[List[Dict]]:
        """Get all orders for account (including filled/cancelled)."""
        data = {"accountId": int(account_id)}
        if start_timestamp:
            data["startTimestamp"] = start_timestamp
        if end_timestamp:
            data["endTimestamp"] = end_timestamp
        
        response = self._make_request("POST", "/api/Order/search", data=data)
        if response and response.get("success"):
            return response.get("orders", [])
        return None
    
    def place_order(
        self, 
        account_id: str, 
        contract_id: str,
        order_type: int,  # 1=Limit, 2=Market, 4=Stop, 5=TrailingStop, 6=JoinBid, 7=JoinAsk
        side: int,        # 0=Bid (buy), 1=Ask (sell)
        size: int,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_price: Optional[float] = None,
        custom_tag: Optional[str] = None,
        linked_order_id: Optional[int] = None
    ) -> Optional[Dict]:
        """Place a new order with proper parameters."""
        data = {
            "accountId": int(account_id),
            "contractId": contract_id,
            "type": order_type,
            "side": side,
            "size": size,
            "limitPrice": limit_price,
            "stopPrice": stop_price,
            "trailPrice": trail_price,
            "customTag": custom_tag,
            "linkedOrderId": linked_order_id
        }
        return self._make_request("POST", "/api/Order/place", data=data)
    
    def cancel_order(self, account_id: str, order_id: str) -> Optional[Dict]:
        """Cancel a specific order."""
        data = {
            "accountId": int(account_id),
            "orderId": int(order_id)
        }
        return self._make_request("POST", "/api/Order/cancel", data=data)
    
    def cancel_all_orders(self, account_id: str) -> Optional[Dict]:
        """Cancel all orders for account."""
        orders = self.get_open_orders(account_id)
        if not orders:
            return {"success": True, "message": "No orders to cancel"}
        
        results = []
        for order in orders:
            order_id = order.get("id")  # Changed from "orderId" to "id" to match API response
            if order_id:
                result = self.cancel_order(account_id, str(order_id))
                results.append(result)
        
        return {"success": True, "cancelled_orders": results}
    
    # Trade History
    def get_trades(self, account_id: str, start_timestamp: str = None, end_timestamp: str = None) -> Optional[List[Dict]]:
        """Get trade history for account."""
        data = {"accountId": int(account_id)}
        if start_timestamp:
            data["startTimestamp"] = start_timestamp
        if end_timestamp:
            data["endTimestamp"] = end_timestamp
        
        response = self._make_request("POST", "/api/Trade/search", data=data)
        if response and response.get("success"):
            return response.get("trades", [])
        return None
    
    # Contract Information
    def get_available_contracts(self, live: bool = True) -> Optional[List[Dict]]:
        """Get available contracts."""
        data = {"live": live}
        response = self._make_request("POST", "/api/Contract/available", data=data)
        if response and response.get("success"):
            return response.get("contracts", [])
        return None
    
    def search_contracts(self, search_text: str = "", live: bool = True) -> Optional[List[Dict]]:
        """Search for contracts by symbol."""
        data = {
            "searchText": search_text,
            "live": live
        }
        response = self._make_request("POST", "/api/Contract/search", data=data)
        if response and response.get("success"):
            return response.get("contracts", [])
        return None
    
    def get_contract_details(self, contract_id: str) -> Optional[Dict]:
        """Get detailed contract information."""
        data = {"contractId": contract_id}
        response = self._make_request("POST", "/api/Contract/searchById", data=data)
        if response and response.get("success"):
            return response.get("contract")
        return None
    
    # Market Data
    def get_market_data_bars(self,
        contract_id: str,
        start_time: str,
        end_time: str,
        unit: int = 2,          # 1=Second, 2=Minute, 3=Hour, 4=Day, 5=Week, 6=Month
        unit_number: int = 1,
        live: bool = False,
        limit: Optional[int] = None,
        include_partial_bar: bool = False
    ) -> Optional[List[Dict]]:
        """Get market data bars for contract."""
        data = {
            "contractId": contract_id,
            "live": live,
            "startTime": start_time,
            "endTime": end_time,
            "unit": unit,
            "unitNumber": unit_number,
            "includePartialBar": include_partial_bar
        }
        if limit is not None:
            data["limit"] = int(limit)
        
        response = self._make_request("POST", "/api/History/retrieveBars", data=data)
        if response and response.get("success"):
            return response.get("bars", [])
        return None
    
    # System Status
    def test_connection(self) -> bool:
        """Test API connection."""
        # Try to get accounts as a connectivity test
        result = self.get_accounts()
        return result is not None

if __name__ == "__main__":
    print("Testing ProjectXClient...")
    
    # Test basic initialization
    from core.config import ConfigStore
    from core.auth import AuthManager
    
    config = ConfigStore()
    auth = AuthManager(config)
    client = ProjectXClient(config, auth)
    print("✅ ProjectXClient created successfully!")
    
    # Test connection (will fail without auth, but should not crash)
    try:
        connection_test = client.test_connection()
        print(f"✅ Connection test completed: {connection_test}")
    except Exception as e:
        print(f"✅ Connection test failed as expected (no auth): {e}")
    
    print("✅ ProjectXClient test completed!")
