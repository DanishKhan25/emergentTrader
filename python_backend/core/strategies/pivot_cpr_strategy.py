"""
Pivot CPR (Central Pivot Range) Strategy - Uses pivot points for support/resistance trading
Focuses on stocks showing clear reactions at pivot levels with volume confirmation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PivotCPRStrategy:
    def __init__(self, name: str = "Pivot CPR"):
        self.name = name
        self.pivot_period = 1  # Daily pivots (can be weekly/monthly)
        self.cpr_width_threshold = 0.02  # 2% maximum CPR width for narrow range
        self.breakout_threshold = 0.005  # 0.5% breakout confirmation
        self.volume_surge_threshold = 1.5  # 1.5x volume surge for confirmation
        self.pivot_reaction_threshold = 0.01  # 1% reaction at pivot levels
        self.max_distance_from_pivot = 0.03  # 3% maximum distance from pivot
        self.trend_confirmation_period = 5  # Days for trend confirmation
        
    def calculate_pivot_points(self, data: pd.DataFrame) -> Dict:
        """
        Calculate pivot points and CPR (Central Pivot Range)
        
        Args:
            data: Historical OHLC data
        
        Returns:
            Dictionary with pivot levels
        """
        try:
            if len(data) < 2:
                return {}
            
            # Get previous day's data for pivot calculation
            prev_day = data.iloc[-2]
            current_day = data.iloc[-1]
            
            high = prev_day['high']
            low = prev_day['low']
            close = prev_day['close']
            
            # Standard Pivot Points
            pivot = (high + low + close) / 3
            
            # Support and Resistance levels
            r1 = (2 * pivot) - low
            s1 = (2 * pivot) - high
            r2 = pivot + (high - low)
            s2 = pivot - (high - low)
            r3 = high + 2 * (pivot - low)
            s3 = low - 2 * (high - pivot)
            
            # CPR (Central Pivot Range) - Camarilla levels
            tc = (high - low) * 1.1 / 12
            cpr_top = close + tc  # Top Central Pivot
            cpr_bottom = close - tc  # Bottom Central Pivot
            cpr_pivot = (cpr_top + cpr_bottom) / 2
            
            # CPR width (narrower CPR indicates potential breakout)
            cpr_width = (cpr_top - cpr_bottom) / cpr_pivot if cpr_pivot > 0 else 0
            
            # Current price position relative to pivots
            current_price = current_day['close']
            
            # Determine position relative to CPR
            if current_price > cpr_top:
                cpr_position = 'ABOVE_CPR'
            elif current_price < cpr_bottom:
                cpr_position = 'BELOW_CPR'
            else:
                cpr_position = 'INSIDE_CPR'
            
            # Distance from key levels
            distances = {
                'from_pivot': abs(current_price - pivot) / pivot,
                'from_cpr_top': abs(current_price - cpr_top) / current_price,
                'from_cpr_bottom': abs(current_price - cpr_bottom) / current_price,
                'from_r1': abs(current_price - r1) / current_price,
                'from_s1': abs(current_price - s1) / current_price
            }
            
            return {
                'pivot': pivot,
                'r1': r1, 'r2': r2, 'r3': r3,
                's1': s1, 's2': s2, 's3': s3,
                'cpr_top': cpr_top,
                'cpr_bottom': cpr_bottom,
                'cpr_pivot': cpr_pivot,
                'cpr_width': cpr_width,
                'cpr_position': cpr_position,
                'distances': distances,
                'is_narrow_cpr': cpr_width <= self.cpr_width_threshold,
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"Error calculating pivot points: {str(e)}")
            return {}
    
    def analyze_pivot_reactions(self, data: pd.DataFrame, pivot_levels: Dict) -> Dict:
        """
        Analyze how price reacts at pivot levels
        
        Args:
            data: Historical price data
            pivot_levels: Calculated pivot levels
        
        Returns:
            Pivot reaction analysis
        """
        try:
            if len(data) < 10 or not pivot_levels:
                return {}
            
            recent_data = data.tail(10)  # Last 10 days
            reactions = []
            
            # Key levels to check for reactions
            key_levels = {
                'pivot': pivot_levels['pivot'],
                'r1': pivot_levels['r1'],
                's1': pivot_levels['s1'],
                'cpr_top': pivot_levels['cpr_top'],
                'cpr_bottom': pivot_levels['cpr_bottom']
            }
            
            # Check for reactions at each level
            for level_name, level_price in key_levels.items():
                level_reactions = []
                
                for i in range(1, len(recent_data)):
                    current = recent_data.iloc[i]
                    previous = recent_data.iloc[i-1]
                    
                    # Check if price approached the level
                    current_distance = abs(current['close'] - level_price) / level_price
                    previous_distance = abs(previous['close'] - level_price) / level_price
                    
                    # If price got close to level (within 1%)
                    if current_distance <= self.pivot_reaction_threshold:
                        # Check for reaction (reversal or bounce)
                        if i < len(recent_data) - 1:
                            next_day = recent_data.iloc[i+1]
                            
                            # Bullish reaction at support
                            if (current['close'] <= level_price and 
                                next_day['close'] > current['close'] and
                                next_day['close'] > level_price):
                                level_reactions.append({
                                    'type': 'BULLISH_BOUNCE',
                                    'strength': (next_day['close'] - current['close']) / current['close'],
                                    'volume_ratio': current.get('volume', 0) / recent_data['volume'].mean() if 'volume' in recent_data.columns else 1
                                })
                            
                            # Bearish reaction at resistance
                            elif (current['close'] >= level_price and 
                                  next_day['close'] < current['close'] and
                                  next_day['close'] < level_price):
                                level_reactions.append({
                                    'type': 'BEARISH_REJECTION',
                                    'strength': (current['close'] - next_day['close']) / current['close'],
                                    'volume_ratio': current.get('volume', 0) / recent_data['volume'].mean() if 'volume' in recent_data.columns else 1
                                })
                
                if level_reactions:
                    reactions.append({
                        'level': level_name,
                        'level_price': level_price,
                        'reactions': level_reactions,
                        'reaction_count': len(level_reactions),
                        'avg_strength': np.mean([r['strength'] for r in level_reactions]),
                        'avg_volume': np.mean([r['volume_ratio'] for r in level_reactions])
                    })
            
            # Overall reaction quality
            total_reactions = sum(r['reaction_count'] for r in reactions)
            strong_reactions = sum(1 for r in reactions for reaction in r['reactions'] if reaction['strength'] > 0.01)
            
            return {
                'reactions': reactions,
                'total_reactions': total_reactions,
                'strong_reactions': strong_reactions,
                'reaction_quality': strong_reactions / max(total_reactions, 1),
                'has_strong_reactions': strong_reactions >= 2
            }
            
        except Exception as e:
            logger.error(f"Error analyzing pivot reactions: {str(e)}")
            return {}
    
    def identify_pivot_setups(self, data: pd.DataFrame, pivot_levels: Dict, reactions: Dict) -> Dict:
        """
        Identify trading setups based on pivot levels
        
        Args:
            data: Price data
            pivot_levels: Pivot levels
            reactions: Pivot reaction analysis
        
        Returns:
            Trading setup identification
        """
        try:
            if not pivot_levels or len(data) < 5:
                return {}
            
            latest = data.iloc[-1]
            current_price = latest['close']
            current_volume = latest.get('volume', 0)
            
            # Average volume for comparison
            avg_volume = data.tail(20)['volume'].mean() if 'volume' in data.columns else 1
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            setups = []
            
            # Setup 1: CPR Breakout
            if pivot_levels.get('is_narrow_cpr', False):
                cpr_position = pivot_levels.get('cpr_position', '')
                
                if cpr_position == 'ABOVE_CPR' and volume_ratio > self.volume_surge_threshold:
                    setups.append({
                        'type': 'CPR_BULLISH_BREAKOUT',
                        'entry_level': pivot_levels['cpr_top'],
                        'target_level': pivot_levels['r1'],
                        'stop_level': pivot_levels['cpr_bottom'],
                        'strength': volume_ratio,
                        'description': 'Bullish breakout above narrow CPR'
                    })
                
                elif cpr_position == 'BELOW_CPR' and volume_ratio > self.volume_surge_threshold:
                    setups.append({
                        'type': 'CPR_BEARISH_BREAKDOWN',
                        'entry_level': pivot_levels['cpr_bottom'],
                        'target_level': pivot_levels['s1'],
                        'stop_level': pivot_levels['cpr_top'],
                        'strength': volume_ratio,
                        'description': 'Bearish breakdown below narrow CPR'
                    })
            
            # Setup 2: Pivot Bounce
            distances = pivot_levels.get('distances', {})
            
            # Bullish bounce at support levels
            if (distances.get('from_s1', 1) <= self.pivot_reaction_threshold and
                current_price > pivot_levels['s1'] and
                volume_ratio > 1.2):
                setups.append({
                    'type': 'PIVOT_SUPPORT_BOUNCE',
                    'entry_level': current_price,
                    'target_level': pivot_levels['pivot'],
                    'stop_level': pivot_levels['s1'] * 0.99,
                    'strength': volume_ratio,
                    'description': 'Bullish bounce from S1 support'
                })
            
            # Bearish rejection at resistance levels
            if (distances.get('from_r1', 1) <= self.pivot_reaction_threshold and
                current_price < pivot_levels['r1'] and
                volume_ratio > 1.2):
                setups.append({
                    'type': 'PIVOT_RESISTANCE_REJECTION',
                    'entry_level': current_price,
                    'target_level': pivot_levels['pivot'],
                    'stop_level': pivot_levels['r1'] * 1.01,
                    'strength': volume_ratio,
                    'description': 'Bearish rejection from R1 resistance'
                })
            
            # Setup 3: Pivot Breakout
            if (current_price > pivot_levels['r1'] * (1 + self.breakout_threshold) and
                volume_ratio > self.volume_surge_threshold):
                setups.append({
                    'type': 'RESISTANCE_BREAKOUT',
                    'entry_level': current_price,
                    'target_level': pivot_levels['r2'],
                    'stop_level': pivot_levels['r1'],
                    'strength': volume_ratio,
                    'description': 'Bullish breakout above R1 resistance'
                })
            
            elif (current_price < pivot_levels['s1'] * (1 - self.breakout_threshold) and
                  volume_ratio > self.volume_surge_threshold):
                setups.append({
                    'type': 'SUPPORT_BREAKDOWN',
                    'entry_level': current_price,
                    'target_level': pivot_levels['s2'],
                    'stop_level': pivot_levels['s1'],
                    'strength': volume_ratio,
                    'description': 'Bearish breakdown below S1 support'
                })
            
            # Rank setups by strength
            setups.sort(key=lambda x: x['strength'], reverse=True)
            
            return {
                'setups': setups,
                'best_setup': setups[0] if setups else None,
                'setup_count': len(setups),
                'has_valid_setup': len(setups) > 0
            }
            
        except Exception as e:
            logger.error(f"Error identifying pivot setups: {str(e)}")
            return {}
    
    def calculate_pivot_score(self, data: pd.DataFrame) -> float:
        """
        Calculate overall pivot CPR strategy score
        
        Args:
            data: Price data with technical indicators
        
        Returns:
            Pivot score (higher indicates better pivot opportunity)
        """
        try:
            if len(data) < 10:
                return 0
            
            # Calculate pivot components
            pivot_levels = self.calculate_pivot_points(data)
            reactions = self.analyze_pivot_reactions(data, pivot_levels)
            setups = self.identify_pivot_setups(data, pivot_levels, reactions)
            
            if not all([pivot_levels, reactions, setups]):
                return 0
            
            score = 0
            
            # 1. Setup quality (40% weight)
            if setups.get('has_valid_setup', False):
                best_setup = setups.get('best_setup', {})
                setup_strength = best_setup.get('strength', 0)
                score += min(setup_strength * 2, 4) * 0.4
            
            # 2. CPR characteristics (25% weight)
            if pivot_levels.get('is_narrow_cpr', False):
                score += 2.5 * 0.25  # Narrow CPR is good for breakouts
            
            cpr_width = pivot_levels.get('cpr_width', 0.1)
            cpr_score = max(0, (self.cpr_width_threshold - cpr_width) / self.cpr_width_threshold * 2)
            score += cpr_score * 0.25
            
            # 3. Historical reactions (20% weight)
            reaction_quality = reactions.get('reaction_quality', 0)
            strong_reactions = reactions.get('strong_reactions', 0)
            reaction_score = (reaction_quality * 1.5 + min(strong_reactions / 3, 1) * 0.5)
            score += reaction_score * 0.2
            
            # 4. Price position (15% weight)
            distances = pivot_levels.get('distances', {})
            # Reward being near key levels
            min_distance = min(distances.values()) if distances else 1
            position_score = max(0, (self.max_distance_from_pivot - min_distance) / self.max_distance_from_pivot * 1.5)
            score += position_score * 0.15
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating pivot score: {str(e)}")
            return 0
    
    def generate_signal(self, symbol: str, data: pd.DataFrame, stock_info: Dict) -> Optional[Dict]:
        """
        Generate pivot CPR signal
        
        Args:
            symbol: Stock symbol
            data: Historical price data with indicators
            stock_info: Fundamental stock information
        
        Returns:
            Signal dictionary or None if no signal
        """
        if data.empty or len(data) < 10:
            return None
        
        try:
            latest = data.iloc[-1]
            current_price = latest['close']
            pivot_score = self.calculate_pivot_score(data)
            
            # Get pivot analysis components
            pivot_levels = self.calculate_pivot_points(data)
            reactions = self.analyze_pivot_reactions(data, pivot_levels)
            setups = self.identify_pivot_setups(data, pivot_levels, reactions)
            
            # Pivot signal criteria
            if (pivot_score > 2.0 and 
                setups.get('has_valid_setup', False) and
                pivot_levels.get('is_narrow_cpr', False)):
                
                best_setup = setups.get('best_setup', {})
                setup_type = best_setup.get('type', '')
                
                # Generate signal based on setup type
                if 'BULLISH' in setup_type or 'BOUNCE' in setup_type or 'BREAKOUT' in setup_type:
                    signal_type = 'BUY'
                    entry_price = current_price
                    target_price = best_setup.get('target_level', current_price * 1.02)
                    stop_loss = best_setup.get('stop_level', current_price * 0.98)
                    
                elif 'BEARISH' in setup_type or 'REJECTION' in setup_type or 'BREAKDOWN' in setup_type:
                    signal_type = 'SELL'
                    entry_price = current_price
                    target_price = best_setup.get('target_level', current_price * 0.98)
                    stop_loss = best_setup.get('stop_level', current_price * 1.02)
                    
                else:
                    return None
                
                # Ensure reasonable risk-reward for BUY signals
                if signal_type == 'BUY':
                    risk_reward = (target_price - entry_price) / (entry_price - stop_loss)
                    if risk_reward < 1.2:  # Minimum 1.2:1 ratio
                        return None
                    
                    # Position sizing
                    risk_amount = 10000 * 0.01  # 1% risk for pivot trades
                    risk_per_share = entry_price - stop_loss
                    position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 100
                    
                    signal = {
                        'signal_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'symbol': symbol,
                        'strategy': self.name,
                        'signal_type': signal_type,
                        'entry_price': round(entry_price, 2),
                        'target_price': round(target_price, 2),
                        'stop_loss': round(stop_loss, 2),
                        'quantity': position_size,
                        'pivot_score': round(pivot_score, 2),
                        
                        # Pivot levels
                        'pivot_point': round(pivot_levels['pivot'], 2),
                        'r1': round(pivot_levels['r1'], 2),
                        's1': round(pivot_levels['s1'], 2),
                        'cpr_top': round(pivot_levels['cpr_top'], 2),
                        'cpr_bottom': round(pivot_levels['cpr_bottom'], 2),
                        'cpr_width': round(pivot_levels['cpr_width'] * 100, 2),
                        'cpr_position': pivot_levels['cpr_position'],
                        
                        # Setup details
                        'setup_type': setup_type,
                        'setup_strength': round(best_setup.get('strength', 0), 2),
                        'setup_description': best_setup.get('description', ''),
                        
                        # Reaction analysis
                        'total_reactions': reactions.get('total_reactions', 0),
                        'strong_reactions': reactions.get('strong_reactions', 0),
                        'reaction_quality': round(reactions.get('reaction_quality', 0), 2),
                        
                        'timestamp': datetime.now().isoformat(),
                        'risk_reward_ratio': round((target_price - entry_price) / (entry_price - stop_loss), 2),
                        'sector': stock_info.get('sector', ''),
                        'market_cap': stock_info.get('market_cap', 0),
                        'confidence_score': min(pivot_score / 4, 1.0),  # Normalize to 0-1
                        'validity_days': 3,  # Pivot signals are short-term (3 days)
                        'strategy_reason': f'Pivot {setup_type.lower().replace("_", " ")} setup',
                        'holding_period': '1-5 days'
                    }
                    
                    logger.info(f"Generated PIVOT CPR signal for {symbol} - {setup_type} - Score: {pivot_score}")
                    return signal
                
                # For SELL signals, return basic signal structure
                elif signal_type == 'SELL':
                    signal = {
                        'signal_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'symbol': symbol,
                        'strategy': self.name,
                        'signal_type': signal_type,
                        'entry_price': entry_price,
                        'target_price': round(target_price, 2),
                        'stop_loss': round(stop_loss, 2),
                        'pivot_score': round(pivot_score, 2),
                        'setup_type': setup_type,
                        'setup_description': best_setup.get('description', ''),
                        'timestamp': datetime.now().isoformat(),
                        'reason': f'Pivot {setup_type.lower().replace("_", " ")} setup',
                        'confidence_score': min(pivot_score / 4, 1.0),
                        'validity_days': 3,
                        'strategy_reason': f'Pivot {setup_type.lower().replace("_", " ")} setup',
                        'holding_period': '1-5 days'
                    }
                    
                    logger.info(f"Generated PIVOT CPR SELL signal for {symbol} - {setup_type} - Score: {pivot_score}")
                    return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating pivot CPR signal for {symbol}: {str(e)}")
            return None
    
    def get_strategy_params(self) -> Dict:
        """Return strategy parameters for configuration"""
        return {
            'name': self.name,
            'pivot_period': self.pivot_period,
            'cpr_width_threshold': self.cpr_width_threshold,
            'breakout_threshold': self.breakout_threshold,
            'volume_surge_threshold': self.volume_surge_threshold,
            'pivot_reaction_threshold': self.pivot_reaction_threshold,
            'max_distance_from_pivot': self.max_distance_from_pivot,
            'trend_confirmation_period': self.trend_confirmation_period
        }
    
    def backtest_signal(self, data: pd.DataFrame, entry_date: str, exit_days: int = 3) -> Dict:
        """
        Backtest a pivot CPR signal (short holding period)
        
        Args:
            data: Historical price data
            entry_date: Date when signal was generated
            exit_days: Number of days to hold (3 days default for pivot trades)
        
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
            
            # Pivot-specific metrics
            holding_data = data.iloc[entry_idx:exit_idx + 1]
            
            # Check if pivot levels were respected
            pivot_levels = self.calculate_pivot_points(data.iloc[:entry_idx])
            if pivot_levels:
                # Track how price behaved relative to pivot levels
                pivot_respect = 0
                for _, row in holding_data.iterrows():
                    price = row['close']
                    # Check if price respected key levels
                    if (pivot_levels['s1'] <= price <= pivot_levels['r1']):
                        pivot_respect += 1
                
                pivot_respect_ratio = pivot_respect / len(holding_data) if len(holding_data) > 0 else 0
            else:
                pivot_respect_ratio = 0
            
            # Maximum favorable and adverse excursions
            max_favorable = ((holding_data['high'].max() - entry_price) / entry_price) * 100
            max_adverse = ((holding_data['low'].min() - entry_price) / entry_price) * 100
            
            # Quick profit achievement (did it reach target quickly?)
            target_achieved_day = None
            if percentage_return > 1:  # If profitable
                for i, (_, row) in enumerate(holding_data.iterrows()):
                    if ((row['high'] - entry_price) / entry_price) >= 0.01:  # 1% target
                        target_achieved_day = i
                        break
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'absolute_return': absolute_return,
                'percentage_return': percentage_return,
                'max_favorable_excursion': max_favorable,
                'max_adverse_excursion': max_adverse,
                'pivot_respect_ratio': pivot_respect_ratio,
                'target_achieved_day': target_achieved_day,
                'quick_profit': target_achieved_day is not None and target_achieved_day <= 1,
                'holding_days': exit_idx - entry_idx,
                'success': percentage_return > 0,
                'strong_pivot_move': abs(percentage_return) > 2,  # 2%+ move
                'strategy_type': 'pivot_cpr'
            }
            
        except Exception as e:
            logger.error(f"Error in pivot CPR backtesting: {str(e)}")
            return {}
