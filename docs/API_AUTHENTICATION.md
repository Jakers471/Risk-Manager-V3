# TopStepX API Authentication

## Overview
TopStepX uses JSON Web Tokens (JWT) for authentication. Obtain a session token required for all future requests.

## Prerequisites
- API key from your firm
- Connection URLs (see [Connection URLs](https://gateway.docs.projectx.com/docs/getting-started/connection-urls))

## Authentication Endpoint

**URL:** `POST https://gateway-api-demo.s2f.projectx.com/api/Auth/loginKey`

**Request Body:**
```json
{
    "userName": "string",
    "apiKey": "string"
}
```

**Response:**
```json
{
    "token": "your_session_token_here",
    "success": true,
    "errorCode": 0,
    "errorMessage": null
}
```

**cURL Example:**
```bash
curl -X 'POST' \
  'https://gateway-api-demo.s2f.projectx.com/api/Auth/loginKey' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
    "userName": "string",
    "apiKey": "string"
  }'
```

## Session Validation

### Token Expiration
Session tokens are only valid for **24 hours**. If your token expires, you must re-validate it to receive a new token.

### Validation Endpoint

**URL:** `POST https://gateway-api-demo.s2f.projectx.com/api/Auth/validate`

**Request:** No body required (uses existing token in Authorization header)

**Response:**
```json
{
  "success": true,
  "errorCode": 0,
  "errorMessage": null,
  "newToken": "NEW_TOKEN"
}
```

**cURL Example:**
```bash
curl -X 'POST' \
  'https://gateway-api-demo.s2f.projectx.com/api/Auth/validate' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json'
```

## Usage Notes
- Store session token securely
- Token provides full access to Gateway API
- Check `success` field and `errorCode` (0 = success)
- Include token in Authorization header for subsequent requests
- **Validate token before expiration** (24-hour limit)
- **Use newToken** from validation response when provided

**Sources:** 
- [ProjectX Gateway API - Authenticate with API Key](https://gateway.docs.projectx.com/docs/getting-started/authenticate/authenticate-api-key)
- [ProjectX Gateway API - Validate Session](https://gateway.docs.projectx.com/docs/getting-started/validate-session)
