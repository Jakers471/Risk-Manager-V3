# Adding Custom Rules

This guide explains how to add new custom rule types to the Risk Manager system.

## Overview

The Risk Manager uses a modular rule system where each rule type inherits from `BaseRule` and provides specific validation and enforcement logic.

## Step 1: Create New Rule File

Create a new file in the `models/` directory following this pattern:

```python
# models/rules_custom.py
from dataclasses import dataclass
from typing import Dict, Any
from .rules_base import BaseRule, RuleValidator

@dataclass
class CustomRule(BaseRule):
    """Your custom rule type."""
    custom_setting1: float = 100.0
    custom_setting2: str = "default"
    
    def __post_init__(self):
        """Initialize after dataclass creation."""
        super().__init__(enabled=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "enabled": self.enabled,
            "custom_setting1": self.custom_setting1,
            "custom_setting2": self.custom_setting2
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomRule':
        """Create from dictionary."""
        rule = cls(
            custom_setting1=data.get("custom_setting1", 100.0),
            custom_setting2=data.get("custom_setting2", "default")
        )
        rule.enabled = data.get("enabled", True)
        return rule
    
    def validate(self) -> bool:
        """Validate custom rule data."""
        try:
            RuleValidator.validate_positive_float(self.custom_setting1, "Custom Setting 1")
            RuleValidator.validate_string(self.custom_setting2, "Custom Setting 2")
            return True
        except ValueError as e:
            raise ValueError(f"Custom Rule validation failed: {e}")
    
    def check_rule_condition(self, current_value: float) -> bool:
        """Check if rule condition is met."""
        if not self.enabled:
            return False
        # Add your custom logic here
        return current_value <= self.custom_setting1
```

## Step 2: Add to Router

Update the `models/rules.py` file to include your custom rule:

```python
# In models/rules.py
class RiskRules:
    def __init__(self):
        # ... existing rules ...
        self.custom_rule = None
        self._initialize_rule_modules()
    
    def _initialize_rule_modules(self):
        """Initialize rule modules with error handling."""
        # ... existing imports ...
        
        try:
            from .rules_custom import CustomRule
            self.custom_rule = CustomRule()
        except ImportError:
            # CustomRule module not created yet
            pass
    
    def to_dict(self):
        """Convert to dictionary for storage."""
        data = {}
        # ... existing rules ...
        
        if self.custom_rule:
            data["custom_rule"] = self.custom_rule.to_dict()
        
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        rules = cls()
        # ... existing rules ...
        
        if "custom_rule" in data and rules.custom_rule:
            rules.custom_rule = rules.custom_rule.__class__.from_dict(data["custom_rule"])
        
        return rules
    
    def get_rule_status(self):
        """Get status of all rule modules."""
        status = {
            # ... existing rules ...
            "custom_rule": self.custom_rule is not None
        }
        return status
```

## Step 3: Add CLI Menu (Optional)

If you want a CLI interface for your custom rule, create a menu file:

```python
# cli/rules_custom.py
from .base_menu import BaseMenu

class RulesCustomMenu(BaseMenu):
    """Custom rule configuration menu."""
    
    def run(self):
        """Run the custom rules menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.view_rules()
            elif choice == "2":
                self.set_custom_setting1()
            elif choice == "3":
                self.set_custom_setting2()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display custom rules menu options."""
        print("\n=== CUSTOM RULES ===")
        print("1) View Current Rules")
        print("2) Set Custom Setting 1")
        print("3) Set Custom Setting 2")
        print("0) Back to rules menu")
    
    def view_rules(self):
        """View current custom rules."""
        print("\n=== CURRENT CUSTOM RULES ===")
        custom_setting1 = self.config.get('risk.custom_setting1', 100.0)
        custom_setting2 = self.config.get('risk.custom_setting2', 'default')
        
        print(f"Custom Setting 1: {custom_setting1}")
        print(f"Custom Setting 2: {custom_setting2}")
        
        input("\nPress Enter to continue...")
    
    def set_custom_setting1(self):
        """Set custom setting 1."""
        current = self.config.get('risk.custom_setting1', 100.0)
        print(f"\nCurrent Custom Setting 1: {current}")
        
        try:
            new_value = input("New Custom Setting 1: ").strip()
            if new_value:
                new_value = float(new_value)
                if new_value >= 0:
                    self.config.set('risk.custom_setting1', new_value)
                    print(f"✅ Custom Setting 1 set to {new_value}")
                else:
                    print("❌ Value must be positive.")
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")
        
        input("\nPress Enter to continue...")
    
    def set_custom_setting2(self):
        """Set custom setting 2."""
        current = self.config.get('risk.custom_setting2', 'default')
        print(f"\nCurrent Custom Setting 2: {current}")
        
        new_value = input("New Custom Setting 2: ").strip()
        if new_value:
            self.config.set('risk.custom_setting2', new_value)
            print(f"✅ Custom Setting 2 set to {new_value}")
        
        input("\nPress Enter to continue...")
```

## Step 4: Update Rules Router

Add your custom menu to the main rules router:

```python
# In cli/rules.py
class RulesMenu(BaseMenu):
    def __init__(self):
        super().__init__()
        # ... existing rules ...
        self.custom_rules = None
        self._initialize_rule_modules()
    
    def _initialize_rule_modules(self):
        """Initialize rule modules with error handling."""
        # ... existing imports ...
        
        try:
            from .rules_custom import RulesCustomMenu
            self.custom_rules = RulesCustomMenu()
        except ImportError:
            self.logger.warning("RulesCustomMenu not available - module not created yet")
    
    def display_menu(self):
        """Display rules menu options."""
        print("\n=== RISK RULES CONFIGURATION ===")
        # ... existing options ...
        print("5) Custom Rules")
        print("6) View All Rules")
        print("0) Back to main menu")
    
    def run(self):
        """Run the rules menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            # ... existing choices ...
            elif choice == "5":
                self._run_custom_rules()
            elif choice == "6":
                self.view_all_rules()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def _run_custom_rules(self):
        """Run custom rules menu with error handling."""
        if self.custom_rules:
            self.custom_rules.run()
        else:
            print("\n=== CUSTOM RULES ===")
            print("Custom rules configuration not implemented yet.")
            input("\nPress Enter to continue...")
```

## Step 5: Update Configuration

Add default values to the configuration:

```python
# In core/config.py
def create_default_config(self) -> None:
    """Create default configuration."""
    self.config = {
        # ... existing config ...
        "risk": {
            # ... existing risk settings ...
            "custom_setting1": 100.0,
            "custom_setting2": "default"
        }
    }
```

## Best Practices

1. **Inherit from BaseRule**: Always inherit from `BaseRule` for consistency
2. **Use dataclass**: Use `@dataclass` decorator for clean initialization
3. **Implement validation**: Always implement the `validate()` method
4. **Handle errors gracefully**: Use try-except blocks for missing modules
5. **Follow naming conventions**: Use descriptive names and consistent patterns
6. **Add documentation**: Include docstrings for all methods
7. **Test thoroughly**: Create comprehensive test cases

## Example Custom Rule Types

- **Correlation Rules**: Limit exposure to correlated assets
- **Volatility Rules**: Adjust position sizes based on market volatility
- **News Rules**: Pause trading during major news events
- **Sector Rules**: Limit exposure to specific market sectors
- **Currency Rules**: Manage currency risk exposure

## Integration with Enforcement Engine

Your custom rule will automatically be integrated with the enforcement engine once added to the `RiskRules` router. The engine will call your rule's validation and condition checking methods during real-time monitoring.
