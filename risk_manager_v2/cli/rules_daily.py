"""
Daily Limits Rules

Handles daily loss, profit, and trade count limits.
"""

from .base_menu import BaseMenu

class RulesDailyMenu(BaseMenu):
    """Daily limits configuration menu."""
    
    def run(self):
        """Run the daily rules menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.view_rules()
            elif choice == "2":
                self.set_daily_loss()
            elif choice == "3":
                self.set_daily_profit()
            elif choice == "4":
                self.set_daily_trades()
            elif choice == "5":
                self.set_daily_volume()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display daily rules menu options."""
        print("\n=== DAILY LIMITS ===")
        print("1) View Current Limits")
        print("2) Set Daily Loss Limit")
        print("3) Set Daily Profit Target")
        print("4) Set Max Daily Trades")
        print("5) Set Max Daily Volume")
        print("0) Back to rules menu")
    
    def view_rules(self):
        """View current daily limits."""
        print("\n=== CURRENT DAILY LIMITS ===")
        print("-" * 40)
        
        # Get current values with defaults
        max_daily_loss = self.config.get('risk.max_daily_loss', 1000.0)
        daily_profit_target = self.config.get('risk.daily_profit_target', 2000.0)
        max_daily_trades = self.config.get('risk.max_daily_trades', 10)
        max_daily_volume = self.config.get('risk.max_daily_volume', 100000.0)
        
        print(f"Max Daily Loss: ${max_daily_loss:,.2f}")
        print(f"Daily Profit Target: ${daily_profit_target:,.2f}")
        print(f"Max Daily Trades: {max_daily_trades}")
        print(f"Max Daily Volume: ${max_daily_volume:,.2f}")
        
        # Show status indicators
        print("\nStatus:")
        if max_daily_loss > 0:
            print("âœ… Daily loss limit: ACTIVE")
        else:
            print("âŒ Daily loss limit: DISABLED")
            
        if daily_profit_target > 0:
            print("âœ… Daily profit target: ACTIVE")
        else:
            print("âŒ Daily profit target: DISABLED")
            
        if max_daily_trades > 0:
            print("âœ… Daily trade limit: ACTIVE")
        else:
            print("âŒ Daily trade limit: DISABLED")
            
        if max_daily_volume > 0:
            print("âœ… Daily volume limit: ACTIVE")
        else:
            print("âŒ Daily volume limit: DISABLED")
        
        input("\nPress Enter to continue...")
    
    def set_daily_loss(self):
        """Set daily loss limit."""
        current = self.config.get('risk.max_daily_loss', 1000.0)
        print(f"\n=== SET DAILY LOSS LIMIT ===")
        print(f"Current Max Daily Loss: ${current:,.2f}")
        print("Enter 0 to disable daily loss limit")
        
        try:
            new_value = input("New Max Daily Loss: $").strip()
            if new_value:
                new_value = float(new_value)
                
                # Validate input
                if new_value < 0:
                    print("âŒ Daily loss limit cannot be negative.")
                    return
                
                if new_value > 100000:
                    print("âŒ Daily loss limit cannot exceed $100,000.")
                    return
                
                self.config.set('risk.max_daily_loss', new_value)
                
                if new_value == 0:
                    print("âœ… Daily loss limit DISABLED")
                else:
                    print(f"âœ… Max Daily Loss set to ${new_value:,.2f}")
                    
        except ValueError:
            print("âŒ Invalid input. Please enter a valid number.")
        except Exception as e:
            self.logger.error(f"Error setting daily loss limit: {e}")
            print("âŒ Error saving configuration.")
        
        input("\nPress Enter to continue...")
    
    def set_daily_profit(self):
        """Set daily profit target."""
        current = self.config.get('risk.daily_profit_target', 2000.0)
        print(f"\n=== SET DAILY PROFIT TARGET ===")
        print(f"Current Daily Profit Target: ${current:,.2f}")
        print("Enter 0 to disable daily profit target")
        
        try:
            new_value = input("New Daily Profit Target: $").strip()
            if new_value:
                new_value = float(new_value)
                
                # Validate input
                if new_value < 0:
                    print("âŒ Daily profit target cannot be negative.")
                    return
                
                if new_value > 100000:
                    print("âŒ Daily profit target cannot exceed $100,000.")
                    return
                
                self.config.set('risk.daily_profit_target', new_value)
                
                if new_value == 0:
                    print("âœ… Daily profit target DISABLED")
                else:
                    print(f"âœ… Daily Profit Target set to ${new_value:,.2f}")
                    
        except ValueError:
            print("âŒ Invalid input. Please enter a valid number.")
        except Exception as e:
            self.logger.error(f"Error setting daily profit target: {e}")
            print("âŒ Error saving configuration.")
        
        input("\nPress Enter to continue...")
    
    def set_daily_trades(self):
        """Set max daily trades."""
        current = self.config.get('risk.max_daily_trades', 10)
        print(f"\n=== SET MAX DAILY TRADES ===")
        print(f"Current Max Daily Trades: {current}")
        print("Enter 0 to disable daily trade limit")
        
        try:
            new_value = input("New Max Daily Trades: ").strip()
            if new_value:
                new_value = int(new_value)
                
                # Validate input
                if new_value < 0:
                    print("âŒ Daily trade limit cannot be negative.")
                    return
                
                if new_value > 1000:
                    print("âŒ Daily trade limit cannot exceed 1,000.")
                    return
                
                self.config.set('risk.max_daily_trades', new_value)
                
                if new_value == 0:
                    print("âœ… Daily trade limit DISABLED")
                else:
                    print(f"âœ… Max Daily Trades set to {new_value}")
                    
        except ValueError:
            print("âŒ Invalid input. Please enter a valid number.")
        except Exception as e:
            self.logger.error(f"Error setting daily trade limit: {e}")
            print("âŒ Error saving configuration.")
        
        input("\nPress Enter to continue...")
    
    def set_daily_volume(self):
        """Set max daily volume."""
        current = self.config.get('risk.max_daily_volume', 100000.0)
        print(f"\n=== SET MAX DAILY VOLUME ===")
        print(f"Current Max Daily Volume: ${current:,.2f}")
        print("Enter 0 to disable daily volume limit")
        
        try:
            new_value = input("New Max Daily Volume: $").strip()
            if new_value:
                new_value = float(new_value)
                
                # Validate input
                if new_value < 0:
                    print("âŒ Daily volume limit cannot be negative.")
                    return
                
                if new_value > 10000000:
                    print("âŒ Daily volume limit cannot exceed $10,000,000.")
                    return
                
                self.config.set('risk.max_daily_volume', new_value)
                
                if new_value == 0:
                    print("âœ… Daily volume limit DISABLED")
                else:
                    print(f"âœ… Max Daily Volume set to ${new_value:,.2f}")
                    
        except ValueError:
            print("âŒ Invalid input. Please enter a valid number.")
        except Exception as e:
            self.logger.error(f"Error setting daily volume limit: {e}")
            print("âŒ Error saving configuration.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("Testing RulesDailyMenu...")
    
    # Test basic initialization
    daily_rules = RulesDailyMenu()
    print("âœ… RulesDailyMenu created successfully!")
    
    # Test display menu
    daily_rules.display_menu()
    print("âœ… RulesDailyMenu test completed!")


