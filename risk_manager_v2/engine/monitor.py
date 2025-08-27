from datetime import datetime, timezone
from typing import List
from risk_manager_v2.schemas.evaluation_context import EvaluationContext, Position, Order
from risk_manager_v2.policy.brain import PolicyBrain
from risk_manager_v2.schemas.action_plan import ActionPlan

# ---- stubs to replace with real ProjectX/Topstep client calls ----
def get_monitored_accounts() -> List[str]:
    return ["11010173"]

def client_get_positions(acct: str) -> List[Position]:
    return []

def client_get_orders(acct: str) -> List[Order]:
    return []

def client_get_day_pnl(acct: str) -> float:
    return 0.0

def client_enforce(acct: str, plan: ActionPlan):
    for a in plan.actions:
        print(f"[ENFORCE] {acct} => {a.kind} {a.symbol} qty={a.qty} reason={a.reason}")

def build_ctx(acct: str) -> EvaluationContext:
    return EvaluationContext(
        ts=datetime.now(timezone.utc),
        account_id=acct,
        day_pnl=client_get_day_pnl(acct),
        max_drawdown_today=0.0,
        risk_tier="t0",
        positions=client_get_positions(acct),
        orders=client_get_orders(acct),
        env={"market_hours": "unknown"}
    )

class RiskMonitor:
    def __init__(self, brain: PolicyBrain | None = None):
        self.brain = brain or PolicyBrain()

    def tick(self):
        for acct in get_monitored_accounts():
            ctx = build_ctx(acct)
            plan = self.brain.evaluate(ctx)
            client_enforce(acct, plan)

def run_monitor_once():
    RiskMonitor().tick()
