"""
Retry utilities with exponential backoff and circuit breaker.

Provides robust retry mechanisms for API calls and network operations.
"""

import time
import random
import functools
from typing import Callable, Any, Optional, List, Dict, Union
from core.logger import get_logger

logger = get_logger(__name__)

class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before trying to close circuit
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
        
        Returns:
            Function result
        
        Raises:
            Exception: Circuit breaker open or function failure
        """
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                logger.info("Circuit breaker: attempting to close")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"Circuit breaker: opened after {self.failure_count} failures")

class TopStepXRetryHandler:
    """Retry handler specifically for TopStepX API errors."""
    
    def __init__(self):
        """Initialize TopStepX API retry handler."""
        # TopStepX API Error Codes and Retry Strategies:
        # - 401 Unauthorized: Retry with token refresh
        # - 429 Too Many Requests: Retry with exponential backoff
        # - 5xx Server Errors: Retry with exponential backoff
        # - 4xx Client Errors: Do not retry (except 429)
        
        self.retryable_status_codes = {
            401: "authentication_error",
            429: "rate_limit_error", 
            500: "server_error",
            502: "server_error",
            503: "server_error",
            504: "server_error"
        }
        
        self.retry_strategies = {
            "authentication_error": {
                "max_retries": 1,
                "base_delay": 0.1,
                "max_delay": 1.0,
                "requires_auth_refresh": True
            },
            "rate_limit_error": {
                "max_retries": 5,
                "base_delay": 1.0,
                "max_delay": 60.0,
                "requires_auth_refresh": False
            },
            "server_error": {
                "max_retries": 3,
                "base_delay": 0.5,
                "max_delay": 10.0,
                "requires_auth_refresh": False
            }
        }
    
    def should_retry(self, status_code: int, error_message: str = "") -> bool:
        """Determine if request should be retried based on status code."""
        return status_code in self.retryable_status_codes
    
    def get_retry_strategy(self, status_code: int) -> Dict[str, Any]:
        """Get retry strategy for status code."""
        error_type = self.retryable_status_codes.get(status_code, "server_error")
        return self.retry_strategies.get(error_type, self.retry_strategies["server_error"])
    
    def calculate_delay(self, attempt: int, strategy: Dict[str, Any]) -> float:
        """Calculate delay for retry attempt."""
        base_delay = strategy["base_delay"]
        max_delay = strategy["max_delay"]
        
        # Exponential backoff with jitter
        delay = min(base_delay * (2 ** attempt), max_delay)
        jitter = random.uniform(0.5, 1.5)
        
        return delay * jitter

def with_backoff(func: Callable, tries: int = 5, base: float = 0.2, 
                max_wait: float = 2.0, jitter: bool = True,
                exceptions: List[type] = None) -> Any:
    """
    Execute function with exponential backoff retry logic.
    
    Args:
        func: Function to retry
        tries: Maximum number of attempts
        base: Base delay in seconds
        max_wait: Maximum delay in seconds
        jitter: Add random jitter to prevent thundering herd
        exceptions: List of exceptions to retry on (None = all exceptions)
    
    Returns:
        Function result on success
    
    Raises:
        Exception: Last exception after all retries exhausted
    """
    if exceptions is None:
        exceptions = [Exception]
    
    last_exception = None
    
    for attempt in range(tries):
        try:
            return func()
        except tuple(exceptions) as e:
            last_exception = e
            logger.warning(f"Attempt {attempt + 1}/{tries} failed: {e}")
            
            if attempt == tries - 1:
                break
            
            # Calculate delay with exponential backoff
            delay = min(base * (2 ** attempt), max_wait)
            
            # Add jitter to prevent synchronized retries
            if jitter:
                delay *= (0.5 + random.random() * 0.5)
            
            logger.info(f"Retrying in {delay:.2f} seconds...")
            time.sleep(delay)
    
    raise last_exception

def retry_on_exception(exception_types: tuple = (Exception,), 
                      tries: int = 3, base: float = 0.1, 
                      max_wait: float = 1.0) -> Callable:
    """
    Decorator for retrying functions on specific exceptions.
    
    Args:
        exception_types: Tuple of exception types to retry on
        tries: Maximum number of attempts
        base: Base delay in seconds
        max_wait: Maximum delay in seconds
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return with_backoff(
                lambda: func(*args, **kwargs),
                tries=tries,
                base=base,
                max_wait=max_wait,
                exceptions=list(exception_types)
            )
        return wrapper
    return decorator

