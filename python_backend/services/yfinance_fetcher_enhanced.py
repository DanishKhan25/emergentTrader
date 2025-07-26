"""
Enhanced YFinance Fetcher with Improved Rate Limiting Resilience
Implements aggressive cache fallback and circuit breaker patterns
"""

import yfinance as yf
import pandas as pd
import logging
import time
import random
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from functools import wraps

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.data_cache import cache

logger = logging.getLogger(__name__)

class RateLimitingState:
    """Track rate limiting state for circuit breaker pattern"""
    def __init__(self):
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.circuit_open = False
        self.circuit_open_time = None
        
    def record_success(self):
        """Record successful API call"""
        self.consecutive_failures = 0
        self.circuit_open = False
        self.circuit_open_time = None
        
    def record_failure(self):
        """Record failed API call"""
        self.consecutive_failures += 1
        self.last_failure_time = datetime.now()
        
        # Open circuit after 3 consecutive failures
        if self.consecutive_failures >= 3:
            self.circuit_open = True
            self.circuit_open_time = datetime.now()
            logger.warning("Circuit breaker opened - switching to cache-only mode")
    
    def should_attempt_api_call(self) -> bool:
        """Check if we should attempt API call or use cache only"""
        if not self.circuit_open:
            return True
            
        # Try to close circuit after 5 minutes
        if self.circuit_open_time and (datetime.now() - self.circuit_open_time).seconds > 300:
            logger.info("Attempting to close circuit breaker")
            self.circuit_open = False
            self.consecutive_failures = 0
            return True
            
        return False

# Global rate limiting state
rate_limit_state = RateLimitingState()

