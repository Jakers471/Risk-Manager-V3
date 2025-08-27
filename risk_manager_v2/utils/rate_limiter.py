"""
Rate limiting utilities for API calls and enforcement actions.

Prevents overwhelming the broker API and ensures compliance with rate limits.
"""

import time
import threading
from collections import deque
from typing import Optional, Callable, Dict, Any
from risk_manager_v2.core.logger import get_logger

logger = get_logger(__name__)

class RateLimiter:
    """Token bucket rate limiter for API calls."""
    
    def __init__(self, max_tokens: int, refill_rate: float, refill_time: float = 1.0):
        """
        Initialize rate limiter.
        
        Args:
            max_tokens: Maximum tokens in bucket
            refill_rate: Tokens per refill_time
            refill_time: Time interval for refill (seconds)
        """
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.refill_time = refill_time
        
        self.tokens = max_tokens
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens from bucket.
        
        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum wait time (None = wait forever)
        
        Returns:
            True if tokens acquired, False if timeout
        """
        start_time = time.time()
        
        while True:
            with self.lock:
                self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    logger.debug(f"Rate limiter: acquired {tokens} tokens, {self.tokens} remaining")
                    return True
                
                if timeout is not None and (time.time() - start_time) > timeout:
                    logger.warning(f"Rate limiter: timeout waiting for {tokens} tokens")
                    return False
            
            # Wait before retry
            time.sleep(0.1)
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        if elapsed >= self.refill_time:
            tokens_to_add = int(elapsed / self.refill_time * self.refill_rate)
            self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
            self.last_refill = now

class TopStepXRateLimiter:
    """Rate limiter specifically for TopStepX API compliance."""
    
    def __init__(self):
        """Initialize TopStepX API rate limiters."""
        # TopStepX API Rate Limits:
        # - POST /api/History/retrieveBars: 50 requests / 30 seconds
        # - All other Endpoints: 200 requests / 60 seconds
        
        # General API rate limiter (200 requests per 60 seconds)
        self.general_limiter = RateLimiter(
            max_tokens=200,
            refill_rate=200/60,  # 200 tokens per 60 seconds
            refill_time=1.0
        )
        
        # Market data rate limiter (50 requests per 30 seconds)
        self.market_data_limiter = RateLimiter(
            max_tokens=50,
            refill_rate=50/30,  # 50 tokens per 30 seconds
            refill_time=1.0
        )
        
        # Emergency action rate limiter (higher priority)
        self.emergency_limiter = RateLimiter(
            max_tokens=50,
            refill_rate=50/60,  # 50 emergency actions per minute
            refill_time=1.0
        )
    
    def consume(self, bucket: str) -> None:
        """Consume a token from the specified bucket (blocking)."""
        if bucket == "bars":
            if not self.market_data_limiter.acquire(timeout=10.0):
                raise Exception("Market data rate limit exceeded")
        elif bucket == "emergency":
            if not self.emergency_limiter.acquire(timeout=5.0):
                raise Exception("Emergency action rate limit exceeded")
        else:  # general
            if not self.general_limiter.acquire(timeout=10.0):
                raise Exception("General API rate limit exceeded")
    
    def acquire_general(self, timeout: Optional[float] = None) -> bool:
        """Acquire token for general API calls."""
        return self.general_limiter.acquire(timeout=timeout)
    
    def acquire_market_data(self, timeout: Optional[float] = None) -> bool:
        """Acquire token for market data API calls."""
        return self.market_data_limiter.acquire(timeout=timeout)
    
    def acquire_emergency(self, timeout: Optional[float] = None) -> bool:
        """Acquire token for emergency actions (priority)."""
        return self.emergency_limiter.acquire(timeout=timeout)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current rate limiting statistics."""
        return {
            'general_api': {
                'tokens_remaining': self.general_limiter.tokens,
                'max_tokens': self.general_limiter.max_tokens,
                'refill_rate': self.general_limiter.refill_rate
            },
            'market_data': {
                'tokens_remaining': self.market_data_limiter.tokens,
                'max_tokens': self.market_data_limiter.max_tokens,
                'refill_rate': self.market_data_limiter.refill_rate
            },
            'emergency': {
                'tokens_remaining': self.emergency_limiter.tokens,
                'max_tokens': self.emergency_limiter.max_tokens,
                'refill_rate': self.emergency_limiter.refill_rate
            }
        }

