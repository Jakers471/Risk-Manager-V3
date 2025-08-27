import yaml
import os
from typing import Dict, Any
from risk_manager_v2.schemas.evaluation_context import EvaluationContext
from risk_manager_v2.schemas.action_plan import ActionPlan, Action
import uuid

class PolicyBrain:
    """
    Deterministic rules first; ML later.
    Rule order: DailyLoss > LockoutActive > SizeGuard > NewsBlackout > LateSession > noop
    """
    
    def __init__(self, config_path: str = "config/policy.yml"):
        self.config_path = config_path
        self.policy_config = self._load_policy_config()
    
    def _load_policy_config(self) -> Dict[str, Any]:
        """Load policy config from YAML file with fallback to built-ins."""
        built_in_config = {
            "tiers": {
                "t0": {"daily_loss": -150, "max_contracts": 1, "max_per_symbol": 1, "news_blackout_min": 15, "late_session_min": 10},
                "t1": {"daily_loss": -300, "max_contracts": 2, "max_per_symbol": 2, "news_blackout_min": 15, "late_session_min": 10},
                "t2": {"daily_loss": -600, "max_contracts": 4, "max_per_symbol": 3, "news_blackout_min": 30, "late_session_min": 15}
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                return built_in_config
        except Exception:
            return built_in_config
    
    def evaluate(self, ctx: EvaluationContext) -> ActionPlan:
        cid = uuid.uuid4().hex
        plan = ActionPlan(correlation_id=cid)
        
        tier_config = self.policy_config["tiers"].get(ctx.risk_tier, self.policy_config["tiers"]["t0"])
        
        # 1) Daily Loss Protection
        if ctx.day_pnl <= tier_config["daily_loss"] * 0.95:
            plan.actions.append(Action(kind="lockout", reason=f"Daily loss limit breached", severity="crit"))
            for p in ctx.positions:
                plan.actions.append(Action(kind="flatten", symbol=p.symbol, reason="DailyLossLock", severity="crit"))
            plan.notes.update({
                "policy": "DailyLoss",
                "threshold": f"${tier_config['daily_loss']}",
                "current": f"${ctx.day_pnl:.2f}",
                "breach_pct": f"{((ctx.day_pnl / tier_config['daily_loss']) * 100):.1f}%"
            })
            return plan
        
        # 2) Lockout Active Check
        if ctx.env.get("lockout_active", False):
            plan.actions.append(Action(kind="lockout", reason="Account lockout active", severity="crit"))
            plan.notes.update({
                "policy": "LockoutActive",
                "reason": "Account is in lockout state"
            })
            return plan
        
        # 3) Size Guard (total + per-symbol)
        total_contracts = sum(abs(p.qty) for p in ctx.positions)
        if total_contracts > tier_config["max_contracts"]:
            overflow = total_contracts - tier_config["max_contracts"]
            biggest = sorted(ctx.positions, key=lambda p: abs(p.qty), reverse=True)[0] if ctx.positions else None
            if biggest:
                plan.actions.append(Action(kind="reduce", symbol=biggest.symbol, qty=overflow, reason="MaxContracts", severity="warn"))
                plan.notes.update({
                    "policy": "SizeGuard",
                    "threshold": f"{tier_config['max_contracts']} total contracts",
                    "current": f"{total_contracts} contracts",
                    "overflow": f"{overflow} contracts"
                })
                return plan
        
        # Check per-symbol limits
        symbol_counts = {}
        for p in ctx.positions:
            symbol_counts[p.symbol] = symbol_counts.get(p.symbol, 0) + abs(p.qty)
        
        for symbol, count in symbol_counts.items():
            if count > tier_config["max_per_symbol"]:
                overflow = count - tier_config["max_per_symbol"]
                plan.actions.append(Action(kind="reduce", symbol=symbol, qty=overflow, reason="MaxPerSymbol", severity="warn"))
                plan.notes.update({
                    "policy": "SizeGuard",
                    "symbol": symbol,
                    "threshold": f"{tier_config['max_per_symbol']} contracts per symbol",
                    "current": f"{count} contracts",
                    "overflow": f"{overflow} contracts"
                })
                return plan
        
        # 4) News Blackout
        news_minutes = ctx.env.get("news_minutes_ago", 999)
        if news_minutes < tier_config["news_blackout_min"]:
            plan.actions.append(Action(kind="lockout", reason="News blackout period", severity="warn"))
            plan.notes.update({
                "policy": "NewsBlackout",
                "threshold": f"{tier_config['news_blackout_min']} minutes",
                "current": f"{news_minutes} minutes ago",
                "remaining": f"{tier_config['news_blackout_min'] - news_minutes} minutes"
            })
            return plan
        
        # 5) Late Session
        session_minutes_left = ctx.env.get("session_minutes_left", 999)
        if session_minutes_left < tier_config["late_session_min"]:
            plan.actions.append(Action(kind="lockout", reason="Late session trading", severity="info"))
            plan.notes.update({
                "policy": "LateSession",
                "threshold": f"{tier_config['late_session_min']} minutes remaining",
                "current": f"{session_minutes_left} minutes remaining"
            })
            return plan
        
        # 6) No-op (within limits)
        plan.actions.append(Action(kind="noop", reason="Within all policy limits", severity="info"))
        plan.notes.update({
            "policy": "noop",
            "daily_loss": f"${ctx.day_pnl:.2f} / ${tier_config['daily_loss']}",
            "total_contracts": f"{total_contracts} / {tier_config['max_contracts']}",
            "status": "All checks passed"
        })
        
        return plan
