"""
Base Rule Class

Foundation for all rule types - makes adding new rules easy.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseRule(ABC):
    """Base class for all rule types."""
    
    def __init__(self, enabled: bool = True):
        """Initialize base rule."""
        self.enabled = enabled
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary for storage."""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseRule':
        """Create rule from dictionary."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate rule data."""
        pass
    
    def get_rule_name(self) -> str:
        """Get the name of this rule type."""
        return self.__class__.__name__.lower()
    
    def is_enabled(self) -> bool:
        """Check if rule is enabled."""
        return self.enabled
    
    def enable(self) -> None:
        """Enable the rule."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the rule."""
        self.enabled = False

class RuleValidator:
    """Utility for validating rule data."""
    
    @staticmethod
    def validate_positive_float(value: float, name: str) -> bool:
        """Validate that a float value is positive."""
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"{name} must be a positive number")
        return True
    
    @staticmethod
    def validate_positive_int(value: int, name: str) -> bool:
        """Validate that an int value is positive."""
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a positive integer")
        return True
    
    @staticmethod
    def validate_time_format(time_str: str, name: str) -> bool:
        """Validate time format (HH:MM)."""
        if not isinstance(time_str, str) or len(time_str) != 5 or time_str[2] != ':':
            raise ValueError(f"{name} must be in HH:MM format")
        
        try:
            hour, minute = map(int, time_str.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except ValueError:
            raise ValueError(f"{name} must be a valid time (00:00-23:59)")
        
        return True
    
    @staticmethod
    def validate_time_range(start_time: str, end_time: str, name: str) -> bool:
        """Validate that start time is before end time."""
        RuleValidator.validate_time_format(start_time, f"{name} start")
        RuleValidator.validate_time_format(end_time, f"{name} end")
        
        try:
            from datetime import datetime
            start = datetime.strptime(start_time, '%H:%M')
            end = datetime.strptime(end_time, '%H:%M')
            
            if start >= end:
                raise ValueError(f"{name} start time must be before end time")
        except ValueError as e:
            if "start time must be before" in str(e):
                raise e
            raise ValueError(f"Invalid {name} time format")
        
        return True
    
    @staticmethod
    def validate_boolean(value: Any, name: str) -> bool:
        """Validate that a value is boolean."""
        if not isinstance(value, bool):
            raise ValueError(f"{name} must be a boolean (True/False)")
        return True
    
    @staticmethod
    def validate_string(value: Any, name: str, min_length: int = 1) -> bool:
        """Validate that a value is a non-empty string."""
        if not isinstance(value, str) or len(value.strip()) < min_length:
            raise ValueError(f"{name} must be a non-empty string")
        return True
    
    @staticmethod
    def validate_range(value: float, name: str, min_val: float, max_val: float) -> bool:
        """Validate that a value is within a range."""
        if not isinstance(value, (int, float)) or value < min_val or value > max_val:
            raise ValueError(f"{name} must be between {min_val} and {max_val}")
        return True

if __name__ == "__main__":
    print("Testing BaseRule and RuleValidator...")
    
    # Test RuleValidator
    try:
        RuleValidator.validate_positive_float(100.0, "test_value")
        RuleValidator.validate_positive_int(10, "test_count")
        RuleValidator.validate_time_format("09:30", "start_time")
        RuleValidator.validate_time_range("09:30", "16:00", "trading_hours")
        RuleValidator.validate_boolean(True, "enabled")
        RuleValidator.validate_string("test", "name")
        RuleValidator.validate_range(50.0, "percentage", 0.0, 100.0)
        print("âœ… All validation tests passed!")
    except ValueError as e:
        print(f"âŒ Validation test failed: {e}")
    
    print("âœ… BaseRule test completed!")

