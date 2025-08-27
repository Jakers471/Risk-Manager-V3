Role: ProjectX Client, Realtime, Rate Limits
Owns: risk_manager_v2/core/clients/projectx.py, risk_manager_v2/core/realtime.py, risk_manager_v2/utils/rate_limits.py
Do not touch: engine/*
Rules: two token buckets (general=200/min, bars=50/30s), correct endpoints (Position/searchOpen, Order/*, History/retrieveBars), 401→validate→reauth, raise typed errors
Definition of done:
- Correct endpoints/payloads wired with rate limiter
- Realtime skeleton with callbacks
- Basic unit tests with mocks
