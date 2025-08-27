"""
Engine Helpers

Helper functions for data mapping and logging.
"""

import json
from datetime import datetime, timezone
from typing import List, Dict
from pathlib import Path

from risk_manager_v2.schemas.evaluation_context import Position, Order
from risk_manager_v2.schemas.action_plan import ActionPlan
from risk_manager_v2.core.client import ProjectXClient
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
