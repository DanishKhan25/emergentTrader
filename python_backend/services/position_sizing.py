"""
Position Sizing Optimization for EmergentTrader
Implements various position sizing algorithms for optimal risk management
"""

import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from services.logging_service import get_logger, log_performance

class PositionSizingOptimizer:
    def __init__(self):
        self.logger = get_logger('portfolio')
        
        # Default risk parameters
        self.default_risk_per_trade = 0.02  # 2% risk per trade
        self.max_position_size = 0.10       # 10% max position size
        self.min_position_size = 0.01       # 1% min position size
        self.max_portfolio_risk = 0.20      # 20% max total portfolio risk
        
        # Confidence-based multipliers
        self.confidence_multipliers = {
            0.95: 1.5,   # Very high confidence
            0.90: 1.3,   # High confidence
            0.85: 1.1,   # Good confidence
            0.80: 1.0,   # Normal confidence
            0.75: 0.8,   # Lower confidence
            0.70: 0.6,   # Low confidence
        }
        
    @log_performance('portfolio')
    def calculate_optimal_position_size(self, 
                                      signal_data: Dict, 
                                      portfolio_data: Dict,
                                      sizing_method: str = 'kelly') -> Dict:
        """
        Calculate optimal position size using specified method
        
        Args:
            signal_data: Signal information with confidence, prices, etc.
            portfolio_data: Current portfolio state
            sizing_method: 'kelly', 'fixed_risk', 'volatility_adjusted', 'confidence_based'
        """
        try:
            self.logger.info(f"Calculating position size using {sizing_method} method")
            
            # Extract signal parameters
            symbol = signal_data.get('symbol', 'UNKNOWN')
            confidence = signal_data.get('confidence', 0.8)
            entry_price = signal_data.get('entry_price', 0)
            target_price = signal_data.get('target_price', 0)
            stop_loss = signal_data.get('stop_loss', 0)
            
            # Extract portfolio parameters
            total_capital = portfolio_data.get('total_value', 1000000)
            available_funds = portfolio_data.get('available_funds', total_capital)
            current_positions = portfolio_data.get('positions', {})
            
            # Validate inputs
            if not all([entry_price, target_price, stop_loss]):
                return {
                    'success': False,
                    'error': 'Missing required price levels'
                }
            
            if entry_price <= 0 or stop_loss >= entry_price:
                return {
                    'success': False,
                    'error': 'Invalid price levels'
                }
            
            # Calculate risk and reward
            risk_per_share = entry_price - stop_loss
            reward_per_share = target_price - entry_price
            risk_reward_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0
            
            # Calculate position size based on method
            if sizing_method == 'kelly':
                position_size = self._kelly_criterion_sizing(
                    confidence, risk_reward_ratio, total_capital, risk_per_share, entry_price
                )
            elif sizing_method == 'fixed_risk':
                position_size = self._fixed_risk_sizing(
                    total_capital, risk_per_share, entry_price
                )
            elif sizing_method == 'volatility_adjusted':
                position_size = self._volatility_adjusted_sizing(
                    signal_data, portfolio_data, risk_per_share, entry_price
                )
            elif sizing_method == 'confidence_based':
                position_size = self._confidence_based_sizing(
                    confidence, total_capital, risk_per_share, entry_price
                )
            else:
                return {
                    'success': False,
                    'error': f'Unknown sizing method: {sizing_method}'
                }
            
            # Apply portfolio-level constraints
            position_size = self._apply_portfolio_constraints(
                position_size, total_capital, available_funds, current_positions, entry_price
            )
            
            # Calculate final metrics
            position_value = position_size * entry_price
            max_loss = position_size * risk_per_share
            max_gain = position_size * reward_per_share
            portfolio_risk_percent = (max_loss / total_capital) * 100
            position_percent = (position_value / total_capital) * 100
            
            result = {
                'success': True,
                'sizing_method': sizing_method,
                'symbol': symbol,
                'position_size': int(position_size),
                'position_value': round(position_value, 2),
                'position_percent': round(position_percent, 2),
                'max_loss': round(max_loss, 2),
                'max_gain': round(max_gain, 2),
                'portfolio_risk_percent': round(portfolio_risk_percent, 2),
                'risk_reward_ratio': round(risk_reward_ratio, 2),
                'confidence': confidence,
                'entry_price': entry_price,
                'target_price': target_price,
                'stop_loss': stop_loss,
                'calculations': {
                    'risk_per_share': round(risk_per_share, 2),
                    'reward_per_share': round(reward_per_share, 2),
                    'available_funds': available_funds,
                    'total_capital': total_capital
                }
            }
            
            self.logger.info(
                f"Position size calculated for {symbol}: {position_size} shares "
                f"({position_percent:.1f}% of portfolio, {portfolio_risk_percent:.1f}% risk)"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def _kelly_criterion_sizing(self, confidence: float, risk_reward_ratio: float, 
                               total_capital: float, risk_per_share: float, entry_price: float) -> float:
        """Calculate position size using Kelly Criterion"""
        
        # Kelly formula: f = (bp - q) / b
        # where: b = odds (risk/reward ratio), p = win probability, q = loss probability
        
        win_probability = confidence
        loss_probability = 1 - confidence
        odds = risk_reward_ratio
        
        if odds <= 0:
            return 0
        
        # Kelly fraction
        kelly_fraction = (odds * win_probability - loss_probability) / odds
        
        # Apply conservative scaling (typically 25-50% of Kelly)
        conservative_kelly = kelly_fraction * 0.25
        
        # Ensure positive and reasonable
        conservative_kelly = max(0, min(conservative_kelly, 0.1))  # Max 10% of capital
        
        # Calculate position size
        capital_to_risk = total_capital * conservative_kelly
        position_size = capital_to_risk / risk_per_share
        
        return position_size
    
    def _fixed_risk_sizing(self, total_capital: float, risk_per_share: float, entry_price: float) -> float:
        """Calculate position size using fixed risk percentage"""
        
        risk_amount = total_capital * self.default_risk_per_trade
        position_size = risk_amount / risk_per_share
        
        return position_size
    
    def _volatility_adjusted_sizing(self, signal_data: Dict, portfolio_data: Dict,
                                   risk_per_share: float, entry_price: float) -> float:
        """Calculate position size adjusted for volatility"""
        
        # Get volatility estimate (simplified - could use historical volatility)
        volatility = signal_data.get('volatility', 0.02)  # Default 2% daily volatility
        
        # Adjust risk based on volatility
        volatility_adjustment = 1 / (1 + volatility * 10)  # Higher volatility = smaller position
        
        total_capital = portfolio_data.get('total_value', 1000000)
        adjusted_risk = total_capital * self.default_risk_per_trade * volatility_adjustment
        
        position_size = adjusted_risk / risk_per_share
        
        return position_size
    
    def _confidence_based_sizing(self, confidence: float, total_capital: float,
                                risk_per_share: float, entry_price: float) -> float:
        """Calculate position size based on signal confidence"""
        
        # Get confidence multiplier
        multiplier = 1.0
        for conf_threshold in sorted(self.confidence_multipliers.keys(), reverse=True):
            if confidence >= conf_threshold:
                multiplier = self.confidence_multipliers[conf_threshold]
                break
        
        # Base risk adjusted by confidence
        adjusted_risk = total_capital * self.default_risk_per_trade * multiplier
        position_size = adjusted_risk / risk_per_share
        
        return position_size
    
    def _apply_portfolio_constraints(self, position_size: float, total_capital: float,
                                   available_funds: float, current_positions: Dict,
                                   entry_price: float) -> float:
        """Apply portfolio-level constraints to position size"""
        
        # Calculate position value
        position_value = position_size * entry_price
        
        # Constraint 1: Available funds
        if position_value > available_funds:
            position_size = available_funds / entry_price
            self.logger.warning(f"Position size limited by available funds: {available_funds}")
        
        # Constraint 2: Maximum position size as % of portfolio
        max_position_value = total_capital * self.max_position_size
        if position_value > max_position_value:
            position_size = max_position_value / entry_price
            self.logger.warning(f"Position size limited by max position size: {self.max_position_size*100}%")
        
        # Constraint 3: Minimum position size
        min_position_value = total_capital * self.min_position_size
        if position_value < min_position_value:
            position_size = min_position_value / entry_price
            self.logger.info(f"Position size increased to minimum: {self.min_position_size*100}%")
        
        # Constraint 4: Total portfolio risk
        current_risk = self._calculate_current_portfolio_risk(current_positions, total_capital)
        new_risk = (position_size * (entry_price - entry_price * 0.9)) / total_capital  # Simplified risk calc
        
        if current_risk + new_risk > self.max_portfolio_risk:
            max_additional_risk = self.max_portfolio_risk - current_risk
            if max_additional_risk > 0:
                position_size = (max_additional_risk * total_capital) / (entry_price * 0.1)  # Simplified
                self.logger.warning(f"Position size limited by portfolio risk limit: {self.max_portfolio_risk*100}%")
            else:
                position_size = 0
                self.logger.warning("Position rejected: would exceed portfolio risk limit")
        
        return max(0, position_size)
    
    def _calculate_current_portfolio_risk(self, positions: Dict, total_capital: float) -> float:
        """Calculate current portfolio risk from existing positions"""
        total_risk = 0
        
        for position in positions.values():
            if position.get('status') == 'active':
                entry_price = position.get('entry_price', 0)
                stop_loss = position.get('stop_loss', entry_price * 0.9)
                quantity = position.get('quantity', 0)
                
                position_risk = quantity * (entry_price - stop_loss)
                total_risk += position_risk
        
        return total_risk / total_capital if total_capital > 0 else 0
    
    def get_sizing_recommendations(self, signal_data: Dict, portfolio_data: Dict) -> Dict:
        """Get position sizing recommendations using multiple methods"""
        try:
            methods = ['kelly', 'fixed_risk', 'volatility_adjusted', 'confidence_based']
            recommendations = {}
            
            for method in methods:
                result = self.calculate_optimal_position_size(signal_data, portfolio_data, method)
                if result.get('success'):
                    recommendations[method] = {
                        'position_size': result['position_size'],
                        'position_value': result['position_value'],
                        'position_percent': result['position_percent'],
                        'portfolio_risk_percent': result['portfolio_risk_percent']
                    }
            
            # Calculate consensus recommendation
            if recommendations:
                sizes = [rec['position_size'] for rec in recommendations.values()]
                consensus_size = int(sum(sizes) / len(sizes))
                
                # Use fixed_risk as baseline for consensus metrics
                baseline = recommendations.get('fixed_risk', list(recommendations.values())[0])
                
                return {
                    'success': True,
                    'symbol': signal_data.get('symbol'),
                    'recommendations': recommendations,
                    'consensus': {
                        'position_size': consensus_size,
                        'position_value': consensus_size * signal_data.get('entry_price', 0),
                        'position_percent': (consensus_size * signal_data.get('entry_price', 0) / portfolio_data.get('total_value', 1)) * 100,
                        'method': 'consensus'
                    }
                }
            else:
                return {'success': False, 'error': 'No valid recommendations generated'}
                
        except Exception as e:
            self.logger.error(f"Error generating sizing recommendations: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def update_sizing_parameters(self, parameters: Dict) -> Dict:
        """Update position sizing parameters"""
        try:
            if 'risk_per_trade' in parameters:
                self.default_risk_per_trade = max(0.001, min(0.1, parameters['risk_per_trade']))
            
            if 'max_position_size' in parameters:
                self.max_position_size = max(0.01, min(0.5, parameters['max_position_size']))
            
            if 'min_position_size' in parameters:
                self.min_position_size = max(0.001, min(0.1, parameters['min_position_size']))
            
            if 'max_portfolio_risk' in parameters:
                self.max_portfolio_risk = max(0.05, min(1.0, parameters['max_portfolio_risk']))
            
            self.logger.info(f"Position sizing parameters updated: {parameters}")
            
            return {
                'success': True,
                'parameters': {
                    'risk_per_trade': self.default_risk_per_trade,
                    'max_position_size': self.max_position_size,
                    'min_position_size': self.min_position_size,
                    'max_portfolio_risk': self.max_portfolio_risk
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error updating sizing parameters: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def get_current_parameters(self) -> Dict:
        """Get current position sizing parameters"""
        return {
            'success': True,
            'parameters': {
                'risk_per_trade': self.default_risk_per_trade,
                'max_position_size': self.max_position_size,
                'min_position_size': self.min_position_size,
                'max_portfolio_risk': self.max_portfolio_risk,
                'confidence_multipliers': self.confidence_multipliers
            }
        }

# Global instance
_position_sizer = None

def get_position_sizer() -> PositionSizingOptimizer:
    """Get global position sizing optimizer instance"""
    global _position_sizer
    if _position_sizer is None:
        _position_sizer = PositionSizingOptimizer()
    return _position_sizer
