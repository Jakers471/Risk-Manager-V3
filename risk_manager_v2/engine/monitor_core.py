"""
Monitor Core Logic

Core monitoring functionality and state management.
"""

from risk_manager_v2.core.config import ConfigStore
from risk_manager_v2.core.auth import AuthManager
from risk_manager_v2.core.client import ProjectXClient
from risk_manager_v2.core.logger import get_logger
from risk_manager_v2.models.rules import RiskRules
from engine.calculator import RiskCalculator
from engine.enforcer import RiskEnforcer

class MonitorCore:
    """Core monitoring logic and state management."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = ConfigStore()
        self.auth = AuthManager(self.config)
        self.client = ProjectXClient(self.config, self.auth)
        
        # Core components
        self.calculator = RiskCalculator()
        self.enforcer = RiskEnforcer(self.client)
        
        # Monitoring state
        self.monitored_accounts = {}
        self.risk_rules = None
        
        self.load_risk_rules()
    
    def load_risk_rules(self):
        """Load risk rules from configuration."""
        try:
            self.risk_rules = RiskRules()
            self.logger.info("Risk rules loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load risk rules: {e}")
            self.risk_rules = None
    
    def initialize_accounts(self, account_ids):
        """Initialize monitoring state for accounts."""
        for account_id in account_ids:
            self.monitored_accounts[account_id] = {
                'last_check': None,
                'daily_pnl': 0.0,
                'daily_trades': 0,
                'violations': []
            }
        
        self.logger.info(f"Initialized monitoring for {len(account_ids)} accounts")
    
    def check_account(self, account_id):
        """Check a single account for risk violations."""
        try:
            # Get current account data
            account_data = self.client.get_account(account_id)
            if not account_data:
                return
            
            # Get current positions and trades
            positions = self.client.get_positions(account_id)
            trades = self._get_todays_trades(account_id)
            
            # Calculate risk metrics
            risk_metrics = self.calculator.calculate_risk_metrics(
                account_data, positions, trades, self.risk_rules
            )
            
            # Check for violations
            violations = self.calculator.check_violations(risk_metrics, self.risk_rules)
            
            # Update state
            self._update_account_state(account_id, risk_metrics, violations)
            
            # Handle violations
            if violations:
                self._handle_violations(account_id, violations, risk_metrics)
            
        except Exception as e:
            self.logger.error(f"Error checking account {account_id}: {e}")
    
    def _get_todays_trades(self, account_id):
        """Get today's trades for account."""
        from datetime import datetime
        today = datetime.now().date()
        return self.client.get_trades(account_id, start_date=today)
    
    def _update_account_state(self, account_id, metrics, violations):
        """Update account monitoring state."""
        from datetime import datetime
        
        self.monitored_accounts[account_id].update({
            'last_check': datetime.now(),
            'daily_pnl': metrics.get('daily_pnl', 0.0),
            'daily_trades': metrics.get('daily_trades', 0),
            'current_violations': violations
        })
    
    def _handle_violations(self, account_id, violations, metrics):
        """Handle detected risk violations."""
        self.logger.warning(f"Risk violations detected for account {account_id}: {violations}")
        
        # Log violations
        from datetime import datetime
        for violation in violations:
            self.monitored_accounts[account_id]['violations'].append({
                'timestamp': datetime.now(),
                'violation': violation,
                'metrics': metrics
            })
        
        # Execute enforcement
        for violation in violations:
            action_taken = self.enforcer.execute_action(account_id, violation, metrics)
            
            if action_taken:
                self.logger.info(f"Enforcement action executed: {action_taken}")
            else:
                self.logger.error(f"Failed to execute enforcement for {violation}")
    
    def is_ready(self):
        """Check if monitoring system is ready."""
        return (self.auth.is_authenticated() and 
                self.risk_rules is not None)
    
    def get_account_status(self, account_id):
        """Get current status for an account."""
        return self.monitored_accounts.get(account_id, {})
    
    def get_all_accounts_status(self):
        """Get status for all monitored accounts."""
        return self.monitored_accounts.copy()
    
    def clear_violations(self, account_id=None):
        """Clear violation history for account(s)."""
        if account_id:
            if account_id in self.monitored_accounts:
                self.monitored_accounts[account_id]['violations'] = []
        else:
            for account_data in self.monitored_accounts.values():
                account_data['violations'] = []

if __name__ == "__main__":
    print("Testing MonitorCore...")
    
    # Test basic initialization
    core = MonitorCore()
    print("âœ… MonitorCore created successfully!")
    
    # Test readiness
    ready = core.is_ready()
    print(f"âœ… System ready: {ready}")
    
    # Test account initialization
    core.initialize_accounts(['test_account_1', 'test_account_2'])
    print(f"âœ… Accounts initialized: {len(core.monitored_accounts)}")
    
    print("âœ… MonitorCore test completed!")

