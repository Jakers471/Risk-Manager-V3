# Task A1 – Monitoring Loop + CLI (DRY-RUN)

BRANCH: feat/engine-loop
OWN: risk_manager_v2/engine/monitor.py, risk_manager_v2/cli/monitoring.py
DO NOT TOUCH: risk_manager_v2/core/clients/*

GOAL
- Implement a minimal, robust monitoring loop in DRY-RUN mode (no live write actions).
- Expose Start/Stop + live counters in a CLI “Monitoring” menu.

LOOP (per tick)
- Get monitored accounts (stub is fine for now).
- For each account:
  - client.get_positions(account_id)
  - client.get_orders(account_id)
  - Build EvaluationContext (dict is OK for now).
  - RiskEngine.evaluate(ctx) → ActionPlan (stub OK)
  - Enforcer.apply(account_id, plan, dry_run=True)  # must honor dry_run
- Track counters: total_evaluations, total_actions, violations_current (dict per account OK).

START/STOP & PACING
- start_monitoring(client, rate_limiter, dry_run) → spawn background thread.
- Use threading.Event for shutdown and pacing: event.wait(0.5–1.0) instead of time.sleep.
- stop_monitoring() → set event, join thread; **no API calls after stopped**.

CLI
- New “Monitoring” menu with:
  - Start Monitoring / Stop Monitoring
  - Live counters (evaluations/actions/violations)
  - Dry-run toggle persisted to config (default True)

CONSTRAINTS
- ≤200 LOC per file; no new dependencies; keep Import Smoke green (no heavy work at import time).
- Small commits; keep scope limited to OWN files.

ACCEPTANCE CRITERIA
- Starts/stops cleanly, no API calls when stopped.
- Dry-run is respected (no write calls executed).
- Live counters update while running.
- Import Smoke is green on PR.
- Manual:
  - `python -m risk_manager_v2.cli.main`
  - Start Monitoring (dry-run)
  - Verify counters increase; Stop Monitoring; verify clean shutdown.

PR CHECKLIST
- Title: `feat(engine-loop): monitoring loop + CLI (dry-run)`
- ≤5 files, ≤400 LOC total (split into follow-ups if needed).
- Description includes **What changed / Why / Test notes**.

MODULARIZATION POLICY
- If a change nears ~400 LOC, you MAY split code across up to 1–3 files inside OWN paths only.
- Keep PRs small; otherwise split into follow-up PRs.
- Do NOT touch DO NOT TOUCH paths; no new dependencies.
