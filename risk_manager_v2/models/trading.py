"""
Trading Data Models Router

Routes to different trading data modules.
"""

from typing import List, Dict, Any
from .trading_orders import Order, OrderSide, OrderType, OrderStatus
from .trading_positions import Position, PositionSide
from .trading_trades import Trade
from .trading_base import BaseTradingData

class TradingData:
    """Complete trading data - aggregates all trading types."""
    
    def __init__(self):
        self.orders = []
        self.positions = []
        self.trades = []
    
    def add_order(self, order: Order):
        """Add an order."""
        self.orders.append(order)
    
    def add_position(self, position: Position):
        """Add a position."""
        self.positions.append(position)
    
    def add_trade(self, trade: Trade):
        """Add a trade."""
        self.trades.append(trade)
    
    def get_pending_orders(self) -> List[Order]:
        """Get all pending orders."""
        return [order for order in self.orders if order.is_pending()]
    
    def get_open_positions(self) -> List[Position]:
        """Get all open positions."""
        return [pos for pos in self.positions if pos.size > 0]
    
    def get_trades_by_symbol(self, symbol: str) -> List[Trade]:
        """Get all trades for a symbol."""
        return [trade for trade in self.trades if trade.symbol == symbol]
    
    def get_orders_by_account(self, account_id: str) -> List[Order]:
        """Get all orders for an account."""
        return [order for order in self.orders if order.account_id == account_id]
    
    def get_positions_by_account(self, account_id: str) -> List[Position]:
        """Get all positions for an account."""
        return [pos for pos in self.positions if pos.account_id == account_id]
    
    def get_trades_by_account(self, account_id: str) -> List[Trade]:
        """Get all trades for an account."""
        return [trade for trade in self.trades if trade.account_id == account_id]
    
    def get_order_by_id(self, order_id: str) -> Order:
        """Get order by ID."""
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None
    
    def get_position_by_id(self, position_id: str) -> Position:
        """Get position by ID."""
        for position in self.positions:
            if position.position_id == position_id:
                return position
        return None
    
    def get_trade_by_id(self, trade_id: str) -> Trade:
        """Get trade by ID."""
        for trade in self.trades:
            if trade.trade_id == trade_id:
                return trade
        return None
    
    def remove_order(self, order_id: str):
        """Remove an order by ID."""
        self.orders = [order for order in self.orders if order.order_id != order_id]
    
    def remove_position(self, position_id: str):
        """Remove a position by ID."""
        self.positions = [pos for pos in self.positions if pos.position_id != position_id]
    
    def remove_trade(self, trade_id: str):
        """Remove a trade by ID."""
        self.trades = [trade for trade in self.trades if trade.trade_id != trade_id]
    
    def clear_orders(self):
        """Clear all orders."""
        self.orders = []
    
    def clear_positions(self):
        """Clear all positions."""
        self.positions = []
    
    def clear_trades(self):
        """Clear all trades."""
        self.trades = []
    
    def get_trading_summary(self) -> Dict[str, Any]:
        """Get comprehensive trading summary."""
        return {
            "total_orders": len(self.orders),
            "pending_orders": len(self.get_pending_orders()),
            "total_positions": len(self.positions),
            "open_positions": len(self.get_open_positions()),
            "total_trades": len(self.trades),
            "orders_by_status": self._get_orders_by_status(),
            "positions_by_side": self._get_positions_by_side(),
            "trades_by_symbol": self._get_trades_by_symbol_count()
        }
    
    def _get_orders_by_status(self) -> Dict[str, int]:
        """Get count of orders by status."""
        status_counts = {}
        for order in self.orders:
            status = order.status.name if hasattr(order.status, 'name') else str(order.status)
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
    def _get_positions_by_side(self) -> Dict[str, int]:
        """Get count of positions by side."""
        side_counts = {}
        for position in self.positions:
            side = position.side.name if hasattr(position.side, 'name') else str(position.side)
            side_counts[side] = side_counts.get(side, 0) + 1
        return side_counts
    
    def _get_trades_by_symbol_count(self) -> Dict[str, int]:
        """Get count of trades by symbol."""
        symbol_counts = {}
        for trade in self.trades:
            symbol = trade.symbol
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        return symbol_counts
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "orders": [order.to_dict() for order in self.orders],
            "positions": [pos.to_dict() for pos in self.positions],
            "trades": [trade.to_dict() for trade in self.trades]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingData':
        """Create from dictionary."""
        trading_data = cls()
        
        for order_data in data.get("orders", []):
            trading_data.add_order(Order.from_dict(order_data))
        
        for position_data in data.get("positions", []):
            trading_data.add_position(Position.from_dict(position_data))
        
        for trade_data in data.get("trades", []):
            trading_data.add_trade(Trade.from_dict(trade_data))
        
        return trading_data

if __name__ == "__main__":
    print("Testing TradingData router...")
    
    # Test basic initialization
    trading_data = TradingData()
    print("âœ… TradingData created successfully!")
    
    # Test summary
    summary = trading_data.get_trading_summary()
    print(f"âœ… Trading summary: {summary}")
    
    print("âœ… TradingData router test completed!")


