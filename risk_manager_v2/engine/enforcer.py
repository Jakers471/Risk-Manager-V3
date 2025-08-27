"""
Risk Enforcer

Executes automated enforcement actions when risk violations are detected.
"""

from typing import Dict, Optional, List
from risk_manager_v2.core.logger import get_logger

class RiskEnforcer:
    """Executes automated risk enforcement actions."""
    
    def __init__(self, client):
        self.logger = get_logger(__name__)
        self.client = client
    
    def execute_action(self, account_id: str, violation: Dict, metrics: Dict) -> Optional[str]:
        """Execute appropriate enforcement action for violation."""
        try:
            violation_type = violation.get('type', '')
            self.logger.warning(f"Executing enforcement action for {violation_type} on account {account_id}")
            
            if violation_type == 'DAILY_LOSS_LIMIT':
                return self._handle_daily_loss_violation(account_id, metrics)
            
            elif violation_type == 'DAILY_PROFIT_TARGET':
                return self._handle_profit_target_reached(account_id, metrics)
            
            elif violation_type == 'DAILY_TRADE_LIMIT':
                return self._handle_trade_limit_violation(account_id, metrics)
            
            elif violation_type == 'POSITION_SIZE_LIMIT':
                return self._handle_position_size_violation(account_id, metrics)
            
            elif violation_type == 'MAX_POSITIONS_EXCEEDED':
                return self._handle_max_positions_violation(account_id, metrics)
            
            elif violation_type == 'OUTSIDE_TRADING_HOURS':
                return self._handle_trading_hours_violation(account_id, metrics)
            
            elif violation_type == 'HIGH_MARGIN_UTILIZATION':
                return self._handle_margin_violation(account_id, metrics)
            
            else:
                self.logger.warning(f"Unknown violation type: {violation_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error executing enforcement action: {e}")
            return None
    
    def emergency_stop(self, account_id: str) -> str:
        """Emergency stop - close all positions and cancel all orders."""
        try:
            self.logger.critical(f"EMERGENCY STOP initiated for account {account_id}")
            
            # Close all positions
            positions_result = self._close_all_positions(account_id)
            
            # Cancel all orders
            orders_result = self._cancel_all_orders(account_id)
            
            return f"Emergency stop completed - {positions_result}, {orders_result}"
            
        except Exception as e:
            self.logger.error(f"Error during emergency stop: {e}")
            return f"Emergency stop failed: {e}"
    
    def _handle_daily_loss_violation(self, account_id: str, metrics: Dict) -> str:
        """Handle daily loss limit violation - close all positions and cancel orders."""
        try:
            # Close all positions using TopStepX API
            positions_result = self._close_all_positions(account_id)
            
            # Cancel all pending orders
            orders_result = self._cancel_all_orders(account_id)
            
            return f"Daily loss limit exceeded - {positions_result}, {orders_result}"
            
        except Exception as e:
            self.logger.error(f"Error handling daily loss violation: {e}")
            return f"Failed to handle daily loss violation: {e}"
    
    def _handle_profit_target_reached(self, account_id: str, metrics: Dict) -> str:
        """Handle daily profit target reached - close all positions."""
        try:
            # Close all positions to lock in profits
            positions_result = self._close_all_positions(account_id)
            
            return f"Profit target reached - {positions_result}"
            
        except Exception as e:
            self.logger.error(f"Error handling profit target: {e}")
            return f"Failed to handle profit target: {e}"
    
    def _handle_trade_limit_violation(self, account_id: str, metrics: Dict) -> str:
        """Handle daily trade limit violation - cancel pending orders."""
        try:
            # Cancel all pending orders to prevent more trades
            orders_result = self._cancel_all_orders(account_id)
            
            return f"Daily trade limit reached - {orders_result}"
            
        except Exception as e:
            self.logger.error(f"Error handling trade limit violation: {e}")
            return f"Failed to handle trade limit violation: {e}"
    
    def _handle_position_size_violation(self, account_id: str, metrics: Dict) -> str:
        """Handle position size limit violation - close oversized positions."""
        try:
            # Get current positions
            positions = self.client.get_positions(account_id)
            if not positions:
                return "Position size violation - no positions to close"
            
            max_size = metrics.get('max_position_size_limit', 0)
            closed_count = 0
            
            for position in positions:
                # TopStepX API position structure: accountId, contractId, size, avgPrice
                size = abs(float(position.get('size', 0)))
                contract_id = position.get('contractId')
                
                if size > max_size and contract_id:
                    # Close the oversized position
                    result = self.client.close_position(account_id, contract_id)
                    if result and result.get('success'):
                        closed_count += 1
                        self.logger.info(f"Closed oversized position {contract_id} (size: {size})")
            
            return f"Position size violation - closed {closed_count} oversized positions"
            
        except Exception as e:
            self.logger.error(f"Error handling position size violation: {e}")
            return f"Failed to handle position size violation: {e}"
    
    def _handle_max_positions_violation(self, account_id: str, metrics: Dict) -> str:
        """Handle maximum positions violation - close oldest positions."""
        try:
            # Get current positions
            positions = self.client.get_positions(account_id)
            if not positions:
                return "Max positions violation - no positions to close"
            
            max_positions = metrics.get('max_open_positions', 0)
            
            if len(positions) > max_positions:
                # Sort by creation time (oldest first) - using contractId as proxy
                # In real implementation, you'd have creation timestamps
                positions.sort(key=lambda x: x.get('contractId', ''))
                
                # Close excess positions
                excess_count = len(positions) - max_positions
                closed_count = 0
                
                for i in range(excess_count):
                    position = positions[i]
                    contract_id = position.get('contractId')
                    
                    if contract_id:
                        result = self.client.close_position(account_id, contract_id)
                        if result and result.get('success'):
                            closed_count += 1
                
                return f"Max positions violation - closed {closed_count} oldest positions"
            
            return "Max positions violation - no action needed"
            
        except Exception as e:
            self.logger.error(f"Error handling max positions violation: {e}")
            return f"Failed to handle max positions violation: {e}"
    
    def _handle_trading_hours_violation(self, account_id: str, metrics: Dict) -> str:
        """Handle trading hours violation - close positions and cancel orders."""
        try:
            # Close all positions and cancel orders
            positions_result = self._close_all_positions(account_id)
            orders_result = self._cancel_all_orders(account_id)
            
            return f"Outside trading hours - {positions_result}, {orders_result}"
            
        except Exception as e:
            self.logger.error(f"Error handling trading hours violation: {e}")
            return f"Failed to handle trading hours violation: {e}"
    
    def _handle_margin_violation(self, account_id: str, metrics: Dict) -> str:
        """Handle high margin utilization violation - close largest positions."""
        try:
            # Get current positions
            positions = self.client.get_positions(account_id)
            if not positions:
                return "Margin violation - no positions to close"
            
            # Sort by position value (largest first)
            for position in positions:
                size = abs(float(position.get('size', 0)))
                avg_price = float(position.get('avgPrice', 0))
                position['value'] = size * avg_price
            
            positions.sort(key=lambda x: x.get('value', 0), reverse=True)
            
            # Close largest position
            largest_position = positions[0]
            contract_id = largest_position.get('contractId')
            
            if contract_id:
                result = self.client.close_position(account_id, contract_id)
                if result and result.get('success'):
                    return f"Margin violation - closed largest position {contract_id}"
            
            return "Margin violation - failed to close largest position"
            
        except Exception as e:
            self.logger.error(f"Error handling margin violation: {e}")
            return f"Failed to handle margin violation: {e}"
    
    def _close_all_positions(self, account_id: str) -> str:
        """Close all positions for an account."""
        try:
            positions = self.client.get_positions(account_id)
            if not positions:
                return "No positions to close"
            
            closed_count = 0
            for position in positions:
                contract_id = position.get('contractId')
                if contract_id:
                    result = self.client.close_position(account_id, contract_id)
                    if result and result.get('success'):
                        closed_count += 1
            
            return f"Closed {closed_count}/{len(positions)} positions"
            
        except Exception as e:
            self.logger.error(f"Error closing all positions: {e}")
            return f"Failed to close positions: {e}"
    
    def _cancel_all_orders(self, account_id: str) -> str:
        """Cancel all pending orders for an account."""
        try:
            # Get open orders using TopStepX API
            orders = self.client.get_open_orders(account_id)
            if not orders:
                return "No orders to cancel"
            
            cancelled_count = 0
            for order in orders:
                # TopStepX API order structure: id, accountId, status, etc.
                order_id = order.get('id')
                status = order.get('status')
                
                # Cancel only pending orders (status 1 = Pending)
                if order_id and status == 1:
                    result = self.client.cancel_order(account_id, order_id)
                    if result and result.get('success'):
                        cancelled_count += 1
            
            return f"Cancelled {cancelled_count}/{len(orders)} orders"
            
        except Exception as e:
            self.logger.error(f"Error cancelling all orders: {e}")
            return f"Failed to cancel orders: {e}"
    
    def get_enforcement_summary(self, account_id: str) -> Dict:
        """Get enforcement action summary for an account."""
        try:
            # Get current positions and orders
            positions = self.client.get_positions(account_id) or []
            orders = self.client.get_open_orders(account_id) or []
            
            return {
                'account_id': account_id,
                'open_positions': len(positions),
                'pending_orders': len([o for o in orders if o.get('status') == 1]),
                'total_exposure': sum(abs(float(p.get('size', 0)) * float(p.get('avgPrice', 0)) for p in positions)),
                'can_enforce': len(positions) > 0 or len(orders) > 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting enforcement summary: {e}")
            return {
                'account_id': account_id,
                'open_positions': 0,
                'pending_orders': 0,
                'total_exposure': 0.0,
                'can_enforce': False,
                'error': str(e)
            }

if __name__ == "__main__":
    print("Testing RiskEnforcer...")
    
    # Test basic initialization
    from risk_manager_v2.core.client import ProjectXClient
    client = ProjectXClient()
    enforcer = RiskEnforcer(client)
    print("âœ… RiskEnforcer created successfully!")
    
    # Test enforcement summary
    summary = enforcer.get_enforcement_summary("123")
    print(f"âœ… Enforcement summary: {summary}")
    
    print("âœ… RiskEnforcer test completed!")

