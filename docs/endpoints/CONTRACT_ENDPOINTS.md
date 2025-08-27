# Contract Endpoints

## Get Available Contracts
**URL:** `POST /api/Contract/available`

**Request Body:**
```json
{
  "live": true
}
```

**Response:**
```json
{
    "contracts": [
        {
            "id": "CON.F.US.BP6.U25",
            "name": "6BU5",
            "description": "British Pound (Globex): September 2025",
            "tickSize": 0.0001,
            "tickValue": 6.25,
            "activeContract": true,
            "symbolId": "F.US.BP6"
        }
    ],
    "success": true,
    "errorCode": 0,
    "errorMessage": null
}
```

**cURL Example:**
```bash
curl -X 'POST' \
  'https://gateway-api-demo.s2f.projectx.com/api/Contract/available' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
    "live": true
  }'
```

## Search Contracts
**URL:** `POST /api/Contract/search`

**Description:** Search for contracts. Note: The response returns up to 20 contracts at a time.

**Parameters:**
| Name       | Type    | Description                                                           | Required | Nullable |
| ---------- | ------- | --------------------------------------------------------------------- | -------- | -------- |
| searchText | string  | The name of the contract to search for.                               | Required | false    |
| live       | boolean | Whether to search for contracts using the sim/live data subscription. | Required | false    |

**Request Body:**
```json
{
  "live": false,
  "searchText": "NQ"
}
```

**Response:**
```json
{
  "contracts": [
      {
          "id": "CON.F.US.ENQ.U25",
          "name": "NQU5",
          "description": "E-mini NASDAQ-100: September 2025",
          "tickSize": 0.25,
          "tickValue": 5,
          "activeContract": true,
          "symbolId": "F.US.ENQ"
      },
      {
          "id": "CON.F.US.MNQ.U25",
          "name": "MNQU5",
          "description": "Micro E-mini Nasdaq-100: September 2025",
          "tickSize": 0.25,
          "tickValue": 0.5,
          "activeContract": true,
          "symbolId": "F.US.MNQ"
      },
      {
          "id": "CON.F.US.NQG.Q25",
          "name": "QGQ5",
          "description": "E-Mini Natural Gas: August 2025",
          "tickSize": 0.005,
          "tickValue": 12.5,
          "activeContract": true,
          "symbolId": "F.US.NQG"
      },
      {
          "id": "CON.F.US.NQM.U25",
          "name": "QMU5",
          "description": "E-Mini Crude Oil: September 2025",
          "tickSize": 0.025,
          "tickValue": 12.5,
          "activeContract": true,
          "symbolId": "F.US.NQM"
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
  'https://gateway-api-demo.s2f.projectx.com/api/Contract/search' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
    "live": false,
    "searchText": "NQ"
  }'
```

## Search Contract by ID
**URL:** `POST /api/Contract/searchById`

**Description:** Search for contracts.

**Parameters:**
| Name       | Type   | Description                           | Required | Nullable |
| ---------- | ------ | ------------------------------------- | -------- | -------- |
| contractId | string | The id of the contract to search for. | Required | false    |

**Request Body:**
```json
{
  "contractId": "CON.F.US.ENQ.H25"
}
```

**Response:**
```json
{
  "contract": {
      "id": "CON.F.US.ENQ.H25",
      "name": "NQH5",
      "description": "E-mini NASDAQ-100: March 2025",
      "tickSize": 0.25,
      "tickValue": 5,
      "activeContract": false,
      "symbolId": "F.US.ENQ"
  },
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
  'https://gateway-api-demo.s2f.projectx.com/api/Contract/searchById' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
    "contractId": "CON.F.US.ENQ.H25"
  }'
```

**Sources:** 
- [ProjectX Gateway API - Search for Contracts](https://gateway.docs.projectx.com/docs/api-reference/market-data/search-contracts)
- [ProjectX Gateway API - Search for Contract by Id](https://gateway.docs.projectx.com/docs/api-reference/market-data/search-contracts-by-id)
