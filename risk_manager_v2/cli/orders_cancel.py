"""
Orders Cancel Menu

Handles canceling orders (single and all).
"""

from .base_menu import BaseMenu

class OrdersCancelMenu(BaseMenu):
    """Orders canceling menu."""
    
    def run(self):
        """Run the orders cancel menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.cancel_single_order()
            elif choice == "2":
                self.cancel_all_orders()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display orders cancel menu options."""
        print("\n=== CANCEL ORDERS ===")
        print("1) Cancel Single Order")
        print("2) Cancel All Orders")
        print("0) Back to orders menu")
    
    def cancel_single_order(self):
        """Cancel a specific order."""
        print("\n=== CANCEL SINGLE ORDER ===")
        
        if not self.auth.is_authenticated():
            print("âŒ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        order_id = input("Enter Order ID: ").strip()
        
        if not account_id or not order_id:
            print("Account ID and Order ID are required.")
            return
        
        confirm = input(f"Cancel order {order_id}? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return
        
        try:
            result = self.client.cancel_order(account_id, order_id)
            
            if result and result.get("success"):
                print("âœ… Order cancelled successfully!")
            else:
                error_msg = result.get("errorMessage", "Unknown error") if result else "No response"
                print(f"âŒ Failed to cancel order: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def cancel_all_orders(self):
        """Cancel all orders for an account."""
        print("\n=== CANCEL ALL ORDERS ===")
        
        if not self.auth.is_authenticated():
            print("âŒ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        if not account_id:
            print("Account ID is required.")
            return
        
        # Show current orders first
        try:
            orders = self.client.get_orders(account_id)
            if orders:
                print(f"\nCurrent orders for account {account_id}:")
                for order in orders:
                    order_id = order.get('id', 'N/A')
                    contract_id = order.get('contractId', 'N/A')
                    size = order.get('size', 0)
                    side = self.get_order_side_display(order.get('side', 0))
                    print(f"  - Order {order_id}: {contract_id} {side} {size}")
            else:
                print(f"No open orders for account {account_id}.")
                return
        except Exception as e:
            self.logger.error(f"Error getting orders: {e}")
            print(f"Error getting orders: {e}")
            return
        
        confirm = input(f"\nCancel ALL orders for account {account_id}? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return
        
        try:
            result = self.client.cancel_all_orders(account_id)
            
            if result and result.get("success"):
                print("âœ… All orders cancelled successfully!")
            else:
                error_msg = result.get("errorMessage", "Unknown error") if result else "No response"
                print(f"âŒ Failed to cancel all orders: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Error cancelling all orders: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def get_order_side_display(self, order_side):
        """Convert order side enum to display string."""
        order_sides = {
            0: "Buy",
            1: "Sell"
        }
        return order_sides.get(order_side, "Unknown")

if __name__ == "__main__":
    print("Testing OrdersCancelMenu...")
    
    # Test basic initialization
    orders_cancel = OrdersCancelMenu()
    print("âœ… OrdersCancelMenu created successfully!")
    
    # Test display menu
    orders_cancel.display_menu()
    print("âœ… OrdersCancelMenu test completed!")

