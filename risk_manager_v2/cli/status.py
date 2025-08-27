"""
System Status Menu

Handles system status, health checks, and diagnostics.
"""

from .base_menu import BaseMenu
from models.rules import RiskRules
from models.account import Account
from models.trading import TradingData

class StatusMenu(BaseMenu):
    """System status and diagnostics menu."""
    
    def run(self):
        """Run the status menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.show_system_status()
            elif choice == "2":
                self.show_auth_status()
            elif choice == "3":
                self.show_api_status()
            elif choice == "4":
                self.show_config_status()
            elif choice == "5":
                self.show_rules_status()
            elif choice == "6":
                self.run_health_check()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display status menu options."""
        print("\n=== SYSTEM STATUS ===")
        print("1) Overall System Status")
        print("2) Authentication Status")
        print("3) API Connection Status")
        print("4) Configuration Status")
        print("5) Risk Rules Status")
        print("6) Run Health Check")
        print("0) Back to main menu")
    
    def show_system_status(self):
        """Show overall system status."""
        print("\n=== OVERALL SYSTEM STATUS ===")
        
        # Check each component
        auth_status = self.auth.is_authenticated()
        api_status = self.client.test_connection() if auth_status else False
        config_status = self.config.config_file.exists()
        
        print(f"Authentication: {'✅ Connected' if auth_status else '❌ Not Connected'}")
        print(f"API Connection: {'✅ Working' if api_status else '❌ Failed'}")
        print(f"Configuration: {'✅ Loaded' if config_status else '❌ Missing'}")
        
        # Overall status
        if auth_status and api_status and config_status:
            print("\n🎉 System Status: HEALTHY")
            print("All components are working correctly.")
        elif auth_status and config_status:
            print("\n⚠️ System Status: PARTIAL")
            print("Authentication and config working, but API connection failed.")
        else:
            print("\n❌ System Status: UNHEALTHY")
            print("Multiple components are not working.")
        
        input("\nPress Enter to continue...")
    
    def show_auth_status(self):
        """Show authentication status details."""
        print("\n=== AUTHENTICATION STATUS ===")
        
        if self.auth.is_authenticated():
            print("✅ Authentication: ACTIVE")
            username = self.config.get("auth.username")
            print(f"   User: {username}")
            
            # Check token expiry
            token_expiry = self.config.get("auth.token_expiry")
            if token_expiry:
                from datetime import datetime
                try:
                    expiry = datetime.fromisoformat(token_expiry)
                    now = datetime.now()
                    if expiry > now:
                        time_left = expiry - now
                        hours = int(time_left.total_seconds() // 3600)
                        minutes = int((time_left.total_seconds() % 3600) // 60)
                        print(f"   Token expires in: {hours}h {minutes}m")
                    else:
                        print("   ⚠️ Token expired")
                except:
                    print("   ⚠️ Token expiry unknown")
        else:
            print("❌ Authentication: INACTIVE")
            print("   No valid authentication credentials found.")
            print("   Use Setup menu to authenticate.")
        
        input("\nPress Enter to continue...")
    
    def show_api_status(self):
        """Show API connection status details."""
        print("\n=== API CONNECTION STATUS ===")
        
        if not self.auth.is_authenticated():
            print("❌ Cannot test API - not authenticated")
            input("\nPress Enter to continue...")
            return
        
        print("Testing API connection...")
        
        try:
            # Test basic connection
            if self.client.test_connection():
                print("✅ API Connection: WORKING")
                print("   TopStepX Gateway API is responding")
                
                # Test account access
                accounts = self.client.get_accounts()
                if accounts:
                    print(f"   Found {len(accounts)} account(s)")
                    for account in accounts[:3]:  # Show first 3
                        account_id = account.get('accountId', 'N/A')
                        name = account.get('name', 'N/A')
                        print(f"     - {name} ({account_id})")
                    if len(accounts) > 3:
                        print(f"     ... and {len(accounts) - 3} more")
                else:
                    print("   ⚠️ No accounts found")
            else:
                print("❌ API Connection: FAILED")
                print("   TopStepX Gateway API is not responding")
                
        except Exception as e:
            print(f"❌ API Connection: ERROR")
            print(f"   Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def show_config_status(self):
        """Show configuration status details."""
        print("\n=== CONFIGURATION STATUS ===")
        
        config_file = self.config.config_file
        if config_file.exists():
            print(f"✅ Configuration File: {config_file}")
            
            # Show key configuration sections
            print("\nConfiguration Sections:")
            
            # API Configuration
            api_url = self.config.get_api_url()
            print(f"   API Base URL: {api_url}")
            
            # Risk Configuration
            max_loss = self.config.get("risk.max_daily_loss")
            max_size = self.config.get("risk.max_position_size")
            print(f"   Max Daily Loss: ${max_loss:,.2f}")
            print(f"   Max Position Size: {max_size} contracts")
            
            # Trading Hours
            start_time = self.config.get("trading_hours.start")
            end_time = self.config.get("trading_hours.end")
            print(f"   Trading Hours: {start_time} - {end_time}")
            
        else:
            print("❌ Configuration File: MISSING")
            print("   Using default configuration")
        
        input("\nPress Enter to continue...")
    
    def show_rules_status(self):
        """Show risk rules status details."""
        print("\n=== RISK RULES STATUS ===")
        
        try:
            # Load risk rules
            risk_rules = RiskRules()
            
            print("✅ Risk Rules: LOADED")
            print("\nCurrent Rules:")
            
            # Daily Limits
            if risk_rules.daily_limits:
                daily = risk_rules.daily_limits
                print(f"   Daily Loss Limit: ${daily.max_daily_loss:,.2f}")
                print(f"   Daily Profit Target: ${daily.daily_profit_target:,.2f}")
                print(f"   Max Daily Trades: {daily.max_daily_trades}")
            else:
                print("   Daily Limits: ❌ Not loaded")
            
            # Position Limits
            if risk_rules.position_limits:
                position = risk_rules.position_limits
                print(f"   Max Position Size: {position.max_position_size} contracts")
                print(f"   Max Open Positions: {position.max_open_positions}")
                print(f"   Max Risk Per Trade: ${position.max_risk_per_trade:,.2f}")
            else:
                print("   Position Limits: ❌ Not loaded")
            
            # Session Rules
            if risk_rules.session_rules:
                session = risk_rules.session_rules
                print(f"   Auto Flatten: {'Enabled' if session.auto_flatten else 'Disabled'}")
                print(f"   Stop on Loss: {'Enabled' if session.stop_on_loss else 'Disabled'}")
                print(f"   Stop on Profit: {'Enabled' if session.stop_on_profit else 'Disabled'}")
            else:
                print("   Session Rules: ❌ Not loaded")
            
        except Exception as e:
            print("❌ Risk Rules: ERROR")
            print(f"   Error loading rules: {e}")
        
        input("\nPress Enter to continue...")
    
    def run_health_check(self):
        """Run comprehensive health check."""
        print("\n=== RUNNING HEALTH CHECK ===")
        
        checks = []
        
        # Check 1: Configuration
        try:
            config_exists = self.config.config_file.exists()
            checks.append(("Configuration", config_exists))
        except:
            checks.append(("Configuration", False))
        
        # Check 2: Authentication
        try:
            auth_working = self.auth.is_authenticated()
            checks.append(("Authentication", auth_working))
        except:
            checks.append(("Authentication", False))
        
        # Check 3: API Connection
        try:
            api_working = self.client.test_connection() if self.auth.is_authenticated() else False
            checks.append(("API Connection", api_working))
        except:
            checks.append(("API Connection", False))
        
        # Check 4: Risk Rules
        try:
            rules = RiskRules()
            rules_working = True
        except:
            rules_working = False
        checks.append(("Risk Rules", rules_working))
        
        # Display results
        print("\nHealth Check Results:")
        for check_name, status in checks:
            status_icon = "✅" if status else "❌"
            status_text = "PASS" if status else "FAIL"
            print(f"   {status_icon} {check_name}: {status_text}")
        
        # Overall health
        passed_checks = sum(1 for _, status in checks if status)
        total_checks = len(checks)
        
        print(f"\nOverall Health: {passed_checks}/{total_checks} checks passed")
        
        if passed_checks == total_checks:
            print("🎉 System is healthy and ready for monitoring!")
        elif passed_checks >= total_checks * 0.75:
            print("⚠️ System is mostly healthy, some issues detected.")
        else:
            print("❌ System has multiple issues that need attention.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("Testing StatusMenu...")
    
    # Test basic initialization
    status_menu = StatusMenu()
    print("✅ StatusMenu created successfully!")
    
    # Test menu display
    status_menu.display_menu()
    print("✅ StatusMenu test completed!")
