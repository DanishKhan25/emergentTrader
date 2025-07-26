"""
Optimized Signal Generator - Enhanced signal generation with caching and better parameters
Focuses on generating high-quality trading signals with reduced API calls
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import concurrent.futures
from threading import Lock
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.data_cache import get_cached_signals, set_cached_signals, cache
from services.yfinance_fetcher import YFinanceFetcher

logger = logging.getLogger(__name__)

class OptimizedSignalGenerator:
    def __init__(self, data_fetcher: YFinanceFetcher):
        self.data_fetcher = data_fetcher
        self.cache_lock = Lock()
        
        # Optimized parameters for better signal generation
        self.signal_params = {
            'momentum': {
                'rsi_oversold': 25,      # More aggressive than 30
                'rsi_overbought': 75,    # More aggressive than 70
                'macd_threshold': 0.1,
                'volume_multiplier': 1.2,
                'min_confidence': 0.4
            },
            'mean_reversion': {
                'bb_std_threshold': 2.0,
                'rsi_extreme_low': 20,
                'rsi_extreme_high': 80,
                'price_deviation': 0.05,
                'min_confidence': 0.35
            },
            'breakout': {
                'volume_surge': 2.0,
                'price_breakout': 0.03,
                'consolidation_days': 10,
                'min_confidence': 0.45
            },
            'value_investing': {
                'max_pe': 15,
                'min_roe': 15,
                'max_debt_ratio': 0.3,
                'min_current_ratio': 1.5,
                'min_confidence': 0.5
            }
        }
    
    def generate_optimized_signals(
        self, 
        strategy_name: str, 
        symbols: List[str], 
        min_confidence: float = 0.3,
        max_symbols: int = 50
    ) -> List[Dict]:
        """
        Generate optimized signals with caching and parallel processing
        
        Args:
            strategy_name: Name of the trading strategy
            symbols: List of stock symbols
            min_confidence: Minimum confidence threshold
            max_symbols: Maximum number of symbols to process
            
        Returns:
            List of trading signals
        """
        try:
            # Limit symbols for performance
            symbols = symbols[:max_symbols]
            
            # Check cache first
            cached_signals = get_cached_signals(strategy_name, symbols)
            if cached_signals is not None:
                logger.info(f"Using cached signals for {strategy_name}: {len(cached_signals)} signals")
                return [s for s in cached_signals if s.get('confidence', 0) >= min_confidence]
            
            logger.info(f"Generating {strategy_name} signals for {len(symbols)} symbols")
            
            # Generate signals based on strategy
            if strategy_name == 'momentum':
                signals = self._generate_momentum_signals(symbols)
            elif strategy_name == 'mean_reversion':
                signals = self._generate_mean_reversion_signals(symbols)
            elif strategy_name == 'breakout':
                signals = self._generate_breakout_signals(symbols)
            elif strategy_name == 'value_investing':
                signals = self._generate_value_signals(symbols)
            else:
                logger.warning(f"Unknown strategy: {strategy_name}")
                return []
            
            # Filter by confidence
            filtered_signals = [s for s in signals if s.get('confidence', 0) >= min_confidence]
            
            # Cache the results
            set_cached_signals(strategy_name, symbols, signals)
            
            logger.info(f"Generated {len(filtered_signals)} {strategy_name} signals above {min_confidence} confidence")
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Error generating optimized signals: {str(e)}")
            return []
    
    def _generate_momentum_signals(self, symbols: List[str]) -> List[Dict]:
        """Generate momentum-based signals with optimized parameters"""
        signals = []
        params = self.signal_params['momentum']
        
        # Process symbols in batches to avoid overwhelming the API
        batch_size = 10
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            
            for symbol in batch:
                try:
                    # Get stock data with caching
                    data = self.data_fetcher.get_nse_stock_data(symbol, period="6mo")
                    if data.empty:
                        continue
                    
                    # Calculate technical indicators
                    data = self.data_fetcher.calculate_technical_indicators(data)
                    
                    if len(data) < 50:  # Need enough data for indicators
                        continue
                    
                    latest = data.iloc[-1]
                    prev = data.iloc[-2]
                    
                    # Momentum signal conditions
                    conditions = []
                    confidence_factors = []
                    
                    # RSI momentum
                    if latest['rsi'] > params['rsi_oversold'] and prev['rsi'] <= params['rsi_oversold']:
                        conditions.append("RSI_BULLISH_CROSSOVER")
                        confidence_factors.append(0.3)
                    elif latest['rsi'] < params['rsi_overbought'] and prev['rsi'] >= params['rsi_overbought']:
                        conditions.append("RSI_BEARISH_CROSSOVER")
                        confidence_factors.append(0.3)
                    
                    # MACD momentum
                    if (latest['macd'] > latest['macd_signal'] and 
                        prev['macd'] <= prev['macd_signal'] and
                        latest['macd'] > params['macd_threshold']):
                        conditions.append("MACD_BULLISH_CROSSOVER")
                        confidence_factors.append(0.4)
                    
                    # Volume confirmation
                    if latest['volume_ratio'] > params['volume_multiplier']:
                        conditions.append("VOLUME_SURGE")
                        confidence_factors.append(0.2)
                    
                    # Price momentum
                    price_change = (latest['close'] - prev['close']) / prev['close']
                    if abs(price_change) > 0.02:  # 2% price movement
                        conditions.append("PRICE_MOMENTUM")
                        confidence_factors.append(0.1)
                    
                    # Generate signal if conditions are met
                    if conditions and sum(confidence_factors) >= params['min_confidence']:
                        signal_type = "BUY" if any("BULLISH" in c for c in conditions) else "SELL"
                        
                        signal = {
                            'symbol': symbol,
                            'strategy': 'momentum',
                            'signal': signal_type,
                            'confidence': min(sum(confidence_factors), 1.0),
                            'price': latest['close'],
                            'conditions': conditions,
                            'technical_data': {
                                'rsi': latest['rsi'],
                                'macd': latest['macd'],
                                'volume_ratio': latest['volume_ratio'],
                                'price_change_pct': price_change * 100
                            },
                            'timestamp': datetime.now().isoformat()
                        }
                        signals.append(signal)
                        logger.debug(f"Generated momentum signal for {symbol}: {signal_type}")
                
                except Exception as e:
                    logger.error(f"Error processing {symbol} for momentum: {str(e)}")
                    continue
        
        return signals
    
    def _generate_mean_reversion_signals(self, symbols: List[str]) -> List[Dict]:
        """Generate mean reversion signals"""
        signals = []
        params = self.signal_params['mean_reversion']
        
        for symbol in symbols[:20]:  # Limit for performance
            try:
                data = self.data_fetcher.get_nse_stock_data(symbol, period="3mo")
                if data.empty:
                    continue
                
                data = self.data_fetcher.calculate_technical_indicators(data)
                
                if len(data) < 30:
                    continue
                
                latest = data.iloc[-1]
                
                conditions = []
                confidence_factors = []
                
                # Bollinger Bands mean reversion
                if latest['close'] <= latest['bb_lower']:
                    conditions.append("OVERSOLD_BB")
                    confidence_factors.append(0.4)
                elif latest['close'] >= latest['bb_upper']:
                    conditions.append("OVERBOUGHT_BB")
                    confidence_factors.append(0.4)
                
                # RSI extreme levels
                if latest['rsi'] <= params['rsi_extreme_low']:
                    conditions.append("RSI_OVERSOLD")
                    confidence_factors.append(0.3)
                elif latest['rsi'] >= params['rsi_extreme_high']:
                    conditions.append("RSI_OVERBOUGHT")
                    confidence_factors.append(0.3)
                
                # Price deviation from moving average
                sma_deviation = abs(latest['close'] - latest['sma_20']) / latest['sma_20']
                if sma_deviation > params['price_deviation']:
                    conditions.append("PRICE_DEVIATION")
                    confidence_factors.append(0.2)
                
                if conditions and sum(confidence_factors) >= params['min_confidence']:
                    signal_type = "BUY" if any("OVERSOLD" in c for c in conditions) else "SELL"
                    
                    signal = {
                        'symbol': symbol,
                        'strategy': 'mean_reversion',
                        'signal': signal_type,
                        'confidence': min(sum(confidence_factors), 1.0),
                        'price': latest['close'],
                        'conditions': conditions,
                        'technical_data': {
                            'rsi': latest['rsi'],
                            'bb_position': (latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower']),
                            'sma_deviation_pct': sma_deviation * 100
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    signals.append(signal)
                    logger.debug(f"Generated mean reversion signal for {symbol}: {signal_type}")
            
            except Exception as e:
                logger.error(f"Error processing {symbol} for mean reversion: {str(e)}")
                continue
        
        return signals
    
    def _generate_breakout_signals(self, symbols: List[str]) -> List[Dict]:
        """Generate breakout signals"""
        signals = []
        params = self.signal_params['breakout']
        
        for symbol in symbols[:15]:  # Limit for performance
            try:
                data = self.data_fetcher.get_nse_stock_data(symbol, period="6mo")
                if data.empty:
                    continue
                
                data = self.data_fetcher.calculate_technical_indicators(data)
                
                if len(data) < 50:
                    continue
                
                latest = data.iloc[-1]
                recent_data = data.tail(params['consolidation_days'])
                
                conditions = []
                confidence_factors = []
                
                # Volume breakout
                if latest['volume_ratio'] > params['volume_surge']:
                    conditions.append("VOLUME_BREAKOUT")
                    confidence_factors.append(0.3)
                
                # Price breakout above resistance
                recent_high = recent_data['high'].max()
                if latest['close'] > recent_high * (1 + params['price_breakout']):
                    conditions.append("UPWARD_BREAKOUT")
                    confidence_factors.append(0.4)
                
                # Price breakdown below support
                recent_low = recent_data['low'].min()
                if latest['close'] < recent_low * (1 - params['price_breakout']):
                    conditions.append("DOWNWARD_BREAKOUT")
                    confidence_factors.append(0.4)
                
                # Consolidation before breakout
                price_range = (recent_data['high'].max() - recent_data['low'].min()) / recent_data['close'].mean()
                if price_range < 0.1:  # Tight consolidation
                    conditions.append("CONSOLIDATION")
                    confidence_factors.append(0.2)
                
                if conditions and sum(confidence_factors) >= params['min_confidence']:
                    signal_type = "BUY" if "UPWARD_BREAKOUT" in conditions else "SELL"
                    
                    signal = {
                        'symbol': symbol,
                        'strategy': 'breakout',
                        'signal': signal_type,
                        'confidence': min(sum(confidence_factors), 1.0),
                        'price': latest['close'],
                        'conditions': conditions,
                        'technical_data': {
                            'volume_ratio': latest['volume_ratio'],
                            'price_range_pct': price_range * 100,
                            'recent_high': recent_high,
                            'recent_low': recent_low
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    signals.append(signal)
                    logger.debug(f"Generated breakout signal for {symbol}: {signal_type}")
            
            except Exception as e:
                logger.error(f"Error processing {symbol} for breakout: {str(e)}")
                continue
        
        return signals
    
    def _generate_value_signals(self, symbols: List[str]) -> List[Dict]:
        """Generate value investing signals"""
        signals = []
        params = self.signal_params['value_investing']
        
        for symbol in symbols[:10]:  # Limit for performance
            try:
                # Get fundamental data
                stock_info = self.data_fetcher.get_stock_info(symbol)
                if not stock_info or 'error' in stock_info:
                    continue
                
                conditions = []
                confidence_factors = []
                
                # P/E ratio check
                pe_ratio = stock_info.get('pe_ratio', 0)
                if 0 < pe_ratio <= params['max_pe']:
                    conditions.append("LOW_PE")
                    confidence_factors.append(0.3)
                
                # ROE check
                roe = stock_info.get('roe', 0)
                if roe >= params['min_roe']:
                    conditions.append("HIGH_ROE")
                    confidence_factors.append(0.3)
                
                # Debt ratio check
                debt_ratio = stock_info.get('debt_equity_ratio', 0)
                if debt_ratio <= params['max_debt_ratio']:
                    conditions.append("LOW_DEBT")
                    confidence_factors.append(0.2)
                
                # Current ratio check
                current_ratio = stock_info.get('current_ratio', 0)
                if current_ratio >= params['min_current_ratio']:
                    conditions.append("GOOD_LIQUIDITY")
                    confidence_factors.append(0.2)
                
                if conditions and sum(confidence_factors) >= params['min_confidence']:
                    signal = {
                        'symbol': symbol,
                        'strategy': 'value_investing',
                        'signal': 'BUY',  # Value signals are typically buy signals
                        'confidence': min(sum(confidence_factors), 1.0),
                        'price': stock_info.get('current_price', 0),
                        'conditions': conditions,
                        'fundamental_data': {
                            'pe_ratio': pe_ratio,
                            'roe': roe,
                            'debt_ratio': debt_ratio,
                            'current_ratio': current_ratio,
                            'market_cap': stock_info.get('market_cap', 0)
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    signals.append(signal)
                    logger.debug(f"Generated value signal for {symbol}")
            
            except Exception as e:
                logger.error(f"Error processing {symbol} for value investing: {str(e)}")
                continue
        
        return signals
    
    def get_cache_stats(self) -> Dict:
        """Get caching statistics"""
        return cache.get_cache_stats()
    
    def clear_signal_cache(self) -> int:
        """Clear signal cache"""
        return cache.clear_all('signals')
