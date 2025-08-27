"""
Risk Monitor Router

Main coordinator for the auto-enforcement system.
"""

from engine.monitor_core import MonitorCore
from engine.monitor_loop import MonitorLoop
from engine.monitor_status import MonitorStatus

class RiskMonitor:
    """Main risk monitoring coordinator."""
    
    def __init__(self):
        self.core = MonitorCore()
        self.loop = MonitorLoop(self.core)
        self.status = MonitorStatus(self.core)
    
    def start_monitoring(self, account_ids=None):
        """Start monitoring specified accounts."""
        return self.loop.start(account_ids)
    
    def stop_monitoring(self):
        """Stop monitoring all accounts."""
        return self.loop.stop()
    
    def get_monitoring_status(self):
        """Get current monitoring status."""
        return self.status.get_status()
    
    def get_violation_history(self, account_id=None):
        """Get violation history for account(s)."""
        if account_id:
            account_status = self.core.get_account_status(account_id)
            return account_status.get('violations', [])
        else:
            all_status = self.core.get_all_accounts_status()
            violations = []
            for account_data in all_status.values():
                violations.extend(account_data.get('violations', []))
            return violations
    
    def add_account(self, account_id):
        """Add account to monitoring."""
        if account_id not in self.core.monitored_accounts:
            self.core.initialize_accounts([account_id])
            return True
        return False
    
    def remove_account(self, account_id):
        """Remove account from monitoring."""
        if account_id in self.core.monitored_accounts:
            del self.core.monitored_accounts[account_id]
            return True
        return False
    
    def get_monitored_accounts(self):
        """Get list of currently monitored accounts."""
        return list(self.core.monitored_accounts.keys())
    
    def is_monitoring(self):
        """Check if monitoring is active."""
        return self.loop.is_running()
    
    def get_last_check_time(self):
        """Get timestamp of last monitoring check."""
        return self.status.get_last_check_time()
    
    def get_monitoring_stats(self):
        """Get monitoring statistics."""
        return self.status.get_stats()

if __name__ == "__main__":
    print("Testing RiskMonitor router...")
    
    # Test basic initialization
    monitor = RiskMonitor()
    print("✅ RiskMonitor created successfully!")
    
    # Test status methods
    status = monitor.get_monitoring_status()
    print(f"✅ Monitoring status: {status}")
    
    # Test account management
    accounts = monitor.get_monitored_accounts()
    print(f"✅ Monitored accounts: {accounts}")
    
    print("✅ RiskMonitor router test completed!")
