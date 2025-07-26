"""
Swing Trading Strategy - Identifies medium-term price swings (3-10 days)
Focuses on stocks with strong directional moves after consolidation periods
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SwingTradingStrategy:
    def __init__(self, name: str = "Swing Trading"):
        self.name = name
        self.swing_period = 5  # Days to identify swing highs/lows
        self.trend_period = 20  # Days for trend analysis
        self.volume_threshold = 1.3  # Minimum volume surge
        self.rsi_oversold = 35  # RSI oversold for swing lows
        self.rsi_overbought = 65  # RSI overbought for swing highs
        self.min_swing_range = 0.03  # Minimum 3% swing range
        self.max_swing_range = 0.20  # Maximum 20% swing range
        self.trend_strength_threshold = 0.05  # 5% trend strength
        
    def identify_swing_points(self, data: pd.DataFrame) -> Dict:
        """
        Identify swing highs and lows in price data
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            Dictionary with swing points information
        """
        if len(data) < self.swing_period * 2:
            return {}
        
        try:
            # Calculate rolling highs and lows
            rolling_high = data['high'].rolling(window=self.swing_period, center=True).max()
            rolling_low = data['low'].rolling(window=self.swing_period, center=True).min()
            
            # Identify swing highs (local maxima)
            swing_highs = []
            swing_lows = []
            
            for i in range(self.swing_period, len(data) - self.swing_period):
                current_high = data.iloc[i]['high']
                current_low = data.iloc[i]['low']
                
                # Check if current point is a swing high
                if current_high == rolling_high.iloc[i]:
                    # Verify it's a true peak (higher than surrounding points)
                    left_max = data.iloc[i-self.swing_period:i]['high'].max()
                    right_max = data.iloc[i+1:i+self.swing_period+1]['high'].max()
                    
                    if current_high > left_max and current_high > right_max:
                        swing_highs.append({
                            'index': i,
                            'date': data.iloc[i]['date'] if 'date' in data.columns else i,
                            'price': current_high,
                            'volume': data.iloc[i]['volume']
                        })
                
                # Check if current point is a swing low
                if current_low == rolling_low.iloc[i]:
                    # Verify it's a true trough (lower than surrounding points)
                    left_min = data.iloc[i-self.swing_period:i]['low'].min()
                    right_min = data.iloc[i+1:i+self.swing_period+1]['low'].min()
                    
                    if current_low < left_min and current_low < right_min:
                        swing_lows.append({
                            'index': i,
                            'date': data.iloc[i]['date'] if 'date' in data.columns else i,
                            'price': current_low,
                            'volume': data.iloc[i]['volume']
                        })
            
            # Get most recent swing points
            recent_swing_high = swing_highs[-1] if swing_highs else None
            recent_swing_low = swing_lows[-1] if swing_lows else None
            
            return {
                'swing_highs': swing_highs[-5:],  # Last 5 swing highs
                'swing_lows': swing_lows[-5:],   # Last 5 swing lows
                'recent_swing_high': recent_swing_high,
                'recent_swing_low': recent_swing_low,
                'total_swings': len(swing_highs) + len(swing_lows)
            }
            
        except Exception as e:
            logger.error(f"Error identifying swing points: {str(e)}")
            return {}
    
    def analyze_trend_context(self, data: pd.DataFrame) -> Dict:
        """
        Analyze the broader trend context for swing trading
        
        Args:
            data: Price data with technical indicators
        
        Returns:
            Trend analysis results
        """
        try:
            if len(data) < self.trend_period:
                return {}
            
            latest = data.iloc[-1]
            trend_data = data.tail(self.trend_period)
            
            # Moving average trend analysis
            sma_20 = latest.get('sma_20', 0)
            sma_50 = latest.get('sma_50', 0)
            current_price = latest['close']
            
            # Trend direction
            if sma_20 > sma_50 and current_price > sma_20:
                trend_direction = 'UPTREND'
                trend_strength = ((current_price - sma_50) / sma_50) if sma_50 > 0 else 0
            elif sma_20 < sma_50 and current_price < sma_20:
                trend_direction = 'DOWNTREND'  
                trend_strength = ((sma_50 - current_price) / sma_50) if sma_50 > 0 else 0
            else:
                trend_direction = 'SIDEWAYS'
                trend_strength = 0
            
            # Price position relative to recent range
            recent_high = trend_data['high'].max()
            recent_low = trend_data['low'].min()
            price_position = (current_price - recent_low) / (recent_high - recent_low) if recent_high > recent_low else 0.5
            
            # Volume trend
            recent_volume = trend_data['volume'].tail(5).mean() if 'volume' in trend_data.columns else 0
            avg_volume = trend_data['volume'].mean() if 'volume' in trend_data.columns else 1
            volume_trend = recent_volume / avg_volume if avg_volume > 0 else 1
            
            return {
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'price_position': price_position,  # 0 = at low, 1 = at high
                'volume_trend': volume_trend,
                'recent_high': recent_high,
                'recent_low': recent_low,
                'range_size': (recent_high - recent_low) / recent_low if recent_low > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trend context: {str(e)}")
            return {}
    
    def calculate_swing_score(self, data: pd.DataFrame) -> float:
        """
        Calculate swing trading score based on swing points and trend context
        
        Args:
            data: DataFrame with OHLCV and technical indicators
        
        Returns:
            Swing trading score (higher indicates better swing opportunity)
        """
        try:
            if len(data) < self.trend_period:
                return 0
            
            latest = data.iloc[-1]
            current_price = latest['close']
            rsi = latest.get('rsi', 50)
            
            # Get swing points and trend context
            swing_points = self.identify_swing_points(data)
            trend_context = self.analyze_trend_context(data)
            
            if not swing_points or not trend_context:
                return 0
            
            # Score components
            score = 0
            
            # 1. Swing setup score (40% weight)
            recent_swing_low = swing_points.get('recent_swing_low')
            recent_swing_high = swing_points.get('recent_swing_high')
            
            if recent_swing_low and recent_swing_high:
                # Check for swing low in uptrend (bullish setup)
                if (trend_context['trend_direction'] == 'UPTREND' and 
                    recent_swing_low['index'] > recent_swing_high['index'] and
                    rsi <= self.rsi_oversold):
                    
                    swing_range = (recent_swing_high['price'] - recent_swing_low['price']) / recent_swing_low['price']
                    if self.min_swing_range <= swing_range <= self.max_swing_range:
                        score += 4 * (swing_range / self.max_swing_range)  # Reward good swing range
                
                # Check for swing high in downtrend (bearish setup)
                elif (trend_context['trend_direction'] == 'DOWNTREND' and 
                      recent_swing_high['index'] > recent_swing_low['index'] and
                      rsi >= self.rsi_overbought):
                    
                    swing_range = (recent_swing_high['price'] - recent_swing_low['price']) / recent_swing_low['price']
                    if self.min_swing_range <= swing_range <= self.max_swing_range:
                        score -= 4 * (swing_range / self.max_swing_range)  # Negative for short setup
            
            # 2. Trend strength score (25% weight)
            if trend_context['trend_strength'] >= self.trend_strength_threshold:
                trend_score = min(trend_context['trend_strength'] * 10, 2.5)
                if trend_context['trend_direction'] == 'UPTREND':
                    score += trend_score
                else:
                    score -= trend_score
            
            # 3. Price position score (20% weight)
            price_pos = trend_context['price_position']
            if trend_context['trend_direction'] == 'UPTREND':
                # Reward buying near swing lows (lower price position)
                score += (1 - price_pos) * 2
            elif trend_context['trend_direction'] == 'DOWNTREND':
                # Reward selling near swing highs (higher price position)
                score -= price_pos * 2
            
            # 4. Volume confirmation score (15% weight)
            volume_score = min(trend_context['volume_trend'], 2.0) - 1  # -1 to +1 range
            score += volume_score * 1.5
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating swing score: {str(e)}")
            return 0
    
    def generate_signal(self, symbol: str, data: pd.DataFrame, stock_info: Dict) -> Optional[Dict]:
        """
        Generate swing trading signal
        
        Args:
            symbol: Stock symbol
            data: Historical price data with indicators
            stock_info: Fundamental stock information
        
        Returns:
            Signal dictionary or None if no signal
        """
        if data.empty or len(data) < self.trend_period:
            return None
        
        try:
            latest = data.iloc[-1]
            current_price = latest['close']
            swing_score = self.calculate_swing_score(data)
            
            # Get analysis components
            swing_points = self.identify_swing_points(data)
            trend_context = self.analyze_trend_context(data)
            
            if not swing_points or not trend_context:
                return None
            
            # BUY Signal: Bullish swing setup
            if (swing_score > 2.0 and 
                trend_context['trend_direction'] == 'UPTREND' and
                trend_context['price_position'] < 0.4):  # Near swing low
                
                # Calculate entry, target, and stop loss
                recent_swing_low = swing_points.get('recent_swing_low')
                recent_swing_high = swing_points.get('recent_swing_high')
                
                if recent_swing_low and recent_swing_high:
                    entry_price = current_price
                    stop_loss = recent_swing_low['price'] * 0.98  # 2% below swing low
                    
                    # Target based on swing range projection
                    swing_range = recent_swing_high['price'] - recent_swing_low['price']
                    target_price = entry_price + (swing_range * 1.2)  # 120% of swing range
                    
                    # Risk-reward validation
                    risk_reward = (target_price - entry_price) / (entry_price - stop_loss)
                    if risk_reward < 1.5:  # Minimum 1.5:1 ratio
                        return None
                    
                    # Position sizing
                    risk_amount = 10000 * 0.015  # 1.5% risk for swing trades
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
                        'swing_score': round(swing_score, 2),
                        'trend_direction': trend_context['trend_direction'],
                        'trend_strength': round(trend_context['trend_strength'] * 100, 2),
                        'price_position': round(trend_context['price_position'] * 100, 2),
                        'swing_low_price': round(recent_swing_low['price'], 2),
                        'swing_high_price': round(recent_swing_high['price'], 2),
                        'volume_confirmation': trend_context['volume_trend'] > self.volume_threshold,
                        'rsi': round(latest.get('rsi', 50), 2),
                        'timestamp': datetime.now().isoformat(),
                        'risk_reward_ratio': round(risk_reward, 2),
                        'sector': stock_info.get('sector', ''),
                        'market_cap': stock_info.get('market_cap', 0),
                        'confidence_score': min(swing_score / 5, 1.0),
                        'validity_days': 7,  # Swing trades valid for a week
                        'strategy_reason': f'Bullish swing setup in {trend_context["trend_direction"].lower()}',
                        'holding_period': '3-10 days'
                    }
                    
                    logger.info(f"Generated SWING BUY signal for {symbol} - Score: {swing_score}")
                    return signal
            
            # SELL Signal: Bearish swing setup
            elif (swing_score < -2.0 and 
                  trend_context['trend_direction'] == 'DOWNTREND' and
                  trend_context['price_position'] > 0.6):  # Near swing high
                
                recent_swing_high = swing_points.get('recent_swing_high')
                recent_swing_low = swing_points.get('recent_swing_low')
                
                if recent_swing_high and recent_swing_low:
                    signal = {
                        'signal_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'symbol': symbol,
                        'strategy': self.name,
                        'signal_type': 'SELL',
                        'entry_price': current_price,
                        'target_price': round(recent_swing_low['price'] * 0.95, 2),
                        'stop_loss': round(recent_swing_high['price'] * 1.02, 2),
                        'swing_score': round(swing_score, 2),
                        'trend_direction': trend_context['trend_direction'],
                        'swing_high_price': round(recent_swing_high['price'], 2),
                        'swing_low_price': round(recent_swing_low['price'], 2),
                        'timestamp': datetime.now().isoformat(),
                        'reason': f'Bearish swing setup in {trend_context["trend_direction"].lower()}',
                        'confidence_score': min(abs(swing_score) / 5, 1.0),
                        'validity_days': 7,
                        'strategy_reason': f'Bearish swing setup in {trend_context["trend_direction"].lower()}',
                        'holding_period': '3-10 days'
                    }
                    
                    logger.info(f"Generated SWING SELL signal for {symbol} - Score: {swing_score}")
                    return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating swing signal for {symbol}: {str(e)}")
            return None
    
    def get_strategy_params(self) -> Dict:
        """Return strategy parameters for configuration"""
        return {
            'name': self.name,
            'swing_period': self.swing_period,
            'trend_period': self.trend_period,
            'volume_threshold': self.volume_threshold,
            'rsi_oversold': self.rsi_oversold,
            'rsi_overbought': self.rsi_overbought,
            'min_swing_range': self.min_swing_range,
            'max_swing_range': self.max_swing_range,
            'trend_strength_threshold': self.trend_strength_threshold
        }
    
    def backtest_signal(self, data: pd.DataFrame, entry_date: str, exit_days: int = 7) -> Dict:
        """
        Backtest a swing trading signal
        
        Args:
            data: Historical price data
            entry_date: Date when signal was generated
            exit_days: Number of days to hold position (typical swing trade duration)
        
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
            
            # Track swing trading specific metrics
            holding_data = data.iloc[entry_idx:exit_idx + 1]
            
            # Maximum favorable excursion (best point during swing)
            max_favorable = ((holding_data['high'].max() - entry_price) / entry_price) * 100
            max_adverse = ((holding_data['low'].min() - entry_price) / entry_price) * 100
            
            # Check if swing target was reached
            swing_points = self.identify_swing_points(data.iloc[:entry_idx])
            target_reached = False
            if swing_points and swing_points.get('recent_swing_high'):
                swing_range = swing_points['recent_swing_high']['price'] - swing_points.get('recent_swing_low', {}).get('price', 0)
                target_price = entry_price + (swing_range * 1.2)
                target_reached = holding_data['high'].max() >= target_price
            
            # Swing efficiency (how much of the available swing was captured)
            available_swing = max_favorable - max_adverse
            captured_swing = percentage_return - max_adverse if percentage_return > max_adverse else 0
            swing_efficiency = (captured_swing / available_swing * 100) if available_swing > 0 else 0
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'absolute_return': absolute_return,
                'percentage_return': percentage_return,
                'max_favorable_excursion': max_favorable,
                'max_adverse_excursion': max_adverse,
                'swing_efficiency': swing_efficiency,
                'target_reached': target_reached,
                'holding_days': exit_idx - entry_idx,
                'success': percentage_return > 0,
                'strong_swing': percentage_return > 5,  # 5%+ considered strong swing
                'strategy_type': 'swing_trading'
            }
            
        except Exception as e:
            logger.error(f"Error in swing trading backtesting: {str(e)}")
            return {}
    
    def analyze_swing_patterns(self, data: pd.DataFrame) -> Dict:
        """
        Analyze historical swing patterns for strategy optimization
        
        Args:
            data: Historical price data
        
        Returns:
            Swing pattern analysis
        """
        try:
            swing_points = self.identify_swing_points(data)
            if not swing_points:
                return {}
            
            swing_highs = swing_points.get('swing_highs', [])
            swing_lows = swing_points.get('swing_lows', [])
            
            # Calculate average swing ranges
            swing_ranges = []
            for i in range(min(len(swing_highs), len(swing_lows))):
                if swing_highs[i] and swing_lows[i]:
                    swing_range = (swing_highs[i]['price'] - swing_lows[i]['price']) / swing_lows[i]['price']
                    swing_ranges.append(swing_range)
            
            # Calculate swing timing
            swing_durations = []
            all_swings = sorted(swing_highs + swing_lows, key=lambda x: x['index'])
            for i in range(1, len(all_swings)):
                duration = all_swings[i]['index'] - all_swings[i-1]['index']
                swing_durations.append(duration)
            
            return {
                'total_swings': len(swing_highs) + len(swing_lows),
                'avg_swing_range': np.mean(swing_ranges) if swing_ranges else 0,
                'max_swing_range': max(swing_ranges) if swing_ranges else 0,
                'min_swing_range': min(swing_ranges) if swing_ranges else 0,
                'avg_swing_duration': np.mean(swing_durations) if swing_durations else 0,
                'swing_frequency': len(all_swings) / len(data) if len(data) > 0 else 0,
                'recent_swing_activity': len([s for s in all_swings if s['index'] > len(data) - 20])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing swing patterns: {str(e)}")
            return {}
