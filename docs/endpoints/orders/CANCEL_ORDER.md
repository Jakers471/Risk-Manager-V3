# Cancel Order

**URL:** `POST /api/Order/cancel`

**Description:** Cancel an order.

**Parameters:**
| Name      | Type    | Description     | Required | Nullable |
| --------- | ------- | --------------- | -------- | -------- |
| accountId | integer | The account ID. | Required | false    |
| orderId   | integer | The order id.   | Required | false    |

**Request Body:**
```json
{
  "accountId": 465,
  "orderId": 26974
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
  'https://gateway-api-demo.s2f.projectx.com/api/Order/cancel' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
    "accountId": 465,
    "orderId": 26974
  }'
```

**Source:** [ProjectX Gateway API - Cancel an Order](https://gateway.docs.projectx.com/docs/api-reference/order/order-cancel)
