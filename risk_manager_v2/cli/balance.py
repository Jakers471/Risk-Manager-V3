"""
Balance Menu

Handles viewing account balance and performance metrics.
"""

from .base_menu import BaseMenu
from datetime import datetime, timedelta

class BalanceMenu(BaseMenu):
    """Account balance menu."""
    
    def run(self):
        """Run the balance menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.view_balance()
            elif choice == "2":
                self.view_margin()
            elif choice == "3":
                self.view_performance()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display balance menu options."""
        print("\n=== ACCOUNT BALANCE ===")
        print("1) View Account Balance")
        print("2) View Margin Information")
        print("3) View Performance Metrics")
        print("0) Back to accounts menu")
    
    def view_balance(self):
        """View account balance information."""
        print("\n=== ACCOUNT BALANCE ===")
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        if not account_id:
            print("Account ID is required.")
            return
        
        try:
            # Get account details (includes balance)
            account = self.client.get_account_details(account_id)
            
            if account:
                self.display_account_details(account)
            else:
                print(f"Account {account_id} not found.")
                
        except Exception as e:
            self.logger.error(f"Error getting account details: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_margin(self):
        """View margin information."""
        print("\n=== MARGIN INFORMATION ===")
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        if not account_id:
            print("Account ID is required.")
            return
        
        try:
            # Get account details and positions for margin calculation
            account = self.client.get_account_details(account_id)
            positions = self.client.get_positions(account_id)
            
            if account:
                self.display_margin_info(account, positions)
            else:
                print(f"Account {account_id} not found.")
                
        except Exception as e:
            self.logger.error(f"Error getting margin information: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_performance(self):
        """View performance metrics."""
        print("\n=== PERFORMANCE METRICS ===")
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated")
            return
        
        account_id = input("Enter Account ID: ").strip()
        if not account_id:
            print("Account ID is required.")
            return
        
        try:
            # Get account details
            account = self.client.get_account_details(account_id)
            if not account:
                print(f"Account {account_id} not found.")
                return
            
            # Get recent trades for performance calculation
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=30)
            
            trades = self.client.get_trades(
                account_id,
                start_timestamp=start_time.isoformat() + "Z",
                end_timestamp=end_time.isoformat() + "Z"
            )
            
            self.display_performance_metrics(account, trades or [])
                
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def display_account_details(self, account):
        """Display account details and balance."""
        print(f"\nAccount Details:")
        print("-" * 50)
        print(f"Account ID: {account.get('id', 'N/A')}")
        print(f"Account Name: {account.get('name', 'N/A')}")
        print(f"Balance: ${account.get('balance', 0):,.2f}")
        print(f"Can Trade: {'Yes' if account.get('canTrade', False) else 'No'}")
        print(f"Visible: {'Yes' if account.get('isVisible', False) else 'No'}")
        print("-" * 50)
        
        # Calculate basic metrics
        balance = account.get('balance', 0)
        if balance > 0:
            print(f"Account Status: Active")
            print(f"Available Balance: ${balance:,.2f}")
        else:
            print(f"Account Status: Inactive/No Balance")
    
    def display_margin_info(self, account, positions):
        """Display margin information."""
        print(f"\nMargin Information for Account {account.get('id', 'N/A')}:")
        print("-" * 60)
        
        balance = account.get('balance', 0)
        total_position_value = 0
        
        if positions:
            print(f"Open Positions: {len(positions)}")
            print("\nPosition Details:")
            print(f"{'Contract':<25} {'Size':<8} {'Avg Price':<12} {'Market Value':<15}")
            print("-" * 60)
            
            for position in positions:
                contract_id = position.get('contractId', 'N/A')
                size = position.get('size', 0)
                avg_price = position.get('avgPrice', 0)
                market_value = abs(size * avg_price)
                total_position_value += market_value
                
                print(f"{contract_id:<25} {size:<8} ${avg_price:<11} ${market_value:<14}")
        else:
            print("No open positions")
        
        print("-" * 60)
        print(f"Account Balance: ${balance:,.2f}")
        print(f"Total Position Value: ${total_position_value:,.2f}")
        
        # Calculate margin metrics
        available_margin = balance - total_position_value
        margin_utilization = (total_position_value / balance * 100) if balance > 0 else 0
        
        print(f"Available Margin: ${available_margin:,.2f}")
        print(f"Margin Utilization: {margin_utilization:.1f}%")
        
        # Margin warnings
        if margin_utilization > 80:
            print("⚠️  WARNING: High margin utilization!")
        elif margin_utilization > 60:
            print("⚠️  CAUTION: Moderate margin utilization")
        else:
            print("✅ Margin utilization is healthy")
    
    def display_performance_metrics(self, account, trades):
        """Display performance metrics."""
        print(f"\nPerformance Metrics for Account {account.get('id', 'N/A')} (Last 30 Days):")
        print("=" * 70)
        
        balance = account.get('balance', 0)
        
        if not trades:
            print("No trading activity in the last 30 days.")
            print(f"Current Balance: ${balance:,.2f}")
            return
        
        # Calculate performance metrics
        total_pnl = 0
        total_fees = 0
        winning_trades = 0
        losing_trades = 0
        total_volume = 0
        largest_win = 0
        largest_loss = 0
        
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
                largest_win = max(largest_win, pnl)
            elif pnl < 0:
                losing_trades += 1
                largest_loss = min(largest_loss, pnl)
        
        net_pnl = total_pnl - total_fees
        total_trades = len(trades)
        
        # Display metrics
        print(f"Current Balance: ${balance:,.2f}")
        print(f"Net P&L (30 days): ${net_pnl:,.2f}")
        print(f"Total Volume: ${total_volume:,.2f}")
        print(f"Total Fees: ${total_fees:,.2f}")
        print()
        
        print(f"Trading Activity:")
        print(f"  Total Trades: {total_trades}")
        print(f"  Winning Trades: {winning_trades}")
        print(f"  Losing Trades: {losing_trades}")
        
        if total_trades > 0:
            win_rate = (winning_trades / total_trades * 100)
            avg_win = largest_win if winning_trades > 0 else 0
            avg_loss = abs(largest_loss) if losing_trades > 0 else 0
            
            print(f"  Win Rate: {win_rate:.1f}%")
            print(f"  Largest Win: ${largest_win:,.2f}")
            print(f"  Largest Loss: ${largest_loss:,.2f}")
            
            if avg_loss > 0:
                profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
                print(f"  Profit Factor: {profit_factor:.2f}")
        
        # Performance rating
        if net_pnl > 0:
            if win_rate > 60:
                print("\n🎯 Performance Rating: EXCELLENT")
            elif win_rate > 50:
                print("\n✅ Performance Rating: GOOD")
            else:
                print("\n⚠️  Performance Rating: NEEDS IMPROVEMENT")
        else:
            print("\n❌ Performance Rating: LOSS")

if __name__ == "__main__":
    print("Testing BalanceMenu...")
    
    # Test basic initialization
    balance = BalanceMenu()
    print("✅ BalanceMenu created successfully!")
    
    # Test display menu
    balance.display_menu()
    print("✅ BalanceMenu test completed!")
