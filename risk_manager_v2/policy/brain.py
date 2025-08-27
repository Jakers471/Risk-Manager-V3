from typing import Dict, Any
from risk_manager_v2.schemas.evaluation_context import EvaluationContext
from risk_manager_v2.schemas.action_plan import ActionPlan, Action
import uuid

class PolicyBrain:
    """
    Deterministic rules first; ML later.
    """
    def evaluate(self, ctx: EvaluationContext) -> ActionPlan:
        cid = uuid.uuid4().hex
        plan = ActionPlan(correlation_id=cid)

        # Example guardrails (replace with real account constraints):
        daily_loss_limit = {"t0": -150.0, "t1": -300.0, "t2": -600.0}.get(ctx.risk_tier, -150.0)
        max_contracts     = {"t0": 1,     "t1": 2,      "t2": 4     }.get(ctx.risk_tier, 1)

        # 1) Daily loss protection
        if ctx.day_pnl <= daily_loss_limit * 0.95:
            plan.actions.append(Action(kind="lockout", reason=f"Hit {ctx.risk_tier} daily loss"))
            for p in ctx.positions:
                plan.actions.append(Action(kind="flatten", symbol=p.symbol, reason="DailyLossLock"))
            plan.notes["policy"] = "DailyLoss"
            return plan

        # 2) Position size guard
        total_contracts = sum(abs(p.qty) for p in ctx.positions)
        if total_contracts > max_contracts:
            overflow = total_contracts - max_contracts
            # Reduce the largest position first (demo logic)
            biggest = sorted(ctx.positions, key=lambda p: abs(p.qty), reverse=True)[0] if ctx.positions else None
            if biggest:
                plan.actions.append(Action(kind="reduce", symbol=biggest.symbol, qty=overflow, reason="MaxContracts"))
                plan.notes["policy"] = "MaxContracts"

        # 3) Otherwise no-op
        if not plan.actions:
            plan.actions.append(Action(kind="noop", reason="Within limits"))
        return plan
