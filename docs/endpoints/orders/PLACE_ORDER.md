# Place Order

**URL:** `POST /api/Order/place`

**Description:** Place an order.

**Parameters:**
| Name          | Type    | Description                                                                                  | Required | Nullable |
| ------------- | ------- | -------------------------------------------------------------------------------------------- | -------- | -------- |
| accountId     | integer | The account ID.                                                                              | Required | false    |
| contractId    | string  | The contract ID.                                                                             | Required | false    |
| type          | integer | The order type: 1=Limit 2=Market 4=Stop 5=TrailingStop 6=JoinBid 7=JoinAsk | Required | false    |
| side          | integer | The side of the order: 0=Bid (buy) 1=Ask (sell)                                        | Required | false    |
| size          | integer | The size of the order.                                                                       | Required | false    |
| limitPrice    | decimal | The limit price for the order, if applicable.                                                | Optional | true     |
| stopPrice     | decimal | The stop price for the order, if applicable.                                                 | Optional | true     |
| trailPrice    | decimal | The trail price for the order, if applicable.                                                | Optional | true     |
| customTag     | string  | An optional custom tag for the order. Must be unique across the account.                     | Optional | true     |
| linkedOrderId | integer | The linked order id.                                                                         | Optional | true     |

**Request Body:**
```json
{
  "accountId": 465,
  "contractId": "CON.F.US.DA6.M25",
  "type": 2,
  "side": 1,
  "size": 1,
  "limitPrice": null,
  "stopPrice": null,
  "trailPrice": null,
  "customTag": null,
  "linkedOrderId": null
}
```

**Response:**
```json
{
    "orderId": 9056,
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
  'https://gateway-api-demo.s2f.projectx.com/api/Order/place' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
    "accountId": 465,
    "contractId": "CON.F.US.DA6.M25",
    "type": 2,
    "side": 1,
    "size": 1,
    "limitPrice": null,
    "stopPrice": null,
    "trailPrice": null,
    "customTag": null,
    "linkedOrderId": null
  }'
```

## Order Types
- **1**: Limit order
- **2**: Market order
- **4**: Stop order
- **5**: TrailingStop order
- **6**: JoinBid order
- **7**: JoinAsk order

## Order Sides
- **0**: Bid (buy)
- **1**: Ask (sell)

**Source:** [ProjectX Gateway API - Place an Order](https://gateway.docs.projectx.com/docs/api-reference/order/order-place)
