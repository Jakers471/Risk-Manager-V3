"""
Trading time window utilities with advanced session handling.

Handles trading hours, session windows, and market timing logic.
"""

from datetime import datetime, time, timedelta
from typing import Optional, List, Dict, Any
import pytz
from risk_manager_v2.core.logger import get_logger

logger = get_logger(__name__)

class TradingSession:
    """Represents a trading session with start/end times."""
    
    def __init__(self, name: str, start_time: str, end_time: str, 
                 timezone: str = "America/New_York"):
        """
        Initialize trading session.
        
        Args:
            name: Session name (e.g., "regular", "pre_market", "after_hours")
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format
            timezone: Timezone string
        """
        self.name = name
        self.start_time = self._parse_time(start_time)
        self.end_time = self._parse_time(end_time)
        self.timezone = pytz.timezone(timezone)
    
    def _parse_time(self, time_str: str) -> time:
        """Parse time string to time object."""
        try:
            hour, minute = map(int, time_str.split(':'))
            return time(hour, minute)
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. Use HH:MM")
    
    def is_active(self, check_time: Optional[datetime] = None) -> bool:
        """Check if session is currently active."""
        if check_time is None:
            check_time = datetime.now(self.timezone)
        elif check_time.tzinfo is None:
            check_time = self.timezone.localize(check_time)
        
        current_time = check_time.time()
        
        # Handle overnight sessions
        if self.start_time > self.end_time:
            return current_time >= self.start_time or current_time <= self.end_time
        else:
            return self.start_time <= current_time <= self.end_time
    
    def time_until_open(self, check_time: Optional[datetime] = None) -> Optional[float]:
        """Calculate seconds until session opens."""
        if check_time is None:
            check_time = datetime.now(self.timezone)
        elif check_time.tzinfo is None:
            check_time = self.timezone.localize(check_time)
        
        # Get next occurrence of start time
        next_start = check_time.replace(
            hour=self.start_time.hour,
            minute=self.start_time.minute,
            second=0,
            microsecond=0
        )
        
        # If start time has passed today, get tomorrow's start
        if next_start <= check_time:
            next_start += timedelta(days=1)
        
        return (next_start - check_time).total_seconds()
    
    def time_until_close(self, check_time: Optional[datetime] = None) -> Optional[float]:
        """Calculate seconds until session closes."""
        if check_time is None:
            check_time = datetime.now(self.timezone)
        elif check_time.tzinfo is None:
            check_time = self.timezone.localize(check_time)
        
        # Get today's end time
        today_end = check_time.replace(
            hour=self.end_time.hour,
            minute=self.end_time.minute,
            second=0,
            microsecond=0
        )
        
        # If end time has passed, session is already closed
        if today_end <= check_time:
            return None
        
        return (today_end - check_time).total_seconds()
    
    def get_session_progress(self, check_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get session progress information."""
        if check_time is None:
            check_time = datetime.now(self.timezone)
        elif check_time.tzinfo is None:
            check_time = self.timezone.localize(check_time)
        
        if not self.is_active(check_time):
            return {
                'active': False,
                'progress': 0.0,
                'time_remaining': None,
                'time_elapsed': None
            }
        
        # Calculate session duration and progress
        session_start = check_time.replace(
            hour=self.start_time.hour,
            minute=self.start_time.minute,
            second=0,
            microsecond=0
        )
        
        session_end = check_time.replace(
            hour=self.end_time.hour,
            minute=self.end_time.minute,
            second=0,
            microsecond=0
        )
        
        # Handle overnight sessions
        if self.start_time > self.end_time:
            if check_time.time() < self.start_time:
                session_start -= timedelta(days=1)
            else:
                session_end += timedelta(days=1)
        
        total_duration = (session_end - session_start).total_seconds()
        elapsed = (check_time - session_start).total_seconds()
        remaining = (session_end - check_time).total_seconds()
        
        progress = min(100.0, max(0.0, (elapsed / total_duration) * 100))
        
        return {
            'active': True,
            'progress': progress,
            'time_remaining': remaining,
            'time_elapsed': elapsed,
            'total_duration': total_duration
        }

class TradingCalendar:
    """Manages multiple trading sessions."""
    
    def __init__(self, timezone: str = "America/New_York"):
        """
        Initialize trading calendar.
        
        Args:
            timezone: Default timezone
        """
        self.timezone = pytz.timezone(timezone)
        self.sessions = {}
    
    def add_session(self, name: str, start_time: str, end_time: str):
        """Add a trading session."""
        self.sessions[name] = TradingSession(name, start_time, end_time, str(self.timezone))
    
    def is_market_open(self) -> bool:
        """Check if any trading session is active."""
        for session in self.sessions.values():
            if session.is_active():
                return True
        return False
    
    def get_active_session(self) -> Optional[str]:
        """Get name of currently active session."""
        for name, session in self.sessions.items():
            if session.is_active():
                return name
        return None
    
    def time_until_next_session(self) -> Optional[float]:
        """Calculate seconds until next session opens."""
        now = datetime.now(self.timezone)
        min_wait = float('inf')
        
        for session in self.sessions.values():
            wait = session.time_until_open(now)
            if wait is not None and wait < min_wait:
                min_wait = wait
        
        return min_wait if min_wait != float('inf') else None
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get comprehensive session status."""
        now = datetime.now(self.timezone)
        status = {
            'current_time': now.isoformat(),
            'timezone': str(self.timezone),
            'market_open': self.is_market_open(),
            'active_session': self.get_active_session(),
            'time_until_next': self.time_until_next_session(),
            'sessions': {}
        }
        
        for name, session in self.sessions.items():
            session_status = session.get_session_progress(now)
            status['sessions'][name] = {
                'active': session.is_active(now),
                'progress': session_status.get('progress', 0.0),
                'time_remaining': session_status.get('time_remaining'),
                'time_until_open': session.time_until_open(now)
            }
        
        return status

def create_standard_calendar() -> TradingCalendar:
    """Create standard US equity trading calendar."""
    calendar = TradingCalendar("America/New_York")
    
    # Regular trading hours (9:30 AM - 4:00 PM ET)
    calendar.add_session("regular", "09:30", "16:00")
    
    # Pre-market (4:00 AM - 9:30 AM ET)
    calendar.add_session("pre_market", "04:00", "09:30")
    
    # After-hours (4:00 PM - 8:00 PM ET)
    calendar.add_session("after_hours", "16:00", "20:00")
    
    return calendar

def create_topstepx_calendar() -> TradingCalendar:
    """Create TopStepX-specific trading calendar."""
    calendar = TradingCalendar("America/New_York")
    
    # TopStepX trading hours based on configuration
    # Regular trading hours
    calendar.add_session("regular", "09:30", "16:00")
    
    # Pre-market (if enabled)
    calendar.add_session("pre_market", "04:00", "09:30")
    
    # After-hours (if enabled)
    calendar.add_session("after_hours", "16:00", "20:00")
    
    return calendar

def is_trading_allowed(check_time: Optional[datetime] = None) -> bool:
    """
    Quick check if trading is allowed.
    
    Args:
        check_time: Time to check (defaults to now)
    
    Returns:
        True if trading is allowed
    """
    calendar = create_standard_calendar()
    return calendar.is_market_open()

def get_market_status() -> dict:
    """
    Get comprehensive market status.
    
    Returns:
        Dictionary with market status information
    """
    calendar = create_standard_calendar()
    return calendar.get_session_status()

def get_topstepx_market_status() -> dict:
    """
    Get TopStepX-specific market status.
    
    Returns:
        Dictionary with TopStepX market status information
    """
    calendar = create_topstepx_calendar()
    status = calendar.get_session_status()
    status['platform'] = 'TopStepX'
    return status

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string."""
    if seconds is None or seconds < 0:
        return "N/A"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def get_next_trading_day() -> datetime:
    """Get the next trading day (Monday-Friday)."""
    now = datetime.now()
    current_weekday = now.weekday()
    
    # If it's Friday (4), next trading day is Monday (0)
    if current_weekday == 4:  # Friday
        days_ahead = 3
    elif current_weekday == 5:  # Saturday
        days_ahead = 2
    elif current_weekday == 6:  # Sunday
        days_ahead = 1
    else:  # Monday-Thursday
        days_ahead = 1
    
    next_trading_day = now + timedelta(days=days_ahead)
    return next_trading_day.replace(hour=9, minute=30, second=0, microsecond=0)

if __name__ == "__main__":
    print("Testing Trading Time Window utilities...")
    
    # Test trading session
    session = TradingSession("regular", "09:30", "16:00")
    print("âœ… TradingSession created successfully!")
    
    # Test trading calendar
    calendar = create_standard_calendar()
    print("âœ… TradingCalendar created successfully!")
    
    # Test market status
    status = get_market_status()
    print("âœ… Market status retrieved successfully!")
    print(f"Market open: {status['market_open']}")
    print(f"Active session: {status['active_session']}")
    
    # Test TopStepX market status
    topstepx_status = get_topstepx_market_status()
    print("âœ… TopStepX market status retrieved successfully!")
    print(f"Platform: {topstepx_status['platform']}")
    
    # Test duration formatting
    formatted = format_duration(3661)  # 1 hour, 1 minute, 1 second
    print(f"âœ… Duration formatting: {formatted}")
    
    # Test next trading day
    next_day = get_next_trading_day()
    print(f"âœ… Next trading day: {next_day.strftime('%Y-%m-%d %H:%M')}")
    
    print("âœ… Trading Time Window utilities test completed!")


