"""
Account Management Router

Routes to different account-related menu modules.
"""

from .accounts_list import AccountsListMenu
from .positions import PositionsMenu
from .orders import OrdersMenu
from .trades import TradesMenu
from .balance import BalanceMenu

class AccountsMenu:
    """Account management router - delegates to specialized modules."""
    
    def __init__(self):
        # Initialize menu modules
        self.accounts_list = AccountsListMenu()
        self.positions = PositionsMenu()
        self.orders = OrdersMenu()
        self.trades = TradesMenu()
        self.balance = BalanceMenu()
    
    def run(self):
        """Run the accounts menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.accounts_list.run()
            elif choice == "2":
                self.positions.run()
            elif choice == "3":
                self.orders.run()
            elif choice == "4":
                self.trades.run()
            elif choice == "5":
                self.balance.run()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display accounts menu options."""
        print("\n=== ACCOUNT MANAGEMENT ===")
        print("1) List All Accounts")
        print("2) View Positions")
        print("3) View Orders")
        print("4) View Trades")
        print("5) View Balance")
        print("0) Back to main menu")

if __name__ == "__main__":
    print("Testing AccountsMenu...")
    
    # Test basic initialization
    accounts = AccountsMenu()
    print("âœ… AccountsMenu created successfully!")
    
    # Test display menu
    accounts.display_menu()
    print("âœ… AccountsMenu test completed!")