def topstepx_retry(max_retries: int = 3, base_delay: float = 0.5, 
                  max_delay: float = 10.0, jitter: bool = True):
    """
    Decorator for TopStepX API retry logic.
    
    Args:
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Add random jitter to prevent thundering herd
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retry_handler = TopStepXRetryHandler()
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if this is a retryable error
                    if hasattr(e, 'status_code'):
                        status_code = e.status_code
                        if not retry_handler.should_retry(status_code):
                            logger.error(f"Non-retryable error {status_code}: {e}")
                            raise e
                        
                        strategy = retry_handler.get_retry_strategy(status_code)
                        if attempt >= strategy["max_retries"]:
                            logger.error(f"Max retries ({strategy['max_retries']}) exceeded for {func.__name__}")
                            raise e
                        
                        delay = retry_handler.calculate_delay(attempt, strategy)
                        logger.warning(f"TopStepX API error {status_code}, retrying in {delay:.2f}s (attempt {attempt + 1})")
                        time.sleep(delay)
                    else:
                        # Generic exception handling
                        if attempt == max_retries:
                            logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                            raise e
                        
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        if jitter:
                            delay *= (0.5 + random.random() * 0.5)
                        
                        logger.warning(f"Generic error, retrying in {delay:.2f}s (attempt {attempt + 1})")
                        time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator

def retry_with_circuit_breaker(failure_threshold: int = 5, 
                              recovery_timeout: float = 60.0,
                              max_retries: int = 3):
    """
    Decorator combining circuit breaker and retry logic.
    
    Args:
        failure_threshold: Circuit breaker failure threshold
        recovery_timeout: Circuit breaker recovery timeout
        max_retries: Maximum retry attempts
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        circuit_breaker = CircuitBreaker(failure_threshold, recovery_timeout)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def retry_func():
                return circuit_breaker.call(func, *args, **kwargs)
            
            return with_backoff(
                retry_func,
                tries=max_retries,
                base=0.5,
                max_wait=10.0,
                jitter=True
            )
        
        return wrapper
    return decorator

def smart_retry(api_type: str = "general", critical: bool = False):
    """
    Smart retry decorator with API-specific strategies.
    
    Args:
        api_type: Type of API call ("general", "auth", "market_data", "enforcement")
        critical: Whether this is a critical operation
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Configure retry strategy based on API type and criticality
            if api_type == "auth":
                max_retries = 2 if critical else 1
                base_delay = 0.1
                max_delay = 1.0
            elif api_type == "enforcement":
                max_retries = 5 if critical else 3
                base_delay = 0.2
                max_delay = 5.0
            elif api_type == "market_data":
                max_retries = 3
                base_delay = 0.5
                max_delay = 10.0
            else:  # general
                max_retries = 3 if critical else 2
                base_delay = 0.3
                max_delay = 5.0
            
            return with_backoff(
                lambda: func(*args, **kwargs),
                tries=max_retries,
                base=base_delay,
                max_wait=max_delay,
                jitter=True
            )
        
        return wrapper
    return decorator

if __name__ == "__main__":
    print("Testing Retry utilities...")
    
    # Test circuit breaker
    circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=10.0)
    print("✅ CircuitBreaker created successfully!")
    
    # Test TopStepX retry handler
    retry_handler = TopStepXRetryHandler()
    print("✅ TopStepXRetryHandler created successfully!")
    
    # Test retry decorators
    @retry_on_exception(tries=2, base=0.1, max_wait=1.0)
    def test_retry_function():
        return "Retry function executed successfully"
    
    print("✅ Retry decorator created successfully!")
    
    # Test TopStepX retry decorator
    @topstepx_retry(max_retries=2, base_delay=0.1, max_delay=1.0)
    def test_topstepx_function():
        return "TopStepX function executed successfully"
    
    print("✅ TopStepX retry decorator created successfully!")
    
    # Test circuit breaker decorator
    @retry_with_circuit_breaker(failure_threshold=2, recovery_timeout=5.0, max_retries=2)
    def test_circuit_breaker_function():
        return "Circuit breaker function executed successfully"
    
    print("✅ Circuit breaker decorator created successfully!")
    
    # Test smart retry decorator
    @smart_retry(api_type="enforcement", critical=True)
    def test_smart_retry_function():
        return "Smart retry function executed successfully"
    
    print("✅ Smart retry decorator created successfully!")
    
    print("✅ Retry utilities test completed!")
