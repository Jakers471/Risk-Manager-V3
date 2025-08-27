# Agent B – ProjectX Client & Rate Limits
OWN: risk_manager_v2/core/clients/projectx.py, risk_manager_v2/utils/rate_limiter.py
DO NOT TOUCH: risk_manager_v2/engine/*
LIMITS: general=200/min; market bars=50/30s (separate bucket)
RETRY: 401->validate/refresh->retry once; 429/5xx backoff
ENDPOINTS:
- POST /api/Account/search
- POST /api/Position/searchOpen
- POST /api/Order/searchOpen, /api/Order/place, /api/Order/cancel
- POST /api/Position/closeContract, /api/Position/partialCloseContract
- POST /api/Trade/search
- POST /api/Contract/available, /api/Contract/search, /api/Contract/searchById
- POST /api/MarketData/bars
TESTS: 1 mocked unit test (endpoint path/payload + 401->retry path)

MODULARIZATION POLICY
- If a change approaches ~400 LOC, you MAY split code across up to 1–3 files INSIDE your OWN paths only:
  OWN: risk_manager_v2/core/clients/projectx.py, risk_manager_v2/utils/rate_limiter.py
- Keep PRs small: ≤5 files and ideally ≤400 LOC total; otherwise split into follow-up PRs.
- No new dependencies. Do NOT touch DO NOT TOUCH paths.
- Keep Import Smoke green: avoid heavy work at module import time.

MODULARIZATION & TESTS POLICY
- If a change approaches ~400 LOC, you MAY split code across up to 1–3 files INSIDE your OWN paths only:
  OWN: risk_manager_v2/core/clients/projectx.py, risk_manager_v2/utils/rate_limiter.py
- Keep PRs small: ≤5 files and ideally ≤400 LOC total; otherwise split into follow-up PRs.
- No new dependencies. Do NOT touch DO NOT TOUCH paths (especially engine/*).
- Keep Import Smoke green: avoid heavy work at module import time.
- Unit tests must live under tests/, fully mocked (no real network).
  Allowed now: tests/test_projectx_client.py only.
