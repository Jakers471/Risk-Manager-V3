Agent B — Policy/Rules
Owns: Load config/policy.yml; rule order: DailyLoss > LockoutActive > SizeGuard(total+per-symbol) > NewsBlackout > LateSession > noop; fill ActionPlan.notes; selftests.
Out of scope: Client/networking (C); enforcement calls (A).
