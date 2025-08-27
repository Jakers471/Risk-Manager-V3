"""
Trading Hours Rule

Handles trading hours and timezone configuration.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime, time
import pytz
from .rules_base import BaseRule, RuleValidator

@dataclass
class TradingHours(BaseRule):
    """Trading hours configuration."""
    start_time: str = "09:30"
    end_time: str = "16:00"
    timezone: str = "America/New_York"
    pre_market_start: str = "04:00"
    pre_market_end: str = "09:30"
    after_hours_start: str = "16:00"
    after_hours_end: str = "20:00"
    enable_pre_market: bool = False
    enable_after_hours: bool = False
    allow_regular: bool = True
    allow_pre_market: bool = False
    allow_after_hours: bool = False
    
    def __post_init__(self):
        """Initialize after dataclass creation."""
        super().__init__(enabled=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "enabled": self.enabled,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "timezone": self.timezone,
            "pre_market_start": self.pre_market_start,
            "pre_market_end": self.pre_market_end,
            "after_hours_start": self.after_hours_start,
            "after_hours_end": self.after_hours_end,
            "enable_pre_market": self.enable_pre_market,
            "enable_after_hours": self.enable_after_hours,
            "allow_regular": self.allow_regular,
            "allow_pre_market": self.allow_pre_market,
            "allow_after_hours": self.allow_after_hours
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingHours':
        """Create from dictionary."""
        hours = cls(
            start_time=data.get("start_time", "09:30"),
            end_time=data.get("end_time", "16:00"),
            timezone=data.get("timezone", "America/New_York"),
            pre_market_start=data.get("pre_market_start", "04:00"),
            pre_market_end=data.get("pre_market_end", "09:30"),
            after_hours_start=data.get("after_hours_start", "16:00"),
            after_hours_end=data.get("after_hours_end", "20:00"),
            enable_pre_market=data.get("enable_pre_market", False),
            enable_after_hours=data.get("enable_after_hours", False),
            allow_regular=data.get("allow_regular", True),
            allow_pre_market=data.get("allow_pre_market", False),
            allow_after_hours=data.get("allow_after_hours", False)
        )
        hours.enabled = data.get("enabled", True)
        return hours
    
    def validate(self) -> bool:
        """Validate trading hours."""
        try:
            # Validate time formats
            RuleValidator.validate_time_format(self.start_time, "Start Time")
            RuleValidator.validate_time_format(self.end_time, "End Time")
            RuleValidator.validate_time_format(self.pre_market_start, "Pre-Market Start")
            RuleValidator.validate_time_format(self.pre_market_end, "Pre-Market End")
            RuleValidator.validate_time_format(self.after_hours_start, "After-Hours Start")
            RuleValidator.validate_time_format(self.after_hours_end, "After-Hours End")
            
            # Validate time ranges
            RuleValidator.validate_time_range(self.start_time, self.end_time, "Regular Trading")
            RuleValidator.validate_time_range(self.pre_market_start, self.pre_market_end, "Pre-Market")
            RuleValidator.validate_time_range(self.after_hours_start, self.after_hours_end, "After-Hours")
            
            # Validate timezone
            try:
                pytz.timezone(self.timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                raise ValueError(f"Invalid timezone: {self.timezone}")
            
            # Validate boolean fields
            RuleValidator.validate_boolean(self.enable_pre_market, "Enable Pre-Market")
            RuleValidator.validate_boolean(self.enable_after_hours, "Enable After-Hours")
            RuleValidator.validate_boolean(self.allow_regular, "Allow Regular")
            RuleValidator.validate_boolean(self.allow_pre_market, "Allow Pre-Market")
            RuleValidator.validate_boolean(self.allow_after_hours, "Allow After-Hours")
            
            return True
        except ValueError as e:
            raise ValueError(f"Trading Hours validation failed: {e}")
    
    def is_within_trading_hours(self, current_time: datetime = None) -> bool:
        """Check if current time is within trading hours."""
        if not self.enabled:
            return True  # If disabled, always allow trading
        
        if current_time is None:
            current_time = datetime.now()
        
        # Convert current time to trading timezone
        tz = pytz.timezone(self.timezone)
        current_time = current_time.astimezone(tz)
        
        # Check regular trading hours
        if self.allow_regular and self._is_within_time_range(current_time, self.start_time, self.end_time):
            return True
        
        # Check pre-market hours
        if self.allow_pre_market and self.enable_pre_market and self._is_within_time_range(current_time, self.pre_market_start, self.pre_market_end):
            return True
        
        # Check after-hours
        if self.allow_after_hours and self.enable_after_hours and self._is_within_time_range(current_time, self.after_hours_start, self.after_hours_end):
            return True
        
        return False
    
    def is_outside_trading_hours(self, current_time: datetime = None) -> bool:
        """Check if current time is outside trading hours."""
        return not self.is_within_trading_hours(current_time)
    
    def is_pre_market_time(self, current_time: datetime = None) -> bool:
        """Check if current time is during pre-market hours."""
        if not self.enabled or not self.enable_pre_market or not self.allow_pre_market:
            return False
        
        if current_time is None:
            current_time = datetime.now()
        
        tz = pytz.timezone(self.timezone)
        current_time = current_time.astimezone(tz)
        
        return self._is_within_time_range(current_time, self.pre_market_start, self.pre_market_end)
    
    def is_after_hours_time(self, current_time: datetime = None) -> bool:
        """Check if current time is during after-hours."""
        if not self.enabled or not self.enable_after_hours or not self.allow_after_hours:
            return False
        
        if current_time is None:
            current_time = datetime.now()
        
        tz = pytz.timezone(self.timezone)
        current_time = current_time.astimezone(tz)
        
        return self._is_within_time_range(current_time, self.after_hours_start, self.after_hours_end)
    
    def is_regular_trading_time(self, current_time: datetime = None) -> bool:
        """Check if current time is during regular trading hours."""
        if not self.enabled or not self.allow_regular:
            return False
        
        if current_time is None:
            current_time = datetime.now()
        
        tz = pytz.timezone(self.timezone)
        current_time = current_time.astimezone(tz)
        
        return self._is_within_time_range(current_time, self.start_time, self.end_time)
    
    def _is_within_time_range(self, current_time: datetime, start_time: str, end_time: str) -> bool:
        """Check if current time is within a specific time range."""
        start_hour, start_minute = map(int, start_time.split(':'))
        end_hour, end_minute = map(int, end_time.split(':'))
        
        start_time_obj = current_time.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        end_time_obj = current_time.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        
        return start_time_obj <= current_time <= end_time_obj
    
    def get_trading_hours_display(self) -> str:
        """Get formatted trading hours string."""
        hours_str = f"Regular: {self.start_time} - {self.end_time}"
        
        if self.enable_pre_market:
            hours_str += f" | Pre-Market: {self.pre_market_start} - {self.pre_market_end}"
        
        if self.enable_after_hours:
            hours_str += f" | After-Hours: {self.after_hours_start} - {self.after_hours_end}"
        
        return f"{hours_str} ({self.timezone})"

if __name__ == "__main__":
    print("Testing TradingHours...")
    
    # Test basic initialization
    trading_hours = TradingHours()
    print("✅ TradingHours created successfully!")
    
    # Test validation
    try:
        trading_hours.validate()
        print("✅ Validation passed!")
    except ValueError as e:
        print(f"❌ Validation failed: {e}")
    
    # Test basic functionality
    print(f"✅ Trading hours display: {trading_hours.get_trading_hours_display()}")
    print(f"✅ Within trading hours: {trading_hours.is_within_trading_hours()}")
    
    print("✅ TradingHours test completed!")
