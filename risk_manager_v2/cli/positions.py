"""
Positions Router

Routes to different position-related menu modules.
"""

from .positions_view import PositionsViewMenu
from .positions_close import PositionsCloseMenu

class PositionsMenu:
    """Positions management router - delegates to specialized modules."""
    
    def __init__(self):
        # Initialize menu modules
        self.positions_view = PositionsViewMenu()
        self.positions_close = PositionsCloseMenu()
    
    def run(self):
        """Run the positions menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.positions_view.run()
            elif choice == "2":
                self.positions_close.run()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display positions menu options."""
        print("\n=== POSITIONS MANAGEMENT ===")
        print("1) View Positions")
        print("2) Close Positions")
        print("0) Back to accounts menu")

if __name__ == "__main__":
    print("Testing PositionsMenu...")
    
    # Test basic initialization
    positions = PositionsMenu()
    print("✅ PositionsMenu created successfully!")
    
    # Test display menu
    positions.display_menu()
    print("✅ PositionsMenu test completed!")
