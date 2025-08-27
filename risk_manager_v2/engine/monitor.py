"""
Risk Monitor Router

Main coordinator for the auto-enforcement system.
"""

import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
from risk_manager_v2.core.logger import get_logger

class RiskMonitor:
    """Main risk monitoring coordinator."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Monitoring state
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        self.is_running = False
        
        # Counters
        self.total_evaluations = 0
        self.total_actions = 0
        self.violations_current = {}  # per account
        
        # Components (stubs for now)
        self.client = None
        self.rate_limiter = None
        self.dry_run = True
        
        # Monitored accounts (stub)
        self.monitored_accounts = []
    
    def start_monitoring(self, client, rate_limiter=None, dry_run=True) -> bool:
        """Start monitoring with background thread."""
        if self.is_running:
            self.logger.warning("Monitoring already running")
            return False
        
        self.client = client
        self.rate_limiter = rate_limiter
        self.dry_run = dry_run
        self.stop_event.clear()
        
        # Get monitored accounts (stub)
        self.monitored_accounts = self._get_monitored_accounts()
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        self.is_running = True
        
        self.logger.info(f"Started monitoring {len(self.monitored_accounts)} accounts (dry_run={dry_run})")
        return True
    
    def stop_monitoring(self) -> bool:
        """Stop monitoring cleanly."""
        if not self.is_running:
            return True
        
        self.logger.info("Stopping monitoring...")
        self.stop_event.set()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
        
        self.is_running = False
        self.logger.info("Monitoring stopped")
        return True
    
    def _monitoring_loop(self):
        """Main monitoring loop with pacing."""
        while not self.stop_event.is_set():
            try:
                # Check each monitored account
                for account_id in self.monitored_accounts:
                    if self.stop_event.is_set():
                        break
                    
                    self._evaluate_account(account_id)
                
                # Wait for next cycle (0.5-1.0 seconds)
                if not self.stop_event.wait(0.75):
                    continue
                    
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                if not self.stop_event.wait(1.0):
                    continue
    
    def _evaluate_account(self, account_id: str):
        """Evaluate a single account for risk violations."""
        try:
            # Get account data (stub - no API calls when stopped)
            if self.stop_event.is_set():
                return
            
            # Get positions and orders
            positions = self.client.get_open_positions(account_id)
            orders = self.client.get_orders(account_id)
            
            # Build minimal EvaluationContext
            evaluation_context = self._build_evaluation_context(account_id, positions, orders)
            
            # Call RiskEngine.evaluate (stub)
            action_plan = self._evaluate_risk_engine(evaluation_context)
            
            # Update counters
            self.total_evaluations += 1
            
            # Apply enforcement if needed
            if action_plan and action_plan.get('actions'):
                self._apply_enforcement(account_id, action_plan)
            
        except Exception as e:
            self.logger.error(f"Error evaluating account {account_id}: {e}")
    
    def _build_evaluation_context(self, account_id: str, positions: List[Dict], orders: List[Dict]) -> Dict:
        """Build minimal evaluation context."""
        return {
            'account_id': account_id,
            'positions': positions,
            'orders': orders,
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run
        }
    
    def _evaluate_risk_engine(self, context: Dict) -> Optional[Dict]:
        """Evaluate risk engine (stub)."""
        # Stub implementation - return empty action plan
        return {
            'account_id': context['account_id'],
            'actions': [],
            'violations': []
        }
    
    def _apply_enforcement(self, account_id: str, action_plan: Dict):
        """Apply enforcement actions."""
        try:
            # Stub enforcement - just count actions
            actions = action_plan.get('actions', [])
            violations = action_plan.get('violations', [])
            
            if actions and not self.dry_run:
                # Would call Enforcer.apply(account_id, action_plan)
                self.total_actions += len(actions)
                self.logger.info(f"Applied {len(actions)} actions for account {account_id}")
            
            # Update violation counters
            if violations:
                self.violations_current[account_id] = len(violations)
            else:
                self.violations_current[account_id] = 0
                
        except Exception as e:
            self.logger.error(f"Error applying enforcement for {account_id}: {e}")
    
    def _get_monitored_accounts(self) -> List[str]:
        """Get list of monitored accounts (stub)."""
        # Stub - would get from config or API
        return ['test_account_1', 'test_account_2']
    
    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status."""
        return {
            'status': 'running' if self.is_running else 'stopped',
            'monitored_accounts': self.monitored_accounts.copy(),
            'metrics': {
                'total_evaluations': self.total_evaluations,
                'total_actions': self.total_actions,
                'violations_current': self.violations_current.copy()
            },
            'dry_run': self.dry_run,
            'last_update': datetime.now().isoformat()
        }
    
    def is_running(self) -> bool:
        """Check if monitoring is active."""
        return self.is_running

if __name__ == "__main__":
    print("Testing RiskMonitor router...")
    
    # Test basic initialization
    monitor = RiskMonitor()
    print("✅ RiskMonitor created successfully!")
    
    # Test status methods
    status = monitor.get_monitoring_status()
    print(f"✅ Monitoring status: {status['status']}")
    
    # Test account management
    accounts = monitor.monitored_accounts
    print(f"✅ Monitored accounts: {accounts}")
    
    print("✅ RiskMonitor router test completed!")


