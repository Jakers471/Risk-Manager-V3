"""
Monitor Loop

Handles the continuous monitoring loop and thread management.
"""

import time
import threading
from core.logger import get_logger

class MonitorLoop:
    """Continuous monitoring loop manager."""
    
    def __init__(self, core):
        self.logger = get_logger(__name__)
        self.core = core
        self.is_running = False
        self.monitoring_thread = None
    
    def start(self, account_ids=None):
        """Start the monitoring loop."""
        if not self.core.is_ready():
            self.logger.error("Cannot start monitoring - system not ready")
            return False
        
        # Get accounts to monitor
        if account_ids is None:
            accounts = self.core.client.get_accounts()
            account_ids = [acc['accountId'] for acc in accounts]
        
        if not account_ids:
            self.logger.error("No accounts to monitor")
            return False
        
        # Initialize accounts
        self.core.initialize_accounts(account_ids)
        
        # Start monitoring thread
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.logger.info(f"Started monitoring loop for {len(account_ids)} accounts")
        return True
    
    def stop(self):
        """Stop the monitoring loop."""
        self.logger.info("Stopping monitoring loop")
        self.is_running = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.core.monitored_accounts.clear()
        self.logger.info("Monitoring loop stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop - runs continuously."""
        self.logger.info("Monitoring loop started")
        
        while self.is_running:
            try:
                # Check each monitored account
                for account_id in list(self.core.monitored_accounts.keys()):
                    self.core.check_account(account_id)
                
                # Wait before next check
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
        
        self.logger.info("Monitoring loop ended")
    
    def is_running(self):
        """Check if monitoring loop is running."""
        return self.is_running and self.monitoring_thread and self.monitoring_thread.is_alive()
    
    def get_loop_status(self):
        """Get current loop status."""
        return {
            'is_running': self.is_running,
            'thread_alive': self.monitoring_thread.is_alive() if self.monitoring_thread else False,
            'accounts_monitored': len(self.core.monitored_accounts)
        }

if __name__ == "__main__":
    print("Testing MonitorLoop...")
    
    # Test basic initialization
    from engine.monitor_core import MonitorCore
    core = MonitorCore()
    loop = MonitorLoop(core)
    print("✅ MonitorLoop created successfully!")
    
    # Test status
    status = loop.get_loop_status()
    print(f"✅ Loop status: {status}")
    
    print("✅ MonitorLoop test completed!")
