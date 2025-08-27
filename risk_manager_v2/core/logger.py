"""
Centralized Logging System

Provides consistent logging across the entire application.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

class LoggerMixin:
    """Mixin to add logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return logging.getLogger(self.__class__.__name__)

def setup_logging(
    level: str = "INFO",
    log_file: str = "logs/risk_manager.log",
    max_size: str = "10MB",
    backup_count: int = 5
) -> logging.Logger:
    """Setup centralized logging system."""
    
    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert max_size string to bytes
    size_map = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}
    if max_size.endswith(("KB", "MB", "GB")):
        size_str = max_size[:-2]
        size_unit = max_size[-2:]
        max_bytes = int(float(size_str) * size_map[size_unit])
    else:
        max_bytes = int(max_size)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)

class RiskManagerLogger:
    """Specialized logger for risk management operations."""
    
    def __init__(self, name: str = "RiskManager"):
        self.logger = get_logger(name)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)

if __name__ == "__main__":
    print("Testing logging system...")
    
    # Test setup_logging
    logger = setup_logging()
    print("✅ Logging system setup successfully!")
    
    # Test RiskManagerLogger
    risk_logger = RiskManagerLogger("TestLogger")
    risk_logger.info("Test info message")
    risk_logger.warning("Test warning message")
    print("✅ RiskManagerLogger test completed!")
    
    # Test LoggerMixin
    class TestClass(LoggerMixin):
        def test_method(self):
            self.logger.info("Test method called")
    
    test_obj = TestClass()
    test_obj.test_method()
    print("✅ LoggerMixin test completed!")
