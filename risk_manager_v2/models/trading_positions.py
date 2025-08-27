"""
Trading Positions Data Model

Handles position information and management.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from .trading_base import BaseTradingData, PositionSide

@dataclass
class Position(BaseTradingData):
    """Position information."""
    position_id: str
    account_id: str
    contract_id: str
    side: PositionSide
    size: int
    average_price: float
    creation_timestamp: datetime = None
    last_updated: datetime = None
    
    def __post_init__(self):
        """Initialize with defaults if not provided."""
        if self.creation_timestamp is None:
            self.creation_timestamp = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "position_id": self.position_id,
            "account_id": self.account_id,
            "contract_id": self.contract_id,
            "side": self.side.value,
            "size": self.size,
            "average_price": self.average_price,
            "creation_timestamp": self.creation_timestamp.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Position':
        """Create from dictionary."""
        return cls(
            position_id=data["position_id"],
            account_id=data["account_id"],
            contract_id=data["contract_id"],
            side=PositionSide(data.get("side", 0)),
            size=data.get("size", 0),
            average_price=data.get("average_price", 0.0),
            creation_timestamp=datetime.fromisoformat(data.get("creation_timestamp", datetime.now().isoformat())),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        )
    
    def validate(self) -> bool:
        """Validate position data."""
        if not self.position_id or not self.account_id or not self.contract_id:
            raise ValueError("Position ID, Account ID, and Contract ID are required")
        
        if self.size < 0:
            raise ValueError("Position size cannot be negative")
        
        if self.average_price < 0:
            raise ValueError("Average price cannot be negative")
        
        return True
    
    def is_long(self) -> bool:
        """Check if position is long."""
        return self.side == PositionSide.LONG and self.size > 0
    
    def is_short(self) -> bool:
        """Check if position is short."""
        return self.side == PositionSide.SHORT and self.size > 0
    
    def is_flat(self) -> bool:
        """Check if position is flat (no position)."""
        return self.size == 0
    
    def get_position_value(self, current_price: float) -> float:
        """Get current position value."""
        return self.size * current_price
    
    def get_unrealized_pnl(self, current_price: float) -> float:
        """Get unrealized P&L."""
        if self.is_long():
            return (current_price - self.average_price) * self.size
        elif self.is_short():
            return (self.average_price - current_price) * self.size
        return 0.0
    
    def get_position_info(self) -> Dict[str, Any]:
        """Get comprehensive position information."""
        return {
            "position_id": self.position_id,
            "account_id": self.account_id,
            "contract_id": self.contract_id,
            "side": self.side.name,
            "size": self.size,
            "average_price": self.average_price,
            "creation_timestamp": self.creation_timestamp.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "is_long": self.is_long(),
            "is_short": self.is_short(),
            "is_flat": self.is_flat()
        }

if __name__ == "__main__":
    print("Testing Position model...")
    
    # Test position creation
    position = Position(
        position_id="12345",
        account_id="67890",
        contract_id="CON.F.US.EP.U25",
        side=PositionSide.LONG,
        size=1,
        average_price=2100.0
    )
    print("✅ Position created successfully!")
    
    # Test validation
    try:
        position.validate()
        print("✅ Position validation passed!")
    except ValueError as e:
        print(f"❌ Position validation failed: {e}")
    
    # Test position info
    info = position.get_position_info()
    print(f"✅ Position info: {info}")
    
    # Test P&L calculation
    current_price = 2105.0
    pnl = position.get_unrealized_pnl(current_price)
    print(f"✅ Unrealized P&L at ${current_price}: ${pnl}")
    
    print("✅ Position model test completed!")
