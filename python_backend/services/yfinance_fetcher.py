"""
YFinance Data Fetcher - Handles all market data retrieval using yfinance
Provides clean, consistent data for trading strategies and backtesting
"""
import os
import time
import random
from functools import wraps

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import requests

# Import caching functionality
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.data_cache import (
    get_cached_stock_data, set_cached_stock_data,
    get_cached_stock_info, set_cached_stock_info,
    cache
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rate_limit(delay_range=(1, 3), max_retries=3):
    """
    Decorator to add rate limiting and retry logic to API calls
    
    Args:
        delay_range: Tuple of (min_delay, max_delay) in seconds
        max_retries: Maximum number of retry attempts
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    # Add random delay to avoid rate limiting
                    if attempt > 0:
                        delay = random.uniform(delay_range[0], delay_range[1]) * (attempt + 1)
                        logger.info(f"Rate limit delay: {delay:.1f}s (attempt {attempt + 1})")
                        time.sleep(delay)
                    
                    result = func(*args, **kwargs)
                    return result
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Check for rate limiting errors
                    if any(phrase in error_msg for phrase in ['rate limit', 'too many requests', '429']):
                        if attempt < max_retries:
                            backoff_delay = random.uniform(5, 15) * (attempt + 1)
                            logger.warning(f"Rate limited. Backing off for {backoff_delay:.1f}s...")
                            time.sleep(backoff_delay)
                            continue
                        else:
                            logger.error(f"Max retries exceeded for rate limiting: {func.__name__}")
                            return pd.DataFrame() if 'DataFrame' in str(func.__annotations__.get('return', '')) else {}
                    
                    # Check for network/connection errors
                    elif any(phrase in error_msg for phrase in ['connection', 'timeout', 'network']):
                        if attempt < max_retries:
                            retry_delay = random.uniform(2, 5)
                            logger.warning(f"Network error. Retrying in {retry_delay:.1f}s...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            logger.error(f"Max retries exceeded for network error: {func.__name__}")
                            return pd.DataFrame() if 'DataFrame' in str(func.__annotations__.get('return', '')) else {}
                    
                    # For other errors, don't retry
                    else:
                        logger.error(f"Error in {func.__name__}: {str(e)}")
                        return pd.DataFrame() if 'DataFrame' in str(func.__annotations__.get('return', '')) else {}
            
            # Should not reach here
            return pd.DataFrame() if 'DataFrame' in str(func.__annotations__.get('return', '')) else {}
        
        return wrapper
    return decorator

class YFinanceFetcher:
    def __init__(self):
        self.nse_suffix = ".NS"  # NSE suffix for Indian stocks
        # Remove custom session - let yfinance handle it internally
        
    @rate_limit(delay_range=(0.5, 2), max_retries=3)
    def get_nse_stock_data(self, symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch stock data for NSE listed stocks with rate limiting and caching
        
        Args:
            symbol: Stock symbol (will add .NS suffix)
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Check cache first
            cached_data = get_cached_stock_data(symbol, period)
            if cached_data is not None and not cached_data.empty:
                logger.debug(f"Using cached data for {symbol}")
                return cached_data
            
            # Add NSE suffix if not present
            if not symbol.endswith(self.nse_suffix):
                symbol += self.nse_suffix
            
            # Let yfinance handle session management
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data found for symbol: {symbol}")
                return pd.DataFrame()
            
            # Clean column names
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            data.reset_index(inplace=True)
            data['symbol'] = symbol.replace(self.nse_suffix, "")
            
            # Cache the data
            clean_symbol = symbol.replace(self.nse_suffix, "")
            set_cached_stock_data(clean_symbol, period, data)
            logger.debug(f"Cached data for {clean_symbol}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch historical data for specific date range
        
        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with historical OHLCV data
        """
        try:
            if not symbol.endswith(self.nse_suffix):
                symbol += self.nse_suffix
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                logger.warning(f"No historical data found for {symbol}")
                return pd.DataFrame()
            
            # Clean and prepare data
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            data.reset_index(inplace=True)
            data['symbol'] = symbol.replace(self.nse_suffix, "")
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    @rate_limit(delay_range=(1, 3), max_retries=3)
    def get_stock_info(self, symbol) -> Dict:
        """
        Get fundamental information about a stock with rate limiting and caching
        
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
            
            # Check cache first
            cached_info = get_cached_stock_info(symbol)
            if cached_info is not None:
                logger.debug(f"Using cached info for {symbol}")
                return cached_info
            
            if not symbol.endswith(self.nse_suffix):
                symbol += self.nse_suffix
            
            # Let yfinance handle session management
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract key fundamental metrics with safe defaults
            fundamental_data = {
                'symbol': symbol.replace(self.nse_suffix, ""),
                'company_name': info.get('longName', ''),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0) or info.get('forwardPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'debt_to_equity': info.get('debtToEquity', 0) / 100 if info.get('debtToEquity') else 0,  # Convert to ratio
                'debt_equity_ratio': info.get('debtToEquity', 0) / 100 if info.get('debtToEquity') else 0,
                'roe': (info.get('returnOnEquity', 0) * 100) if info.get('returnOnEquity') else 0,  # Convert to percentage
                'current_ratio': info.get('currentRatio', 0),
                'current_price': info.get('currentPrice', 0) or info.get('regularMarketPrice', 0),
                'beta': info.get('beta', 1.0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'dividend_yield': (info.get('dividendYield', 0) * 100) if info.get('dividendYield') else 0,  # Convert to percentage
                'earnings_growth': (info.get('earningsGrowth', 0) * 100) if info.get('earningsGrowth') else 0,
                'profit_growth': (info.get('earningsGrowth', 0) * 100) if info.get('earningsGrowth') else 0,
                'revenue_growth': (info.get('revenueGrowth', 0) * 100) if info.get('revenueGrowth') else 0,
                'book_value_per_share': info.get('bookValue', 0),
                'eps': info.get('trailingEps', 0) or info.get('forwardEps', 0),
                'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'ebitda': info.get('ebitda', 0),
                'total_cash': info.get('totalCash', 0),
                'total_debt': info.get('totalDebt', 0),
                'free_cash_flow': info.get('freeCashflow', 0),
                'operating_margin': (info.get('operatingMargins', 0) * 100) if info.get('operatingMargins') else 0,
                'profit_margin': (info.get('profitMargins', 0) * 100) if info.get('profitMargins') else 0,
                'gross_margin': (info.get('grossMargins', 0) * 100) if info.get('grossMargins') else 0,
                'last_updated': datetime.now().isoformat()
            }
            
            # Cache the data
            clean_symbol = symbol.replace(self.nse_suffix, "")
            set_cached_stock_info(clean_symbol, fundamental_data)
            logger.debug(f"Cached info for {clean_symbol}")
            
            logger.debug(f"Successfully fetched info for {symbol}")
            return fundamental_data
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {str(e)}")
            # Return default structure to prevent downstream errors
            clean_symbol = symbol.replace(self.nse_suffix, "") if isinstance(symbol, str) and symbol.endswith(self.nse_suffix) else str(symbol)
            return {
                'symbol': clean_symbol,
                'company_name': '',
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market_cap': 0,
                'pe_ratio': 0,
                'pb_ratio': 0,
                'debt_equity_ratio': 0,
                'roe': 0,
                'current_ratio': 1.0,
                'current_price': 0,
                'beta': 1.0,
                'dividend_yield': 0,
                'profit_growth': 0,
                'eps': 0,
                'book_value_per_share': 0,
                'last_updated': datetime.now().isoformat(),
                'error': str(e)
            }

    def get_nse_universe(self) -> List[Dict]:
        """
        Get list of actively traded NSE equity stocks for screening with caching.

        Returns:
            List of stock dictionaries with symbol and basic info
        """
        try:
            # Check cache first
            cached_universe = cache.get('nse_universe', 'stocks_list')
            if cached_universe is not None:
                logger.info(f"Using cached NSE universe with {len(cached_universe)} stocks")
                return cached_universe
            
            # Try to load from local cache first
            cache_file = "python_backend/data/nse_raw.csv"
            if os.path.exists(cache_file):
                df = pd.read_csv(cache_file)
            else:
                url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    logger.error(f"Failed to download NSE data: HTTP {response.status_code}")
                    # Return fallback list
                    fallback_universe = self._get_fallback_nse_universe()
                    cache.set('nse_universe', 'stocks_list', fallback_universe)
                    return fallback_universe

                os.makedirs("python_backend/data", exist_ok=True)
                with open(cache_file, "wb") as f:
                    f.write(response.content)
                df = pd.read_csv(cache_file)

            df.columns = df.columns.str.strip()
            symbol_col = 'SYMBOL'
            series_col = 'SERIES'

            if symbol_col not in df.columns:
                logger.error(f"Column '{symbol_col}' not found in NSE data")
                fallback_universe = self._get_fallback_nse_universe()
                cache.set('nse_universe', 'stocks_list', fallback_universe)
                return fallback_universe

            # Filter only EQ series (equity stocks)
            df_eq = df[df[series_col] == 'EQ']
            
            # Convert to list of dictionaries
            nse_stocks = []
            for _, row in df_eq.iterrows():
                nse_stocks.append({
                    'symbol': row[symbol_col],
                    'name': row.get('NAME OF COMPANY', ''),
                    'series': row.get(series_col, 'EQ'),
                    'date_of_listing': row.get('DATE OF LISTING', ''),
                    'paid_up_value': row.get('PAID UP VALUE', 0),
                    'market_lot': row.get('MARKET LOT', 1),
                    'isin_number': row.get('ISIN NUMBER', ''),
                    'face_value': row.get('FACE VALUE', 0)
                })

            # Cache the universe
            cache.set('nse_universe', 'stocks_list', nse_stocks)
            logger.info(f"Loaded and cached {len(nse_stocks)} NSE stocks from universe")
            return nse_stocks
            
        except Exception as e:
            logger.error(f"Error loading NSE universe: {str(e)}")
            fallback_universe = self._get_fallback_nse_universe()
            cache.set('nse_universe', 'stocks_list', fallback_universe)
            return fallback_universe
    
    def _get_fallback_nse_universe(self) -> List[Dict]:
        """Fallback NSE universe with major stocks"""
        fallback_stocks = [
            {'symbol': 'RELIANCE', 'name': 'Reliance Industries Limited', 'sector': 'Oil & Gas'},
            {'symbol': 'TCS', 'name': 'Tata Consultancy Services Limited', 'sector': 'Information Technology'},
            {'symbol': 'HDFCBANK', 'name': 'HDFC Bank Limited', 'sector': 'Banking'},
            {'symbol': 'INFY', 'name': 'Infosys Limited', 'sector': 'Information Technology'},
            {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever Limited', 'sector': 'FMCG'},
            {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Limited', 'sector': 'Banking'},
            {'symbol': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank Limited', 'sector': 'Banking'},
            {'symbol': 'BHARTIARTL', 'name': 'Bharti Airtel Limited', 'sector': 'Telecommunications'},
            {'symbol': 'ITC', 'name': 'ITC Limited', 'sector': 'FMCG'},
            {'symbol': 'SBIN', 'name': 'State Bank of India', 'sector': 'Banking'},
            {'symbol': 'MARUTI', 'name': 'Maruti Suzuki India Limited', 'sector': 'Automobile'},
            {'symbol': 'DIVISLAB', 'name': 'Divi\'s Laboratories Limited', 'sector': 'Pharmaceuticals'},
            {'symbol': 'WIPRO', 'name': 'Wipro Limited', 'sector': 'Information Technology'},
            {'symbol': 'TECHM', 'name': 'Tech Mahindra Limited', 'sector': 'Information Technology'},
            {'symbol': 'HCLTECH', 'name': 'HCL Technologies Limited', 'sector': 'Information Technology'}
        ]
        logger.info(f"Using fallback NSE universe with {len(fallback_stocks)} stocks")
        return fallback_stocks
    
    def get_multiple_stock_info(self, symbols: List, batch_size: int = 5) -> Dict[str, Dict]:
        """
        Get stock info for multiple symbols with batch processing and rate limiting
        
        Args:
            symbols: List of stock symbols (strings) or stock dictionaries
            batch_size: Number of stocks to process in each batch
            
        Returns:
            Dictionary mapping symbols to their info
        """
        stock_info = {}
        total_symbols = len(symbols)
        
        logger.info(f"Fetching info for {total_symbols} stocks in batches of {batch_size}")
        
        for i in range(0, total_symbols, batch_size):
            batch = symbols[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_symbols + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches}: {batch}")
            
            for symbol_input in batch:
                try:
                    # Extract symbol string from input
                    if isinstance(symbol_input, dict):
                        symbol = symbol_input.get('symbol', '')
                    else:
                        symbol = str(symbol_input)
                    
                    if not symbol:
                        continue
                    
                    info = self.get_stock_info(symbol)
                    stock_info[symbol] = info
                    
                    # Small delay between stocks in the same batch
                    time.sleep(random.uniform(0.2, 0.5))
                    
                except Exception as e:
                    symbol_str = str(symbol_input) if not isinstance(symbol_input, dict) else symbol_input.get('symbol', 'unknown')
                    logger.error(f"Error fetching info for {symbol_str}: {str(e)}")
                    stock_info[symbol_str] = {'error': str(e)}
            
            # Longer delay between batches
            if i + batch_size < total_symbols:
                batch_delay = random.uniform(2, 4)
                logger.info(f"Batch delay: {batch_delay:.1f}s")
                time.sleep(batch_delay)
        
        logger.info(f"Successfully fetched info for {len([k for k, v in stock_info.items() if 'error' not in v])}/{total_symbols} stocks")
        return stock_info
    
    def get_multiple_stock_data(self, symbols: List, period: str = "1y", batch_size: int = 10) -> Dict[str, pd.DataFrame]:
        """
        Get historical data for multiple symbols with batch processing
        
        Args:
            symbols: List of stock symbols (strings) or stock dictionaries
            period: Data period
            batch_size: Number of stocks to process in each batch
            
        Returns:
            Dictionary mapping symbols to their DataFrames
        """
        stock_data = {}
        total_symbols = len(symbols)
        
        logger.info(f"Fetching data for {total_symbols} stocks in batches of {batch_size}")
        
        for i in range(0, total_symbols, batch_size):
            batch = symbols[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_symbols + batch_size - 1) // batch_size
            
            logger.info(f"Processing data batch {batch_num}/{total_batches}")
            
            for symbol_input in batch:
                try:
                    # Extract symbol string from input
                    if isinstance(symbol_input, dict):
                        symbol = symbol_input.get('symbol', '')
                    else:
                        symbol = str(symbol_input)
                    
                    if not symbol:
                        continue
                    
                    data = self.get_nse_stock_data(symbol, period=period)
                    if not data.empty:
                        stock_data[symbol] = data
                    
                    # Small delay between requests
                    time.sleep(random.uniform(0.1, 0.3))
                    
                except Exception as e:
                    symbol_str = str(symbol_input) if not isinstance(symbol_input, dict) else symbol_input.get('symbol', 'unknown')
                    logger.error(f"Error fetching data for {symbol_str}: {str(e)}")
            
            # Delay between batches
            if i + batch_size < total_symbols:
                time.sleep(random.uniform(1, 2))
        
        logger.info(f"Successfully fetched data for {len(stock_data)}/{total_symbols} stocks")
        return stock_data
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate common technical indicators for the data
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            DataFrame with technical indicators added
        """
        if data.empty:
            return data
        
        try:
            # Moving Averages
            data['sma_20'] = data['close'].rolling(window=20).mean()
            data['sma_50'] = data['close'].rolling(window=50).mean()
            data['sma_200'] = data['close'].rolling(window=200).mean()
            
            # Exponential Moving Averages
            data['ema_12'] = data['close'].ewm(span=12).mean()
            data['ema_26'] = data['close'].ewm(span=26).mean()
            
            # MACD
            data['macd'] = data['ema_12'] - data['ema_26']
            data['macd_signal'] = data['macd'].ewm(span=9).mean()
            data['macd_histogram'] = data['macd'] - data['macd_signal']
            
            # RSI
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            data['bb_middle'] = data['close'].rolling(window=20).mean()
            bb_std = data['close'].rolling(window=20).std()
            data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
            data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
            
            # ATR (Average True Range)
            data['tr'] = np.maximum(
                data['high'] - data['low'],
                np.maximum(
                    abs(data['high'] - data['close'].shift(1)),
                    abs(data['low'] - data['close'].shift(1))
                )
            )
            data['atr'] = data['tr'].rolling(window=14).mean()
            
            # Volume indicators
            data['volume_sma'] = data['volume'].rolling(window=20).mean()
            data['volume_ratio'] = data['volume'] / data['volume_sma']
            
            return data
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return data

if __name__ == "__main__":
    fetcher = YFinanceFetcher()
    stock_list = fetcher.get_nse_universe()
    print(stock_list)