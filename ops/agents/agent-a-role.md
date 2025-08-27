# Agent A – Engine & Monitor
OWN: risk_manager_v2/engine/monitor.py, risk_manager_v2/cli/monitoring.py
DO NOT TOUCH: risk_manager_v2/core/clients/*
STYLE: ≤200 LOC per file, small commits, no new deps.
LOOP:
- get monitored accounts (stub ok)
- for each: client.get_positions(), client.get_orders()
- build EvaluationContext (dict ok if no builder)
- RiskEngine.evaluate(ctx) -> ActionPlan (stub ok)
- Enforcer.apply(account_id, plan) honoring dry_run
- counters: total_evaluations, total_actions, violations_current (per account ok)
START/STOP:
- start_monitoring(client, rate_limiter, dry_run) -> thread + threading.Event.wait() for pacing
- stop_monitoring() -> set event, join; no API calls when stopped
CLI:
- Start/Stop Monitoring, live counters, dry_run toggle persisted to config
ACCEPTANCE: starts/stops cleanly; dry-run respected; no busy sleep; no calls when stopped
