"""
Trades Menu

Handles viewing trade history and P&L calculations.
"""

from .base_menu import BaseMenu
from datetime import datetime, timedelta

class TradesMenu(BaseMenu):
    """Trade history menu."""
    
    def run(self):
        """Run the trades menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.view_recent_trades()
            elif choice == "2":
                self.view_trades_by_date()
            elif choice == "3":
                self.calculate_pnl()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display trades menu options."""
        print("\n=== TRADE HISTORY ===")
        print("1) View Recent Trades")
        print("2) View Trades by Date")
        print("3) Calculate P&L")
        print("0) Back to accounts menu")
    
    def view_recent_trades(self):
        """View recent trades for an account."""
        print("\n=== RECENT TRADES ===")
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        if not account_id:
            print("Account ID is required.")
            return
        
        # Get trades from last 7 days by default
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        
        try:
            trades = self.client.get_trades(
                account_id, 
                start_timestamp=start_time.isoformat() + "Z",
                end_timestamp=end_time.isoformat() + "Z"
            )
            
            if trades:
                self.display_trades(trades, account_id)
            else:
                print(f"No trades found for account {account_id} in the last 7 days.")
                
        except Exception as e:
            self.logger.error(f"Error getting trades: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_trades_by_date(self):
        """View trades for a specific date range."""
        print("\n=== TRADES BY DATE ===")
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        if not account_id:
            print("Account ID is required.")
            return
        
        # Get date range
        start_date = input("Start Date (YYYY-MM-DD, default: 7 days ago): ").strip()
        end_date = input("End Date (YYYY-MM-DD, default: today): ").strip()
        
        try:
            # Parse dates
            if start_date:
                start_time = datetime.strptime(start_date, "%Y-%m-%d")
            else:
                start_time = datetime.utcnow() - timedelta(days=7)
            
            if end_date:
                end_time = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)  # Include full day
            else:
                end_time = datetime.utcnow()
            
            trades = self.client.get_trades(
                account_id,
                start_timestamp=start_time.isoformat() + "Z",
                end_timestamp=end_time.isoformat() + "Z"
            )
            
            if trades:
                self.display_trades(trades, account_id)
            else:
                print(f"No trades found for account {account_id} in the specified date range.")
                
        except ValueError as e:
            print(f"Invalid date format: {e}")
        except Exception as e:
            self.logger.error(f"Error getting trades: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def calculate_pnl(self):
        """Calculate P&L for trades."""
        print("\n=== P&L CALCULATION ===")
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        if not account_id:
            print("Account ID is required.")
            return
        
        # Get trades from last 30 days for P&L calculation
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=30)
        
        try:
            trades = self.client.get_trades(
                account_id,
                start_timestamp=start_time.isoformat() + "Z",
                end_timestamp=end_time.isoformat() + "Z"
            )
            
            if trades:
                self.calculate_and_display_pnl(trades, account_id)
            else:
                print(f"No trades found for account {account_id} in the last 30 days.")
                
        except Exception as e:
            self.logger.error(f"Error calculating P&L: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def display_trades(self, trades, account_id):
        """Display trades in a formatted table."""
        print(f"\nTrade History for Account {account_id}:")
        print("-" * 120)
        print(f"{'Time':<20} {'Contract':<25} {'Side':<8} {'Size':<8} {'Price':<12} {'P&L':<12} {'Fees':<8}")
        print("-" * 120)
        
        total_pnl = 0
        total_fees = 0
        
        for trade in trades:
            # Get contract details for display
            contract_id = trade.get('contractId', 'N/A')
            contract_name = self.get_contract_display_name(contract_id)
            
            # Format timestamp
            timestamp = trade.get('creationTimestamp', 'N/A')
            if timestamp != 'N/A':
                # Parse ISO timestamp and format for display
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    time_str = timestamp[:19]  # Fallback to first 19 chars
            else:
                time_str = 'N/A'
            
            # Get trade details
            side = self.get_trade_side_display(trade.get('side', 0))
            size = trade.get('size', 0)
            price = trade.get('price', 0)
            pnl = trade.get('profitAndLoss', 0) or 0  # Handle null values
            fees = trade.get('fees', 0)
            
            total_pnl += pnl
            total_fees += fees
            
            print(f"{time_str:<20} {contract_name:<25} {side:<8} {size:<8} ${price:<11} ${pnl:<11} ${fees:<7}")
        
        print("-" * 120)
        print(f"Total Realized P&L: ${total_pnl:.2f}")
        print(f"Total Fees: ${total_fees:.2f}")
        print(f"Net P&L: ${(total_pnl - total_fees):.2f}")
        
        # Calculate win/loss ratio
        winning_trades = sum(1 for trade in trades if (trade.get('profitAndLoss', 0) or 0) > 0)
        total_trades = len(trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        print(f"\nTotal Trades: {total_trades}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Win Rate: {win_rate:.1f}%")
    
    def calculate_and_display_pnl(self, trades, account_id):
        """Calculate and display detailed P&L analysis."""
        print(f"\nP&L Analysis for Account {account_id} (Last 30 Days):")
        print("=" * 60)
        
        total_pnl = 0
        total_fees = 0
        winning_trades = 0
        losing_trades = 0
        total_volume = 0
        
        for trade in trades:
            pnl = trade.get('profitAndLoss', 0) or 0
            fees = trade.get('fees', 0)
            size = trade.get('size', 0)
            price = trade.get('price', 0)
            
            total_pnl += pnl
            total_fees += fees
            total_volume += size * price
            
            if pnl > 0:
                winning_trades += 1
            elif pnl < 0:
                losing_trades += 1
        
        net_pnl = total_pnl - total_fees
        
        print(f"Total Realized P&L: ${total_pnl:.2f}")
        print(f"Total Fees: ${total_fees:.2f}")
        print(f"Net P&L: ${net_pnl:.2f}")
        print(f"Total Volume: ${total_volume:.2f}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Losing Trades: {losing_trades}")
        
        total_trades = len(trades)
        if total_trades > 0:
            win_rate = (winning_trades / total_trades * 100)
            avg_win = total_pnl / winning_trades if winning_trades > 0 else 0
            avg_loss = total_pnl / losing_trades if losing_trades > 0 else 0
            
            print(f"Win Rate: {win_rate:.1f}%")
            print(f"Average Win: ${avg_win:.2f}")
            print(f"Average Loss: ${avg_loss:.2f}")
            print(f"Profit Factor: {abs(avg_win / avg_loss):.2f}" if avg_loss != 0 else "Profit Factor: N/A")
    
    def get_contract_display_name(self, contract_id: str) -> str:
        """Get contract display name from contract ID."""
        if contract_id == 'N/A':
            return 'N/A'
        
        try:
            contract = self.client.get_contract_details(contract_id)
            if contract:
                return contract.get('name', contract_id)
            else:
                return contract_id
        except Exception as e:
            self.logger.error(f"Error getting contract details: {e}")
            return contract_id
    
    def get_trade_side_display(self, side: int) -> str:
        """Convert trade side enum to display string."""
        trade_sides = {
            0: "Buy",
            1: "Sell"
        }
        return trade_sides.get(side, "Unknown")

if __name__ == "__main__":
    print("Testing TradesMenu...")
    
    # Test basic initialization
    trades = TradesMenu()
    print("✅ TradesMenu created successfully!")
    
    # Test display menu
    trades.display_menu()
    print("✅ TradesMenu test completed!")
