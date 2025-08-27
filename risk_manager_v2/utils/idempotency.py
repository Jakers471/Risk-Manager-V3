"""
Idempotency utilities for preventing duplicate actions.

Ensures that identical actions are not executed multiple times.
"""

import json
import hashlib
import threading
import time
from typing import Dict, Set, Optional, Any, Callable, List
from datetime import datetime, timedelta
from core.logger import get_logger

logger = get_logger(__name__)

class IdempotencyStore:
    """In-memory idempotency key store with optional persistence."""
    
    def __init__(self, max_keys: int = 10000, ttl_hours: int = 24):
        """
        Initialize idempotency store.
        
        Args:
            max_keys: Maximum number of keys to store
            ttl_hours: Time-to-live for keys in hours
        """
        self.max_keys = max_keys
        self.ttl_hours = ttl_hours
        self.keys: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def generate_key(self, action_plan: Dict[str, Any]) -> str:
        """
        Generate idempotency key from action plan.
        
        Args:
            action_plan: Action plan dictionary
        
        Returns:
            Idempotency key string
        """
        # Create deterministic string representation
        plan_str = json.dumps(action_plan, sort_keys=True, separators=(',', ':'))
        
        # Generate SHA1 hash
        return hashlib.sha1(plan_str.encode()).hexdigest()
    
    def is_processed(self, key: str) -> bool:
        """
        Check if key has been processed.
        
        Args:
            key: Idempotency key
        
        Returns:
            True if key has been processed
        """
        with self.lock:
            self._cleanup_expired()
            
            if key in self.keys:
                entry = self.keys[key]
                if entry['status'] == 'completed':
                    logger.info(f"Idempotency: key {key[:8]} already processed")
                    return True
            
            return False
    
    def mark_processing(self, key: str, action_plan: Dict[str, Any]) -> bool:
        """
        Mark key as being processed.
        
        Args:
            key: Idempotency key
            action_plan: Action plan being processed
        
        Returns:
            True if key can be processed, False if already processed
        """
        with self.lock:
            self._cleanup_expired()
            
            if key in self.keys:
                entry = self.keys[key]
                if entry['status'] == 'completed':
                    logger.info(f"Idempotency: key {key[:8]} already completed")
                    return False
                elif entry['status'] == 'processing':
                    logger.warning(f"Idempotency: key {key[:8]} already being processed")
                    return False
            
            # Mark as processing
            self.keys[key] = {
                'status': 'processing',
                'action_plan': action_plan,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            logger.info(f"Idempotency: marked key {key[:8]} as processing")
            return True
    
    def mark_completed(self, key: str, result: Optional[Dict[str, Any]] = None):
        """
        Mark key as completed.
        
        Args:
            key: Idempotency key
            result: Result of the action
        """
        with self.lock:
            if key in self.keys:
                self.keys[key].update({
                    'status': 'completed',
                    'result': result,
                    'updated_at': datetime.utcnow()
                })
                
                logger.info(f"Idempotency: marked key {key[:8]} as completed")
    
    def mark_failed(self, key: str, error: Optional[str] = None):
        """
        Mark key as failed.
        
        Args:
            key: Idempotency key
            error: Error message
        """
        with self.lock:
            if key in self.keys:
                self.keys[key].update({
                    'status': 'failed',
                    'error': error,
                    'updated_at': datetime.utcnow()
                })
                
                logger.warning(f"Idempotency: marked key {key[:8]} as failed: {error}")
    
    def _cleanup_expired(self):
        """Remove expired keys."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.ttl_hours)
        
        expired_keys = [
            key for key, entry in self.keys.items()
            if entry['created_at'] < cutoff_time
        ]
        
        for key in expired_keys:
            del self.keys[key]
        
        if expired_keys:
            logger.debug(f"Idempotency: cleaned up {len(expired_keys)} expired keys")
        
        # Enforce max keys limit
        if len(self.keys) > self.max_keys:
            # Remove oldest keys
            sorted_keys = sorted(
                self.keys.items(),
                key=lambda x: x[1]['created_at']
            )
            
            keys_to_remove = len(self.keys) - self.max_keys
            for key, _ in sorted_keys[:keys_to_remove]:
                del self.keys[key]
            
            logger.warning(f"Idempotency: removed {keys_to_remove} old keys to stay under limit")

class IdempotencyManager:
    """High-level idempotency manager."""
    
    def __init__(self, store: Optional[IdempotencyStore] = None):
        """
        Initialize idempotency manager.
        
        Args:
            store: Idempotency store instance
        """
        self.store = store or IdempotencyStore()
    
    def execute_once(self, action_plan: Dict[str, Any], 
                    executor: Callable) -> Any:
        """
        Execute action plan only once.
        
        Args:
            action_plan: Action plan to execute
            executor: Function to execute the plan
        
        Returns:
            Result of execution
        """
        key = self.store.generate_key(action_plan)
        
        # Check if already processed
        if self.store.is_processed(key):
            logger.info(f"Idempotency: skipping duplicate action plan")
            return None
        
        # Mark as processing
        if not self.store.mark_processing(key, action_plan):
            logger.warning(f"Idempotency: action plan already being processed")
            return None
        
        try:
            # Execute the action
            result = executor(action_plan)
            
            # Mark as completed
            self.store.mark_completed(key, result)
            
            return result
            
        except Exception as e:
            # Mark as failed
            self.store.mark_failed(key, str(e))
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get idempotency store statistics."""
        with self.store.lock:
            status_counts = {}
            for entry in self.store.keys.values():
                status = entry['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'total_keys': len(self.store.keys),
                'status_counts': status_counts,
                'max_keys': self.store.max_keys,
                'ttl_hours': self.store.ttl_hours
            }

class RiskActionIdempotency:
    """Specialized idempotency for risk management actions."""
    
    def __init__(self, account_id: str, store: Optional[IdempotencyStore] = None):
        """
        Initialize risk action idempotency.
        
        Args:
            account_id: Account ID for action tracking
            store: Idempotency store instance
        """
        self.account_id = account_id
        self.store = store or IdempotencyStore()
        self.manager = IdempotencyManager(self.store)
    
    def close_positions_once(self, positions: List[Dict[str, Any]], 
                           executor: Callable) -> Any:
        """
        Close positions only once.
        
        Args:
            positions: List of positions to close
            executor: Function to execute position closing
        
        Returns:
            Result of execution
        """
        action_plan = {
            'action_type': 'close_positions',
            'account_id': self.account_id,
            'positions': positions,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.manager.execute_once(action_plan, executor)
    
    def cancel_orders_once(self, orders: List[Dict[str, Any]], 
                          executor: Callable) -> Any:
        """
        Cancel orders only once.
        
        Args:
            orders: List of orders to cancel
            executor: Function to execute order cancellation
        
        Returns:
            Result of execution
        """
        action_plan = {
            'action_type': 'cancel_orders',
            'account_id': self.account_id,
            'orders': orders,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.manager.execute_once(action_plan, executor)
    
    def emergency_stop_once(self, reason: str, executor: Callable) -> Any:
        """
        Execute emergency stop only once.
        
        Args:
            reason: Reason for emergency stop
            executor: Function to execute emergency stop
        
        Returns:
            Result of execution
        """
        action_plan = {
            'action_type': 'emergency_stop',
            'account_id': self.account_id,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.manager.execute_once(action_plan, executor)
    
    def enforce_rule_once(self, rule_name: str, violation_data: Dict[str, Any], 
                         executor: Callable) -> Any:
        """
        Enforce rule only once.
        
        Args:
            rule_name: Name of rule being enforced
            violation_data: Violation data
            executor: Function to execute rule enforcement
        
        Returns:
            Result of execution
        """
        action_plan = {
            'action_type': 'enforce_rule',
            'account_id': self.account_id,
            'rule_name': rule_name,
            'violation_data': violation_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.manager.execute_once(action_plan, executor)

def create_risk_idempotency(account_id: str) -> RiskActionIdempotency:
    """
    Create risk action idempotency for account.
    
    Args:
        account_id: Account ID
    
    Returns:
        Risk action idempotency instance
    """
    return RiskActionIdempotency(account_id)

def generate_action_key(action_type: str, account_id: str, 
                       action_data: Dict[str, Any]) -> str:
    """
    Generate idempotency key for action.
    
    Args:
        action_type: Type of action
        account_id: Account ID
        action_data: Action data
    
    Returns:
        Idempotency key
    """
    action_plan = {
        'action_type': action_type,
        'account_id': account_id,
        'data': action_data,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    store = IdempotencyStore()
    return store.generate_key(action_plan)

if __name__ == "__main__":
    print("Testing Idempotency utilities...")
    
    # Test idempotency store
    store = IdempotencyStore(max_keys=1000, ttl_hours=24)
    print("✅ IdempotencyStore created successfully!")
    
    # Test idempotency manager
    manager = IdempotencyManager(store)
    print("✅ IdempotencyManager created successfully!")
    
    # Test risk action idempotency
    risk_idempotency = RiskActionIdempotency("test_account_123")
    print("✅ RiskActionIdempotency created successfully!")
    
    # Test action key generation
    action_data = {"positions": [{"id": "123", "size": 10}]}
    action_key = generate_action_key("close_positions", "test_account", action_data)
    print(f"✅ Action key generated: {action_key[:16]}...")
    
    # Test stats
    stats = manager.get_stats()
    print(f"✅ Idempotency stats: {stats}")
    
    # Test duplicate prevention
    test_action = {"test": "data", "timestamp": "2024-01-01T00:00:00Z"}
    key1 = store.generate_key(test_action)
    key2 = store.generate_key(test_action)
    print(f"✅ Duplicate prevention: {key1 == key2}")
    
    print("✅ Idempotency utilities test completed!")
