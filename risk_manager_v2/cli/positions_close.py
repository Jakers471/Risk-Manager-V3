"""
Positions Close Menu

Handles closing positions (single, partial, and all).
"""

from .base_menu import BaseMenu

class PositionsCloseMenu(BaseMenu):
    """Positions closing menu."""
    
    def run(self):
        """Run the positions close menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.close_single_position()
            elif choice == "2":
                self.close_partial_position()
            elif choice == "3":
                self.close_all_positions()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display positions close menu options."""
        print("\n=== CLOSE POSITIONS ===")
        print("1) Close Single Position")
        print("2) Close Partial Position")
        print("3) Close All Positions")
        print("0) Back to positions menu")
    
    def close_single_position(self):
        """Close a specific position."""
        print("\n=== CLOSE SINGLE POSITION ===")
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        contract_id = input("Enter Contract ID: ").strip()
        
        if not account_id or not contract_id:
            print("Account ID and Contract ID are required.")
            return
        
        confirm = input(f"Close position for contract {contract_id}? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return
        
        try:
            result = self.client.close_position(account_id, contract_id)
            
            if result and result.get("success"):
                print("✅ Position closed successfully!")
            else:
                error_msg = result.get("errorMessage", "Unknown error") if result else "No response"
                print(f"❌ Failed to close position: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def close_partial_position(self):
        """Close a partial position."""
        print("\n=== CLOSE PARTIAL POSITION ===")
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        contract_id = input("Enter Contract ID: ").strip()
        size = input("Enter size to close: ").strip()
        
        if not account_id or not contract_id or not size:
            print("Account ID, Contract ID, and size are required.")
            return
        
        try:
            size_int = int(size)
            if size_int <= 0:
                print("Size must be a positive number.")
                return
        except ValueError:
            print("Size must be a valid number.")
            return
        
        confirm = input(f"Close {size_int} contracts for {contract_id}? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return
        
        try:
            result = self.client.close_partial_position(account_id, contract_id, size_int)
            
            if result and result.get("success"):
                print(f"✅ {size_int} contracts closed successfully!")
            else:
                error_msg = result.get("errorMessage", "Unknown error") if result else "No response"
                print(f"❌ Failed to close position: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Error closing partial position: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def close_all_positions(self):
        """Close all positions for an account."""
        print("\n=== CLOSE ALL POSITIONS ===")
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        if not account_id:
            print("Account ID is required.")
            return
        
        # Show current positions first
        try:
            positions = self.client.get_positions(account_id)
            if positions:
                print(f"\nCurrent positions for account {account_id}:")
                for pos in positions:
                    contract_id = pos.get('contractId', 'N/A')
                    size = pos.get('size', 0)
                    print(f"  - {contract_id}: {size} contracts")
            else:
                print(f"No open positions for account {account_id}.")
                return
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            print(f"Error getting positions: {e}")
            return
        
        confirm = input(f"\nClose ALL positions for account {account_id}? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return
        
        try:
            result = self.client.close_all_positions(account_id)
            
            if result and result.get("success"):
                print("✅ All positions closed successfully!")
            else:
                error_msg = result.get("errorMessage", "Unknown error") if result else "No response"
                print(f"❌ Failed to close all positions: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Error closing all positions: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("Testing PositionsCloseMenu...")
    
    # Test basic initialization
    positions_close = PositionsCloseMenu()
    print("✅ PositionsCloseMenu created successfully!")
    
    # Test display menu
    positions_close.display_menu()
    print("✅ PositionsCloseMenu test completed!")
