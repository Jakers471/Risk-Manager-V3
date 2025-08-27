"""
Risk Calculator

Calculates risk metrics and checks for rule violations.
"""

from datetime import datetime, date
from typing import Dict, List, Optional
from risk_manager_v2.core.logger import get_logger

class RiskCalculator:
    """Calculates risk metrics and detects violations."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def calculate_risk_metrics(self, account_data: Dict, positions: List[Dict], 
                             trades: List[Dict], risk_rules) -> Dict:
        """Calculate comprehensive risk metrics for an account."""
        try:
            metrics = {
                'account_id': account_data.get('id'),  # TopStepX API uses 'id'
                'timestamp': datetime.now(),
                'daily_pnl': 0.0,
                'daily_trades': 0,
                'total_positions': len(positions),
                'total_exposure': 0.0,
                'max_position_size': 0,
                'margin_utilization': 0.0,
                'largest_position': None
            }
            
            # Calculate daily P&L from trades
            metrics['daily_pnl'] = self._calculate_daily_pnl(trades)
            
            # Count daily trades
            metrics['daily_trades'] = len(trades)
            
            # Calculate position metrics
            if positions:
                position_metrics = self._calculate_position_metrics(positions)
                metrics.update(position_metrics)
            
            # Calculate margin utilization
            metrics['margin_utilization'] = self._calculate_margin_utilization(account_data)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    def check_violations(self, metrics: Dict, risk_rules) -> List[Dict]:
        """Check for risk rule violations."""
        violations = []
        
        if not risk_rules:
            return violations
        
        try:
            # Check daily loss limit
            if risk_rules.daily_limits and risk_rules.daily_limits.is_enabled():
                daily_pnl = metrics.get('daily_pnl', 0)
                max_loss = risk_rules.daily_limits.max_daily_loss
                
                if daily_pnl < -max_loss:
                    violations.append({
                        'type': 'DAILY_LOSS_LIMIT',
                        'message': f'Daily loss limit exceeded: ${daily_pnl:.2f} (limit: ${max_loss:.2f})',
                        'severity': 'CRITICAL',
                        'metric': 'daily_pnl',
                        'value': daily_pnl,
                        'limit': max_loss
                    })
                
                # Check daily profit target
                profit_target = risk_rules.daily_limits.daily_profit_target
                if daily_pnl > profit_target:
                    violations.append({
                        'type': 'DAILY_PROFIT_TARGET',
                        'message': f'Daily profit target reached: ${daily_pnl:.2f} (target: ${profit_target:.2f})',
                        'severity': 'WARNING',
                        'metric': 'daily_pnl',
                        'value': daily_pnl,
                        'limit': profit_target
                    })
                
                # Check daily trade count
                daily_trades = metrics.get('daily_trades', 0)
                max_trades = risk_rules.daily_limits.max_daily_trades
                
                if daily_trades >= max_trades:
                    violations.append({
                        'type': 'DAILY_TRADE_LIMIT',
                        'message': f'Daily trade limit reached: {daily_trades} (limit: {max_trades})',
                        'severity': 'WARNING',
                        'metric': 'daily_trades',
                        'value': daily_trades,
                        'limit': max_trades
                    })
            
            # Check position size limits
            if risk_rules.position_limits and risk_rules.position_limits.is_enabled():
                max_size = risk_rules.position_limits.max_position_size
                current_max = metrics.get('max_position_size', 0)
                
                if current_max > max_size:
                    violations.append({
                        'type': 'POSITION_SIZE_LIMIT',
                        'message': f'Position size limit exceeded: {current_max} (limit: {max_size})',
                        'severity': 'WARNING',
                        'metric': 'max_position_size',
                        'value': current_max,
                        'limit': max_size
                    })
                
                # Check open positions count
                total_positions = metrics.get('total_positions', 0)
                max_positions = risk_rules.position_limits.max_open_positions
                
                if total_positions > max_positions:
                    violations.append({
                        'type': 'MAX_POSITIONS_EXCEEDED',
                        'message': f'Maximum open positions exceeded: {total_positions} (limit: {max_positions})',
                        'severity': 'WARNING',
                        'metric': 'total_positions',
                        'value': total_positions,
                        'limit': max_positions
                    })
            
            # Check trading hours
            if risk_rules.trading_hours and risk_rules.trading_hours.is_enabled():
                if not self._is_within_trading_hours(risk_rules.trading_hours):
                    violations.append({
                        'type': 'OUTSIDE_TRADING_HOURS',
                        'message': 'Trading outside allowed hours',
                        'severity': 'WARNING',
                        'metric': 'trading_hours',
                        'value': 'outside_hours',
                        'limit': 'trading_hours_only'
                    })
            
            # Check margin utilization
            margin_util = metrics.get('margin_utilization', 0)
            if margin_util > 80.0:  # 80% margin utilization threshold
                violations.append({
                    'type': 'HIGH_MARGIN_UTILIZATION',
                    'message': f'High margin utilization: {margin_util:.1f}% (threshold: 80%)',
                    'severity': 'WARNING',
                    'metric': 'margin_utilization',
                    'value': margin_util,
                    'limit': 80.0
                })
            
        except Exception as e:
            self.logger.error(f"Error checking violations: {e}")
        
        return violations
    
    def _calculate_daily_pnl(self, trades: List[Dict]) -> float:
        """Calculate daily P&L from trades using TopStepX API structure."""
        daily_pnl = 0.0
        
        for trade in trades:
            # TopStepX API uses 'profitAndLoss' field
            pnl = trade.get('profitAndLoss')
            if pnl is not None:  # Check for None since P&L can be null for half-turn trades
                daily_pnl += float(pnl)
        
        return daily_pnl
    
    def _calculate_position_metrics(self, positions: List[Dict]) -> Dict:
        """Calculate position-related metrics using TopStepX API structure."""
        total_exposure = 0.0
        max_position_size = 0
        largest_position = None
        
        for position in positions:
            # TopStepX API position structure: accountId, contractId, size, avgPrice
            size = abs(float(position.get('size', 0)))
            avg_price = float(position.get('avgPrice', 0))
            contract_id = position.get('contractId', 'Unknown')
            
            # Calculate position value
            position_value = size * avg_price
            total_exposure += position_value
            
            # Track largest position
            if size > max_position_size:
                max_position_size = size
                largest_position = {
                    'contract_id': contract_id,
                    'size': size,
                    'avg_price': avg_price,
                    'value': position_value
                }
        
        return {
            'total_exposure': total_exposure,
            'max_position_size': max_position_size,
            'largest_position': largest_position
        }
    
    def _calculate_margin_utilization(self, account_data: Dict) -> float:
        """Calculate margin utilization percentage using TopStepX API structure."""
        try:
            # TopStepX API account structure: id, name, balance, canTrade, isVisible
            balance = float(account_data.get('balance', 0))
            
            # For demo purposes, estimate margin used based on balance
            # In real implementation, this would come from account details endpoint
            # For now, we'll use a conservative estimate
            margin_used = balance * 0.1  # Assume 10% of balance is used as margin
            
            if balance > 0:
                return (margin_used / balance) * 100
            return 0.0
            
        except (ValueError, TypeError):
            return 0.0
    
    def _is_within_trading_hours(self, trading_hours) -> bool:
        """Check if current time is within trading hours."""
        try:
            if trading_hours and hasattr(trading_hours, 'is_within_trading_hours'):
                return trading_hours.is_within_trading_hours()
            return True  # Default to allowing trading if check fails
        except Exception as e:
            self.logger.error(f"Error checking trading hours: {e}")
            return True  # Default to allowing trading if check fails
    
    def get_risk_summary(self, metrics: Dict, violations: List[Dict]) -> Dict:
        """Get comprehensive risk summary."""
        return {
            'account_id': metrics.get('account_id'),
            'timestamp': metrics.get('timestamp'),
            'risk_level': self._calculate_risk_level(violations),
            'metrics': metrics,
            'violations': violations,
            'violation_count': len(violations),
            'critical_violations': len([v for v in violations if v.get('severity') == 'CRITICAL']),
            'warnings': len([v for v in violations if v.get('severity') == 'WARNING'])
        }
    
    def _calculate_risk_level(self, violations: List[Dict]) -> str:
        """Calculate overall risk level based on violations."""
        if not violations:
            return 'LOW'
        
        critical_count = len([v for v in violations if v.get('severity') == 'CRITICAL'])
        warning_count = len([v for v in violations if v.get('severity') == 'WARNING'])
        
        if critical_count > 0:
            return 'CRITICAL'
        elif warning_count >= 3:
            return 'HIGH'
        elif warning_count >= 1:
            return 'MEDIUM'
        else:
            return 'LOW'

if __name__ == "__main__":
    print("Testing RiskCalculator...")
    
    # Test basic initialization
    calculator = RiskCalculator()
    print("âœ… RiskCalculator created successfully!")
    
    # Test metrics calculation with TopStepX API structure
    account_data = {
        'id': 123,
        'name': 'TEST_ACCOUNT',
        'balance': 50000,
        'canTrade': True,
        'isVisible': True
    }
    
    positions = [
        {
            'accountId': 123,
            'contractId': 'CON.F.US.EP.H25',
            'size': 2,
            'avgPrice': 2100.0
        }
    ]
    
    trades = [
        {
            'id': 8604,
            'accountId': 123,
            'contractId': 'CON.F.US.EP.H25',
            'profitAndLoss': 50.0,
            'side': 1,
            'size': 1
        }
    ]
    
    metrics = calculator.calculate_risk_metrics(account_data, positions, trades, None)
    print(f"âœ… Metrics calculated: {metrics}")
    
    # Test violation checking
    violations = calculator.check_violations(metrics, None)
    print(f"âœ… Violations checked: {len(violations)} violations")
    
    # Test risk summary
    summary = calculator.get_risk_summary(metrics, violations)
    print(f"âœ… Risk summary: {summary}")
    
    print("âœ… RiskCalculator test completed!")


