"""
Real-time Market Data Service for Market Regime Analysis
Fetches live market data from various sources for accurate regime detection
"""

import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio
import aiohttp
import logging
from services.logging_service import get_logger

logger = get_logger('market_data')

class RealTimeMarketDataService:
    def __init__(self):
        self.logger = get_logger('market_data')
        
        # Indian market indices for regime analysis
        self.primary_indices = {
            'NIFTY50': '^NSEI',
            'SENSEX': '^BSESN',
            'BANKNIFTY': '^NSEBANK',
            'NIFTY_IT': '^CNXIT',
            'NIFTY_AUTO': '^CNXAUTO'
        }
        
        # Cache for market data to avoid excessive API calls
        self.data_cache = {}
        self.cache_expiry = {}
        self.cache_duration = 300  # 5 minutes cache
        
        # Market hours (IST)
        self.market_open_time = 9.25  # 9:15 AM
        self.market_close_time = 15.5  # 3:30 PM
        
    async def get_live_market_data(self, period_days: int = 30) -> Dict:
        """
        Fetch real-time market data for regime analysis
        
        Args:
            period_days: Number of days of historical data to fetch
        """
        try:
            self.logger.info(f"Fetching live market data for {period_days} days")
            
            # Check if market is open
            market_status = self._get_market_status()
            
            # Fetch data for primary indices
            market_data = {}
            
            for index_name, symbol in self.primary_indices.items():
                try:
                    data = await self._fetch_index_data(symbol, period_days)
                    if data is not None:
                        market_data[index_name] = data
                        self.logger.debug(f"Fetched data for {index_name}: {len(data)} records")
                except Exception as e:
                    self.logger.error(f"Error fetching data for {index_name}: {e}")
                    continue
            
            if not market_data:
                self.logger.error("No market data could be fetched")
                return {'success': False, 'error': 'Unable to fetch market data'}
            
            # Use NIFTY50 as primary index for regime analysis
            primary_data = market_data.get('NIFTY50') or market_data.get('SENSEX')
            
            if primary_data is None:
                return {'success': False, 'error': 'Primary index data unavailable'}
            
            # Calculate additional market metrics
            market_metrics = await self._calculate_market_metrics(market_data)
            
            # Get current market snapshot
            current_snapshot = await self._get_current_market_snapshot()
            
            result = {
                'success': True,
                'data': {
                    'primary_index': primary_data,
                    'all_indices': market_data,
                    'market_metrics': market_metrics,
                    'current_snapshot': current_snapshot,
                    'market_status': market_status,
                    'timestamp': datetime.now().isoformat(),
                    'data_source': 'yahoo_finance'
                }
            }
            
            self.logger.info("Live market data fetched successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching live market data: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    async def _fetch_index_data(self, symbol: str, period_days: int) -> Optional[Dict]:
        """Fetch data for a specific index"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{period_days}"
            if self._is_cache_valid(cache_key):
                self.logger.debug(f"Using cached data for {symbol}")
                return self.data_cache[cache_key]
            
            # Fetch from Yahoo Finance
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            hist_data = ticker.history(
                start=start_date,
                end=end_date,
                interval='1d'
            )
            
            if hist_data.empty:
                self.logger.warning(f"No historical data for {symbol}")
                return None
            
            # Get current quote
            try:
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                
                if current_price is None and not hist_data.empty:
                    current_price = hist_data['Close'].iloc[-1]
                    
            except Exception as e:
                self.logger.warning(f"Could not get current price for {symbol}: {e}")
                current_price = hist_data['Close'].iloc[-1] if not hist_data.empty else None
            
            # Process the data
            processed_data = {
                'symbol': symbol,
                'current_price': float(current_price) if current_price else None,
                'prices': hist_data['Close'].tolist(),
                'volumes': hist_data['Volume'].tolist(),
                'dates': [date.strftime('%Y-%m-%d') for date in hist_data.index],
                'high_prices': hist_data['High'].tolist(),
                'low_prices': hist_data['Low'].tolist(),
                'open_prices': hist_data['Open'].tolist(),
                'last_updated': datetime.now().isoformat()
            }
            
            # Cache the data
            self.data_cache[cache_key] = processed_data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    async def _calculate_market_metrics(self, market_data: Dict) -> Dict:
        """Calculate comprehensive market metrics from multiple indices"""
        try:
            metrics = {}
            
            for index_name, data in market_data.items():
                if not data or not data.get('prices'):
                    continue
                
                prices = np.array(data['prices'])
                volumes = np.array(data.get('volumes', []))
                
                # Basic metrics
                current_price = prices[-1]
                prev_price = prices[-2] if len(prices) > 1 else current_price
                
                # Price changes
                daily_change = current_price - prev_price
                daily_change_pct = (daily_change / prev_price) * 100 if prev_price != 0 else 0
                
                # Moving averages
                sma_5 = np.mean(prices[-5:]) if len(prices) >= 5 else current_price
                sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else current_price
                sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else current_price
                
                # Volatility (20-day)
                returns = np.diff(prices) / prices[:-1]
                volatility_20d = np.std(returns[-20:]) * np.sqrt(252) if len(returns) >= 20 else 0
                
                # RSI calculation
                rsi = self._calculate_rsi(prices)
                
                # Support and resistance
                recent_high = np.max(prices[-20:]) if len(prices) >= 20 else current_price
                recent_low = np.min(prices[-20:]) if len(prices) >= 20 else current_price
                
                # Trend strength
                trend_strength = (sma_5 - sma_20) / sma_20 if sma_20 != 0 else 0
                
                # Volume analysis
                avg_volume = np.mean(volumes) if len(volumes) > 0 else 0
                recent_volume = np.mean(volumes[-5:]) if len(volumes) >= 5 else avg_volume
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
                
                metrics[index_name] = {
                    'current_price': float(current_price),
                    'daily_change': float(daily_change),
                    'daily_change_pct': float(daily_change_pct),
                    'sma_5': float(sma_5),
                    'sma_20': float(sma_20),
                    'sma_50': float(sma_50),
                    'volatility_20d': float(volatility_20d),
                    'rsi': float(rsi),
                    'recent_high': float(recent_high),
                    'recent_low': float(recent_low),
                    'trend_strength': float(trend_strength),
                    'volume_ratio': float(volume_ratio),
                    'support_level': float(recent_low),
                    'resistance_level': float(recent_high)
                }
            
            # Calculate market-wide metrics
            if metrics:
                market_wide = self._calculate_market_wide_metrics(metrics)
                metrics['MARKET_WIDE'] = market_wide
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating market metrics: {e}")
            return {}
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        try:
            if len(prices) < period + 1:
                return 50.0  # Neutral RSI
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception:
            return 50.0
    
    def _calculate_market_wide_metrics(self, index_metrics: Dict) -> Dict:
        """Calculate overall market metrics from all indices"""
        try:
            # Exclude MARKET_WIDE from calculation
            indices = {k: v for k, v in index_metrics.items() if k != 'MARKET_WIDE'}
            
            if not indices:
                return {}
            
            # Average metrics across indices
            avg_daily_change_pct = np.mean([m['daily_change_pct'] for m in indices.values()])
            avg_volatility = np.mean([m['volatility_20d'] for m in indices.values()])
            avg_rsi = np.mean([m['rsi'] for m in indices.values()])
            avg_trend_strength = np.mean([m['trend_strength'] for m in indices.values()])
            avg_volume_ratio = np.mean([m['volume_ratio'] for m in indices.values()])
            
            # Market breadth (how many indices are positive)
            positive_indices = sum(1 for m in indices.values() if m['daily_change_pct'] > 0)
            market_breadth = positive_indices / len(indices)
            
            # Market momentum
            strong_uptrend = sum(1 for m in indices.values() if m['trend_strength'] > 0.02)
            strong_downtrend = sum(1 for m in indices.values() if m['trend_strength'] < -0.02)
            
            return {
                'avg_daily_change_pct': float(avg_daily_change_pct),
                'avg_volatility': float(avg_volatility),
                'avg_rsi': float(avg_rsi),
                'avg_trend_strength': float(avg_trend_strength),
                'avg_volume_ratio': float(avg_volume_ratio),
                'market_breadth': float(market_breadth),
                'indices_in_uptrend': int(strong_uptrend),
                'indices_in_downtrend': int(strong_downtrend),
                'total_indices': len(indices)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating market-wide metrics: {e}")
            return {}
    
    async def _get_current_market_snapshot(self) -> Dict:
        """Get current market snapshot with real-time prices"""
        try:
            snapshot = {}
            
            for index_name, symbol in self.primary_indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                    prev_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
                    
                    if current_price and prev_close:
                        change = current_price - prev_close
                        change_pct = (change / prev_close) * 100
                        
                        snapshot[index_name] = {
                            'current_price': float(current_price),
                            'previous_close': float(prev_close),
                            'change': float(change),
                            'change_pct': float(change_pct),
                            'last_updated': datetime.now().isoformat()
                        }
                        
                except Exception as e:
                    self.logger.warning(f"Could not get snapshot for {index_name}: {e}")
                    continue
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Error getting market snapshot: {e}")
            return {}
    
    def _get_market_status(self) -> Dict:
        """Determine if market is currently open"""
        try:
            now = datetime.now()
            current_time = now.hour + now.minute / 60
            
            # Check if it's a weekday
            is_weekday = now.weekday() < 5  # Monday = 0, Sunday = 6
            
            # Check if within market hours (9:15 AM to 3:30 PM IST)
            is_market_hours = self.market_open_time <= current_time <= self.market_close_time
            
            is_open = is_weekday and is_market_hours
            
            # Determine market session
            if is_open:
                if current_time < 10:
                    session = "opening"
                elif current_time > 15:
                    session = "closing"
                else:
                    session = "active"
            else:
                session = "closed"
            
            return {
                'is_open': is_open,
                'session': session,
                'current_time': now.strftime('%H:%M:%S'),
                'next_open': self._get_next_market_open(),
                'timezone': 'IST'
            }
            
        except Exception as e:
            self.logger.error(f"Error determining market status: {e}")
            return {'is_open': False, 'session': 'unknown'}
    
    def _get_next_market_open(self) -> str:
        """Get next market opening time"""
        try:
            now = datetime.now()
            
            # If it's a weekday and before market open
            if now.weekday() < 5 and now.hour < 9:
                next_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
            else:
                # Next weekday
                days_ahead = 1
                while (now + timedelta(days=days_ahead)).weekday() >= 5:
                    days_ahead += 1
                
                next_open = (now + timedelta(days=days_ahead)).replace(
                    hour=9, minute=15, second=0, microsecond=0
                )
            
            return next_open.strftime('%Y-%m-%d %H:%M:%S')
            
        except Exception:
            return "Unknown"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.data_cache:
            return False
        
        if cache_key not in self.cache_expiry:
            return False
        
        return datetime.now() < self.cache_expiry[cache_key]
    
    async def get_intraday_data(self, symbol: str = '^NSEI', interval: str = '5m') -> Dict:
        """Get intraday data for more granular regime analysis"""
        try:
            self.logger.info(f"Fetching intraday data for {symbol}")
            
            ticker = yf.Ticker(symbol)
            
            # Get today's intraday data
            intraday_data = ticker.history(
                period='1d',
                interval=interval
            )
            
            if intraday_data.empty:
                return {'success': False, 'error': 'No intraday data available'}
            
            processed_data = {
                'symbol': symbol,
                'interval': interval,
                'prices': intraday_data['Close'].tolist(),
                'volumes': intraday_data['Volume'].tolist(),
                'timestamps': [ts.strftime('%H:%M:%S') for ts in intraday_data.index],
                'high_prices': intraday_data['High'].tolist(),
                'low_prices': intraday_data['Low'].tolist(),
                'last_updated': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'data': processed_data
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching intraday data: {e}")
            return {'success': False, 'error': str(e)}
    
    def clear_cache(self):
        """Clear all cached data"""
        self.data_cache.clear()
        self.cache_expiry.clear()
        self.logger.info("Market data cache cleared")

# Global instance
_market_data_service = None

def get_market_data_service() -> RealTimeMarketDataService:
    """Get global market data service instance"""
    global _market_data_service
    if _market_data_service is None:
        _market_data_service = RealTimeMarketDataService()
    return _market_data_service
