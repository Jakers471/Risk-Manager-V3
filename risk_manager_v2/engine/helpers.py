"""
Engine Helpers

Helper functions for enforcement actions and lockout management.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

from risk_manager_v2.core.client import ProjectXClient
from risk_manager_v2.schemas.action_plan import ActionPlan
from risk_manager_v2.core.logger import get_logger

logger = get_logger(__name__)

def enforce_flatten(client: ProjectXClient, account_id: str, symbol: str, reason: str) -> Dict[str, Any]:
    """Flatten position: cancel orders then market close."""
    try:
        # 1. Cancel all open orders for symbol
        cancel_result = client.cancel_orders(account_id, symbol)
        
        # 2. Get current position and close it
        positions = client.get_positions(account_id)
        position = next((p for p in positions if p.symbol == symbol), None)
        
        if position and position.qty != 0:
            # Market order to close position
            side = "sell" if position.qty > 0 else "buy"
            close_result = client.place_market(account_id, symbol, abs(position.qty), side)
            logger.info(f"Flattened {symbol} position: {position.qty} contracts")
            return {"status": "success", "cancelled": cancel_result, "closed": close_result}
        else:
            return {"status": "success", "cancelled": cancel_result, "closed": None}
            
    except Exception as e:
        logger.error(f"Error flattening {symbol} for {account_id}: {e}")
        return {"status": "error", "error": str(e)}

def enforce_reduce(client: ProjectXClient, account_id: str, symbol: str, qty: float, reason: str) -> Dict[str, Any]:
    """Reduce position by specified quantity."""
    try:
        positions = client.get_positions(account_id)
        position = next((p for p in positions if p.symbol == symbol), None)
        
        if position and position.qty != 0:
            reduce_size = min(abs(position.qty), abs(qty))
            side = "sell" if position.qty > 0 else "buy"
            
            result = client.place_market(account_id, symbol, reduce_size, side)
            logger.info(f"Reduced {symbol} position by {reduce_size} contracts")
            return {"status": "success", "reduced": result}
        else:
            return {"status": "no_position", "message": f"No position in {symbol}"}
            
    except Exception as e:
        logger.error(f"Error reducing {symbol} for {account_id}: {e}")
        return {"status": "error", "error": str(e)}

def enforce_cancel_orders(client: ProjectXClient, account_id: str, symbol: str, reason: str) -> Dict[str, Any]:
    """Cancel all open orders for symbol."""
    try:
        result = client.cancel_orders(account_id, symbol)
        logger.info(f"Cancelled orders for {symbol}")
        return {"status": "success", "cancelled": result}
        
    except Exception as e:
        logger.error(f"Error cancelling orders for {symbol}: {e}")
        return {"status": "error", "error": str(e)}

def enforce_lockout(account_id: str, reason: str, duration_hours: int = 24) -> Dict[str, Any]:
    """Create lockout file to block new risk."""
    try:
        runtime_dir = Path("runtime")
        runtime_dir.mkdir(exist_ok=True)
        
        lock_data = {
            "locked": True,
            "reason": reason,
            "account_id": account_id,
            "until": (datetime.now(timezone.utc) + timedelta(hours=duration_hours)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        lock_file = runtime_dir / "lock.json"
        with open(lock_file, 'w') as f:
            json.dump(lock_data, f, indent=2)
        
        logger.warning(f"Lockout created for {account_id}: {reason}")
        return {"status": "success", "lockout": lock_data}
        
    except Exception as e:
        logger.error(f"Error creating lockout for {account_id}: {e}")
        return {"status": "error", "error": str(e)}

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

def log_tick_event(correlation_id: str, ctx_data: Dict, action_plan: ActionPlan, results: Dict[str, Any]):
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
                        "reason": action.reason
                    }
                    for action in action_plan.actions
                ],
                "notes": action_plan.notes
            },
            "results": results
        }
        
        event_file = runtime_dir / f"{correlation_id}.json"
        with open(event_file, 'w') as f:
            json.dump(event_data, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error logging tick event {correlation_id}: {e}")
