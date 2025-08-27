# Task A1 – Monitoring Loop + CLI
BRANCH: feat/engine-loop
SCOPE: risk_manager_v2/engine/monitor.py, risk_manager_v2/cli/monitoring.py
DO:
- Implement start_monitoring()/stop_monitoring() with background thread + threading.Event.wait(0.5–1.0)
- Per tick build EvaluationContext, call RiskEngine.evaluate(ctx) (stub ok), Enforcer.apply(..., dry_run)
- Maintain counters & expose get_monitoring_status()
- Wire CLI: Start/Stop Monitoring, live counters, dry_run toggle persisted to config
DONE WHEN:
- Import Smoke green
- Manual: python -m risk_manager_v2.cli.main -> start/stop works, counters increase (dry-run)
