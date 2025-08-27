from datetime import datetime, timezone
from typing import List
from risk_manager_v2.schemas.evaluation_context import EvaluationContext, Position, Order
from risk_manager_v2.policy.brain import PolicyBrain
from risk_manager_v2.schemas.action_plan import ActionPlan
from risk_manager_v2.core.config import ConfigStore
from risk_manager_v2.core.auth import AuthManager
from risk_manager_v2.core.client import ProjectXClient
from risk_manager_v2.engine.helpers import (
    map_position_data, map_order_data, get_day_pnl_from_trades, log_tick_event
)
from risk_manager_v2.engine.enforcement import (
    enforce_flatten, enforce_reduce, enforce_cancel_orders, enforce_lockout, check_lockout
)
from risk_manager_v2.core.logger import get_logger

logger = get_logger(__name__)

# Global client instance
_client = None

def get_client() -> ProjectXClient:
    """Get or create ProjectX client instance."""
    global _client
    if _client is None:
        config = ConfigStore()
        auth = AuthManager(config)
        _client = ProjectXClient(config, auth)
    return _client

def get_monitored_accounts() -> List[str]:
    """Get list of monitored accounts."""
    try:
        client = get_client()
        accounts = client.get_accounts(only_active=True)
        return [str(account.get("id")) for account in accounts if account.get("id")]
    except Exception as e:
        logger.error(f"Error getting monitored accounts: {e}")
        return ["11010173"]  # fallback

def client_get_positions(acct: str) -> List[Position]:
    """Get positions from API and map to dataclasses."""
    try:
        client = get_client()
        raw_positions = client.get_open_positions(acct)
        return [map_position_data(pos) for pos in raw_positions]
    except Exception as e:
        logger.error(f"Error getting positions for {acct}: {e}")
        return []

def client_get_orders(acct: str) -> List[Order]:
    """Get orders from API and map to dataclasses."""
    try:
        client = get_client()
        raw_orders = client.get_open_orders(acct)
        return [map_order_data(order) for order in raw_orders]
    except Exception as e:
        logger.error(f"Error getting orders for {acct}: {e}")
        return []

def client_get_day_pnl(acct: str) -> float:
    """Get day P&L from trades."""
    try:
        client = get_client()
        return get_day_pnl_from_trades(client, acct)
    except Exception as e:
        logger.error(f"Error getting day P&L for {acct}: {e}")
        return 0.0

def client_enforce(acct: str, plan: ActionPlan):
    """Execute enforcement actions."""
    try:
        client = get_client()
        
        for action in plan.actions:
            logger.info(f"[ENFORCE] {acct} => {action.kind} {action.symbol} qty={action.qty} reason={action.reason}")
            
            if action.kind == "flatten":
                enforce_flatten(client, acct, action.symbol, action.reason)
            elif action.kind == "reduce":
                enforce_reduce(client, acct, action.symbol, action.qty, action.reason)
            elif action.kind == "cancel_orders":
                enforce_cancel_orders(client, acct, action.symbol, action.reason)
            elif action.kind == "lockout":
                enforce_lockout(acct, action.reason)
            elif action.kind == "noop":
                logger.info(f"No action needed for {acct}: {action.reason}")
            else:
                logger.warning(f"Unknown action kind: {action.kind}")
                
    except Exception as e:
        logger.error(f"Error enforcing actions for {acct}: {e}")

def build_ctx(acct: str) -> EvaluationContext:
    """Build evaluation context with real data."""
    # Check lockout first
    if check_lockout(acct):
        logger.warning(f"Account {acct} is locked out, skipping evaluation")
        return None
    
    try:
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
    except Exception as e:
        logger.error(f"Error building context for {acct}: {e}")
        return None

class RiskMonitor:
    def __init__(self, brain: PolicyBrain | None = None):
        self.brain = brain or PolicyBrain()

    def tick(self):
        """Execute one monitoring tick."""
        for acct in get_monitored_accounts():
            try:
                # Build context
                ctx = build_ctx(acct)
                if ctx is None:
                    continue
                
                # Evaluate with policy brain
                plan = self.brain.evaluate(ctx)
                
                # Log the tick event
                ctx_data = {
                    "account_id": ctx.account_id,
                    "day_pnl": ctx.day_pnl,
                    "risk_tier": ctx.risk_tier,
                    "positions_count": len(ctx.positions),
                    "orders_count": len(ctx.orders),
                    "timestamp": ctx.ts.isoformat()
                }
                log_tick_event(plan.correlation_id, ctx_data, plan)
                
                # Execute enforcement
                client_enforce(acct, plan)
                
            except Exception as e:
                logger.error(f"Error in tick for account {acct}: {e}")

def run_monitor_once():
    """Run one monitoring tick."""
    RiskMonitor().tick()
