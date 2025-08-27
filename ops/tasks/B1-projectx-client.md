# Task B1 – ProjectX Client + Rate-Limit Buckets (+ 1 mocked test)

BRANCH: feat/projectx-client
OWN: risk_manager_v2/core/clients/projectx.py, risk_manager_v2/utils/rate_limiter.py
DO NOT TOUCH: risk_manager_v2/engine/*

GOAL
- Replace the shim with a real ProjectXClient with correct endpoints + error handling.
- Enforce two rate-limit buckets:
  - general = 200/min
  - market bars = 50 per 30s (separate bucket)

ENDPOINTS (POST unless noted)
- /api/Account/search
- /api/Position/searchOpen
- /api/Order/searchOpen, /api/Order/place, /api/Order/cancel
- /api/Position/closeContract, /api/Position/partialCloseContract
- /api/Trade/search
- /api/Contract/available, /api/Contract/search, /api/Contract/searchById
- /api/MarketData/bars  (USES the bars bucket)

RETRY / BACKOFF
- 401 → validate/refresh → retry **once**.
- 429/5xx → exponential backoff (e.g., 1s, 2s) then give up (return None).
- Timeouts handled similarly (limited retries).

TESTS (mocked; no real HTTP)
- Add `tests/test_projectx_client.py` with:
  - Asserts correct endpoint path + payload shape for one call.
  - 401 → refresh → retry path covered.
  - No network calls (mock session).

CONSTRAINTS
- ≤200 LOC per file; no new dependencies; keep Import Smoke green.
- Small commits; keep scope limited to OWN files.

ACCEPTANCE CRITERIA
- Methods implemented for the listed endpoints.
- Rate limiter buckets applied correctly (general vs bars).
- 401 retry logic works; 429/5xx backoff handled.
- Import Smoke is green on PR.
- `pytest -q` passes locally (mocked test only).

PR CHECKLIST
- Title: `feat(projectx-client): endpoints + buckets + mocked test`
- ≤5 files, ≤400 LOC total (split if bigger).
- Description includes **What changed / Why / Tests** (mention mocked tests).

MODULARIZATION & TESTS POLICY
- If a change nears ~400 LOC, you MAY split code across up to 1–3 files in OWN paths only.
- Keep PRs small; otherwise split into follow-ups.
- Tests must live under `tests/` and be fully mocked (no real network).
