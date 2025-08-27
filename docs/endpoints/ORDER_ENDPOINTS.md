# Order Endpoints

## Overview
Order management endpoints for placing, searching, and modifying orders. All detailed endpoint information is organized in focused documentation files.

## Order Endpoint Categories

### **[Place Order](orders/PLACE_ORDER.md)**
- Create new market orders

### **[Search Orders](orders/SEARCH_ORDERS.md)**
- Search orders with timestamp filtering

### **[Search Open Orders](orders/SEARCH_OPEN_ORDERS.md)**
- Find currently open orders

### **[Cancel Order](orders/CANCEL_ORDER.md)**
- Cancel existing orders

### **[Modify Order](orders/MODIFY_ORDER.md)**
- Modify order parameters (price, size, etc.)

## Quick Reference

### Base URL
`https://gateway-api-demo.s2f.projectx.com`

### Common Response Format
```json
{
    "success": true,
    "errorCode": 0,
    "errorMessage": null
}
```

---
*See individual endpoint files for detailed information.*
