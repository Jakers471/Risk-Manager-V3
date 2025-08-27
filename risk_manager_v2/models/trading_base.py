"""
Trading Base Data Models

Base classes and enums for trading data structures.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

class OrderSide(Enum):
    """Order side enumeration."""
    BID = 0  # Buy
    ASK = 1  # Sell

class OrderType(Enum):
    """Order type enumeration."""
    UNKNOWN = 0
    LIMIT = 1
    MARKET = 2
    STOP_LIMIT = 3
    STOP = 4
    TRAILING_STOP = 5
    JOIN_BID = 6
    JOIN_ASK = 7

class OrderStatus(Enum):
    """Order status enumeration."""
    NONE = 0
    OPEN = 1
    FILLED = 2
    CANCELLED = 3
    EXPIRED = 4
    REJECTED = 5
    PENDING = 6

class PositionSide(Enum):
    """Position side enumeration."""
    UNDEFINED = 0
    LONG = 1
    SHORT = 2

@dataclass
class BaseTradingData:
    """Base class for all trading data objects."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        raise NotImplementedError("Subclasses must implement to_dict")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        raise NotImplementedError("Subclasses must implement from_dict")
    
    def validate(self) -> bool:
        """Validate data."""
        raise NotImplementedError("Subclasses must implement validate")

if __name__ == "__main__":
    print("Testing trading base models...")
    
    # Test enums
    print(f"âœ… OrderSide.BID: {OrderSide.BID}")
    print(f"âœ… OrderSide.ASK: {OrderSide.ASK}")
    print(f"âœ… OrderType.MARKET: {OrderType.MARKET}")
    print(f"âœ… OrderStatus.OPEN: {OrderStatus.OPEN}")
    print(f"âœ… PositionSide.LONG: {PositionSide.LONG}")
    
    print("âœ… Trading base models test completed!")


