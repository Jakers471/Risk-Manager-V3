"""
Trading Trades Data Model

Handles trade information and management.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from .trading_base import BaseTradingData, OrderSide

@dataclass
class Trade(BaseTradingData):
    """Trade information."""
    trade_id: str
    account_id: str
    contract_id: str
    symbol: str
    price: float
    size: int
    side: OrderSide
    profit_and_loss: Optional[float] = None
    fees: float = 0.0
    voided: bool = False
    order_id: Optional[str] = None
    creation_timestamp: datetime = None
    
    def __post_init__(self):
        """Initialize with defaults if not provided."""
        if self.creation_timestamp is None:
            self.creation_timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "trade_id": self.trade_id,
            "account_id": self.account_id,
            "contract_id": self.contract_id,
            "symbol": self.symbol,
            "price": self.price,
            "size": self.size,
            "side": self.side.value,
            "profit_and_loss": self.profit_and_loss,
            "fees": self.fees,
            "voided": self.voided,
            "order_id": self.order_id,
            "creation_timestamp": self.creation_timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Trade':
        """Create from dictionary."""
        return cls(
            trade_id=data["trade_id"],
            account_id=data["account_id"],
            contract_id=data["contract_id"],
            symbol=data["symbol"],
            price=data.get("price", 0.0),
            size=data.get("size", 0),
            side=OrderSide(data.get("side", 0)),
            profit_and_loss=data.get("profit_and_loss"),
            fees=data.get("fees", 0.0),
            voided=data.get("voided", False),
            order_id=data.get("order_id"),
            creation_timestamp=datetime.fromisoformat(data.get("creation_timestamp", datetime.now().isoformat()))
        )
    
    def validate(self) -> bool:
        """Validate trade data."""
        if not self.trade_id or not self.account_id or not self.contract_id:
            raise ValueError("Trade ID, Account ID, and Contract ID are required")
        
        if not self.symbol:
            raise ValueError("Symbol is required")
        
        if self.price <= 0:
            raise ValueError("Trade price must be positive")
        
        if self.size <= 0:
            raise ValueError("Trade size must be positive")
        
        if self.fees < 0:
            raise ValueError("Fees cannot be negative")
        
        return True
    
    def is_buy(self) -> bool:
        """Check if trade is a buy."""
        return self.side == OrderSide.BID
    
    def is_sell(self) -> bool:
        """Check if trade is a sell."""
        return self.side == OrderSide.ASK
    
    def is_winning_trade(self) -> bool:
        """Check if trade is winning (positive P&L)."""
        return self.profit_and_loss is not None and self.profit_and_loss > 0
    
    def is_losing_trade(self) -> bool:
        """Check if trade is losing (negative P&L)."""
        return self.profit_and_loss is not None and self.profit_and_loss < 0
    
    def is_breakeven_trade(self) -> bool:
        """Check if trade is breakeven (zero P&L)."""
        return self.profit_and_loss is not None and self.profit_and_loss == 0
    
    def get_trade_value(self) -> float:
        """Get total trade value."""
        return self.price * self.size
    
    def get_net_pnl(self) -> float:
        """Get net P&L (P&L minus fees)."""
        if self.profit_and_loss is not None:
            return self.profit_and_loss - self.fees
        return 0.0
    
    def get_trade_info(self) -> Dict[str, Any]:
        """Get comprehensive trade information."""
        return {
            "trade_id": self.trade_id,
            "account_id": self.account_id,
            "contract_id": self.contract_id,
            "symbol": self.symbol,
            "price": self.price,
            "size": self.size,
            "side": self.side.name,
            "profit_and_loss": self.profit_and_loss,
            "fees": self.fees,
            "voided": self.voided,
            "order_id": self.order_id,
            "creation_timestamp": self.creation_timestamp.isoformat(),
            "is_buy": self.is_buy(),
            "is_sell": self.is_sell(),
            "is_winning": self.is_winning_trade(),
            "is_losing": self.is_losing_trade(),
            "is_breakeven": self.is_breakeven_trade(),
            "trade_value": self.get_trade_value(),
            "net_pnl": self.get_net_pnl()
        }

if __name__ == "__main__":
    print("Testing Trade model...")
    
    # Test trade creation
    trade = Trade(
        trade_id="12345",
        account_id="67890",
        contract_id="CON.F.US.EP.U25",
        symbol="F.US.EP",
        price=2100.0,
        size=1,
        side=OrderSide.BID,
        profit_and_loss=50.0,
        fees=2.50
    )
    print("âœ… Trade created successfully!")
    
    # Test validation
    try:
        trade.validate()
        print("âœ… Trade validation passed!")
    except ValueError as e:
        print(f"âŒ Trade validation failed: {e}")
    
    # Test trade info
    info = trade.get_trade_info()
    print(f"âœ… Trade info: {info}")
    
    print("âœ… Trade model test completed!")