class ActionRateLimiter:
    """Rate limiter specifically for enforcement actions."""
    
    def __init__(self, max_actions_per_minute: int = 200):
        """
        Initialize action rate limiter.
        
        Args:
            max_actions_per_minute: Maximum actions per minute
        """
        self.max_actions = max_actions_per_minute
        self.action_times = deque()
        self.lock = threading.Lock()
    
    def can_execute_action(self) -> bool:
        """
        Check if action can be executed.
        
        Returns:
            True if action can be executed
        """
        now = time.time()
        
        with self.lock:
            # Remove old actions (older than 1 minute)
            while self.action_times and (now - self.action_times[0]) > 60:
                self.action_times.popleft()
            
            # Check if we can add another action
            if len(self.action_times) < self.max_actions:
                self.action_times.append(now)
                return True
            
            return False
    
    def get_stats(self) -> dict:
        """Get current rate limiting statistics."""
        now = time.time()
        
        with self.lock:
            # Clean old actions
            while self.action_times and (now - self.action_times[0]) > 60:
                self.action_times.popleft()
            
            return {
                'actions_in_window': len(self.action_times),
                'max_actions_per_minute': self.max_actions,
                'actions_remaining': max(0, self.max_actions - len(self.action_times)),
                'oldest_action_age': now - self.action_times[0] if self.action_times else 0
            }

def rate_limited(max_calls: int, time_window: float = 60.0):
    """
    Decorator for rate limiting function calls.
    
    Args:
        max_calls: Maximum calls per time window
        time_window: Time window in seconds
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        limiter = RateLimiter(max_calls, max_calls / time_window, time_window)
        
        def wrapper(*args, **kwargs):
            if limiter.acquire(timeout=5.0):
                return func(*args, **kwargs)
            else:
                raise Exception(f"Rate limit exceeded for {func.__name__}")
        
        return wrapper
    return decorator

def topstepx_rate_limited(endpoint_type: str = "general"):
    """
    Decorator for TopStepX API rate limiting.
    
    Args:
        endpoint_type: Type of endpoint ("general", "market_data", "emergency")
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        # Create a single rate limiter instance for the decorated function
        if endpoint_type == "market_data":
            limiter = RateLimiter(50, 50/30, 1.0)  # 50 requests per 30 seconds
        elif endpoint_type == "emergency":
            limiter = RateLimiter(50, 50/60, 1.0)  # 50 emergency actions per minute
        else:
            limiter = RateLimiter(200, 200/60, 1.0)  # 200 requests per 60 seconds
        
        def wrapper(*args, **kwargs):
            if limiter.acquire(timeout=10.0):
                return func(*args, **kwargs)
            else:
                logger.error(f"TopStepX rate limit exceeded for {func.__name__} ({endpoint_type})")
                raise Exception(f"TopStepX API rate limit exceeded for {func.__name__}")
        
        return wrapper
    return decorator

def exponential_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for exponential backoff retry logic.
    
    Args:
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {delay}s: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {e}")
                        raise last_exception
            
            raise last_exception
        
        return wrapper
    return decorator

if __name__ == "__main__":
    print("Testing RateLimiter...")
    
    # Test basic rate limiter
    limiter = RateLimiter(max_tokens=10, refill_rate=1, refill_time=1.0)
    print("âœ… Basic RateLimiter created successfully!")
    
    # Test TopStepX rate limiter
    topstepx_limiter = TopStepXRateLimiter()
    print("âœ… TopStepX RateLimiter created successfully!")
    
    # Test action rate limiter
    action_limiter = ActionRateLimiter(max_actions_per_minute=100)
    print("âœ… Action RateLimiter created successfully!")
    
    # Test rate limiting decorator
    @rate_limited(max_calls=5, time_window=10.0)
    def test_function():
        return "Function executed successfully"
    
    print("âœ… Rate limiting decorator created successfully!")
    
    # Test TopStepX rate limiting decorator
    @topstepx_rate_limited(endpoint_type="general")
    def test_api_call():
        return "API call executed successfully"
    
    print("âœ… TopStepX rate limiting decorator created successfully!")
    
    # Test exponential backoff decorator
    @exponential_backoff(max_retries=2, base_delay=0.1)
    def test_retry_function():
        return "Retry function executed successfully"
    
    print("âœ… Exponential backoff decorator created successfully!")
    
    print("âœ… RateLimiter test completed!")


