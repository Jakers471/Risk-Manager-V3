"""
Position Limits Rule

Handles position size and risk per trade limits.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from .rules_base import BaseRule, RuleValidator

@dataclass
class PositionLimits(BaseRule):
    """Position size and risk limits."""
    max_position_size: int = 10
    max_open_positions: int = 5
    max_risk_per_trade: float = 500.0
    
    def __post_init__(self):
        """Initialize after dataclass creation."""
        super().__init__(enabled=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "enabled": self.enabled,
            "max_position_size": self.max_position_size,
            "max_open_positions": self.max_open_positions,
            "max_risk_per_trade": self.max_risk_per_trade
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PositionLimits':
        """Create from dictionary."""
        limits = cls(
            max_position_size=data.get("max_position_size", 10),
            max_open_positions=data.get("max_open_positions", 5),
            max_risk_per_trade=data.get("max_risk_per_trade", 500.0)
        )
        limits.enabled = data.get("enabled", True)
        return limits
    
    def validate(self) -> bool:
        """Validate position limits."""
        try:
            RuleValidator.validate_positive_int(self.max_position_size, "Max Position Size")
            RuleValidator.validate_positive_int(self.max_open_positions, "Max Open Positions")
            RuleValidator.validate_positive_float(self.max_risk_per_trade, "Max Risk Per Trade")
            
            # Additional business logic validation
            if self.max_position_size > 10000:
                raise ValueError("Max Position Size cannot exceed 10,000 contracts")
            if self.max_open_positions > 1000:
                raise ValueError("Max Open Positions cannot exceed 1,000")
            if self.max_risk_per_trade > 1000000:
                raise ValueError("Max Risk Per Trade cannot exceed $1,000,000")
            
            return True
        except ValueError as e:
            raise ValueError(f"Position Limits validation failed: {e}")
    
    def is_position_size_exceeded(self, current_size: int) -> bool:
        """Check if position size limit is exceeded."""
        if not self.enabled or self.max_position_size <= 0:
            return False
        return current_size > self.max_position_size
    
    def is_open_positions_exceeded(self, current_positions: int) -> bool:
        """Check if max open positions limit is exceeded."""
        if not self.enabled or self.max_open_positions <= 0:
            return False
        return current_positions >= self.max_open_positions
    
    def is_risk_per_trade_exceeded(self, trade_risk: float) -> bool:
        """Check if risk per trade limit is exceeded."""
        if not self.enabled or self.max_risk_per_trade <= 0:
            return False
        return trade_risk > self.max_risk_per_trade
    
    def get_remaining_position_capacity(self, current_size: int) -> int:
        """Get remaining position size capacity."""
        if not self.enabled or self.max_position_size <= 0:
            return float('inf')
        return max(0, self.max_position_size - current_size)
    
    def get_remaining_position_slots(self, current_positions: int) -> int:
        """Get remaining open position slots."""
        if not self.enabled or self.max_open_positions <= 0:
            return float('inf')
        return max(0, self.max_open_positions - current_positions)
    
    def get_remaining_risk_capacity(self, current_risk: float) -> float:
        """Get remaining risk capacity before limit is hit."""
        if not self.enabled or self.max_risk_per_trade <= 0:
            return float('inf')
        return max(0, self.max_risk_per_trade - current_risk)
    
    def get_position_utilization(self, current_size: int) -> float:
        """Get position size utilization percentage."""
        if not self.enabled or self.max_position_size <= 0:
            return 0.0
        return (current_size / self.max_position_size) * 100
    
    def get_positions_utilization(self, current_positions: int) -> float:
        """Get open positions utilization percentage."""
        if not self.enabled or self.max_open_positions <= 0:
            return 0.0
        return (current_positions / self.max_open_positions) * 100
    
    def get_risk_utilization(self, current_risk: float) -> float:
        """Get risk utilization percentage."""
        if not self.enabled or self.max_risk_per_trade <= 0:
            return 0.0
        return (current_risk / self.max_risk_per_trade) * 100
    
    def get_risk_status(self, current_size: int, current_positions: int, 
                       current_risk: float) -> Dict[str, Any]:
        """Get comprehensive risk status for all position limits."""
        return {
            "size_exceeded": self.is_position_size_exceeded(current_size),
            "positions_exceeded": self.is_open_positions_exceeded(current_positions),
            "risk_exceeded": self.is_risk_per_trade_exceeded(current_risk),
            "remaining_size": self.get_remaining_position_capacity(current_size),
            "remaining_slots": self.get_remaining_position_slots(current_positions),
            "remaining_risk": self.get_remaining_risk_capacity(current_risk),
            "size_utilization": self.get_position_utilization(current_size),
            "positions_utilization": self.get_positions_utilization(current_positions),
            "risk_utilization": self.get_risk_utilization(current_risk)
        }

if __name__ == "__main__":
    print("Testing PositionLimits...")
    
    # Test basic initialization
    position_limits = PositionLimits()
    print("âœ… PositionLimits created successfully!")
    
    # Test validation
    try:
        position_limits.validate()
        print("âœ… Validation passed!")
    except ValueError as e:
        print(f"âŒ Validation failed: {e}")
    
    # Test risk status
    status = position_limits.get_risk_status(5, 3, 250.0)
    print(f"âœ… Risk status: {status}")
    
    # Test to_dict/from_dict
    data = position_limits.to_dict()
    restored = PositionLimits.from_dict(data)
    print(f"âœ… Serialization test: {restored.to_dict()}")
    
    print("âœ… PositionLimits test completed!")

