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
