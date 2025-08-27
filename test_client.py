#!/usr/bin/env python3
"""
Test script for ProjectX client functionality.
"""

import os
from risk_manager_v2.core.client import ProjectXClient

def test_client():
    """Test the ProjectX client with mock data."""
    print("Testing ProjectX Client...")
    
    # Enable simulator mode
    os.environ["PX_SIM"] = "1"
    
    # Initialize client
    client = ProjectXClient()
    print(f"✓ Client initialized with base_url: {client.base_url}")
    print(f"✓ Simulator mode: {client.simulator()}")
    
    # Test account ID
    account_id = "11010173"
    
    # Test get_positions
    print("\n--- Testing get_positions ---")
    positions = client.get_positions(account_id)
    print(f"✓ Retrieved {len(positions)} positions")
    for pos in positions:
        print(f"  - {pos.contract_id}: {pos.side.name} {pos.size} @ ${pos.average_price}")
    
    # Test get_orders
    print("\n--- Testing get_orders ---")
    orders = client.get_orders(account_id)
    print(f"✓ Retrieved {len(orders)} orders")
    for order in orders:
        print(f"  - {order.order_id}: {order.symbol_id} {order.side.name} {order.size} ({order.status.name})")
    
    # Test get_day_pnl
    print("\n--- Testing get_day_pnl ---")
    pnl = client.get_day_pnl(account_id)
    print(f"✓ Daily P&L: ${pnl}")
    
    # Test cancel_orders
    print("\n--- Testing cancel_orders ---")
    result = client.cancel_orders(account_id)
    print(f"✓ Cancel result: {result}")
    
    # Test place_market
    print("\n--- Testing place_market ---")
    result = client.place_market(account_id, "ES", 1, "buy")
    print(f"✓ Place market result: {result}")
    
    print("\n✓ All tests completed successfully!")

if __name__ == "__main__":
    test_client()
