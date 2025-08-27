"""
Orders Router

Routes to different order-related menu modules.
"""

from .orders_view import OrdersViewMenu
from .orders_cancel import OrdersCancelMenu
from .orders_place import OrdersPlaceMenu

class OrdersMenu:
    """Orders management router - delegates to specialized modules."""
    
    def __init__(self):
        # Initialize order modules
        self.orders_view = OrdersViewMenu()
        self.orders_cancel = OrdersCancelMenu()
        self.orders_place = OrdersPlaceMenu()
    
    def run(self):
        """Run the orders menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.orders_view.run()
            elif choice == "2":
                self.orders_cancel.run()
            elif choice == "3":
                self.orders_place.run()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display orders menu options."""
        print("\n=== ORDERS MANAGEMENT ===")
        print("1) View Orders")
        print("2) Cancel Orders")
        print("3) Place Orders")
        print("0) Back to accounts menu")

if __name__ == "__main__":
    print("Testing OrdersMenu...")
    
    # Test basic initialization
    orders = OrdersMenu()
    print("âœ… OrdersMenu created successfully!")
    
    # Test display menu
    orders.display_menu()
    print("âœ… OrdersMenu test completed!")


