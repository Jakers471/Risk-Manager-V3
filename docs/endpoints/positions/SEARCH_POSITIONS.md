# Search Positions

**URL:** `POST /api/Position/search`

**Description:** Search for positions.

**Parameters:**
| Name      | Type    | Description     | Required | Nullable |
| --------- | ------- | --------------- | -------- | -------- |
| accountId | integer | The account ID. | Required | false    |

**Request Body:**
```json
{
  "accountId": 536
}
```

**Response:**
```json
{
    "positions": [
        {
            "accountId": 536,
            "contractId": "CON.F.US.GMET.J25",
            "size": 5,
            "avgPrice": 1604.50
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
  'https://gateway-api-demo.s2f.projectx.com/api/Position/search' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
    "accountId": 536
  }'
```

**Source:** [ProjectX Gateway API - Search for Positions](https://gateway.docs.projectx.com/docs/api-reference/positions/search-positions)