def enhanced_rate_limit(delay_range=(1, 3), max_retries=2):
    """Enhanced rate limiting decorator with circuit breaker and aggressive cache fallback"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check circuit breaker first
            if not rate_limit_state.should_attempt_api_call():
                logger.info(f"Circuit breaker open - using cache-only mode for {func.__name__}")
                return _get_cached_data_aggressively(args, kwargs, func.__name__)
            
            for attempt in range(max_retries + 1):
                try:
                    # Add random delay to avoid rate limiting
                    if attempt > 0:
                        delay = random.uniform(delay_range[0], delay_range[1]) * (attempt + 1)
                        logger.info(f"Rate limit delay: {delay:.1f}s (attempt {attempt + 1})")
                        time.sleep(delay)
                    
                    result = func(*args, **kwargs)
                    
                    # Record success if we got valid data
                    if result and (isinstance(result, dict) and result.get('symbol')) or (isinstance(result, pd.DataFrame) and not result.empty):
                        rate_limit_state.record_success()
                        return result
                    else:
                        # Empty result might indicate rate limiting
                        logger.warning(f"Empty result from {func.__name__} - might be rate limited")
                        if attempt == max_retries:
                            rate_limit_state.record_failure()
                            return _get_cached_data_aggressively(args, kwargs, func.__name__)
                        continue
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Check for rate limiting errors
                    if any(phrase in error_msg for phrase in ['rate limit', 'too many requests', '429']):
                        rate_limit_state.record_failure()
                        
                        if attempt < max_retries:
                            backoff_delay = random.uniform(10, 20) * (attempt + 1)
                            logger.warning(f"Rate limited. Backing off for {backoff_delay:.1f}s...")
                            time.sleep(backoff_delay)
                            continue
                        else:
                            logger.error(f"Max retries exceeded for rate limiting: {func.__name__}")
                            return _get_cached_data_aggressively(args, kwargs, func.__name__)
                    
                    # Check for network/connection errors
                    elif any(phrase in error_msg for phrase in ['connection', 'timeout', 'network']):
                        if attempt < max_retries:
                            retry_delay = random.uniform(2, 5)
                            logger.warning(f"Network error. Retrying in {retry_delay:.1f}s...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            logger.error(f"Max retries exceeded for network error: {func.__name__}")
                            return _get_cached_data_aggressively(args, kwargs, func.__name__)
                    
                    # For other errors, try cache fallback
                    else:
                        logger.error(f"Error in {func.__name__}: {str(e)}")
                        return _get_cached_data_aggressively(args, kwargs, func.__name__)
            
            # If we get here, all retries failed
            return _get_cached_data_aggressively(args, kwargs, func.__name__)
        
        return wrapper
    return decorator

def _get_cached_data_aggressively(args, kwargs, func_name: str):
    """Aggressively try to get cached data when API fails"""
    try:
        if func_name == 'get_stock_info' and args:
            symbol = args[1] if len(args) > 1 else args[0]  # Handle self parameter
            if isinstance(symbol, dict):
                symbol = symbol.get('symbol', '')
            symbol = str(symbol)
            
            # Try different cache strategies
            cached_data = None
            
            # 1. Try normal cache
            cached_data = cache.get('stock_info', symbol)
            if cached_data:
                logger.info(f"Using cached stock info for {symbol} (normal cache)")
                return cached_data
            
            # 2. Try to get any cached data by checking cache files directly
            try:
                cache_file = cache._get_cache_file_path('stock_info', symbol)
                if os.path.exists(cache_file):
                    with open(cache_file, 'rb') as f:
                        import pickle
                        cached_data = pickle.load(f)
                        logger.info(f"Using expired cached stock info for {symbol}")
                        return cached_data
            except Exception as e:
                logger.debug(f"Could not access expired cache for {symbol}: {str(e)}")
            
            # 3. Try alternative symbol formats
            alt_symbols = [
                symbol.replace('.NS', ''),
                symbol + '.NS' if not symbol.endswith('.NS') else symbol,
                symbol.upper(),
                symbol.lower()
            ]
            
            for alt_symbol in alt_symbols:
                cached_data = cache.get('stock_info', alt_symbol)
                if cached_data:
                    logger.info(f"Using cached stock info for {symbol} via alternative symbol {alt_symbol}")
                    return cached_data
            
            # 4. Return minimal data structure to prevent crashes
            logger.warning(f"No cached data found for {symbol} - returning minimal structure")
            return {
                'symbol': symbol.replace('.NS', ''),
                'company_name': '',
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market_cap': 0,
                'pe_ratio': 0,
                'pb_ratio': 0,
                'debt_to_equity': 0,
                'data_source': 'fallback_minimal'
            }
        
        elif func_name in ['get_stock_data', 'get_historical_data'] and args:
            symbol = args[1] if len(args) > 1 else args[0]
            period = args[2] if len(args) > 2 else '6mo'
            
            # Try cached historical data
            cached_data = cache.get('stock_data', f"{symbol}_{period}")
            if cached_data is not None and not cached_data.empty:
                logger.info(f"Using cached historical data for {symbol} ({period})")
                return cached_data
            
            # Try different periods
            alt_periods = ['1y', '6mo', '3mo', '1mo']
            for alt_period in alt_periods:
                if alt_period != period:
                    cached_data = cache.get('stock_data', f"{symbol}_{alt_period}")
                    if cached_data is not None and not cached_data.empty:
                        logger.info(f"Using cached historical data for {symbol} ({alt_period} instead of {period})")
                        return cached_data
            
            # Return empty DataFrame
            logger.warning(f"No cached historical data found for {symbol}")
            return pd.DataFrame()
        
        # Default fallback
        if 'DataFrame' in str(func_name):
            return pd.DataFrame()
        else:
            return {}
            
    except Exception as e:
        logger.error(f"Error in aggressive cache fallback: {str(e)}")
        return pd.DataFrame() if 'data' in func_name.lower() else {}

class EnhancedYFinanceFetcher:
    """Enhanced YFinance fetcher with improved rate limiting resilience"""
    
    def __init__(self):
        self.nse_suffix = ".NS"
        self.name = "Enhanced YFinance Fetcher"
        logger.info("Initialized Enhanced YFinance Fetcher with circuit breaker pattern")
    
    @enhanced_rate_limit(delay_range=(2, 5), max_retries=2)
    def get_stock_info(self, symbol) -> Dict:
        """
        Get fundamental information about a stock with enhanced rate limiting resilience
        
        Args:
            symbol: Stock symbol (string) or stock dictionary
        
        Returns:
            Dictionary with stock information
        """
        try:
            # Handle case where symbol might be a dictionary
            if isinstance(symbol, dict):
                symbol = symbol.get('symbol', '')
            
            # Ensure symbol is a string
            symbol = str(symbol)
            
            if not symbol:
                logger.error("Empty symbol provided to get_stock_info")
                return {}
            
            # Check cache first with extended TTL during rate limiting
            cache_ttl_hours = 168 if rate_limit_state.circuit_open else 24  # 7 days vs 1 day
            cached_info = cache.get('stock_info', symbol)
            
            if cached_info is not None:
                # Check cache age
                cache_time = cached_info.get('cache_time')
                if cache_time:
                    cache_age = (datetime.now() - datetime.fromisoformat(cache_time)).total_seconds() / 3600
                    if cache_age < cache_ttl_hours:
                        logger.debug(f"Using cached info for {symbol} (age: {cache_age:.1f}h)")
                        return cached_info
                    elif rate_limit_state.circuit_open:
                        logger.info(f"Using expired cache for {symbol} due to circuit breaker (age: {cache_age:.1f}h)")
                        return cached_info
            
            if not symbol.endswith(self.nse_suffix):
                symbol += self.nse_suffix
            
            # Fetch from Yahoo Finance
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or not info.get('symbol'):
                logger.warning(f"No data returned from Yahoo Finance for {symbol}")
                return {}
            
            # Extract key fundamental metrics with safe defaults
            fundamental_data = {
                'symbol': symbol.replace(self.nse_suffix, ""),
                'company_name': info.get('longName', ''),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0) or info.get('forwardPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'debt_to_equity': info.get('debtToEquity', 0) / 100 if info.get('debtToEquity') else 0,
                'current_price': info.get('currentPrice', 0) or info.get('regularMarketPrice', 0),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 1.0),
                'cache_time': datetime.now().isoformat(),
                'data_source': 'yahoo_finance'
            }
            
            # Cache the result with extended TTL if needed
            cache_hours = cache_ttl_hours
            cache.set('stock_info', symbol.replace(self.nse_suffix, ""), fundamental_data, ttl_hours=cache_hours)
            
            logger.debug(f"Fetched and cached stock info for {symbol}")
            return fundamental_data
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {str(e)}")
            raise  # Let the decorator handle the error
    
    @enhanced_rate_limit(delay_range=(1, 3), max_retries=2)
    def get_stock_data(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        """
        Get historical stock data with enhanced rate limiting resilience
        
        Args:
            symbol: Stock symbol
            period: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            DataFrame with historical stock data
        """
        try:
            # Check cache first
            cache_key = f"{symbol}_{period}"
            cached_data = cache.get('stock_data', cache_key)
            
            if cached_data is not None and not cached_data.empty:
                # Check cache age
                cache_age_hours = 24 if rate_limit_state.circuit_open else 6
                if hasattr(cached_data, 'attrs') and 'cache_time' in cached_data.attrs:
                    cache_time = datetime.fromisoformat(cached_data.attrs['cache_time'])
                    age_hours = (datetime.now() - cache_time).total_seconds() / 3600
                    
                    if age_hours < cache_age_hours:
                        logger.debug(f"Using cached data for {symbol} {period} (age: {age_hours:.1f}h)")
                        return cached_data
                    elif rate_limit_state.circuit_open:
                        logger.info(f"Using expired cache for {symbol} due to circuit breaker")
                        return cached_data
            
            if not symbol.endswith(self.nse_suffix):
                symbol += self.nse_suffix
            
            # Fetch from Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                logger.warning(f"No historical data returned for {symbol} {period}")
                return pd.DataFrame()
            
            # Add metadata
            data.attrs = {
                'symbol': symbol.replace(self.nse_suffix, ""),
                'period': period,
                'cache_time': datetime.now().isoformat(),
                'data_source': 'yahoo_finance'
            }
            
            # Cache the result
            cache_hours = 24 if rate_limit_state.circuit_open else 6
            cache.set('stock_data', cache_key, data, ttl_hours=cache_hours)
            
            logger.debug(f"Fetched and cached historical data for {symbol} {period}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol} {period}: {str(e)}")
            raise  # Let the decorator handle the error
    
    def get_rate_limiting_status(self) -> Dict:
        """Get current rate limiting status"""
        return {
            'circuit_open': rate_limit_state.circuit_open,
            'consecutive_failures': rate_limit_state.consecutive_failures,
            'last_failure_time': rate_limit_state.last_failure_time.isoformat() if rate_limit_state.last_failure_time else None,
            'circuit_open_time': rate_limit_state.circuit_open_time.isoformat() if rate_limit_state.circuit_open_time else None,
            'cache_only_mode': rate_limit_state.circuit_open
        }
    
    def reset_rate_limiting_state(self):
        """Reset rate limiting state (for testing or manual intervention)"""
        global rate_limit_state
        rate_limit_state = RateLimitingState()
        logger.info("Rate limiting state reset")

# Backward compatibility
YFinanceFetcher = EnhancedYFinanceFetcher
