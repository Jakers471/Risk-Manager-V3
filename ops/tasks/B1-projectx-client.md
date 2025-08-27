# Task B1 – ProjectX Client + Buckets
BRANCH: feat/projectx-client
SCOPE: risk_manager_v2/core/clients/projectx.py, risk_manager_v2/utils/rate_limiter.py, tests/test_projectx_client.py
DO:
- Replace shim with real methods for listed endpoints
- Inject limiter; apply correct bucket per call
- 401 -> validate/refresh -> retry once; 429/5xx backoff
- Add one mocked unit test (no real HTTP)
DONE WHEN:
- Import Smoke green
- Test passes locally: `pytest -q` (minimal is fine)
