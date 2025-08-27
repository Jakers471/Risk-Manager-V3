# Close Positions

**URL:** `POST /api/Position/closeContract`

**Description:** Close a position.

**Parameters:**
| Name       | Type    | Description      | Required | Nullable |
| ---------- | ------- | ---------------- | -------- | -------- |
| accountId  | integer | The account ID.  | Required | false    |
| contractId | string  | The contract ID. | Required | false    |

**Request Body:**
```json
{
  "accountId": 536,
  "contractId": "CON.F.US.GMET.J25"
}
```

**Response:**
```json
{
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
  'https://gateway-api-demo.s2f.projectx.com/api/Position/closeContract' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
    "accountId": 536,
    "contractId": "CON.F.US.GMET.J25"
  }'
```

**Source:** [ProjectX Gateway API - Close Positions](https://gateway.docs.projectx.com/docs/api-reference/positions/close-positions)
