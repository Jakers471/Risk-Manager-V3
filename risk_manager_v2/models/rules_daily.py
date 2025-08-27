"""
Daily Limits Rule

Handles daily loss, profit, and trade count limits.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from .rules_base import BaseRule, RuleValidator

@dataclass
class DailyLimits(BaseRule):
    """Daily trading limits."""
    max_daily_loss: float = 1000.0
    daily_profit_target: float = 2000.0
    max_daily_trades: int = 10
    max_daily_volume: float = 100000.0
    
    def __post_init__(self):
        """Initialize after dataclass creation."""
        super().__init__(enabled=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "enabled": self.enabled,
            "max_daily_loss": self.max_daily_loss,
            "daily_profit_target": self.daily_profit_target,
            "max_daily_trades": self.max_daily_trades,
            "max_daily_volume": self.max_daily_volume
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DailyLimits':
        """Create from dictionary."""
        limits = cls(
            max_daily_loss=data.get("max_daily_loss", 1000.0),
            daily_profit_target=data.get("daily_profit_target", 2000.0),
            max_daily_trades=data.get("max_daily_trades", 10),
            max_daily_volume=data.get("max_daily_volume", 100000.0)
        )
        limits.enabled = data.get("enabled", True)
        return limits
    
    def validate(self) -> bool:
        """Validate daily limits."""
        try:
            RuleValidator.validate_positive_float(self.max_daily_loss, "Max Daily Loss")
            RuleValidator.validate_positive_float(self.daily_profit_target, "Daily Profit Target")
            RuleValidator.validate_positive_int(self.max_daily_trades, "Max Daily Trades")
            RuleValidator.validate_positive_float(self.max_daily_volume, "Max Daily Volume")
            
            # Additional business logic validation
            if self.max_daily_loss > 1000000:
                raise ValueError("Max Daily Loss cannot exceed $1,000,000")
            if self.daily_profit_target > 1000000:
                raise ValueError("Daily Profit Target cannot exceed $1,000,000")
            if self.max_daily_trades > 10000:
                raise ValueError("Max Daily Trades cannot exceed 10,000")
            if self.max_daily_volume > 100000000:
                raise ValueError("Max Daily Volume cannot exceed $100,000,000")
            
            return True
        except ValueError as e:
            raise ValueError(f"Daily Limits validation failed: {e}")
    
    def is_daily_loss_breached(self, current_loss: float) -> bool:
        """Check if daily loss limit is breached."""
        if not self.enabled or self.max_daily_loss <= 0:
            return False
        return current_loss >= self.max_daily_loss
    
    def is_daily_profit_hit(self, current_profit: float) -> bool:
        """Check if daily profit target is hit."""
        if not self.enabled or self.daily_profit_target <= 0:
            return False
        return current_profit >= self.daily_profit_target
    
    def is_trade_count_exceeded(self, current_trades: int) -> bool:
        """Check if daily trade count is exceeded."""
        if not self.enabled or self.max_daily_trades <= 0:
            return False
        return current_trades >= self.max_daily_trades
    
    def is_volume_exceeded(self, current_volume: float) -> bool:
        """Check if daily volume limit is exceeded."""
        if not self.enabled or self.max_daily_volume <= 0:
            return False
        return current_volume >= self.max_daily_volume
    
    def get_remaining_loss_capacity(self, current_loss: float) -> float:
        """Get remaining loss capacity before limit is hit."""
        if not self.enabled or self.max_daily_loss <= 0:
            return float('inf')
        return max(0, self.max_daily_loss - current_loss)
    
    def get_remaining_profit_needed(self, current_profit: float) -> float:
        """Get remaining profit needed to hit target."""
        if not self.enabled or self.daily_profit_target <= 0:
            return 0
        return max(0, self.daily_profit_target - current_profit)
    
    def get_remaining_trades(self, current_trades: int) -> int:
        """Get remaining trades before limit is hit."""
        if not self.enabled or self.max_daily_trades <= 0:
            return float('inf')
        return max(0, self.max_daily_trades - current_trades)
    
    def get_remaining_volume(self, current_volume: float) -> float:
        """Get remaining volume capacity before limit is hit."""
        if not self.enabled or self.max_daily_volume <= 0:
            return float('inf')
        return max(0, self.max_daily_volume - current_volume)
    
    def get_risk_status(self, current_loss: float, current_profit: float, 
                       current_trades: int, current_volume: float) -> Dict[str, Any]:
        """Get comprehensive risk status for all daily limits."""
        return {
            "loss_breached": self.is_daily_loss_breached(current_loss),
            "profit_hit": self.is_daily_profit_hit(current_profit),
            "trades_exceeded": self.is_trade_count_exceeded(current_trades),
            "volume_exceeded": self.is_volume_exceeded(current_volume),
            "remaining_loss": self.get_remaining_loss_capacity(current_loss),
            "remaining_profit": self.get_remaining_profit_needed(current_profit),
            "remaining_trades": self.get_remaining_trades(current_trades),
            "remaining_volume": self.get_remaining_volume(current_volume),
            "loss_percentage": (current_loss / self.max_daily_loss * 100) if self.max_daily_loss > 0 else 0,
            "profit_percentage": (current_profit / self.daily_profit_target * 100) if self.daily_profit_target > 0 else 0,
            "trades_percentage": (current_trades / self.max_daily_trades * 100) if self.max_daily_trades > 0 else 0,
            "volume_percentage": (current_volume / self.max_daily_volume * 100) if self.max_daily_volume > 0 else 0
        }

if __name__ == "__main__":
    print("Testing DailyLimits...")
    
    # Test basic initialization
    daily_limits = DailyLimits()
    print("✅ DailyLimits created successfully!")
    
    # Test validation
    try:
        daily_limits.validate()
        print("✅ Validation passed!")
    except ValueError as e:
        print(f"❌ Validation failed: {e}")
    
    # Test risk status
    status = daily_limits.get_risk_status(500.0, 1000.0, 5, 50000.0)
    print(f"✅ Risk status: {status}")
    
    # Test to_dict/from_dict
    data = daily_limits.to_dict()
    restored = DailyLimits.from_dict(data)
    print(f"✅ Serialization test: {restored.to_dict()}")
    
    print("✅ DailyLimits test completed!")
