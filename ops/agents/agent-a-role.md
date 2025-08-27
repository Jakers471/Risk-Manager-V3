Role: Engine & Monitor
Owns: risk_manager_v2/engine/*, risk_manager_v2/cli/monitoring.py
Do not touch: core/clients/*, auth, docs
Rules: ≤200 LOC/file, ≤40 LOC/function, no new deps, DI for clients/limiters, idempotent enforcement, respect dry_run
Definition of done:
- start(client, rate_limiter, dry_run) / stop loop
- build EvaluationContext → RiskEngine.evaluate → Enforcer.apply
- metrics exposed: total_evaluations, total_actions, violations_current
- CLI dry-run toggle works and persists; emergency stop sets kill switch
