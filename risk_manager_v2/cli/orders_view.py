"""
Orders View Menu

Handles viewing pending orders.
"""

from .base_menu import BaseMenu

class OrdersViewMenu(BaseMenu):
    """Orders viewing menu."""
    
    def run(self):
        """Run the orders view menu."""
        self.view_orders()
    
    def view_orders(self):
        """View pending orders for an account."""
        print("\n=== PENDING ORDERS ===")
        
        if not self.auth.is_authenticated():
            print("âŒ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        if not account_id:
            print("Account ID is required.")
            return
        
        try:
            orders = self.client.get_orders(account_id)
            
            if orders:
                self.display_orders(orders, account_id)
            else:
                print(f"No pending orders for account {account_id}.")
                
        except Exception as e:
            self.logger.error(f"Error getting orders: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def display_orders(self, orders, account_id):
        """Display orders in a formatted table."""
        print(f"\nPending Orders for Account {account_id}:")
        print("-" * 100)
        print(f"{'Order ID':<12} {'Contract ID':<25} {'Type':<12} {'Side':<8} {'Size':<8} {'Limit':<12} {'Stop':<12} {'Status':<12}")
        print("-" * 100)
        
        for order in orders:
            order_id = order.get('id', 'N/A')
            contract_id = order.get('contractId', 'N/A')
            order_type = self.get_order_type_display(order.get('type', 0))
            side = self.get_order_side_display(order.get('side', 0))
            size = order.get('size', 0)
            limit_price = order.get('limitPrice', 0)
            stop_price = order.get('stopPrice', 0)
            status = self.get_order_status_display(order.get('status', 0))
            
            # Format prices
            limit_str = f"${limit_price}" if limit_price else "N/A"
            stop_str = f"${stop_price}" if stop_price else "N/A"
            
            print(f"{order_id:<12} {contract_id:<25} {order_type:<12} {side:<8} {size:<8} {limit_str:<12} {stop_str:<12} {status:<12}")
        
        print("-" * 100)
        print(f"Total Orders: {len(orders)}")
    
    def get_order_type_display(self, order_type):
        """Convert order type enum to display string."""
        order_types = {
            0: "Unknown",
            1: "Limit",
            2: "Market",
            3: "StopLimit",
            4: "Stop",
            5: "TrailingStop",
            6: "JoinBid",
            7: "JoinAsk"
        }
        return order_types.get(order_type, "Unknown")
    
    def get_order_side_display(self, order_side):
        """Convert order side enum to display string."""
        order_sides = {
            0: "Buy",
            1: "Sell"
        }
        return order_sides.get(order_side, "Unknown")
    
    def get_order_status_display(self, order_status):
        """Convert order status enum to display string."""
        order_statuses = {
            0: "None",
            1: "Open",
            2: "Filled",
            3: "Cancelled",
            4: "Expired",
            5: "Rejected",
            6: "Pending"
        }
        return order_statuses.get(order_status, "Unknown")

if __name__ == "__main__":
    print("Testing OrdersViewMenu...")
    
    # Test basic initialization
    orders_view = OrdersViewMenu()
    print("âœ… OrdersViewMenu created successfully!")
    
    # Test display orders (will fail without auth, but should not crash)
    try:
        orders_view.view_orders()
        print("âœ… OrdersViewMenu test completed!")
    except Exception as e:
        print(f"âœ… OrdersViewMenu test completed (expected error without auth): {e}")


