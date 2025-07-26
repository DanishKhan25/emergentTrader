"""
Mean Reversion Trading Strategy - Identifies oversold/overbought stocks that may revert to mean
Focuses on stocks that have deviated significantly from their average price
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MeanReversionStrategy:
    def __init__(self, name: str = "Mean Reversion"):
        self.name = name
        self.lookback_period = 20  # Days for mean calculation
        self.bollinger_period = 20  # Bollinger bands period
        self.bollinger_std = 2  # Standard deviations for bands
        self.rsi_oversold = 30  # RSI oversold threshold
        self.rsi_overbought = 70  # RSI overbought threshold
        self.min_volume_ratio = 1.1  # Minimum volume confirmation
        self.price_deviation_threshold = 0.05  # 5% deviation from mean
        
    def calculate_bollinger_bands(self, data: pd.DataFrame) -> Dict:
        """
        Calculate Bollinger Bands for mean reversion analysis
        
        Args:
            data: DataFrame with price data
        
        Returns:
            Dictionary with upper, middle, and lower bands
        """
        if len(data) < self.bollinger_period:
            return {}
        
        try:
            close_prices = data['close'].tail(self.bollinger_period)
            
            # Calculate moving average (middle band)
            middle_band = close_prices.mean()
            
            # Calculate standard deviation
            std_dev = close_prices.std()
            
            # Calculate upper and lower bands
            upper_band = middle_band + (self.bollinger_std * std_dev)
            lower_band = middle_band - (self.bollinger_std * std_dev)
            
            return {
                'upper_band': upper_band,
                'middle_band': middle_band,
                'lower_band': lower_band,
                'std_dev': std_dev
            }
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return {}
    
    def calculate_mean_reversion_score(self, data: pd.DataFrame) -> float:
        """
        Calculate mean reversion score based on price deviation and technical indicators
        
        Args:
            data: DataFrame with OHLCV and technical indicators
        
        Returns:
            Mean reversion score (higher indicates stronger reversion potential)
        """
        if len(data) < self.lookback_period:
            return 0
        
        try:
            latest = data.iloc[-1]
            current_price = latest['close']
            
            # Calculate Bollinger Bands
            bb_data = self.calculate_bollinger_bands(data)
            if not bb_data:
                return 0
            
            # Price position relative to Bollinger Bands
            if current_price <= bb_data['lower_band']:
                # Oversold condition (positive score for mean reversion)
                band_score = (bb_data['lower_band'] - current_price) / bb_data['std_dev']
            elif current_price >= bb_data['upper_band']:
                # Overbought condition (negative score, potential short)
                band_score = -(current_price - bb_data['upper_band']) / bb_data['std_dev']
            else:
                # Within bands, no strong reversion signal
                band_score = 0
            
            # RSI confirmation
            rsi = latest.get('rsi', 50)
            if rsi <= self.rsi_oversold:
                rsi_score = (self.rsi_oversold - rsi) / 10  # Stronger oversold = higher score
            elif rsi >= self.rsi_overbought:
                rsi_score = -(rsi - self.rsi_overbought) / 10  # Overbought = negative score
            else:
                rsi_score = 0
            
            # Volume confirmation
            volume_score = latest.get('volume_ratio', 1)
            if volume_score < self.min_volume_ratio:
                volume_score = 0.5  # Reduce score if volume is low
            else:
                volume_score = min(volume_score / 2, 1.5)  # Cap at 1.5x
            
            # Price deviation from moving average
            sma_20 = latest.get('sma_20', current_price)
            price_deviation = abs(current_price - sma_20) / sma_20
            deviation_score = price_deviation if price_deviation > self.price_deviation_threshold else 0
            
            # Combined mean reversion score
            # Positive score indicates oversold (buy opportunity)
            # Negative score indicates overbought (sell/short opportunity)
            reversion_score = (band_score + rsi_score) * volume_score * (1 + deviation_score)
            
            return reversion_score
            
        except Exception as e:
            logger.error(f"Error calculating mean reversion score: {str(e)}")
            return 0
    
    def generate_signal(self, symbol: str, data: pd.DataFrame, stock_info: Dict) -> Optional[Dict]:
        """
        Generate buy/sell signal based on mean reversion strategy
        
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
            reversion_score = self.calculate_mean_reversion_score(data)
            current_price = latest['close']
            rsi = latest.get('rsi', 50)
            
            # Calculate Bollinger Bands for reference
            bb_data = self.calculate_bollinger_bands(data)
            if not bb_data:
                return None
            
            # BUY Signal: Oversold conditions
            if (reversion_score > 1.0 and 
                rsi <= self.rsi_oversold and 
                current_price <= bb_data['lower_band']):
                
                # Calculate entry price and targets
                entry_price = current_price
                atr = latest.get('atr', entry_price * 0.015)  # 1.5% default for mean reversion
                
                # Mean reversion targets (expect return to middle band)
                target_price = bb_data['middle_band']  # Target middle Bollinger Band
                stop_loss = entry_price - (atr * 1.5)  # Tighter stop for mean reversion
                
                # Ensure minimum risk-reward ratio
                risk_reward = (target_price - entry_price) / (entry_price - stop_loss)
                if risk_reward < 1.5:  # Minimum 1.5:1 ratio
                    return None
                
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
                    'reversion_score': round(reversion_score, 2),
                    'rsi': round(rsi, 2),
                    'volume_ratio': round(latest.get('volume_ratio', 1), 2),
                    'bollinger_position': 'Below Lower Band',
                    'distance_from_mean': round(((bb_data['middle_band'] - entry_price) / entry_price) * 100, 2),
                    'timestamp': datetime.now().isoformat(),
                    'risk_reward_ratio': round(risk_reward, 2),
                    'sector': stock_info.get('sector', ''),
                    'market_cap': stock_info.get('market_cap', 0),
                    'confidence_score': min(abs(reversion_score) / 3, 1.0),  # Normalize to 0-1
                    'validity_days': 3,  # Mean reversion signals are shorter-term
                    'strategy_reason': 'Oversold mean reversion opportunity'
                }
                
                logger.info(f"Generated BUY signal for {symbol} - Mean reversion score: {reversion_score}")
                return signal
            
            # SELL Signal: Overbought conditions (for existing positions or short)
            elif (reversion_score < -1.0 and 
                  rsi >= self.rsi_overbought and 
                  current_price >= bb_data['upper_band']):
                
                signal = {
                    'signal_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'strategy': self.name,
                    'signal_type': 'SELL',
                    'entry_price': current_price,
                    'target_price': round(bb_data['middle_band'], 2),
                    'reversion_score': round(reversion_score, 2),
                    'rsi': round(rsi, 2),
                    'bollinger_position': 'Above Upper Band',
                    'distance_from_mean': round(((current_price - bb_data['middle_band']) / bb_data['middle_band']) * 100, 2),
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'Overbought mean reversion signal',
                    'confidence_score': min(abs(reversion_score) / 3, 1.0),
                    'validity_days': 3,
                    'strategy_reason': 'Overbought mean reversion opportunity'
                }
                
                logger.info(f"Generated SELL signal for {symbol} - Mean reversion score: {reversion_score}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating mean reversion signal for {symbol}: {str(e)}")
            return None
    
    def get_strategy_params(self) -> Dict:
        """Return strategy parameters for configuration"""
        return {
            'name': self.name,
            'lookback_period': self.lookback_period,
            'bollinger_period': self.bollinger_period,
            'bollinger_std': self.bollinger_std,
            'rsi_oversold': self.rsi_oversold,
            'rsi_overbought': self.rsi_overbought,
            'min_volume_ratio': self.min_volume_ratio,
            'price_deviation_threshold': self.price_deviation_threshold
        }
    
    def backtest_signal(self, data: pd.DataFrame, entry_date: str, exit_days: int = 5) -> Dict:
        """
        Backtest a mean reversion signal
        
        Args:
            data: Historical price data
            entry_date: Date when signal was generated
            exit_days: Number of days to hold position (shorter for mean reversion)
        
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
            
            # Calculate max favorable excursion (best point during holding)
            holding_data = data.iloc[entry_idx:exit_idx + 1]
            max_favorable = ((holding_data['close'].max() - entry_price) / entry_price) * 100
            max_adverse = ((holding_data['close'].min() - entry_price) / entry_price) * 100
            
            # Check if target (middle band) was reached
            bb_data = self.calculate_bollinger_bands(data.iloc[:entry_idx])
            target_reached = False
            if bb_data:
                target_price = bb_data['middle_band']
                target_reached = holding_data['close'].max() >= target_price
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'absolute_return': absolute_return,
                'percentage_return': percentage_return,
                'max_favorable_excursion': max_favorable,
                'max_adverse_excursion': max_adverse,
                'target_reached': target_reached,
                'holding_days': exit_idx - entry_idx,
                'success': percentage_return > 0,
                'strategy_type': 'mean_reversion'
            }
            
        except Exception as e:
            logger.error(f"Error in mean reversion backtesting: {str(e)}")
            return {}
    
    def calculate_support_resistance(self, data: pd.DataFrame, window: int = 10) -> Dict:
        """
        Calculate support and resistance levels for mean reversion analysis
        
        Args:
            data: Price data
            window: Window for local min/max calculation
        
        Returns:
            Dictionary with support and resistance levels
        """
        try:
            if len(data) < window * 2:
                return {}
            
            # Calculate local minima (support) and maxima (resistance)
            highs = data['high'].rolling(window=window, center=True).max()
            lows = data['low'].rolling(window=window, center=True).min()
            
            # Find recent support and resistance levels
            recent_data = data.tail(50)  # Last 50 days
            
            resistance_levels = recent_data[recent_data['high'] == highs]['high'].unique()
            support_levels = recent_data[recent_data['low'] == lows]['low'].unique()
            
            # Sort and get most relevant levels
            resistance_levels = sorted(resistance_levels, reverse=True)[:3]
            support_levels = sorted(support_levels)[-3:]
            
            return {
                'resistance_levels': resistance_levels.tolist() if hasattr(resistance_levels, 'tolist') else list(resistance_levels),
                'support_levels': support_levels.tolist() if hasattr(support_levels, 'tolist') else list(support_levels),
                'current_price': data.iloc[-1]['close']
            }
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {str(e)}")
            return {}
