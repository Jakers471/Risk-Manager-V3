"""
Session Rules

Handles session enforcement and auto-flattening configuration.
"""

from .base_menu import BaseMenu

class RulesSessionMenu(BaseMenu):
    """Session rules configuration menu."""
    
    def run(self):
        """Run the session rules menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.view_rules()
            elif choice == "2":
                self.set_auto_flatten()
            elif choice == "3":
                self.set_stop_on_loss()
            elif choice == "4":
                self.set_stop_on_profit()
            elif choice == "5":
                self.set_end_of_day_flatten()
            elif choice == "6":
                self.set_session_timeout()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display session rules menu options."""
        print("\n=== SESSION RULES ===")
        print("1) View Current Rules")
        print("2) Set Auto Flatten")
        print("3) Set Stop on Loss")
        print("4) Set Stop on Profit")
        print("5) Set End-of-Day Flatten")
        print("6) Set Session Timeout")
        print("0) Back to rules menu")
    
    def view_rules(self):
        """View current session rules."""
        print("\n=== CURRENT SESSION RULES ===")
        print("-" * 50)
        
        # Get current values with defaults
        auto_flatten = self.config.get('risk.auto_flatten', True)
        stop_on_loss = self.config.get('risk.stop_on_loss', True)
        stop_on_profit = self.config.get('risk.stop_on_profit', True)
        end_of_day_flatten = self.config.get('risk.end_of_day_flatten', True)
        session_timeout = self.config.get('risk.session_timeout', 30)
        
        print(f"Auto Flatten: {'✅ ENABLED' if auto_flatten else '❌ DISABLED'}")
        print(f"Stop on Loss: {'✅ ENABLED' if stop_on_loss else '❌ DISABLED'}")
        print(f"Stop on Profit: {'✅ ENABLED' if stop_on_profit else '❌ DISABLED'}")
        print(f"End-of-Day Flatten: {'✅ ENABLED' if end_of_day_flatten else '❌ DISABLED'}")
        print(f"Session Timeout: {session_timeout} minutes")
        
        print("\nRule Descriptions:")
        print("• Auto Flatten: Close positions when risk limits are breached")
        print("• Stop on Loss: Stop trading when daily loss limit is hit")
        print("• Stop on Profit: Stop trading when daily profit target is hit")
        print("• End-of-Day Flatten: Close all positions at market close")
        print("• Session Timeout: Auto-logout after inactivity period")
        
        input("\nPress Enter to continue...")
    
    def set_auto_flatten(self):
        """Set auto flatten behavior."""
        current = self.config.get('risk.auto_flatten', True)
        print(f"\n=== SET AUTO FLATTEN ===")
        print(f"Current Auto Flatten: {'✅ ENABLED' if current else '❌ DISABLED'}")
        
        print("\nAuto Flatten will automatically close positions when:")
        print("• Daily loss limit is exceeded")
        print("• Position size limits are breached")
        print("• Trading outside allowed hours")
        print("• Account margin requirements are not met")
        
        choice = input("\nEnable Auto Flatten? (y/N): ").strip().lower()
        try:
            if choice in ['y', 'yes']:
                self.config.set('risk.auto_flatten', True)
                print("✅ Auto Flatten ENABLED")
            elif choice in ['n', 'no']:
                self.config.set('risk.auto_flatten', False)
                print("✅ Auto Flatten DISABLED")
            else:
                print("❌ Invalid choice. Using current setting.")
        except Exception as e:
            self.logger.error(f"Error setting auto flatten: {e}")
            print("❌ Error saving configuration.")
        
        input("\nPress Enter to continue...")
    
    def set_stop_on_loss(self):
        """Set stop on loss behavior."""
        current = self.config.get('risk.stop_on_loss', True)
        print(f"\n=== SET STOP ON LOSS ===")
        print(f"Current Stop on Loss: {'✅ ENABLED' if current else '❌ DISABLED'}")
        
        print("\nStop on Loss will:")
        print("• Close all positions when daily loss limit is hit")
        print("• Cancel all pending orders")
        print("• Prevent new trades for the rest of the day")
        print("• Send notification alerts")
        
        choice = input("\nEnable Stop on Loss? (y/N): ").strip().lower()
        try:
            if choice in ['y', 'yes']:
                self.config.set('risk.stop_on_loss', True)
                print("✅ Stop on Loss ENABLED")
            elif choice in ['n', 'no']:
                self.config.set('risk.stop_on_loss', False)
                print("✅ Stop on Loss DISABLED")
            else:
                print("❌ Invalid choice. Using current setting.")
        except Exception as e:
            self.logger.error(f"Error setting stop on loss: {e}")
            print("❌ Error saving configuration.")
        
        input("\nPress Enter to continue...")
    
    def set_stop_on_profit(self):
        """Set stop on profit behavior."""
        current = self.config.get('risk.stop_on_profit', True)
        print(f"\n=== SET STOP ON PROFIT ===")
        print(f"Current Stop on Profit: {'✅ ENABLED' if current else '❌ DISABLED'}")
        
        print("\nStop on Profit will:")
        print("• Close all positions when daily profit target is hit")
        print("• Cancel all pending orders")
        print("• Prevent new trades for the rest of the day")
        print("• Send notification alerts")
        
        choice = input("\nEnable Stop on Profit? (y/N): ").strip().lower()
        try:
            if choice in ['y', 'yes']:
                self.config.set('risk.stop_on_profit', True)
                print("✅ Stop on Profit ENABLED")
            elif choice in ['n', 'no']:
                self.config.set('risk.stop_on_profit', False)
                print("✅ Stop on Profit DISABLED")
            else:
                print("❌ Invalid choice. Using current setting.")
        except Exception as e:
            self.logger.error(f"Error setting stop on profit: {e}")
            print("❌ Error saving configuration.")
        
        input("\nPress Enter to continue...")
    
    def set_end_of_day_flatten(self):
        """Set end-of-day flatten behavior."""
        current = self.config.get('risk.end_of_day_flatten', True)
        print(f"\n=== SET END-OF-DAY FLATTEN ===")
        print(f"Current End-of-Day Flatten: {'✅ ENABLED' if current else '❌ DISABLED'}")
        
        print("\nEnd-of-Day Flatten will:")
        print("• Close all positions at market close")
        print("• Cancel all pending orders")
        print("• Reset daily counters for next session")
        print("• Generate end-of-day report")
        
        choice = input("\nEnable End-of-Day Flatten? (y/N): ").strip().lower()
        try:
            if choice in ['y', 'yes']:
                self.config.set('risk.end_of_day_flatten', True)
                print("✅ End-of-Day Flatten ENABLED")
            elif choice in ['n', 'no']:
                self.config.set('risk.end_of_day_flatten', False)
                print("✅ End-of-Day Flatten DISABLED")
            else:
                print("❌ Invalid choice. Using current setting.")
        except Exception as e:
            self.logger.error(f"Error setting end-of-day flatten: {e}")
            print("❌ Error saving configuration.")
        
        input("\nPress Enter to continue...")
    
    def set_session_timeout(self):
        """Set session timeout duration."""
        current = self.config.get('risk.session_timeout', 30)
        print(f"\n=== SET SESSION TIMEOUT ===")
        print(f"Current Session Timeout: {current} minutes")
        
        print("\nSession Timeout will:")
        print("• Auto-logout after specified inactivity period")
        print("• Close all positions before logout")
        print("• Cancel all pending orders")
        print("• Save session state for next login")
        
        try:
            new_timeout = input("New Session Timeout (minutes, 5-480): ").strip()
            if new_timeout:
                new_timeout = int(new_timeout)
                
                # Validate input
                if 5 <= new_timeout <= 480:
                    self.config.set('risk.session_timeout', new_timeout)
                    print(f"✅ Session Timeout set to {new_timeout} minutes")
                else:
                    print("❌ Timeout must be between 5 and 480 minutes.")
            else:
                print("❌ No timeout value entered.")
                
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")
        except Exception as e:
            self.logger.error(f"Error setting session timeout: {e}")
            print("❌ Error saving configuration.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("Testing RulesSessionMenu...")
    
    # Test basic initialization
    session_rules = RulesSessionMenu()
    print("✅ RulesSessionMenu created successfully!")
    
    # Test display menu
    session_rules.display_menu()
    print("✅ RulesSessionMenu test completed!")
