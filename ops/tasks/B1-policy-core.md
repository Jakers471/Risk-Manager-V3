B1 — Policy Config + Precedence + Selftests
1) Load config/policy.yml (fallback defaults).
2) Rule order: DailyLoss > LockoutActive > SizeGuard(total+per-symbol) > NewsBlackout > LateSession > noop.
3) Fill ActionPlan.notes with thresholds and rule hits.
4) Add 3 selftests in cli/policy.py (loss breach, oversize, news blackout); print plans.
Acceptance: 3 printed plans with clear notes; smoke passes.
