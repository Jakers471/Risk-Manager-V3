# TopStepX API Reference

## Overview
Reference documentation for TopStepX API integration. All detailed information is organized in focused documentation files.

## Documentation Index

### Core API Documentation
- **[Authentication](docs/API_AUTHENTICATION.md)** - JWT authentication and token management
- **[REST Endpoints](docs/API_ENDPOINTS.md)** - Account, position, order, and trade endpoints
- **[WebSocket Connection](docs/WEBSOCKET_CONNECTION.md)** - Real-time data streaming
- **[Data Structures](docs/DATA_STRUCTURES.md)** - Position, order, and trade models
- **[Error Handling](docs/API_ERROR_HANDLING.md)** - Error codes and response patterns

### Additional Resources
- **[Rate Limits](docs/API_RATE_LIMITS.md)** - API rate limiting and handling strategies
- **[Connection URLs](docs/CONNECTION_URLS.md)** - Environment-specific endpoints

## Quick Reference

### Authentication
```bash
POST /api/Auth/loginKey
Content-Type: application/json
{
    "userName": "string",
    "apiKey": "string"
}
```

### Base URL
`https://gateway-api-demo.s2f.projectx.com`

---
*See individual documentation files for detailed information.*
