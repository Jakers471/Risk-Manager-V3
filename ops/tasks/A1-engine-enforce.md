A1 — Engine Enforce + Logs + Lockout (MVP)
1) Wire monitor to ProjectXClient (replace stubs).
2) Implement enforce: flatten, reduce, cancel_orders, lockout.
3) Lockout guard: if runtime/lock.json.locked → only reduce/flatten.
4) Emit runtime/events/<correlation_id>.json {ctx, plan, results}.
Acceptance: one tick prints actions, writes event JSON, honors lockout.
