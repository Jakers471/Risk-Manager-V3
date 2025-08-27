from datetime import datetime, timezone
from typing import List, Dict, Any
from risk_manager_v2.schemas.evaluation_context import EvaluationContext, Position, Order
from risk_manager_v2.policy.brain import PolicyBrain
from risk_manager_v2.schemas.action_plan import ActionPlan
from risk_manager_v2.core.client import ProjectXClient
from risk_manager_v2.engine.helpers import (
    enforce_flatten, enforce_reduce, enforce_cancel_orders, enforce_lockout,
    check_lockout, log_tick_event
)
from risk_manager_v2.core.logger import get_logger

logger = get_logger(__name__)

# Global client instance
_client = None

def get_client() -> ProjectXClient:
    """Get or create ProjectX client instance."""
    global _client
    if _client is None:
        # Use new client interface with environment variables
        _client = ProjectXClient()
    return _client

def get_monitored_accounts() -> List[str]:
    """Get list of monitored accounts."""
    return ["11010173"]  # TODO: get from config

def client_get_positions(acct: str) -> List[Position]:
    """Get positions from ProjectX client."""
    try:
        client = get_client()
        raw_positions = client.get_positions(acct)
        return [_map_position_data(pos) for pos in raw_positions]
    except Exception as e:
        logger.error(f"Error getting positions for {acct}: {e}")
        return []

def _map_position_data(position: Position) -> Position:
    """Map Position dataclass to evaluation context Position."""
    from risk_manager_v2.schemas.evaluation_context import Position as EvalPosition
    return EvalPosition(
        symbol=position.contract_id,
        qty=float(position.size),
        entry_price=float(position.average_price),
        unrealized_pnl=0.0,  # Will be calculated later
        side="long" if position.side.value == 1 else "short"
    )

def client_get_orders(acct: str) -> List[Order]:
    """Get orders from ProjectX client."""
    try:
        client = get_client()
        raw_orders = client.get_orders(acct)
        return [_map_order_data(order) for order in raw_orders]
    except Exception as e:
        logger.error(f"Error getting orders for {acct}: {e}")
        return []

def _map_order_data(order: Order) -> Order:
    """Map Order dataclass to evaluation context Order."""
    from risk_manager_v2.schemas.evaluation_context import Order as EvalOrder
    return EvalOrder(
        id=order.order_id,
        symbol=order.symbol_id,
        side="buy" if order.side.value == 0 else "sell",
        qty=float(order.size),
        type=_map_order_type(order.order_type.value),
        status=_map_order_status(order.status.value)
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

def client_get_day_pnl(acct: str) -> float:
    """Get day P&L from ProjectX client."""
    try:
        client = get_client()
        return client.get_day_pnl(acct)
    except Exception as e:
        logger.error(f"Error getting day P&L for {acct}: {e}")
        return 0.0

def client_enforce(acct: str, plan: ActionPlan) -> Dict[str, Any]:
    """Execute enforcement actions with lockout guard."""
    results = {"account_id": acct, "actions": []}
    
    # Check lockout first
    if check_lockout(acct):
        logger.warning(f"Account {acct} is locked out, only allowing reduce/flatten actions")
        # Filter actions to only allow reduce/flatten when locked
        allowed_actions = [a for a in plan.actions if a.kind in ["reduce", "flatten"]]
        if not allowed_actions:
            results["actions"].append({"status": "skipped", "reason": "locked_out"})
            return results
    else:
        allowed_actions = plan.actions
    
    client = get_client()
    
    for action in allowed_actions:
        logger.info(f"[ENFORCE] {acct} => {action.kind} {action.symbol} qty={action.qty} reason={action.reason}")
        
        if action.kind == "flatten":
            result = enforce_flatten(client, acct, action.symbol, action.reason)
        elif action.kind == "reduce":
            result = enforce_reduce(client, acct, action.symbol, action.qty, action.reason)
        elif action.kind == "cancel_orders":
            result = enforce_cancel_orders(client, acct, action.symbol, action.reason)
        elif action.kind == "lockout":
            result = enforce_lockout(acct, action.reason)
        elif action.kind == "noop":
            result = {"status": "success", "action": "noop"}
        else:
            result = {"status": "error", "error": f"Unknown action kind: {action.kind}"}
        
        results["actions"].append({
            "action": action.kind,
            "symbol": action.symbol,
            "qty": action.qty,
            "reason": action.reason,
            "result": result
        })
    
    return results

def build_ctx(acct: str) -> EvaluationContext:
    """Build evaluation context with real data."""
    return EvaluationContext(
        ts=datetime.now(timezone.utc),
        account_id=acct,
        day_pnl=client_get_day_pnl(acct),
        max_drawdown_today=0.0,  # TODO: calculate from trade history
        risk_tier="t0",  # TODO: get from account config
        positions=client_get_positions(acct),
        orders=client_get_orders(acct),
        env={"market_hours": "unknown"}  # TODO: get from market data
    )

class RiskMonitor:
    def __init__(self, brain: PolicyBrain | None = None):
        self.brain = brain or PolicyBrain()

    def tick(self):
        """Execute one monitoring tick with logging."""
        for acct in get_monitored_accounts():
            try:
                # Build context
                ctx = build_ctx(acct)
                
                # Evaluate with policy brain
                plan = self.brain.evaluate(ctx)
                
                # Execute enforcement
                results = client_enforce(acct, plan)
                
                # Log the tick event
                ctx_data = {
                    "account_id": ctx.account_id,
                    "day_pnl": ctx.day_pnl,
                    "risk_tier": ctx.risk_tier,
                    "positions_count": len(ctx.positions),
                    "orders_count": len(ctx.orders),
                    "timestamp": ctx.ts.isoformat()
                }
                log_tick_event(plan.correlation_id, ctx_data, plan, results)
                
            except Exception as e:
                logger.error(f"Error in tick for account {acct}: {e}")

def run_monitor_once():
    """Run one monitoring tick."""
    RiskMonitor().tick()
