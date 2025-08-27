"""
Session Rules

Handles session enforcement and auto-flattening configuration.
"""

from dataclasses import dataclass
from typing import Dict, Any
from .rules_base import BaseRule, RuleValidator

@dataclass
class SessionRules(BaseRule):
    """Session enforcement rules."""
    auto_flatten: bool = True
    stop_on_loss: bool = True
    stop_on_profit: bool = True
    end_of_day_flatten: bool = True
    session_timeout: int = 30  # minutes
    
    def __post_init__(self):
        """Initialize after dataclass creation."""
        super().__init__(enabled=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "enabled": self.enabled,
            "auto_flatten": self.auto_flatten,
            "stop_on_loss": self.stop_on_loss,
            "stop_on_profit": self.stop_on_profit,
            "end_of_day_flatten": self.end_of_day_flatten,
            "session_timeout": self.session_timeout
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionRules':
        """Create from dictionary."""
        rules = cls(
            auto_flatten=data.get("auto_flatten", True),
            stop_on_loss=data.get("stop_on_loss", True),
            stop_on_profit=data.get("stop_on_profit", True),
            end_of_day_flatten=data.get("end_of_day_flatten", True),
            session_timeout=data.get("session_timeout", 30)
        )
        rules.enabled = data.get("enabled", True)
        return rules
    
    def validate(self) -> bool:
        """Validate session rules."""
        try:
            # Validate boolean fields
            RuleValidator.validate_boolean(self.auto_flatten, "Auto Flatten")
            RuleValidator.validate_boolean(self.stop_on_loss, "Stop on Loss")
            RuleValidator.validate_boolean(self.stop_on_profit, "Stop on Profit")
            RuleValidator.validate_boolean(self.end_of_day_flatten, "End of Day Flatten")
            
            # Validate session timeout
            RuleValidator.validate_range(self.session_timeout, "Session Timeout", 5, 480)
            
            return True
        except ValueError as e:
            raise ValueError(f"Session Rules validation failed: {e}")
    
    def should_auto_flatten(self) -> bool:
        """Check if auto-flattening is enabled."""
        return self.enabled and self.auto_flatten
    
    def should_stop_on_loss(self) -> bool:
        """Check if trading should stop on daily loss."""
        return self.enabled and self.stop_on_loss
    
    def should_stop_on_profit(self) -> bool:
        """Check if trading should stop on daily profit."""
        return self.enabled and self.stop_on_profit
    
    def should_end_of_day_flatten(self) -> bool:
        """Check if end-of-day flattening is enabled."""
        return self.enabled and self.end_of_day_flatten
    
    def get_session_timeout_seconds(self) -> int:
        """Get session timeout in seconds."""
        return self.session_timeout * 60
    
    def get_session_timeout_minutes(self) -> int:
        """Get session timeout in minutes."""
        return self.session_timeout
    
    def is_session_enforcement_enabled(self) -> bool:
        """Check if any session enforcement is enabled."""
        if not self.enabled:
            return False
        return any([
            self.auto_flatten,
            self.stop_on_loss,
            self.stop_on_profit,
            self.end_of_day_flatten
        ])
    
    def get_enforcement_status(self) -> Dict[str, bool]:
        """Get status of all enforcement rules."""
        return {
            "auto_flatten": self.should_auto_flatten(),
            "stop_on_loss": self.should_stop_on_loss(),
            "stop_on_profit": self.should_stop_on_profit(),
            "end_of_day_flatten": self.should_end_of_day_flatten(),
            "session_timeout_enabled": self.session_timeout > 0
        }
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get comprehensive session information."""
        return {
            "enabled": self.enabled,
            "session_timeout_minutes": self.session_timeout,
            "session_timeout_seconds": self.get_session_timeout_seconds(),
            "enforcement_enabled": self.is_session_enforcement_enabled(),
            "enforcement_rules": self.get_enforcement_status(),
            "auto_flatten_description": "Close positions when risk limits are breached",
            "stop_on_loss_description": "Stop trading when daily loss limit is hit",
            "stop_on_profit_description": "Stop trading when daily profit target is hit",
            "end_of_day_flatten_description": "Close all positions at market close",
            "session_timeout_description": f"Auto-logout after {self.session_timeout} minutes of inactivity"
        }

if __name__ == "__main__":
    print("Testing SessionRules...")
    
    # Test basic initialization
    session_rules = SessionRules()
    print("âœ… SessionRules created successfully!")
    
    # Test validation
    try:
        session_rules.validate()
        print("âœ… Validation passed!")
    except ValueError as e:
        print(f"âŒ Validation failed: {e}")
    
    # Test enforcement status
    status = session_rules.get_enforcement_status()
    print(f"âœ… Enforcement status: {status}")
    
    # Test session info
    info = session_rules.get_session_info()
    print(f"âœ… Session info: {info}")
    
    print("âœ… SessionRules test completed!")

