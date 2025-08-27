"""
Structured JSON logging utilities.

Provides structured logging with correlation IDs, idempotency keys, and metrics.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, List
from core.logger import get_logger

logger = get_logger(__name__)

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def __init__(self, include_timestamp: bool = True, include_level: bool = True):
        """
        Initialize JSON formatter.
        
        Args:
            include_timestamp: Include timestamp in log entries
            include_level: Include log level in log entries
        """
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
        
        Returns:
            JSON formatted log string
        """
        log_entry = {
            'message': record.getMessage(),
            'logger': record.name,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if self.include_timestamp:
            log_entry['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        if self.include_level:
            log_entry['level'] = record.levelname
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)

class StructuredLogger:
    """Structured logger with correlation and idempotency tracking."""
    
    def __init__(self, name: str, correlation_id: Optional[str] = None):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            correlation_id: Correlation ID for request tracking
        """
        self.logger = logging.getLogger(name)
        self.correlation_id = correlation_id or self._generate_correlation_id()
        self.start_time = time.time()
        self.metrics = {}
    
    def _generate_correlation_id(self) -> str:
        """Generate correlation ID."""
        return f"corr_{uuid.uuid4().hex[:16]}"
    
    def _generate_idempotency_key(self, data: Dict) -> str:
        """Generate idempotency key from data."""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        return f"idem_{hashlib.md5(data_str.encode()).hexdigest()[:16]}"
    
    def log_event(self, event: str, severity: str = "INFO", **kwargs):
        """
        Log structured event.
        
        Args:
            event: Event name
            severity: Log severity
            **kwargs: Additional event data
        """
        log_data = {
            'event': event,
            'severity': severity,
            'correlation_id': self.correlation_id,
            'latency_ms': int((time.time() - self.start_time) * 1000),
            **kwargs
        }
        
        if severity.upper() == 'ERROR':
            self.logger.error(json.dumps(log_data))
        elif severity.upper() == 'WARNING':
            self.logger.warning(json.dumps(log_data))
        elif severity.upper() == 'DEBUG':
            self.logger.debug(json.dumps(log_data))
        else:
            self.logger.info(json.dumps(log_data))
    
    def log_risk_event(self, account_id: str, rule: str, decision: str, 
                      action_plan: Optional[Dict] = None, **kwargs):
        """
        Log risk management event.
        
        Args:
            account_id: Account ID
            rule: Rule that was evaluated
            decision: Decision made
            action_plan: Action plan if applicable
            **kwargs: Additional event data
        """
        log_data = {
            'account_id': account_id,
            'rule': rule,
            'decision': decision,
            'idempotency_key': self._generate_idempotency_key(action_plan) if action_plan else None,
            **kwargs
        }
        
        if action_plan:
            log_data['action_plan'] = action_plan
        
        self.log_event('risk_evaluation', 'INFO', **log_data)
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, 
                    latency_ms: int, quota_remaining: Optional[int] = None, **kwargs):
        """
        Log API call.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            latency_ms: Request latency in milliseconds
            quota_remaining: Remaining API quota
            **kwargs: Additional call data
        """
        log_data = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'latency_ms': latency_ms,
            'quota_remaining': quota_remaining,
            **kwargs
        }
        
        severity = 'ERROR' if status_code >= 400 else 'INFO'
        self.log_event('api_call', severity, **log_data)
    
    def log_enforcement_action(self, account_id: str, action_type: str, 
                             positions_closed: int = 0, orders_cancelled: int = 0,
                             reason: str = "", **kwargs):
        """
        Log enforcement action.
        
        Args:
            account_id: Account ID
            action_type: Type of enforcement action
            positions_closed: Number of positions closed
            orders_cancelled: Number of orders cancelled
            reason: Reason for enforcement
            **kwargs: Additional action data
        """
        log_data = {
            'account_id': account_id,
            'action_type': action_type,
            'positions_closed': positions_closed,
            'orders_cancelled': orders_cancelled,
            'reason': reason,
            **kwargs
        }
        
        self.log_event('enforcement_action', 'WARNING', **log_data)
    
    def log_violation(self, account_id: str, violation_type: str, 
                     current_value: float, limit_value: float, 
                     severity: str = "MEDIUM", **kwargs):
        """
        Log risk violation.
        
        Args:
            account_id: Account ID
            violation_type: Type of violation
            current_value: Current metric value
            limit_value: Limit value
            severity: Violation severity
            **kwargs: Additional violation data
        """
        log_data = {
            'account_id': account_id,
            'violation_type': violation_type,
            'current_value': current_value,
            'limit_value': limit_value,
            'severity': severity,
            'exceeded_by': current_value - limit_value,
            **kwargs
        }
        
        self.log_event('risk_violation', 'WARNING', **log_data)
    
    def log_metric(self, metric_name: str, value: float, unit: str = "", 
                  tags: Optional[Dict[str, str]] = None):
        """
        Log metric.
        
        Args:
            metric_name: Metric name
            value: Metric value
            unit: Metric unit
            tags: Metric tags
        """
        log_data = {
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'tags': tags or {}
        }
        
        self.log_event('metric', 'INFO', **log_data)
        self.metrics[metric_name] = value
    
    def log_session_start(self, account_id: str, session_type: str = "risk_monitoring"):
        """Log session start."""
        self.log_event('session_start', 'INFO', 
                      account_id=account_id, session_type=session_type)
    
    def log_session_end(self, account_id: str, duration_seconds: float, 
                       total_events: int = 0, total_violations: int = 0):
        """Log session end."""
        self.log_event('session_end', 'INFO',
                      account_id=account_id,
                      duration_seconds=duration_seconds,
                      total_events=total_events,
                      total_violations=total_violations)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            'correlation_id': self.correlation_id,
            'duration_ms': int((time.time() - self.start_time) * 1000),
            'metrics': self.metrics.copy()
        }

class RiskLogger:
    """Specialized logger for risk management operations."""
    
    def __init__(self, account_id: str):
        """
        Initialize risk logger.
        
        Args:
            account_id: Account ID for logging
        """
        self.account_id = account_id
        self.structured_logger = StructuredLogger(f"risk_manager.{account_id}")
    
    def log_rule_evaluation(self, rule_name: str, result: bool, 
                           current_value: float, threshold: float, **kwargs):
        """Log rule evaluation."""
        self.structured_logger.log_event('rule_evaluation', 'INFO',
                                        account_id=self.account_id,
                                        rule_name=rule_name,
                                        result=result,
                                        current_value=current_value,
                                        threshold=threshold,
                                        **kwargs)
    
    def log_position_update(self, position_id: str, size: int, 
                           avg_price: float, pnl: float, **kwargs):
        """Log position update."""
        self.structured_logger.log_event('position_update', 'INFO',
                                        account_id=self.account_id,
                                        position_id=position_id,
                                        size=size,
                                        avg_price=avg_price,
                                        pnl=pnl,
                                        **kwargs)
    
    def log_order_update(self, order_id: str, status: str, 
                        filled_quantity: int = 0, **kwargs):
        """Log order update."""
        self.structured_logger.log_event('order_update', 'INFO',
                                        account_id=self.account_id,
                                        order_id=order_id,
                                        status=status,
                                        filled_quantity=filled_quantity,
                                        **kwargs)
    
    def log_emergency_action(self, action: str, reason: str, **kwargs):
        """Log emergency action."""
        self.structured_logger.log_event('emergency_action', 'ERROR',
                                        account_id=self.account_id,
                                        action=action,
                                        reason=reason,
                                        **kwargs)

def setup_json_logging(logger_name: str, log_file: str = None, 
                      log_level: str = "INFO") -> StructuredLogger:
    """
    Setup JSON logging.
    
    Args:
        logger_name: Logger name
        log_file: Log file path (optional)
        log_level: Log level
    
    Returns:
        Configured structured logger
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create JSON formatter
    formatter = JSONFormatter(include_timestamp=True, include_level=True)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return StructuredLogger(logger_name)

def create_risk_logger(account_id: str) -> RiskLogger:
    """
    Create risk logger for account.
    
    Args:
        account_id: Account ID
    
    Returns:
        Risk logger instance
    """
    return RiskLogger(account_id)

if __name__ == "__main__":
    print("Testing Structured JSON Logging utilities...")
    
    # Test JSON formatter
    formatter = JSONFormatter()
    print("✅ JSONFormatter created successfully!")
    
    # Test structured logger
    logger = StructuredLogger("test_logger")
    print("✅ StructuredLogger created successfully!")
    
    # Test risk logger
    risk_logger = RiskLogger("test_account")
    print("✅ RiskLogger created successfully!")
    
    # Test logging functions
    logger.log_event("test_event", "INFO", test_data="sample")
    logger.log_risk_event("test_account", "daily_loss", "PASS", None)
    logger.log_api_call("/api/test", "GET", 200, 150)
    logger.log_enforcement_action("test_account", "close_positions", 2, 1, "daily_loss_limit")
    logger.log_violation("test_account", "daily_loss", 1200.0, 1000.0, "HIGH")
    logger.log_metric("api_calls", 42, "count", {"endpoint": "test"})
    
    # Test setup function
    setup_logger = setup_json_logging("setup_test")
    print("✅ JSON logging setup completed successfully!")
    
    # Test metrics summary
    summary = logger.get_metrics_summary()
    print(f"✅ Metrics summary: {summary['metrics']}")
    
    print("✅ Structured JSON Logging utilities test completed!")
