# Modify Order

**URL:** `POST /api/Order/modify`

**Description:** Modify an open order.

**Parameters:**
| Name       | Type    | Description                                   | Required | Nullable |
| ---------- | ------- | --------------------------------------------- | -------- | -------- |
| accountId  | integer | The account ID.                               | Required | false    |
| orderId    | integer | The order id.                                 | Required | false    |
| size       | integer | The size of the order.                        | Optional | true     |
| limitPrice | decimal | The limit price for the order, if applicable. | Optional | true     |
| stopPrice  | decimal | The stop price for the order, if applicable.  | Optional | true     |
| trailPrice | decimal | The trail price for the order, if applicable. | Optional | true     |

**Request Body:**
```json
{
  "accountId": 465,
  "orderId": 26974,
  "size": 1,
  "limitPrice": null,
  "stopPrice": 1604,
  "trailPrice": null
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
  'https://gateway-api-demo.s2f.projectx.com/api/Order/modify' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
    "accountId": 465,
    "orderId": 26974,
    "size": 1,
    "limitPrice": null,
    "stopPrice": 1604,
    "trailPrice": null
  }'
```

**Source:** [ProjectX Gateway API - Modify an Order](https://gateway.docs.projectx.com/docs/api-reference/order/order-modify)
