"""
Monitor Status

Handles monitoring status and violation history tracking.
"""

from risk_manager_v2.core.logger import get_logger

class MonitorStatus:
    """Monitoring status and history management."""
    
    def __init__(self, core):
        self.logger = get_logger(__name__)
        self.core = core
    
    def get_status(self):
        """Get current monitoring status."""
        if not self.core.monitored_accounts:
            return {'status': 'stopped'}
        
        status = {
            'status': 'running',
            'monitored_accounts': len(self.core.monitored_accounts),
            'accounts': {}
        }
        
        for account_id, data in self.core.monitored_accounts.items():
            status['accounts'][account_id] = {
                'last_check': data['last_check'].isoformat() if data['last_check'] else None,
                'daily_pnl': data['daily_pnl'],
                'daily_trades': data['daily_trades'],
                'current_violations': data.get('current_violations', []),
                'total_violations': len(data['violations'])
            }
        
        return status
    
    def get_violation_history(self, account_id=None):
        """Get violation history for account(s)."""
        if account_id:
            return self.core.monitored_accounts.get(account_id, {}).get('violations', [])
        
        all_violations = []
        for account_data in self.core.monitored_accounts.values():
            all_violations.extend(account_data.get('violations', []))
        
        return sorted(all_violations, key=lambda x: x['timestamp'], reverse=True)
    
    def get_account_summary(self, account_id):
        """Get detailed summary for specific account."""
        if account_id not in self.core.monitored_accounts:
            return None
        
        data = self.core.monitored_accounts[account_id]
        
        return {
            'account_id': account_id,
            'last_check': data['last_check'],
            'daily_pnl': data['daily_pnl'],
            'daily_trades': data['daily_trades'],
            'current_violations': data.get('current_violations', []),
            'violation_count': len(data['violations']),
            'recent_violations': data['violations'][-5:]  # Last 5 violations
        }
    
    def get_last_check_time(self):
        """Get timestamp of last monitoring check."""
        if not self.core.monitored_accounts:
            return None
        
        latest_check = None
        for data in self.core.monitored_accounts.values():
            if data['last_check']:
                if latest_check is None or data['last_check'] > latest_check:
                    latest_check = data['last_check']
        
        return latest_check
    
    def get_stats(self):
        """Get monitoring statistics."""
        if not self.core.monitored_accounts:
            return {
                'total_accounts': 0,
                'total_violations': 0,
                'accounts_with_violations': 0,
                'average_daily_pnl': 0.0,
                'total_daily_trades': 0
            }
        
        total_violations = 0
        accounts_with_violations = 0
        total_daily_pnl = 0.0
        total_daily_trades = 0
        
        for data in self.core.monitored_accounts.values():
            violations = len(data['violations'])
            total_violations += violations
            if violations > 0:
                accounts_with_violations += 1
            
            total_daily_pnl += data['daily_pnl']
            total_daily_trades += data['daily_trades']
        
        account_count = len(self.core.monitored_accounts)
        
        return {
            'total_accounts': account_count,
            'total_violations': total_violations,
            'accounts_with_violations': accounts_with_violations,
            'average_daily_pnl': total_daily_pnl / account_count if account_count > 0 else 0.0,
            'total_daily_trades': total_daily_trades
        }

if __name__ == "__main__":
    print("Testing MonitorStatus...")
    
    # Test basic initialization
    from engine.monitor_core import MonitorCore
    core = MonitorCore()
    status = MonitorStatus(core)
    print("âœ… MonitorStatus created successfully!")
    
    # Test status methods
    current_status = status.get_status()
    print(f"âœ… Current status: {current_status}")
    
    # Test stats
    stats = status.get_stats()
    print(f"âœ… Monitoring stats: {stats}")
    
    print("âœ… MonitorStatus test completed!")


