# Risk Manager V3 - Modular Architecture

## Project Overview
Automated trading risk management system that enforces rules and flattens positions in real-time via TopStepX integration.

## Core Principles

### File Size Limits
- **Maximum**: 300 lines per file
- **Target**: 100-200 lines for optimal AI assistance
- **Action**: Split immediately if approaching limits

### Single Responsibility
- One clear purpose per file
- No mixed functionality
- Clear file names that describe purpose

### Modular Design
- Explicit imports only
- No circular dependencies
- Clear interfaces between modules
- Test each module independently

## Data Flow
```
TopStepX WebSocket → Real-time Data → Risk Engine → Enforcement Actions → TopStepX API
```

## Success Metrics
1. **Functionality**: Trade detection, rule enforcement, real-time monitoring
2. **Maintainability**: Easy to add features, debug, and get AI assistance
3. **Scalability**: New rules/features = new modules, no breaking changes
