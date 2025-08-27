"""
Auto-Enforcement Engine

Real-time monitoring and automated risk management system.

This module provides the core enforcement engine that continuously monitors
trading accounts and automatically enforces risk management rules in real-time.

Key Components:
- RiskMonitor: Continuous monitoring of account status and positions
- RuleEnforcer: Automated enforcement of risk rules and limits
- AlertManager: Real-time alerts and notifications for rule violations
- ActionExecutor: Automated actions (close positions, cancel orders, etc.)
- WebSocketManager: Real-time data streaming from TopStepX API

Features:
- Real-time position monitoring and P&L tracking
- Automated daily loss limit enforcement
- Position size and count limit monitoring
- Trading hours enforcement
- Session timeout management
- Emergency stop functionality
- Comprehensive alerting system
- Action logging and audit trails

Usage:
    from engine import RiskManager
    
    # Initialize the risk manager
    risk_manager = RiskManager()
    
    # Start monitoring
    risk_manager.start_monitoring()
    
    # Stop monitoring
    risk_manager.stop_monitoring()
"""

from .monitor import RiskMonitor

__all__ = [
    'RiskMonitor'
]

__version__ = "1.0.0"
__author__ = "Risk Manager V3 Team"
__description__ = "Real-time automated risk management system for TopStepX trading"

