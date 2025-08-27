# TopStepX API Rate Limits

## Overview
The Gateway API employs a rate limiting system for all authenticated requests to promote fair usage, prevent abuse, and ensure service stability.

## Rate Limit Table

| Endpoint(s)                    | Limit                     |
| ------------------------------ | ------------------------- |
| POST /api/History/retrieveBars | 50 requests / 30 seconds  |
| All other Endpoints            | 200 requests / 60 seconds |

## Rate Limit Exceeded

### HTTP Response
When rate limits are exceeded, the API responds with:
- **Status Code:** `429 Too Many Requests`
- **Action Required:** Reduce request frequency and retry after delay

### Handling Strategy
- **Implement exponential backoff** for retry logic
- **Monitor request frequency** to stay within limits
- **Queue requests** when approaching limits
- **Prioritize critical operations** (risk management actions)

## Implementation Notes
- **Risk management system** must respect these limits
- **Real-time monitoring** should optimize request frequency
- **Emergency actions** (position flattening) should have priority
- **Batch operations** when possible to reduce request count

**Source:** [ProjectX Gateway API - Rate Limits](https://gateway.docs.projectx.com/docs/getting-started/rate-limits)
