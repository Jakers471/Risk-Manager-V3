"""
Account Data Models

Handles account information, balance, and performance data.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
from .rules_base import BaseRule, RuleValidator

@dataclass
class AccountBalance:
    """Account balance information."""
    cash: float = 0.0
    buying_power: float = 0.0
    equity: float = 0.0
    margin_used: float = 0.0
    margin_available: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "cash": self.cash,
            "buying_power": self.buying_power,
            "equity": self.equity,
            "margin_used": self.margin_used,
            "margin_available": self.margin_available,
            "unrealized_pnl": self.unrealized_pnl,
            "realized_pnl": self.realized_pnl
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountBalance':
        """Create from dictionary."""
        return cls(
            cash=data.get("cash", 0.0),
            buying_power=data.get("buying_power", 0.0),
            equity=data.get("equity", 0.0),
            margin_used=data.get("margin_used", 0.0),
            margin_available=data.get("margin_available", 0.0),
            unrealized_pnl=data.get("unrealized_pnl", 0.0),
            realized_pnl=data.get("realized_pnl", 0.0)
        )
    
    def validate(self) -> bool:
        """Validate balance data."""
        try:
            RuleValidator.validate_positive_float(self.cash, "Cash")
            RuleValidator.validate_positive_float(self.buying_power, "Buying Power")
            RuleValidator.validate_positive_float(self.equity, "Equity")
            RuleValidator.validate_positive_float(self.margin_used, "Margin Used")
            RuleValidator.validate_positive_float(self.margin_available, "Margin Available")
            return True
        except ValueError as e:
            raise ValueError(f"Account Balance validation failed: {e}")
    
    def get_margin_utilization(self) -> float:
        """Calculate margin utilization percentage."""
        if self.buying_power > 0:
            return (self.margin_used / self.buying_power) * 100
        return 0.0
    
    def get_total_pnl(self) -> float:
        """Get total P&L (realized + unrealized)."""
        return self.realized_pnl + self.unrealized_pnl
    
    def is_margin_call_risk(self, threshold: float = 80.0) -> bool:
        """Check if account is at risk of margin call."""
        return self.get_margin_utilization() >= threshold
    
    def get_balance_status(self) -> Dict[str, Any]:
        """Get comprehensive balance status."""
        return {
            "cash": self.cash,
            "buying_power": self.buying_power,
            "equity": self.equity,
            "margin_used": self.margin_used,
            "margin_available": self.margin_available,
            "unrealized_pnl": self.unrealized_pnl,
            "realized_pnl": self.realized_pnl,
            "total_pnl": self.get_total_pnl(),
            "margin_utilization": self.get_margin_utilization(),
            "margin_call_risk": self.is_margin_call_risk()
        }

@dataclass
class AccountPerformance:
    """Account performance metrics."""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    total_pnl: float = 0.0
    daily_pnl: float = 0.0
    monthly_pnl: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "average_win": self.average_win,
            "average_loss": self.average_loss,
            "largest_win": self.largest_win,
            "largest_loss": self.largest_loss,
            "total_pnl": self.total_pnl,
            "daily_pnl": self.daily_pnl,
            "monthly_pnl": self.monthly_pnl
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountPerformance':
        """Create from dictionary."""
        return cls(
            total_trades=data.get("total_trades", 0),
            winning_trades=data.get("winning_trades", 0),
            losing_trades=data.get("losing_trades", 0),
            win_rate=data.get("win_rate", 0.0),
            average_win=data.get("average_win", 0.0),
            average_loss=data.get("average_loss", 0.0),
            largest_win=data.get("largest_win", 0.0),
            largest_loss=data.get("largest_loss", 0.0),
            total_pnl=data.get("total_pnl", 0.0),
            daily_pnl=data.get("daily_pnl", 0.0),
            monthly_pnl=data.get("monthly_pnl", 0.0)
        )
    
    def validate(self) -> bool:
        """Validate performance data."""
        try:
            RuleValidator.validate_positive_int(self.total_trades, "Total Trades")
            RuleValidator.validate_positive_int(self.winning_trades, "Winning Trades")
            RuleValidator.validate_positive_int(self.losing_trades, "Losing Trades")
            RuleValidator.validate_range(self.win_rate, "Win Rate", 0.0, 100.0)
            return True
        except ValueError as e:
            raise ValueError(f"Account Performance validation failed: {e}")
    
    def calculate_win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.total_trades > 0:
            return (self.winning_trades / self.total_trades) * 100
        return 0.0
    
    def get_profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        gross_profit = self.winning_trades * self.average_win
        gross_loss = self.losing_trades * abs(self.average_loss)
        
        if gross_loss > 0:
            return gross_profit / gross_loss
        return 0.0 if gross_profit == 0 else float('inf')
    
    def get_performance_status(self) -> Dict[str, Any]:
        """Get comprehensive performance status."""
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.calculate_win_rate(),
            "average_win": self.average_win,
            "average_loss": self.average_loss,
            "largest_win": self.largest_win,
            "largest_loss": self.largest_loss,
            "total_pnl": self.total_pnl,
            "daily_pnl": self.daily_pnl,
            "monthly_pnl": self.monthly_pnl,
            "profit_factor": self.get_profit_factor()
        }

@dataclass
class Account:
    """Complete account information."""
    account_id: str
    name: str
    status: str = "active"
    balance: Optional[AccountBalance] = None
    performance: Optional[AccountPerformance] = None
    created_at: datetime = None
    last_updated: datetime = None
    
    def __post_init__(self):
        """Initialize with defaults if not provided."""
        if self.balance is None:
            self.balance = AccountBalance()
        if self.performance is None:
            self.performance = AccountPerformance()
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "account_id": self.account_id,
            "name": self.name,
            "status": self.status,
            "balance": self.balance.to_dict(),
            "performance": self.performance.to_dict(),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        """Create from dictionary."""
        return cls(
            account_id=data["account_id"],
            name=data["name"],
            status=data.get("status", "active"),
            balance=AccountBalance.from_dict(data.get("balance", {})),
            performance=AccountPerformance.from_dict(data.get("performance", {})),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        )
    
    def validate(self) -> bool:
        """Validate account data."""
        try:
            RuleValidator.validate_string(self.account_id, "Account ID")
            RuleValidator.validate_string(self.name, "Account Name")
            RuleValidator.validate_string(self.status, "Account Status")
            
            # Validate nested objects
            self.balance.validate()
            self.performance.validate()
            
            return True
        except ValueError as e:
            raise ValueError(f"Account validation failed: {e}")
    
    def update_balance(self, new_balance: AccountBalance):
        """Update account balance."""
        self.balance = new_balance
        self.last_updated = datetime.now()
    
    def update_performance(self, new_performance: AccountPerformance):
        """Update account performance."""
        self.performance = new_performance
        self.last_updated = datetime.now()
    
    def is_active(self) -> bool:
        """Check if account is active."""
        return self.status.lower() == "active"
    
    def get_daily_pnl(self) -> float:
        """Get daily P&L."""
        return self.performance.daily_pnl
    
    def get_total_pnl(self) -> float:
        """Get total P&L."""
        return self.performance.total_pnl
    
    def get_account_status(self) -> Dict[str, Any]:
        """Get comprehensive account status."""
        return {
            "account_id": self.account_id,
            "name": self.name,
            "status": self.status,
            "is_active": self.is_active(),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "balance_status": self.balance.get_balance_status(),
            "performance_status": self.performance.get_performance_status()
        }

if __name__ == "__main__":
    print("Testing Account models...")
    
    # Test AccountBalance
    balance = AccountBalance(cash=10000.0, buying_power=9500.0, equity=10500.0)
    print("✅ AccountBalance created!")
    print(f"Margin Utilization: {balance.get_margin_utilization():.1f}%")
    print(f"Total P&L: ${balance.get_total_pnl():.2f}")
    
    # Test AccountPerformance
    performance = AccountPerformance(total_trades=100, winning_trades=65, average_win=150.0, average_loss=100.0)
    print("✅ AccountPerformance created!")
    print(f"Win Rate: {performance.calculate_win_rate():.1f}%")
    print(f"Profit Factor: {performance.get_profit_factor():.2f}")
    
    # Test Account
    account = Account(account_id="12345", name="Test Account", balance=balance, performance=performance)
    print("✅ Account created!")
    print(f"Account Status: {account.get_account_status()}")
    
    print("✅ Account models test completed!")
