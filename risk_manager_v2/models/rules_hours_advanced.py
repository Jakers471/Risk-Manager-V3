"""
Trading Hours Advanced Features

Advanced time calculations and status methods for trading hours.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pytz
from .rules_hours import TradingHours

class TradingHoursAdvanced:
    """Advanced trading hours functionality."""
    
    def __init__(self, trading_hours: TradingHours):
        """Initialize with a TradingHours instance."""
        self.trading_hours = trading_hours
    
    def get_time_until_open(self, current_time: datetime = None) -> str:
        """Get time until market opens."""
        if not self.trading_hours.enabled:
            return "Trading hours disabled"
        
        if current_time is None:
            current_time = datetime.now()
        
        tz = pytz.timezone(self.trading_hours.timezone)
        current_time = current_time.astimezone(tz)
        
        # Check if market is currently open
        if self.trading_hours.is_within_trading_hours(current_time):
            return "Market is open"
        
        # Find next opening time
        next_open = self._get_next_opening_time(current_time)
        if next_open:
            time_diff = next_open - current_time
            hours = int(time_diff.total_seconds() // 3600)
            minutes = int((time_diff.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m until open"
        
        return "Market closed"
    
    def _get_next_opening_time(self, current_time: datetime) -> Optional[datetime]:
        """Get the next market opening time."""
        # Check regular trading hours first
        if self.trading_hours.allow_regular:
            start_hour, start_minute = map(int, self.trading_hours.start_time.split(':'))
            today_open = current_time.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            
            if current_time < today_open:
                return today_open
        
        # Check pre-market if enabled
        if self.trading_hours.allow_pre_market and self.trading_hours.enable_pre_market:
            start_hour, start_minute = map(int, self.trading_hours.pre_market_start.split(':'))
            today_pre_open = current_time.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            
            if current_time < today_pre_open:
                return today_pre_open
        
        # Check after-hours if enabled
        if self.trading_hours.allow_after_hours and self.trading_hours.enable_after_hours:
            start_hour, start_minute = map(int, self.trading_hours.after_hours_start.split(':'))
            today_after_open = current_time.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            
            if current_time < today_after_open:
                return today_after_open
        
        return None
    
    def get_trading_status(self, current_time: datetime = None) -> Dict[str, Any]:
        """Get comprehensive trading hours status."""
        if current_time is None:
            current_time = datetime.now()
        
        return {
            "enabled": self.trading_hours.enabled,
            "within_trading_hours": self.trading_hours.is_within_trading_hours(current_time),
            "outside_trading_hours": self.trading_hours.is_outside_trading_hours(current_time),
            "is_pre_market": self.trading_hours.is_pre_market_time(current_time),
            "is_after_hours": self.trading_hours.is_after_hours_time(current_time),
            "is_regular_trading": self.trading_hours.is_regular_trading_time(current_time),
            "time_until_open": self.get_time_until_open(current_time),
            "current_timezone": self.trading_hours.timezone,
            "regular_hours": f"{self.trading_hours.start_time} - {self.trading_hours.end_time}",
            "pre_market_hours": f"{self.trading_hours.pre_market_start} - {self.trading_hours.pre_market_end}" if self.trading_hours.enable_pre_market else "Disabled",
            "after_hours": f"{self.trading_hours.after_hours_start} - {self.trading_hours.after_hours_end}" if self.trading_hours.enable_after_hours else "Disabled"
        }
    
    def get_session_info(self, current_time: datetime = None) -> Dict[str, Any]:
        """Get detailed session information."""
        if current_time is None:
            current_time = datetime.now()
        
        tz = pytz.timezone(self.trading_hours.timezone)
        current_time = current_time.astimezone(tz)
        
        return {
            "current_time": current_time.strftime("%H:%M:%S"),
            "current_date": current_time.strftime("%Y-%m-%d"),
            "timezone": self.trading_hours.timezone,
            "session_type": self._get_current_session_type(current_time),
            "next_session": self._get_next_session_info(current_time),
            "session_progress": self._get_session_progress(current_time)
        }
    
    def _get_current_session_type(self, current_time: datetime) -> str:
        """Get the current session type."""
        if self.trading_hours.is_regular_trading_time(current_time):
            return "Regular Trading"
        elif self.trading_hours.is_pre_market_time(current_time):
            return "Pre-Market"
        elif self.trading_hours.is_after_hours_time(current_time):
            return "After-Hours"
        else:
            return "Closed"
    
    def _get_next_session_info(self, current_time: datetime) -> Dict[str, Any]:
        """Get information about the next trading session."""
        next_open = self._get_next_opening_time(current_time)
        if not next_open:
            return {"session": "None", "time": "N/A", "duration": "N/A"}
        
        time_diff = next_open - current_time
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        
        # Determine session type
        if self.trading_hours.allow_pre_market and self.trading_hours.enable_pre_market:
            start_hour, start_minute = map(int, self.trading_hours.pre_market_start.split(':'))
            pre_open = current_time.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            if current_time < pre_open:
                return {
                    "session": "Pre-Market",
                    "time": f"{hours}h {minutes}m",
                    "duration": "5h 30m"
                }
        
        if self.trading_hours.allow_regular:
            start_hour, start_minute = map(int, self.trading_hours.start_time.split(':'))
            reg_open = current_time.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            if current_time < reg_open:
                return {
                    "session": "Regular Trading",
                    "time": f"{hours}h {minutes}m",
                    "duration": "6h 30m"
                }
        
        return {"session": "After-Hours", "time": f"{hours}h {minutes}m", "duration": "4h"}
    
    def _get_session_progress(self, current_time: datetime) -> Dict[str, Any]:
        """Get progress through current session."""
        if self.trading_hours.is_regular_trading_time(current_time):
            return self._calculate_session_progress(current_time, self.trading_hours.start_time, self.trading_hours.end_time, "Regular Trading")
        elif self.trading_hours.is_pre_market_time(current_time):
            return self._calculate_session_progress(current_time, self.trading_hours.pre_market_start, self.trading_hours.pre_market_end, "Pre-Market")
        elif self.trading_hours.is_after_hours_time(current_time):
            return self._calculate_session_progress(current_time, self.trading_hours.after_hours_start, self.trading_hours.after_hours_end, "After-Hours")
        else:
            return {"session": "Closed", "progress": 0, "elapsed": "0h 0m", "remaining": "0h 0m"}
    
    def _calculate_session_progress(self, current_time: datetime, start_time: str, end_time: str, session_name: str) -> Dict[str, Any]:
        """Calculate progress through a specific session."""
        start_hour, start_minute = map(int, start_time.split(':'))
        end_hour, end_minute = map(int, end_time.split(':'))
        
        session_start = current_time.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        session_end = current_time.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        
        total_duration = session_end - session_start
        elapsed = current_time - session_start
        remaining = session_end - current_time
        
        progress = (elapsed.total_seconds() / total_duration.total_seconds()) * 100 if total_duration.total_seconds() > 0 else 0
        
        return {
            "session": session_name,
            "progress": round(progress, 1),
            "elapsed": f"{int(elapsed.total_seconds() // 3600)}h {int((elapsed.total_seconds() % 3600) // 60)}m",
            "remaining": f"{int(remaining.total_seconds() // 3600)}h {int((remaining.total_seconds() % 3600) // 60)}m"
        }

if __name__ == "__main__":
    print("Testing TradingHoursAdvanced...")
    
    # Test with basic TradingHours
    from .rules_hours import TradingHours
    trading_hours = TradingHours()
    advanced = TradingHoursAdvanced(trading_hours)
    
    print("✅ TradingHoursAdvanced created successfully!")
    
    # Test advanced functionality
    status = advanced.get_trading_status()
    print(f"✅ Trading status: {status}")
    
    session_info = advanced.get_session_info()
    print(f"✅ Session info: {session_info}")
    
    print("✅ TradingHoursAdvanced test completed!")
