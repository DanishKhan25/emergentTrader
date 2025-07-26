"""
Breakout Trading Strategy - Identifies stocks breaking out of consolidation patterns
Focuses on stocks breaking above resistance or below support with volume confirmation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class BreakoutStrategy:
    def __init__(self, name: str = "Breakout"):
        self.name = name
        self.consolidation_period = 20  # Days to look for consolidation
        self.breakout_threshold = 0.02  # 2% breakout from consolidation range
        self.min_volume_surge = 1.5  # Minimum volume surge for confirmation
        self.max_consolidation_range = 0.15  # Maximum 15% range for consolidation
        self.min_consolidation_range = 0.03  # Minimum 3% range for valid consolidation
        self.atr_multiplier = 2.0  # ATR multiplier for stop loss
        self.target_multiplier = 3.0  # Risk-reward ratio
        
    def identify_consolidation(self, data: pd.DataFrame) -> Dict:
        """
        Identify consolidation patterns in price data
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            Dictionary with consolidation details
        """
        if len(data) < self.consolidation_period:
            return {}
        
        try:
            # Get recent data for consolidation analysis
            recent_data = data.tail(self.consolidation_period)
            
            # Calculate consolidation range
            high_price = recent_data['high'].max()
            low_price = recent_data['low'].min()
            range_pct = (high_price - low_price) / low_price
            
            # Check if range is within consolidation criteria
            if not (self.min_consolidation_range <= range_pct <= self.max_consolidation_range):
                return {}
            
            # Calculate consolidation strength (lower volatility = stronger consolidation)
            price_volatility = recent_data['close'].std() / recent_data['close'].mean()
            
            # Check for sideways movement (no strong trend)
            first_close = recent_data.iloc[0]['close']
            last_close = recent_data.iloc[-1]['close']
            trend_strength = abs(last_close - first_close) / first_close
            
            # Valid consolidation: low volatility and minimal trend
            if price_volatility < 0.05 and trend_strength < 0.08:
                return {
                    'resistance': high_price,
                    'support': low_price,
                    'range_pct': range_pct,
                    'volatility': price_volatility,
                    'trend_strength': trend_strength,
                    'consolidation_days': len(recent_data),
                    'is_valid': True
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error identifying consolidation: {str(e)}")
            return {}
    
    def detect_breakout(self, data: pd.DataFrame, consolidation: Dict) -> Dict:
        """
        Detect breakout from consolidation pattern
        
        Args:
            data: Price data
            consolidation: Consolidation pattern details
        
        Returns:
            Breakout detection results
        """
        if not consolidation or data.empty:
            return {}
        
        try:
            latest = data.iloc[-1]
            current_price = latest['close']
            current_volume = latest.get('volume', 0)
            
            # Calculate average volume during consolidation
            recent_data = data.tail(self.consolidation_period)
            avg_volume = recent_data['volume'].mean() if 'volume' in recent_data.columns else 1
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            resistance = consolidation['resistance']
            support = consolidation['support']
            
            # Check for upward breakout
            if current_price > resistance * (1 + self.breakout_threshold):
                breakout_strength = (current_price - resistance) / resistance
                
                return {
                    'type': 'UPWARD',
                    'breakout_price': current_price,
                    'breakout_level': resistance,
                    'breakout_strength': breakout_strength,
                    'volume_confirmation': volume_ratio >= self.min_volume_surge,
                    'volume_ratio': volume_ratio,
                    'is_valid': volume_ratio >= self.min_volume_surge
                }
            
            # Check for downward breakout
            elif current_price < support * (1 - self.breakout_threshold):
                breakout_strength = (support - current_price) / support
                
                return {
                    'type': 'DOWNWARD',
                    'breakout_price': current_price,
                    'breakout_level': support,
                    'breakout_strength': breakout_strength,
                    'volume_confirmation': volume_ratio >= self.min_volume_surge,
                    'volume_ratio': volume_ratio,
                    'is_valid': volume_ratio >= self.min_volume_surge
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error detecting breakout: {str(e)}")
            return {}
    
    def calculate_breakout_score(self, data: pd.DataFrame) -> float:
        """
        Calculate breakout score based on pattern strength and volume
        
        Args:
            data: DataFrame with OHLCV and technical indicators
        
        Returns:
            Breakout score (higher indicates stronger breakout potential)
        """
        try:
            # Identify consolidation pattern
            consolidation = self.identify_consolidation(data)
            if not consolidation.get('is_valid'):
                return 0
            
            # Detect breakout
            breakout = self.detect_breakout(data, consolidation)
            if not breakout.get('is_valid'):
                return 0
            
            # Calculate score components
            volume_score = min(breakout['volume_ratio'] / 2, 2.0)  # Cap at 2x
            strength_score = breakout['breakout_strength'] * 10  # Scale up
            consolidation_score = (1 - consolidation['volatility']) * 2  # Lower volatility = higher score
            
            # Bonus for longer consolidation (more significant breakout)
            time_score = min(consolidation['consolidation_days'] / 30, 1.5)
            
            # Combined breakout score
            breakout_score = (strength_score + volume_score + consolidation_score) * time_score
            
            # Negative score for downward breakouts (sell signals)
            if breakout['type'] == 'DOWNWARD':
                breakout_score = -breakout_score
            
            return breakout_score
            
        except Exception as e:
            logger.error(f"Error calculating breakout score: {str(e)}")
            return 0
    
    def generate_signal(self, symbol: str, data: pd.DataFrame, stock_info: Dict) -> Optional[Dict]:
        """
        Generate buy/sell signal based on breakout strategy
        
        Args:
            symbol: Stock symbol
            data: Historical price data with indicators
            stock_info: Fundamental stock information
        
        Returns:
            Signal dictionary or None if no signal
        """
        if data.empty or len(data) < self.consolidation_period:
            return None
        
        try:
            latest = data.iloc[-1]
            breakout_score = self.calculate_breakout_score(data)
            
            if abs(breakout_score) < 1.0:  # Minimum score threshold
                return None
            
            # Get consolidation and breakout details
            consolidation = self.identify_consolidation(data)
            breakout = self.detect_breakout(data, consolidation)
            
            if not (consolidation.get('is_valid') and breakout.get('is_valid')):
                return None
            
            current_price = latest['close']
            atr = latest.get('atr', current_price * 0.02)  # 2% default ATR
            
            # BUY Signal: Upward breakout
            if breakout['type'] == 'UPWARD' and breakout_score > 1.0:
                entry_price = current_price
                stop_loss = consolidation['support']  # Use consolidation support as stop
                
                # Target based on consolidation range
                consolidation_range = consolidation['resistance'] - consolidation['support']
                target_price = entry_price + (consolidation_range * self.target_multiplier)
                
                # Ensure minimum risk-reward ratio
                risk_reward = (target_price - entry_price) / (entry_price - stop_loss)
                if risk_reward < 2.0:  # Minimum 2:1 ratio for breakouts
                    target_price = entry_price + ((entry_price - stop_loss) * 2)
                
                # Position size based on 1% risk
                risk_amount = 10000 * 0.01
                risk_per_share = entry_price - stop_loss
                position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 100
                
                signal = {
                    'signal_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'strategy': self.name,
                    'signal_type': 'BUY',
                    'entry_price': round(entry_price, 2),
                    'target_price': round(target_price, 2),
                    'stop_loss': round(stop_loss, 2),
                    'quantity': position_size,
                    'breakout_score': round(breakout_score, 2),
                    'breakout_type': breakout['type'],
                    'breakout_strength': round(breakout['breakout_strength'] * 100, 2),
                    'volume_ratio': round(breakout['volume_ratio'], 2),
                    'consolidation_days': consolidation['consolidation_days'],
                    'consolidation_range': round(consolidation['range_pct'] * 100, 2),
                    'resistance_level': round(consolidation['resistance'], 2),
                    'support_level': round(consolidation['support'], 2),
                    'timestamp': datetime.now().isoformat(),
                    'risk_reward_ratio': round((target_price - entry_price) / (entry_price - stop_loss), 2),
                    'sector': stock_info.get('sector', ''),
                    'market_cap': stock_info.get('market_cap', 0),
                    'confidence_score': min(breakout_score / 5, 1.0),  # Normalize to 0-1
                    'validity_days': 7,  # Breakout signals valid for a week
                    'strategy_reason': f'Upward breakout from {consolidation["consolidation_days"]}-day consolidation'
                }
                
                logger.info(f"Generated BUY breakout signal for {symbol} - Score: {breakout_score}")
                return signal
            
            # SELL Signal: Downward breakout
            elif breakout['type'] == 'DOWNWARD' and breakout_score < -1.0:
                signal = {
                    'signal_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'strategy': self.name,
                    'signal_type': 'SELL',
                    'entry_price': current_price,
                    'target_price': round(consolidation['support'] - (consolidation['resistance'] - consolidation['support']), 2),
                    'stop_loss': round(consolidation['resistance'], 2),
                    'breakout_score': round(breakout_score, 2),
                    'breakout_type': breakout['type'],
                    'breakout_strength': round(breakout['breakout_strength'] * 100, 2),
                    'volume_ratio': round(breakout['volume_ratio'], 2),
                    'consolidation_days': consolidation['consolidation_days'],
                    'timestamp': datetime.now().isoformat(),
                    'reason': f'Downward breakout from {consolidation["consolidation_days"]}-day consolidation',
                    'confidence_score': min(abs(breakout_score) / 5, 1.0),
                    'validity_days': 7,
                    'strategy_reason': f'Downward breakout from {consolidation["consolidation_days"]}-day consolidation'
                }
                
                logger.info(f"Generated SELL breakout signal for {symbol} - Score: {breakout_score}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating breakout signal for {symbol}: {str(e)}")
            return None
    
    def get_strategy_params(self) -> Dict:
        """Return strategy parameters for configuration"""
        return {
            'name': self.name,
            'consolidation_period': self.consolidation_period,
            'breakout_threshold': self.breakout_threshold,
            'min_volume_surge': self.min_volume_surge,
            'max_consolidation_range': self.max_consolidation_range,
            'min_consolidation_range': self.min_consolidation_range,
            'atr_multiplier': self.atr_multiplier,
            'target_multiplier': self.target_multiplier
        }
    
    def backtest_signal(self, data: pd.DataFrame, entry_date: str, exit_days: int = 10) -> Dict:
        """
        Backtest a breakout signal
        
        Args:
            data: Historical price data
            entry_date: Date when signal was generated
            exit_days: Number of days to hold position
        
        Returns:
            Backtest results dictionary
        """
        try:
            entry_idx = data[data['date'] >= entry_date].index[0]
            exit_idx = min(entry_idx + exit_days, len(data) - 1)
            
            entry_price = data.iloc[entry_idx]['close']
            exit_price = data.iloc[exit_idx]['close']
            
            # Calculate returns
            absolute_return = exit_price - entry_price
            percentage_return = (absolute_return / entry_price) * 100
            
            # Track breakout follow-through
            holding_data = data.iloc[entry_idx:exit_idx + 1]
            max_price = holding_data['high'].max()
            min_price = holding_data['low'].min()
            
            # Calculate maximum favorable and adverse excursions
            max_favorable = ((max_price - entry_price) / entry_price) * 100
            max_adverse = ((min_price - entry_price) / entry_price) * 100
            
            # Check if breakout continued (price stayed above/below breakout level)
            breakout_sustained = True
            if percentage_return > 0:  # Upward breakout
                breakout_sustained = min_price >= entry_price * 0.98  # Allow 2% pullback
            else:  # Downward breakout
                breakout_sustained = max_price <= entry_price * 1.02  # Allow 2% bounce
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'absolute_return': absolute_return,
                'percentage_return': percentage_return,
                'max_favorable_excursion': max_favorable,
                'max_adverse_excursion': max_adverse,
                'breakout_sustained': breakout_sustained,
                'holding_days': exit_idx - entry_idx,
                'success': percentage_return > 0,
                'strategy_type': 'breakout'
            }
            
        except Exception as e:
            logger.error(f"Error in breakout backtesting: {str(e)}")
            return {}
    
    def identify_chart_patterns(self, data: pd.DataFrame) -> Dict:
        """
        Identify common chart patterns that often lead to breakouts
        
        Args:
            data: Price data
        
        Returns:
            Dictionary with identified patterns
        """
        try:
            if len(data) < 30:
                return {}
            
            recent_data = data.tail(30)
            patterns = {}
            
            # Triangle pattern detection
            highs = recent_data['high']
            lows = recent_data['low']
            
            # Ascending triangle: horizontal resistance, rising support
            resistance_slope = np.polyfit(range(len(highs)), highs, 1)[0]
            support_slope = np.polyfit(range(len(lows)), lows, 1)[0]
            
            if abs(resistance_slope) < 0.1 and support_slope > 0.1:
                patterns['ascending_triangle'] = True
            elif abs(support_slope) < 0.1 and resistance_slope < -0.1:
                patterns['descending_triangle'] = True
            elif support_slope > 0.1 and resistance_slope < -0.1:
                patterns['symmetrical_triangle'] = True
            
            # Flag pattern: sharp move followed by consolidation
            if len(data) >= 50:
                pre_consolidation = data.iloc[-50:-30]
                consolidation_period = data.tail(20)
                
                pre_move = (pre_consolidation['close'].iloc[-1] - pre_consolidation['close'].iloc[0]) / pre_consolidation['close'].iloc[0]
                consolidation_range = (consolidation_period['high'].max() - consolidation_period['low'].min()) / consolidation_period['close'].mean()
                
                if abs(pre_move) > 0.1 and consolidation_range < 0.05:
                    patterns['flag_pattern'] = True
                    patterns['flag_direction'] = 'bullish' if pre_move > 0 else 'bearish'
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error identifying chart patterns: {str(e)}")
            return {}
