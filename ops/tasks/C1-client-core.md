C1 — Endpoints + Mapping + PX_SIM + RateLimit
1) Auth header + base URL from env.
2) Implement endpoints: get_positions, get_orders, get_day_pnl, cancel_orders, place_market.
3) Map payloads → Position/Order dataclasses.
4) PX_SIM=1 returns deterministic mock payloads.
5) Use read/trade buckets in utils/rate_limiter.py.
6) Update docs/clients/USAGE.md with examples.
Acceptance: simple smoke returns shaped objects; smoke passes.
