"""
Orders Place Menu

Handles placing new orders (market, limit, stop).
"""

from .base_menu import BaseMenu

class OrdersPlaceMenu(BaseMenu):
    """Orders placing menu."""
    
    def run(self):
        """Run the orders place menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.place_market_order()
            elif choice == "2":
                self.place_limit_order()
            elif choice == "3":
                self.place_stop_order()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display orders place menu options."""
        print("\n=== PLACE ORDERS ===")
        print("1) Place Market Order")
        print("2) Place Limit Order")
        print("3) Place Stop Order")
        print("0) Back to orders menu")
    
    def search_contract(self, symbol: str) -> str:
        """Search for contract ID by symbol."""
        try:
            contracts = self.client.search_contracts(symbol, live=True)
            if not contracts:
                print(f"No contracts found for symbol: {symbol}")
                return None
            
            print(f"\nAvailable contracts for '{symbol}':")
            for i, contract in enumerate(contracts[:10], 1):  # Show first 10
                print(f"{i}) {contract.get('name', 'N/A')} - {contract.get('description', 'N/A')}")
            
            if len(contracts) > 10:
                print(f"... and {len(contracts) - 10} more")
            
            choice = input(f"\nSelect contract (1-{min(10, len(contracts))}) or 'c' to cancel: ").strip()
            if choice.lower() == 'c':
                return None
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(contracts):
                    return contracts[index].get('id')
                else:
                    print("Invalid selection.")
                    return None
            except ValueError:
                print("Invalid selection.")
                return None
                
        except Exception as e:
            self.logger.error(f"Error searching contracts: {e}")
            print(f"Error searching contracts: {e}")
            return None
    
    def place_market_order(self):
        """Place a market order."""
        print("\n=== PLACE MARKET ORDER ===")
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated")
            return
        
        # Get order details
        account_id = input("Account ID: ").strip()
        symbol = input("Symbol (e.g., ES, NQ): ").strip()
        side = input("Side (buy/sell): ").strip().lower()
        size = input("Size (contracts): ").strip()
        
        if not all([account_id, symbol, side, size]):
            print("All fields are required.")
            return
        
        if side not in ['buy', 'sell']:
            print("Side must be 'buy' or 'sell'.")
            return
        
        try:
            size = int(size)
        except ValueError:
            print("Size must be a number.")
            return
        
        # Search for contract
        contract_id = self.search_contract(symbol)
        if not contract_id:
            print("Contract selection cancelled.")
            return
        
        # Convert side to API format
        side_int = 0 if side == 'buy' else 1  # 0=Bid (buy), 1=Ask (sell)
        
        confirm = input(f"Place {side} {size} {symbol} at market? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Order cancelled.")
            return
        
        try:
            result = self.client.place_order(
                account_id=account_id,
                contract_id=contract_id,
                order_type=2,  # Market order
                side=side_int,
                size=size
            )
            
            if result and result.get("success"):
                order_id = result.get("orderId", "N/A")
                print(f"✅ Market order placed successfully!")
                print(f"Order ID: {order_id}")
            else:
                error_msg = result.get("errorMessage", "Unknown error") if result else "No response"
                print(f"❌ Failed to place market order: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Error placing market order: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def place_limit_order(self):
        """Place a limit order."""
        print("\n=== PLACE LIMIT ORDER ===")
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated")
            return
        
        # Get order details
        account_id = input("Account ID: ").strip()
        symbol = input("Symbol (e.g., ES, NQ): ").strip()
        side = input("Side (buy/sell): ").strip().lower()
        size = input("Size (contracts): ").strip()
        price = input("Limit Price: ").strip()
        
        if not all([account_id, symbol, side, size, price]):
            print("All fields are required.")
            return
        
        if side not in ['buy', 'sell']:
            print("Side must be 'buy' or 'sell'.")
            return
        
        try:
            size = int(size)
            price = float(price)
        except ValueError:
            print("Size and price must be numbers.")
            return
        
        # Search for contract
        contract_id = self.search_contract(symbol)
        if not contract_id:
            print("Contract selection cancelled.")
            return
        
        # Convert side to API format
        side_int = 0 if side == 'buy' else 1  # 0=Bid (buy), 1=Ask (sell)
        
        confirm = input(f"Place {side} {size} {symbol} at ${price}? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Order cancelled.")
            return
        
        try:
            result = self.client.place_order(
                account_id=account_id,
                contract_id=contract_id,
                order_type=1,  # Limit order
                side=side_int,
                size=size,
                limit_price=price
            )
            
            if result and result.get("success"):
                order_id = result.get("orderId", "N/A")
                print(f"✅ Limit order placed successfully!")
                print(f"Order ID: {order_id}")
            else:
                error_msg = result.get("errorMessage", "Unknown error") if result else "No response"
                print(f"❌ Failed to place limit order: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Error placing limit order: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def place_stop_order(self):
        """Place a stop order."""
        print("\n=== PLACE STOP ORDER ===")
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated")
            return
        
        # Get order details
        account_id = input("Account ID: ").strip()
        symbol = input("Symbol (e.g., ES, NQ): ").strip()
        side = input("Side (buy/sell): ").strip().lower()
        size = input("Size (contracts): ").strip()
        stop_price = input("Stop Price: ").strip()
        limit_price = input("Limit Price (optional, for stop-limit): ").strip()
        
        if not all([account_id, symbol, side, size, stop_price]):
            print("Account ID, Symbol, Side, Size, and Stop Price are required.")
            return
        
        if side not in ['buy', 'sell']:
            print("Side must be 'buy' or 'sell'.")
            return
        
        try:
            size = int(size)
            stop_price = float(stop_price)
            limit_price = float(limit_price) if limit_price else None
        except ValueError:
            print("Size and prices must be numbers.")
            return
        
        # Search for contract
        contract_id = self.search_contract(symbol)
        if not contract_id:
            print("Contract selection cancelled.")
            return
        
        # Convert side to API format
        side_int = 0 if side == 'buy' else 1  # 0=Bid (buy), 1=Ask (sell)
        
        # Determine order type
        order_type = 3 if limit_price else 4  # 3=StopLimit, 4=Stop
        
        order_desc = f"stop-limit at ${stop_price}/${limit_price}" if limit_price else f"stop at ${stop_price}"
        confirm = input(f"Place {side} {size} {symbol} {order_desc}? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Order cancelled.")
            return
        
        try:
            result = self.client.place_order(
                account_id=account_id,
                contract_id=contract_id,
                order_type=order_type,
                side=side_int,
                size=size,
                limit_price=limit_price,
                stop_price=stop_price
            )
            
            if result and result.get("success"):
                order_id = result.get("orderId", "N/A")
                print(f"✅ Stop order placed successfully!")
                print(f"Order ID: {order_id}")
            else:
                error_msg = result.get("errorMessage", "Unknown error") if result else "No response"
                print(f"❌ Failed to place stop order: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Error placing stop order: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("Testing OrdersPlaceMenu...")
    
    # Test basic initialization
    orders_place = OrdersPlaceMenu()
    print("✅ OrdersPlaceMenu created successfully!")
    
    # Test display menu
    orders_place.display_menu()
    print("✅ OrdersPlaceMenu test completed!")
