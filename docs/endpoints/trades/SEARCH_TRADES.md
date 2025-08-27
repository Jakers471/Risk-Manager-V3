# Search Trades

**URL:** `POST /api/Trade/search`

**Description:** Search for trades from the request parameters.

**Parameters:**
| Name           | Type     | Description                        | Required | Nullable |
| -------------- | -------- | ---------------------------------- | -------- | -------- |
| accountId      | integer  | The account ID.                    | Required | false    |
| startTimestamp | datetime | The start of the timestamp filter. | Required | false    |
| endTimestamp   | datetime | The end of the timestamp filter.   | Optional | true     |

**Request Body:**
```json
{
  "accountId": 203,
  "startTimestamp": "2025-01-20T15:47:39.882Z",
  "endTimestamp": "2025-01-30T15:47:39.882Z"
}
```

**Response:**
```json
{
    "trades": [
        {
            "id": 8604,
            "accountId": 203,
            "contractId": "CON.F.US.EP.H25",
            "creationTimestamp": "2025-01-21T16:13:52.523293+00:00",
            "price": 6065.250000000,
            "profitAndLoss": 50.000000000,
            "fees": 1.4000,
            "side": 1,
            "size": 1,
            "voided": false,
            "orderId": 14328
        },
        {
            "id": 8603,
            "accountId": 203,
            "contractId": "CON.F.US.EP.H25",
            "creationTimestamp": "2025-01-21T16:13:04.142302+00:00",
            "price": 6064.250000000,
            "profitAndLoss": null,
            "fees": 1.4000,
            "side": 0,
            "size": 1,
            "voided": false,
            "orderId": 14326
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
  'https://gateway-api-demo.s2f.projectx.com/api/Trade/search' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
    "accountId": 203,
    "startTimestamp": "2025-01-20T15:47:39.882Z",
    "endTimestamp": "2025-01-30T15:47:39.882Z"
  }'
```

## Trade Response Fields
- **id**: Unique trade identifier
- **accountId**: Account that executed the trade
- **contractId**: Contract that was traded
- **creationTimestamp**: When the trade was executed
- **price**: Execution price
- **profitAndLoss**: Realized P&L (null for half-turn trades)
- **fees**: Trading fees
- **side**: 0 = Bid (buy), 1 = Ask (sell)
- **size**: Number of contracts
- **voided**: Whether trade was voided
- **orderId**: Associated order ID

**Source:** [ProjectX Gateway API - Search for Trades](https://gateway.docs.projectx.com/docs/api-reference/trade/trade-search)
