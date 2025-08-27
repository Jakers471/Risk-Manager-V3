"""
Risk Rules Data Models Router

Routes to different rule type modules.
"""

class RiskRules:
    """Complete risk rules configuration - aggregates all rule types."""
    
    def __init__(self):
        # Initialize rule modules with error handling
        self.daily_limits = None
        self.position_limits = None
        self.trading_hours = None
        self.session_rules = None
        self.custom_rules = {}  # For your custom rules
        
        # Try to import rule modules (they may not exist yet)
        self._initialize_rule_modules()
    
    def _initialize_rule_modules(self):
        """Initialize rule modules with error handling."""
        try:
            from .rules_daily import DailyLimits
            self.daily_limits = DailyLimits()
        except ImportError:
            # DailyLimits module not created yet
            pass
        
        try:
            from .rules_position import PositionLimits
            self.position_limits = PositionLimits()
        except ImportError:
            # PositionLimits module not created yet
            pass
        
        try:
            from .rules_hours import TradingHours
            self.trading_hours = TradingHours()
        except ImportError:
            # TradingHours module not created yet
            pass
        
        try:
            from .rules_session import SessionRules
            self.session_rules = SessionRules()
        except ImportError:
            # SessionRules module not created yet
            pass
    
    def add_custom_rule(self, rule_name: str, rule):
        """Add a custom rule type."""
        self.custom_rules[rule_name] = rule
    
    def get_custom_rule(self, rule_name: str):
        """Get a custom rule type."""
        return self.custom_rules.get(rule_name)
    
    def to_dict(self):
        """Convert to dictionary for storage."""
        data = {}
        
        # Add available rule modules
        if self.daily_limits:
            data["daily_limits"] = self.daily_limits.to_dict()
        if self.position_limits:
            data["position_limits"] = self.position_limits.to_dict()
        if self.trading_hours:
            data["trading_hours"] = self.trading_hours.to_dict()
        if self.session_rules:
            data["session_rules"] = self.session_rules.to_dict()
        
        # Add custom rules
        for name, rule in self.custom_rules.items():
            data[f"custom_{name}"] = rule.to_dict()
        
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        rules = cls()
        
        # Load available rule modules
        if "daily_limits" in data and rules.daily_limits:
            rules.daily_limits = rules.daily_limits.__class__.from_dict(data["daily_limits"])
        if "position_limits" in data and rules.position_limits:
            rules.position_limits = rules.position_limits.__class__.from_dict(data["position_limits"])
        if "trading_hours" in data and rules.trading_hours:
            rules.trading_hours = rules.trading_hours.__class__.from_dict(data["trading_hours"])
        if "session_rules" in data and rules.session_rules:
            rules.session_rules = rules.session_rules.__class__.from_dict(data["session_rules"])
        
        # Load custom rules
        for key, value in data.items():
            if key.startswith("custom_"):
                rule_name = key[7:]  # Remove "custom_" prefix
                # You can add custom rule loading logic here
        
        return rules
    
    def get_rule_status(self):
        """Get status of all rule modules."""
        status = {
            "daily_limits": self.daily_limits is not None,
            "position_limits": self.position_limits is not None,
            "trading_hours": self.trading_hours is not None,
            "session_rules": self.session_rules is not None,
            "custom_rules": len(self.custom_rules)
        }
        return status

if __name__ == "__main__":
    print("Testing RiskRules...")
    
    # Test basic initialization
    rules = RiskRules()
    print("✅ RiskRules created successfully!")
    
    # Test rule status
    status = rules.get_rule_status()
    print(f"✅ Rule status: {status}")
    
    # Test to_dict
    data = rules.to_dict()
    print(f"✅ To dict: {data}")
    
    print("✅ RiskRules test completed!")
