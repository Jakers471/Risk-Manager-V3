# Development Rules & Guidelines

## Critical Rules (Never Break)

### 1. File Size Enforcement
- **NEVER exceed 300 lines** in any file
- **Target 100-200 lines** for optimal AI assistance
- **Split immediately** if approaching limits
- **No exceptions** - this is the root cause of previous failures

### 2. Single Responsibility Principle
- **One clear purpose** per file
- **No mixed functionality** (e.g., don't mix monitoring + enforcement + UI)
- **Clear file names** that describe purpose
- **If unsure, split the file**

### 3. No Breaking Changes During "Improvements"
- **Never remove debugging logs** during refactoring
- **Never remove critical functionality** while "improving" structure
- **Test thoroughly** before committing changes
- **If it works, don't "fix" it**

### 4. AI Development Guidelines
- **Work on one module at a time**
- **Verify functionality** before moving to next module
- **Keep context focused** - don't try to understand entire system at once
- **Ask for clarification** if file approaches size limits
- **Keep responses concise** - no massive paragraphs, short and effective

## Module Development Order

### Phase 1: Foundation (Start Here)
1. Configuration management
2. Centralized logging
3. Authentication handling
4. API client wrapper

### Phase 2: Data Models
1. Account data structures
2. Position & order models
3. Risk rule models

### Phase 3: Core Engine
1. Position tracking
2. Rule checking
3. Position flattening
4. Trading hours management

### Phase 4: Real-time
1. Connection management
2. Message processing
3. Data storage

### Phase 5: CLI Interface
1. Menu router
2. Configuration wizard
3. Testing tools

## Testing Requirements

### Before Moving to Next Module
- **Test current module** independently
- **Verify all functions** work as expected
- **Check logging** is working properly
- **No broken imports** or dependencies

### Debugging Strategy
- **Keep all debug logs** in place
- **Use print() statements** for quick debugging
- **Add try/except** blocks for error handling
- **Test with mock data** when possible

## Common Pitfalls to Avoid

### 1. Monolithic Files
- **Don't create large files** even if it seems "more organized"
- **Split by responsibility** not by convenience
- **If file grows >200 lines**, split it immediately

### 2. Mixed Responsibilities
- **Don't mix UI with business logic**
- **Don't mix monitoring with enforcement**
- **Don't mix data models with processing**

### 3. Over-Engineering
- **Start simple** and add complexity only when needed
- **Don't add features** that aren't immediately required
- **Focus on core functionality** first

### 4. Breaking Working Code
- **If it works, don't change it**
- **Add new functionality** in new modules
- **Test thoroughly** before replacing existing code

## Success Checklist

### For Each Module
- [ ] File size < 300 lines
- [ ] Single clear responsibility
- [ ] All functions documented
- [ ] Type hints added
- [ ] Error handling included
- [ ] Debug logs in place
- [ ] Tested independently
- [ ] No circular dependencies

### For Integration
- [ ] All modules work together
- [ ] No broken imports
- [ ] Logging works end-to-end
- [ ] Error handling works
- [ ] Core functionality verified

## Emergency Procedures

### If File Gets Too Large
1. **Stop immediately**
2. **Identify responsibilities**
3. **Split into multiple files**
4. **Test each new file**
5. **Update imports**

### If Functionality Breaks
1. **Revert to last working state**
2. **Identify what changed**
3. **Fix in isolation**
4. **Test thoroughly**
5. **Document the issue**

### If AI Gets Confused
1. **Focus on one file at a time**
2. **Provide specific context**
3. **Ask for clarification**
4. **Don't make assumptions**
