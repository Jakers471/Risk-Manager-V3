"""
Engine Helpers

Helper functions for risk monitoring and enforcement.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from risk_manager_v2.schemas.evaluation_context import Position, Order
from risk_manager_v2.schemas.action_plan import ActionPlan, Action
from risk_manager_v2.core.client import ProjectXClient, ProjectXError
from risk_manager_v2.core.logger import get_logger

logger = get_logger(__name__)

def map_position_data(raw_position: Dict) -> Position:
    """Map raw API position data to Position dataclass."""
    return Position(
        symbol=raw_position.get("contractId", ""),
        qty=float(raw_position.get("size", 0)),
        entry_price=float(raw_position.get("avgPrice", 0)),
        unrealized_pnl=float(raw_position.get("unrealizedPnl", 0)),
        side="long" if raw_position.get("size", 0) > 0 else "short"
    )

def map_order_data(raw_order: Dict) -> Order:
    """Map raw API order data to Order dataclass."""
    return Order(
        id=str(raw_order.get("id", "")),
        symbol=raw_order.get("contractId", ""),
        side="buy" if raw_order.get("side", 0) == 0 else "sell",
        qty=float(raw_order.get("size", 0)),
        type=_map_order_type(raw_order.get("type", 1)),
        status=_map_order_status(raw_order.get("status", 0))
    )

def _map_order_type(order_type: int) -> str:
    """Map order type enum to string."""
    types = {
        1: "limit",
        2: "market", 
        4: "stop",
        5: "trailing_stop",
        6: "join_bid",
        7: "join_ask"
    }
    return types.get(order_type, "unknown")

def _map_order_status(status: int) -> str:
    """Map order status enum to string."""
    statuses = {
        0: "pending",
        1: "filled",
        2: "cancelled",
        3: "rejected"
    }
    return statuses.get(status, "unknown")

def get_day_pnl_from_trades(client: ProjectXClient, account_id: str) -> float:
    """Calculate day P&L from today's trades."""
    try:
        from datetime import date
        today = date.today().isoformat()
        trades = client.get_trades(account_id, start_timestamp=today)
        
        total_pnl = 0.0
        for trade in trades:
            pnl = trade.get("realizedPnl", 0)
            if pnl is not None:
                total_pnl += float(pnl)
        
        return total_pnl
    except Exception as e:
        logger.error(f"Error getting day P&L for {account_id}: {e}")
        return 0.0

def enforce_flatten(client: ProjectXClient, account_id: str, symbol: str, reason: str):
    """Flatten position: cancel orders then market close."""
    try:
        # 1. Cancel all open orders for symbol
        orders = client.get_open_orders(account_id)
        for order in orders:
            if order.get("contractId") == symbol:
                client.cancel_order(account_id, str(order.get("id")))
        
        # 2. Get current position
        positions = client.get_open_positions(account_id)
        position = next((p for p in positions if p.get("contractId") == symbol), None)
        
        if position and position.get("size", 0) != 0:
            # 3. Market order to close position
            size = abs(position.get("size", 0))
            side = 1 if position.get("size", 0) > 0 else 0  # 0=buy, 1=sell
            client.place_order(
                account_id=account_id,
                contract_id=symbol,
                order_type=2,  # market
                side=side,
                size=int(size)
            )
            logger.info(f"Flattened {symbol} position: {size} contracts")
            
    except Exception as e:
        logger.error(f"Error flattening {symbol} for {account_id}: {e}")

def enforce_reduce(client: ProjectXClient, account_id: str, symbol: str, qty: float, reason: str):
    """Reduce position by specified quantity."""
    try:
        positions = client.get_open_positions(account_id)
        position = next((p for p in positions if p.get("contractId") == symbol), None)
        
        if position and position.get("size", 0) != 0:
            current_size = position.get("size", 0)
            reduce_size = min(abs(current_size), abs(qty))
            
            # Determine side: opposite of current position
            side = 1 if current_size > 0 else 0  # 0=buy, 1=sell
            
            client.place_order(
                account_id=account_id,
                contract_id=symbol,
                order_type=2,  # market
                side=side,
                size=int(reduce_size)
            )
            logger.info(f"Reduced {symbol} position by {reduce_size} contracts")
            
    except Exception as e:
        logger.error(f"Error reducing {symbol} for {account_id}: {e}")

def enforce_cancel_orders(client: ProjectXClient, account_id: str, symbol: str, reason: str):
    """Cancel all open orders for symbol."""
    try:
        orders = client.get_open_orders(account_id)
        cancelled = 0
        
        for order in orders:
            if order.get("contractId") == symbol:
                client.cancel_order(account_id, str(order.get("id")))
                cancelled += 1
        
        if cancelled > 0:
            logger.info(f"Cancelled {cancelled} orders for {symbol}")
            
    except Exception as e:
        logger.error(f"Error cancelling orders for {symbol}: {e}")

def enforce_lockout(account_id: str, reason: str, duration_hours: int = 24):
    """Create lockout file to block new risk."""
    try:
        runtime_dir = Path("runtime")
        runtime_dir.mkdir(exist_ok=True)
        
        lock_data = {
            "locked": True,
            "reason": reason,
            "account_id": account_id,
            "until": (datetime.now(timezone.utc) + 
                     timedelta(hours=duration_hours)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        lock_file = runtime_dir / "lock.json"
        with open(lock_file, 'w') as f:
            json.dump(lock_data, f, indent=2)
        
        logger.warning(f"Lockout created for {account_id}: {reason}")
        
    except Exception as e:
        logger.error(f"Error creating lockout for {account_id}: {e}")

def check_lockout(account_id: str) -> bool:
    """Check if account is locked out."""
    try:
        lock_file = Path("runtime/lock.json")
        if not lock_file.exists():
            return False
        
        with open(lock_file, 'r') as f:
            lock_data = json.load(f)
        
        if not lock_data.get("locked", False):
            return False
        
        # Check if lock applies to this account
        lock_account = lock_data.get("account_id")
        if lock_account and lock_account != account_id:
            return False
        
        # Check if lock has expired
        until_str = lock_data.get("until")
        if until_str:
            until_time = datetime.fromisoformat(until_str.replace('Z', '+00:00'))
            if datetime.now(timezone.utc) > until_time:
                # Lock expired, remove it
                lock_file.unlink()
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking lockout for {account_id}: {e}")
        return False

def log_tick_event(correlation_id: str, ctx_data: Dict, action_plan: ActionPlan):
    """Log tick event to JSON file."""
    try:
        runtime_dir = Path("runtime/events")
        runtime_dir.mkdir(parents=True, exist_ok=True)
        
        event_data = {
            "correlation_id": correlation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": ctx_data,
            "action_plan": {
                "correlation_id": action_plan.correlation_id,
                "actions": [
                    {
                        "kind": action.kind,
                        "symbol": action.symbol,
                        "qty": action.qty,
                        "reason": action.reason,
                        "severity": action.severity
                    }
                    for action in action_plan.actions
                ],
                "notes": action_plan.notes
            }
        }
        
        event_file = runtime_dir / f"{correlation_id}.json"
        with open(event_file, 'w') as f:
            json.dump(event_data, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error logging tick event {correlation_id}: {e}")
