"""
ProjectX Client Implementation

Handles REST API communication with ProjectX trading platform.
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from risk_manager_v2.models.trading_positions import Position
from risk_manager_v2.models.trading_orders import Order
from risk_manager_v2.models.trading_base import PositionSide, OrderSide, OrderType, OrderStatus
from risk_manager_v2.utils.rate_limiter import TopStepXRateLimiter, topstepx_rate_limited, exponential_backoff
from risk_manager_v2.core.logger import get_logger

logger = get_logger(__name__)

class ProjectXClient:
    """ProjectX REST API client with rate limiting and mock data support."""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize ProjectX client."""
        self.base_url = base_url or os.getenv("PROJECTX_BASE_URL", "https://gateway-api-demo.s2f.projectx.com")
        self.api_key = api_key or os.getenv("PROJECTX_API_KEY", "")
        self.rate_limiter = TopStepXRateLimiter()
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Add auth header if API key provided
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     use_read_bucket: bool = True) -> Dict[str, Any]:
        """Make HTTP request with rate limiting."""
        url = f"{self.base_url}{endpoint}"
        
        # Acquire rate limit token
        if use_read_bucket:
            if not self.rate_limiter.acquire_general(timeout=10.0):
                raise Exception("Rate limit exceeded for read operations")
        else:
            if not self.rate_limiter.acquire_emergency(timeout=10.0):
                raise Exception("Rate limit exceeded for trade operations")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def simulator(self) -> bool:
        """Check if simulator mode is enabled."""
        return os.getenv("PX_SIM", "0") == "1"
    
    def _get_mock_positions(self, account_id: str) -> List[Dict[str, Any]]:
        """Generate deterministic mock positions."""
        return [
            {
                "positionId": "pos_001",
                "accountId": account_id,
                "contractId": "ESZ24",
                "side": "LONG",
                "size": 2,
                "averagePrice": 4500.50,
                "creationTimestamp": "2024-01-15T09:30:00Z",
                "lastUpdated": "2024-01-15T14:30:00Z"
            },
            {
                "positionId": "pos_002", 
                "accountId": account_id,
                "contractId": "NQZ24",
                "side": "SHORT",
                "size": 1,
                "averagePrice": 16500.25,
                "creationTimestamp": "2024-01-15T10:15:00Z",
                "lastUpdated": "2024-01-15T14:30:00Z"
            }
        ]
    
    def _get_mock_orders(self, account_id: str) -> List[Dict[str, Any]]:
        """Generate deterministic mock orders."""
        return [
            {
                "orderId": "ord_001",
                "accountId": account_id,
                "contractId": "ESZ24",
                "symbolId": "ES",
                "status": "OPEN",
                "orderType": "LIMIT",
                "side": "BUY",
                "size": 1,
                "limitPrice": 4501.00,
                "fillVolume": 0,
                "creationTimestamp": "2024-01-15T14:25:00Z",
                "updateTimestamp": "2024-01-15T14:25:00Z"
            },
            {
                "orderId": "ord_002",
                "accountId": account_id,
                "contractId": "NQZ24", 
                "symbolId": "NQ",
                "status": "FILLED",
                "orderType": "MARKET",
                "side": "SELL",
                "size": 1,
                "fillVolume": 1,
                "filledPrice": 16500.25,
                "creationTimestamp": "2024-01-15T10:15:00Z",
                "updateTimestamp": "2024-01-15T10:15:05Z"
            }
        ]
    
    def _map_position_payload(self, payload: Dict[str, Any]) -> Position:
        """Map API payload to Position dataclass."""
        return Position(
            position_id=payload["positionId"],
            account_id=payload["accountId"],
            contract_id=payload["contractId"],
            side=PositionSide.LONG if payload["side"] == "LONG" else PositionSide.SHORT,
            size=payload["size"],
            average_price=payload["averagePrice"],
            creation_timestamp=datetime.fromisoformat(payload["creationTimestamp"].replace("Z", "+00:00")),
            last_updated=datetime.fromisoformat(payload["lastUpdated"].replace("Z", "+00:00"))
        )
    
    def _map_order_payload(self, payload: Dict[str, Any]) -> Order:
        """Map API payload to Order dataclass."""
        status_map = {
            "OPEN": OrderStatus.OPEN,
            "FILLED": OrderStatus.FILLED,
            "CANCELLED": OrderStatus.CANCELLED,
            "REJECTED": OrderStatus.REJECTED
        }
        
        type_map = {
            "MARKET": OrderType.MARKET,
            "LIMIT": OrderType.LIMIT,
            "STOP": OrderType.STOP
        }
        
        side_map = {
            "BUY": OrderSide.BID,
            "SELL": OrderSide.ASK
        }
        
        return Order(
            order_id=payload["orderId"],
            account_id=payload["accountId"],
            contract_id=payload["contractId"],
            symbol_id=payload["symbolId"],
            status=status_map.get(payload["status"], OrderStatus.OPEN),
            order_type=type_map.get(payload["orderType"], OrderType.MARKET),
            side=side_map.get(payload["side"], OrderSide.BUY),
            size=payload["size"],
            limit_price=payload.get("limitPrice"),
            stop_price=payload.get("stopPrice"),
            fill_volume=payload.get("fillVolume", 0),
            filled_price=payload.get("filledPrice"),
            creation_timestamp=datetime.fromisoformat(payload["creationTimestamp"].replace("Z", "+00:00")),
            update_timestamp=datetime.fromisoformat(payload["updateTimestamp"].replace("Z", "+00:00"))
        )
    
    @topstepx_rate_limited(endpoint_type="general")
    @exponential_backoff(max_retries=3, base_delay=1.0)
    def get_positions(self, account_id: str) -> List[Position]:
        """Get positions for account."""
        if self.simulator():
            logger.info("Using mock positions data")
            mock_data = self._get_mock_positions(account_id)
            return [self._map_position_payload(pos) for pos in mock_data]
        
        try:
            response = self._make_request("GET", f"/api/positions/{account_id}", use_read_bucket=True)
            positions = response.get("positions", [])
            return [self._map_position_payload(pos) for pos in positions]
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    @topstepx_rate_limited(endpoint_type="general")
    @exponential_backoff(max_retries=3, base_delay=1.0)
    def get_orders(self, account_id: str) -> List[Order]:
        """Get orders for account."""
        if self.simulator():
            logger.info("Using mock orders data")
            mock_data = self._get_mock_orders(account_id)
            return [self._map_order_payload(order) for order in mock_data]
        
        try:
            response = self._make_request("GET", f"/api/orders/{account_id}", use_read_bucket=True)
            orders = response.get("orders", [])
            return [self._map_order_payload(order) for order in orders]
        except Exception as e:
            logger.error(f"Failed to get orders: {e}")
            return []
    
    @topstepx_rate_limited(endpoint_type="general")
    @exponential_backoff(max_retries=3, base_delay=1.0)
    def get_day_pnl(self, account_id: str) -> float:
        """Get daily P&L for account."""
        if self.simulator():
            logger.info("Using mock P&L data")
            return 1250.75  # Deterministic mock value
        
        try:
            response = self._make_request("GET", f"/api/pnl/{account_id}/daily", use_read_bucket=True)
            return response.get("pnl", 0.0)
        except Exception as e:
            logger.error(f"Failed to get daily P&L: {e}")
            return 0.0
    
    @topstepx_rate_limited(endpoint_type="emergency")
    @exponential_backoff(max_retries=3, base_delay=1.0)
    def cancel_orders(self, account_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Cancel orders for account."""
        if self.simulator():
            logger.info("Using mock cancel response")
            return {"status": "ok", "cancelled": 2, "message": "Orders cancelled successfully"}
        
        try:
            data = {"accountId": account_id}
            if symbol:
                data["symbol"] = symbol
            
            response = self._make_request("POST", "/api/orders/cancel", data=data, use_read_bucket=False)
            return response
        except Exception as e:
            logger.error(f"Failed to cancel orders: {e}")
            return {"status": "error", "message": str(e)}
    
    @topstepx_rate_limited(endpoint_type="emergency")
    @exponential_backoff(max_retries=3, base_delay=1.0)
    def place_market(self, account_id: str, symbol: str, qty: float, side: str) -> Dict[str, Any]:
        """Place market order."""
        if self.simulator():
            logger.info("Using mock order placement response")
            return {
                "status": "ok",
                "orderId": f"mock_ord_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "message": "Market order placed successfully"
            }
        
        try:
            data = {
                "accountId": account_id,
                "symbol": symbol,
                "quantity": qty,
                "side": side.upper(),
                "orderType": "MARKET"
            }
            
            response = self._make_request("POST", "/api/orders/place", data=data, use_read_bucket=False)
            return response
        except Exception as e:
            logger.error(f"Failed to place market order: {e}")
            return {"status": "error", "message": str(e)}
