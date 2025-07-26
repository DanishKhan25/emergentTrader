"""
Momentum Trading Strategy - Identifies stocks with strong price momentum
Focuses on trending stocks with good volume confirmation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MomentumStrategy:
    def __init__(self, name: str = "Momentum Trading"):
        self.name = name
        self.lookback_period = 20  # Days for momentum calculation
        self.min_volume_ratio = 1.2  # Minimum volume vs average
        self.min_momentum_score = 5  # Minimum momentum percentage
        self.max_rsi = 70  # Avoid overbought stocks
        self.min_rsi = 40  # Avoid oversold stocks
        
    def calculate_momentum_score(self, data: pd.DataFrame) -> float:
        """
        Calculate momentum score based on price and volume
        
        Args:
            data: DataFrame with OHLCV and technical indicators
        
        Returns:
            Momentum score (higher is better)
        """
        if len(data) < self.lookback_period:
            return 0
        
        try:
            latest = data.iloc[-1]
            lookback_price = data.iloc[-self.lookback_period]['close']
            
            # Price momentum (percentage change)
            price_momentum = ((latest['close'] - lookback_price) / lookback_price) * 100
            
            # Volume confirmation
            volume_momentum = latest['volume_ratio'] if 'volume_ratio' in data.columns else 1
            
            # Moving average alignment (bullish when price > SMA)
            ma_alignment_score = 0
            if 'sma_20' in data.columns and latest['close'] > latest['sma_20']:
                ma_alignment_score += 1
            if 'sma_50' in data.columns and latest['close'] > latest['sma_50']:
                ma_alignment_score += 1
                
            # RSI check (avoid extreme levels)
            rsi_score = 1 if self.min_rsi <= latest.get('rsi', 50) <= self.max_rsi else 0.5
            
            # Combined momentum score
            momentum_score = (price_momentum * volume_momentum * rsi_score * (1 + ma_alignment_score * 0.2))
            
            return momentum_score
            
        except Exception as e:
            logger.error(f"Error calculating momentum score: {str(e)}")
            return 0
    
    def generate_signal(self, symbol: str, data: pd.DataFrame, stock_info: Dict) -> Optional[Dict]:
        """
        Generate buy/sell signal based on momentum strategy
        
        Args:
            symbol: Stock symbol
            data: Historical price data with indicators
            stock_info: Fundamental stock information
        
        Returns:
            Signal dictionary or None if no signal
        """
        if data.empty or len(data) < self.lookback_period:
            return None
        
        try:
            latest = data.iloc[-1]
            momentum_score = self.calculate_momentum_score(data)
            
            # Signal generation conditions
            if momentum_score >= self.min_momentum_score:
                # Calculate entry price and targets
                entry_price = latest['close']
                atr = latest.get('atr', entry_price * 0.02)  # 2% default if ATR not available
                
                # Risk-reward setup (1:2 ratio)
                stop_loss = entry_price - (atr * 2)  # 2 ATR stop loss
                target_price = entry_price + (atr * 4)  # 4 ATR target (1:2 risk-reward)
                
                # Position size based on 1% risk
                risk_amount = 10000 * 0.01  # Assuming 10k capital, 1% risk
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
                    'momentum_score': round(momentum_score, 2),
                    'rsi': round(latest.get('rsi', 50), 2),
                    'volume_ratio': round(latest.get('volume_ratio', 1), 2),
                    'timestamp': datetime.now().isoformat(),
                    'risk_reward_ratio': round((target_price - entry_price) / (entry_price - stop_loss), 2),
                    'sector': stock_info.get('sector', ''),
                    'market_cap': stock_info.get('market_cap', 0),
                    'confidence_score': min(momentum_score / 10, 1.0),  # Normalize to 0-1
                    'validity_days': 5  # Signal valid for 5 days
                }
                
                logger.info(f"Generated BUY signal for {symbol} with momentum score: {momentum_score}")
                return signal
            
            # Check for sell signals (for existing positions)
            elif momentum_score < 0:  # Negative momentum
                signal = {
                    'signal_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'strategy': self.name,
                    'signal_type': 'SELL',
                    'entry_price': latest['close'],
                    'momentum_score': round(momentum_score, 2),
                    'rsi': round(latest.get('rsi', 50), 2),
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'Negative momentum detected'
                }
                
                logger.info(f"Generated SELL signal for {symbol} with momentum score: {momentum_score}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            return None
    
    def get_strategy_params(self) -> Dict:
        """Return strategy parameters for configuration"""
        return {
            'name': self.name,
            'lookback_period': self.lookback_period,
            'min_volume_ratio': self.min_volume_ratio,
            'min_momentum_score': self.min_momentum_score,
            'max_rsi': self.max_rsi,
            'min_rsi': self.min_rsi
        }
    
    def backtest_signal(self, data: pd.DataFrame, entry_date: str, exit_days: int = 10) -> Dict:
        """
        Backtest a signal to see how it would have performed
        
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
            
            # Calculate max drawdown during holding period
            holding_data = data.iloc[entry_idx:exit_idx + 1]
            cumulative_returns = (holding_data['close'] / entry_price - 1) * 100
            max_drawdown = cumulative_returns.min()
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'absolute_return': absolute_return,
                'percentage_return': percentage_return,
                'max_drawdown': max_drawdown,
                'holding_days': exit_idx - entry_idx,
                'success': percentage_return > 0
            }
            
        except Exception as e:
            logger.error(f"Error in backtesting: {str(e)}")
            return {}