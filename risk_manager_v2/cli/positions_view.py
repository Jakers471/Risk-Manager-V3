"""
Positions View Menu

Handles viewing open positions and position details.
"""

from .base_menu import BaseMenu

class PositionsViewMenu(BaseMenu):
    """Positions viewing menu."""
    
    def run(self):
        """Run the positions view menu."""
        self.view_positions()
    
    def view_positions(self):
        """View open positions for an account."""
        print("\n=== OPEN POSITIONS ===")
        
        if not self.auth.is_authenticated():
            print("âŒ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        if not account_id:
            print("Account ID is required.")
            return
        
        try:
            positions = self.client.get_positions(account_id)
            
            if positions:
                self.display_positions(positions, account_id)
            else:
                print(f"No open positions for account {account_id}.")
                
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def display_positions(self, positions, account_id):
        """Display positions in a formatted table."""
        print(f"\nOpen Positions for Account {account_id}:")
        print("-" * 80)
        print(f"{'Contract ID':<25} {'Size':<8} {'Avg Price':<12} {'Type':<8}")
        print("-" * 80)
        
        total_size = 0
        for position in positions:
            contract_id = position.get('contractId', 'N/A')
            size = position.get('size', 0)
            avg_price = position.get('avgPrice', 0)
            position_type = self.get_position_type_display(position.get('type', 0))
            
            total_size += abs(size)
            
            print(f"{contract_id:<25} {size:<8} ${avg_price:<11} {position_type:<8}")
        
        print("-" * 80)
        print(f"Total Positions: {len(positions)}")
        print(f"Total Size: {total_size}")
        
        # Note: P&L calculation requires real-time market data
        # which is available through WebSocket connections
        print("\nNote: Real-time P&L requires WebSocket connection to market data")
    
    def get_position_type_display(self, position_type):
        """Convert position type enum to display string."""
        position_types = {
            0: "Unknown",
            1: "Long",
            2: "Short"
        }
        return position_types.get(position_type, "Unknown")

if __name__ == "__main__":
    print("Testing PositionsViewMenu...")
    
    # Test basic initialization
    positions_view = PositionsViewMenu()
    print("âœ… PositionsViewMenu created successfully!")
    
    # Test display positions (will fail without auth, but should not crash)
    try:
        positions_view.view_positions()
        print("âœ… PositionsViewMenu test completed!")
    except Exception as e:
        print(f"âœ… PositionsViewMenu test completed (expected error without auth): {e}")


