# Market Data Endpoints

## Retrieve Bars
**URL:** `POST /api/History/retrieveBars`

**Description:** Retrieve historical bar data with configurable time aggregation.

**Note:** Maximum 20,000 bars per request.

**Parameters:**
| Name              | Type     | Description                                                                                                      | Required | Nullable |
| ----------------- | -------- | ---------------------------------------------------------------------------------------------------------------- | -------- | -------- |
| contractId        | integer  | The contract ID.                                                                                                 | Required | false    |
| live              | boolean  | Whether to retrieve bars using the sim or live data subscription.                                                | Required | false    |
| startTime         | datetime | The start time of the historical data.                                                                           | Required | false    |
| endTime           | datetime | The end time of the historical data.                                                                             | Required | false    |
| unit              | integer  | The unit of aggregation: 1=Second 2=Minute 3=Hour 4=Day 5=Week 6=Month | Required | false    |
| unitNumber        | integer  | The number of units to aggregate.                                                                                | Required | false    |
| limit             | integer  | The maximum number of bars to retrieve.                                                                          | Required | false    |
| includePartialBar | boolean  | Whether to include a partial bar representing the current time unit.                                             | Required | false    |

**Request Body:**
```json
{
    "contractId": "CON.F.US.RTY.Z24",
    "live": false,
    "startTime": "2024-12-01T00:00:00Z",
    "endTime": "2024-12-31T21:00:00Z",
    "unit": 3,
    "unitNumber": 1,
    "limit": 7,
    "includePartialBar": false
}
```

**Response:**
```json
{
    "bars": [
        {
            "t": "2024-12-20T14:00:00+00:00",
            "o": 2208.100000000,
            "h": 2217.000000000,
            "l": 2206.700000000,
            "c": 2210.100000000,
            "v": 87
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
  'https://gateway-api-demo.s2f.projectx.com/api/History/retrieveBars' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
    "contractId": "CON.F.US.RTY.Z24",
    "live": false,
    "startTime": "2024-12-01T00:00:00Z",
    "endTime": "2024-12-31T21:00:00Z",
    "unit": 3,
    "unitNumber": 1,
    "limit": 7,
    "includePartialBar": false
  }'
```

**Source:** [ProjectX Gateway API - Retrieve Bars](https://gateway.docs.projectx.com/docs/api-reference/market-data/retrieve-bars)
