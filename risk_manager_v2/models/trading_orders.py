"""
Trading Orders Data Model

Handles order information and management.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from .trading_base import BaseTradingData, OrderSide, OrderType, OrderStatus

@dataclass
class Order(BaseTradingData):
    """Order information."""
    order_id: str
    account_id: str
    contract_id: str
    symbol_id: str
    status: OrderStatus
    order_type: OrderType
    side: OrderSide
    size: int
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    trail_price: Optional[float] = None
    fill_volume: int = 0
    filled_price: Optional[float] = None
    custom_tag: Optional[str] = None
    linked_order_id: Optional[str] = None
    creation_timestamp: datetime = None
    update_timestamp: datetime = None
    
    def __post_init__(self):
        """Initialize with defaults if not provided."""
        if self.creation_timestamp is None:
            self.creation_timestamp = datetime.now()
        if self.update_timestamp is None:
            self.update_timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "order_id": self.order_id,
            "account_id": self.account_id,
            "contract_id": self.contract_id,
            "symbol_id": self.symbol_id,
            "status": self.status.value,
            "order_type": self.order_type.value,
            "side": self.side.value,
            "size": self.size,
            "limit_price": self.limit_price,
            "stop_price": self.stop_price,
            "trail_price": self.trail_price,
            "fill_volume": self.fill_volume,
            "filled_price": self.filled_price,
            "custom_tag": self.custom_tag,
            "linked_order_id": self.linked_order_id,
            "creation_timestamp": self.creation_timestamp.isoformat(),
            "update_timestamp": self.update_timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        """Create from dictionary."""
        return cls(
            order_id=data["order_id"],
            account_id=data["account_id"],
            contract_id=data["contract_id"],
            symbol_id=data["symbol_id"],
            status=OrderStatus(data.get("status", 0)),
            order_type=OrderType(data.get("order_type", 0)),
            side=OrderSide(data.get("side", 0)),
            size=data.get("size", 0),
            limit_price=data.get("limit_price"),
            stop_price=data.get("stop_price"),
            trail_price=data.get("trail_price"),
            fill_volume=data.get("fill_volume", 0),
            filled_price=data.get("filled_price"),
            custom_tag=data.get("custom_tag"),
            linked_order_id=data.get("linked_order_id"),
            creation_timestamp=datetime.fromisoformat(data.get("creation_timestamp", datetime.now().isoformat())),
            update_timestamp=datetime.fromisoformat(data.get("update_timestamp", datetime.now().isoformat()))
        )
    
    def validate(self) -> bool:
        """Validate order data."""
        if not self.order_id or not self.account_id or not self.contract_id:
            raise ValueError("Order ID, Account ID, and Contract ID are required")
        
        if self.size <= 0:
            raise ValueError("Order size must be positive")
        
        if self.order_type == OrderType.LIMIT and self.limit_price is None:
            raise ValueError("Limit orders must have a limit price")
        
        if self.order_type == OrderType.STOP and self.stop_price is None:
            raise ValueError("Stop orders must have a stop price")
        
        return True
    
    def is_pending(self) -> bool:
        """Check if order is pending."""
        return self.status in [OrderStatus.OPEN, OrderStatus.PENDING]
    
    def is_filled(self) -> bool:
        """Check if order is filled."""
        return self.status == OrderStatus.FILLED
    
    def is_cancelled(self) -> bool:
        """Check if order is cancelled."""
        return self.status == OrderStatus.CANCELLED
    
    def is_rejected(self) -> bool:
        """Check if order is rejected."""
        return self.status == OrderStatus.REJECTED
    
    def get_remaining_size(self) -> int:
        """Get remaining unfilled size."""
        return max(0, self.size - self.fill_volume)
    
    def is_fully_filled(self) -> bool:
        """Check if order is fully filled."""
        return self.fill_volume >= self.size
    
    def get_fill_percentage(self) -> float:
        """Get fill percentage."""
        if self.size > 0:
            return (self.fill_volume / self.size) * 100
        return 0.0
    
    def update_status(self, new_status: OrderStatus):
        """Update order status."""
        self.status = new_status
        self.update_timestamp = datetime.now()
    
    def update_fill(self, fill_volume: int, fill_price: float):
        """Update order fill information."""
        self.fill_volume += fill_volume
        self.filled_price = fill_price
        self.update_timestamp = datetime.now()
        
        if self.is_fully_filled():
            self.status = OrderStatus.FILLED
    
    def get_order_info(self) -> Dict[str, Any]:
        """Get comprehensive order information."""
        return {
            "order_id": self.order_id,
            "account_id": self.account_id,
            "contract_id": self.contract_id,
            "symbol_id": self.symbol_id,
            "status": self.status.name,
            "order_type": self.order_type.name,
            "side": self.side.name,
            "size": self.size,
            "remaining_size": self.get_remaining_size(),
            "fill_percentage": self.get_fill_percentage(),
            "limit_price": self.limit_price,
            "stop_price": self.stop_price,
            "trail_price": self.trail_price,
            "fill_volume": self.fill_volume,
            "filled_price": self.filled_price,
            "custom_tag": self.custom_tag,
            "linked_order_id": self.linked_order_id,
            "creation_timestamp": self.creation_timestamp.isoformat(),
            "update_timestamp": self.update_timestamp.isoformat(),
            "is_pending": self.is_pending(),
            "is_filled": self.is_filled(),
            "is_cancelled": self.is_cancelled(),
            "is_rejected": self.is_rejected(),
            "is_fully_filled": self.is_fully_filled()
        }

if __name__ == "__main__":
    print("Testing Order model...")
    
    # Test order creation
    order = Order(
        order_id="12345",
        account_id="67890",
        contract_id="CON.F.US.EP.U25",
        symbol_id="F.US.EP",
        status=OrderStatus.OPEN,
        order_type=OrderType.MARKET,
        side=OrderSide.BID,
        size=1
    )
    print("âœ… Order created successfully!")
    
    # Test validation
    try:
        order.validate()
        print("âœ… Order validation passed!")
    except ValueError as e:
        print(f"âŒ Order validation failed: {e}")
    
    # Test order info
    info = order.get_order_info()
    print(f"âœ… Order info: {info}")
    
    print("âœ… Order model test completed!")

