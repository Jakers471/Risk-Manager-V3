"""
Risk Rules Router

Routes to different rule configuration modules.
"""

from .base_menu import BaseMenu

class RulesMenu(BaseMenu):
    """Risk rules configuration router - delegates to specialized modules."""
    
    def __init__(self):
        super().__init__()
        # Initialize rule modules with error handling
        self.daily_rules = None
        self.position_rules = None
        self.hours_rules = None
        self.session_rules = None
        
        # Try to import rule modules (they may not exist yet)
        self._initialize_rule_modules()
    
    def _initialize_rule_modules(self):
        """Initialize rule modules with error handling."""
        try:
            from .rules_daily import RulesDailyMenu
            self.daily_rules = RulesDailyMenu()
        except ImportError:
            self.logger.warning("RulesDailyMenu not available - module not created yet")
        
        try:
            from .rules_position import RulesPositionMenu
            self.position_rules = RulesPositionMenu()
        except ImportError:
            self.logger.warning("RulesPositionMenu not available - module not created yet")
        
        try:
            from .rules_hours import RulesHoursMenu
            self.hours_rules = RulesHoursMenu()
        except ImportError:
            self.logger.warning("RulesHoursMenu not available - module not created yet")
        
        try:
            from .rules_session import RulesSessionMenu
            self.session_rules = RulesSessionMenu()
        except ImportError:
            self.logger.warning("RulesSessionMenu not available - module not created yet")
    
    def run(self):
        """Run the rules menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self._run_daily_rules()
            elif choice == "2":
                self._run_position_rules()
            elif choice == "3":
                self._run_hours_rules()
            elif choice == "4":
                self._run_session_rules()
            elif choice == "5":
                self.view_all_rules()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display rules menu options."""
        print("\n=== RISK RULES CONFIGURATION ===")
        print("1) Daily Limits")
        print("2) Position Limits")
        print("3) Trading Hours")
        print("4) Session Rules")
        print("5) View All Rules")
        print("0) Back to main menu")
    
    def _run_daily_rules(self):
        """Run daily rules menu with error handling."""
        if self.daily_rules:
            self.daily_rules.run()
        else:
            print("\n=== DAILY LIMITS ===")
            print("Daily limits configuration not implemented yet.")
            print("This will include:")
            print("- Maximum daily loss limits")
            print("- Maximum daily profit targets")
            print("- Daily trade count limits")
            print("- Daily volume limits")
            input("\nPress Enter to continue...")
    
    def _run_position_rules(self):
        """Run position rules menu with error handling."""
        if self.position_rules:
            self.position_rules.run()
        else:
            print("\n=== POSITION LIMITS ===")
            print("Position limits configuration not implemented yet.")
            print("This will include:")
            print("- Maximum position size")
            print("- Maximum open positions")
            print("- Position concentration limits")
            print("- Stop loss levels")
            input("\nPress Enter to continue...")
    
    def _run_hours_rules(self):
        """Run trading hours menu with error handling."""
        if self.hours_rules:
            self.hours_rules.run()
        else:
            print("\n=== TRADING HOURS ===")
            print("Trading hours configuration not implemented yet.")
            print("This will include:")
            print("- Market hours configuration")
            print("- Pre-market and after-hours settings")
            print("- Time zone management")
            print("- Holiday calendar")
            input("\nPress Enter to continue...")
    
    def _run_session_rules(self):
        """Run session rules menu with error handling."""
        if self.session_rules:
            self.session_rules.run()
        else:
            print("\n=== SESSION RULES ===")
            print("Session rules configuration not implemented yet.")
            print("This will include:")
            print("- Session-based limits")
            print("- Intraday position management")
            print("- End-of-day flattening rules")
            print("- Session performance tracking")
            input("\nPress Enter to continue...")
    
    def view_all_rules(self):
        """View all current rules."""
        print("\n=== ALL CURRENT RULES ===")
        
        # Show current configuration from settings
        try:
            risk_config = self.config.get("risk", {})
            trading_hours = self.config.get("trading_hours", {})
            
            print("Current Risk Configuration:")
            print("-" * 40)
            for key, value in risk_config.items():
                print(f"  {key}: {value}")
            
            print("\nCurrent Trading Hours:")
            print("-" * 40)
            for key, value in trading_hours.items():
                print(f"  {key}: {value}")
            
            # Show rule module status
            print("\nRule Module Status:")
            print("-" * 40)
            print(f"  Daily Rules: {'âœ… Available' if self.daily_rules else 'âŒ Not implemented'}")
            print(f"  Position Rules: {'âœ… Available' if self.position_rules else 'âŒ Not implemented'}")
            print(f"  Hours Rules: {'âœ… Available' if self.hours_rules else 'âŒ Not implemented'}")
            print(f"  Session Rules: {'âœ… Available' if self.session_rules else 'âŒ Not implemented'}")
            
        except Exception as e:
            self.logger.error(f"Error viewing rules: {e}")
            print("Error loading current rules configuration.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("Testing RulesMenu...")
    
    # Test basic initialization
    rules = RulesMenu()
    print("âœ… RulesMenu created successfully!")
    
    # Test display menu
    rules.display_menu()
    print("âœ… RulesMenu test completed!")


