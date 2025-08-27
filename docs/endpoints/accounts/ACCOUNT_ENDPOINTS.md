# Account Endpoints

## Search Active Accounts
**URL:** `POST /api/Account/search`

**Description:** Search for accounts with optional filtering for active accounts only.

**Parameters:**
| Name               | Type    | Description                             | Required | Nullable |
| ------------------ | ------- | --------------------------------------- | -------- | -------- |
| onlyActiveAccounts | boolean | Whether to filter only active accounts. | Required | false    |

**Request Body:**
```json
{
  "onlyActiveAccounts": true
}
```

**Response:**
```json
{
    "accounts": [
        {
            "id": 1,
            "name": "TEST_ACCOUNT_1",
            "balance": 50000,
            "canTrade": true,
            "isVisible": true
        }
    ],
    "success": true,
    "errorCode": 0,
    "errorMessage": null
}
```

**Error Response:**
```
Error: response status is 401
```

**cURL Example:**
```bash
curl -X 'POST' \
  'https://gateway-api-demo.s2f.projectx.com/api/Account/search' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
    "onlyActiveAccounts": true
  }'
```

**Source:** [ProjectX Gateway API - Search for Account](https://gateway.docs.projectx.com/docs/api-reference/account/search-accounts)
