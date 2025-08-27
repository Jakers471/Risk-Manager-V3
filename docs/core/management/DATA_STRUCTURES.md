# TopStepX Data Structures

## Overview
Data models and structures for positions, orders, trades, and account information.

## Account Models

### Account Object
```json
{
    "id": 1,
    "name": "TEST_ACCOUNT_1",
    "balance": 50000,
    "canTrade": true,
    "isVisible": true
}
```

### Account Search Request
```json
{
    "onlyActiveAccounts": true
}
```

## Contract Models

### Contract Object
```json
{
    "id": "CON.F.US.BP6.U25",
    "name": "6BU5",
    "description": "British Pound (Globex): September 2025",
    "tickSize": 0.0001,
    "tickValue": 6.25,
    "activeContract": true,
    "symbolId": "F.US.BP6"
}
```

### Contract Search Request
```json
{
    "live": false,
    "searchText": "NQ"
}
```

### Contract Search by ID Request
```json
{
    "contractId": "CON.F.US.ENQ.H25"
}
```

### Contract Search by ID Response
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

## Order Models

### Order Request
```json
{
    "accountId": 1,
    "contractId": "CON.F.US.BP6.U25",
    "type": 2,
    "side": 1,
    "size": 1
}
```

### Order Response
```json
{
    "orderId": 9056,
    "success": true,
    "errorCode": 0,
    "errorMessage": null
}
```

### Order Parameters
- **type**: Order type (2 = Market order)
- **side**: Order side (1 = Ask/Sell, 2 = Bid/Buy)
- **size**: Number of contracts

## Position Models
*[To be populated with position data structures]*

## Market Data Models

### Bar Data Request
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

### Bar Data Response
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

### Bar Object
- **t**: Timestamp
- **o**: Open price
- **h**: High price
- **l**: Low price
- **c**: Close price
- **v**: Volume

### Time Units
- 1 = Second
- 2 = Minute
- 3 = Hour
- 4 = Day
- 5 = Week
- 6 = Month

## Trade Models
*[To be populated with trade execution data structures]*

**Sources:** 
- [ProjectX Gateway API - Placing Your First Order](https://gateway.docs.projectx.com/docs/getting-started/placing-your-first-order)
- [ProjectX Gateway API - Search for Account](https://gateway.docs.projectx.com/docs/api-reference/account/search-accounts)

---
*This document will be updated as data structure information is provided.*
