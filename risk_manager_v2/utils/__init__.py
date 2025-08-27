"""
Utility modules for risk management system.

Provides helper functions, data processing utilities, and common operations
used throughout the risk management system.
"""

# Future utility modules to be implemented:
# - validators.py: Data validation functions
# - formatters.py: Data formatting utilities
# - calculators.py: Financial calculation helpers
# - converters.py: Data type conversion utilities

__all__ = [
    # Validators (to be implemented)
    # 'validate_account_id',
    # 'validate_risk_rules',
    # 'validate_trading_data',
    
    # Formatters (to be implemented)
    # 'format_currency',
    # 'format_percentage',
    # 'format_timestamp',
    # 'format_duration',
    
    # Calculators (to be implemented)
    # 'calculate_pnl',
    # 'calculate_win_rate',
    # 'calculate_profit_factor',
    # 'calculate_max_drawdown',
    
    # Converters (to be implemented)
    # 'convert_enum_to_api',
    # 'convert_api_to_enum',
    # 'convert_timestamp',
    # 'convert_side'
]

__version__ = "1.0.0"
__author__ = "Risk Manager V3 Team"
__description__ = "Utility modules for automated risk management system"

def get_utils_info():
    """Get information about available utility modules."""
    return {
        'version': __version__,
        'description': __description__,
        'planned_modules': [
            'validators.py - Data validation functions',
            'formatters.py - Data formatting utilities', 
            'calculators.py - Financial calculation helpers',
            'converters.py - Data type conversion utilities'
        ]
    }

