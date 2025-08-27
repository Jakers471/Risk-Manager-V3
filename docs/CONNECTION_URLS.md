# Connection URLs

## Overview
Complete list of ProjectX Gateway API connection endpoints for both REST API and WebSocket connections.

---

## **API Endpoints**

### **Base API URL**
```
https://gateway-api-demo.s2f.projectx.com
```

### **Authentication Endpoints**
- **Login:** `POST /api/Auth/loginKey`
- **Session Validation:** `POST /api/Auth/validate`

### **Account Endpoints**
- **Search Accounts:** `POST /api/Account/search`

### **Contract Endpoints**
- **Available Contracts:** `POST /api/Contract/available`
- **Search Contracts:** `POST /api/Contract/search`
- **Search Contract by ID:** `POST /api/Contract/searchById`

### **Market Data Endpoints**
- **Retrieve Bars:** `POST /api/MarketData/bars`

### **Order Endpoints**
- **Place Order:** `POST /api/Order/place`
- **Search Orders:** `POST /api/Order/search`
- **Search Open Orders:** `POST /api/Order/searchOpen`
- **Cancel Order:** `POST /api/Order/cancel`
- **Modify Order:** `POST /api/Order/modify`

### **Position Endpoints**
- **Close Positions:** `POST /api/Position/closeContract`
- **Partially Close Positions:** `POST /api/Position/partialCloseContract`
- **Search Positions:** `POST /api/Position/search`

### **Trade Endpoints**
- **Search Trades:** `POST /api/Trade/search`

---

## **WebSocket Endpoints**

### **Real-Time Connection URLs**

#### **User Hub**
```
https://gateway-rtc-demo.s2f.projectx.com/hubs/user
```

**Purpose:** Real-time updates for user-specific data
- Account balance and status updates
- Order status and fill updates
- Position changes and updates
- Trade execution notifications

#### **Market Hub**
```
https://gateway-rtc-demo.s2f.projectx.com/hubs/market
```

**Purpose:** Real-time market data
- Market quotes and pricing
- Market depth/DOM updates
- Market trade notifications

---

## **Connection Parameters**

### **Authentication**
- **Method:** JWT Bearer Token
- **Header:** `Authorization: Bearer <token>`
- **URL Parameter:** `?access_token=<token>`

### **WebSocket Configuration**
- **Transport:** WebSockets (SignalR)
- **Timeout:** 10 seconds
- **Auto-reconnect:** Enabled
- **Skip Negotiation:** true

---

## **Usage Examples**

### **REST API Call**
```bash
curl -X POST \
  'https://gateway-api-demo.s2f.projectx.com/api/Auth/loginKey' \
  -H 'Content-Type: application/json' \
  -d '{
    "userName": "your_username",
    "apiKey": "your_api_key"
  }'
```

### **WebSocket Connection**
```javascript
const userHubUrl = 'https://gateway-rtc-demo.s2f.projectx.com/hubs/user?access_token=YOUR_JWT_TOKEN';
const marketHubUrl = 'https://gateway-rtc-demo.s2f.projectx.com/hubs/market?access_token=YOUR_JWT_TOKEN';
```

---

## **Environment Notes**

### **Demo Environment**
- **Base URL:** `gateway-api-demo.s2f.projectx.com`
- **WebSocket:** `gateway-rtc-demo.s2f.projectx.com`
- **Purpose:** Development and testing

### **Production Environment**
- **Base URL:** `gateway-api.s2f.projectx.com` (expected)
- **WebSocket:** `gateway-rtc.s2f.projectx.com` (expected)
- **Purpose:** Live trading

---

**Source:** [ProjectX Gateway API - Connection URLs](https://gateway.docs.projectx.com/docs/getting-started/connection-urls)
