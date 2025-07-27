"""
Real Market Data Service
Connects to various APIs for live stock prices
"""

import requests
import yfinance as yf
import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StockPrice:
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    timestamp: datetime = None

class MarketDataService:
    def __init__(self):
        # API Keys (set these in environment variables)
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.iex_token = os.getenv('IEX_CLOUD_TOKEN')
        self.fmp_key = os.getenv('FMP_API_KEY')
        
        # Cache for price data
        self.price_cache = {}
        self.cache_duration = 60  # 1 minute cache
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1  # 1 second between requests
        
    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached price is still valid"""
        if symbol not in self.price_cache:
            return False
        
        cache_time = self.price_cache[symbol].get('timestamp')
        if not cache_time:
            return False
            
        return (datetime.now() - cache_time).seconds < self.cache_duration
    
    def _should_make_request(self, api_name: str) -> bool:
        """Rate limiting check"""
        if api_name not in self.last_request_time:
            return True
            
        time_since_last = (datetime.now() - self.last_request_time[api_name]).seconds
        return time_since_last >= self.min_request_interval

    # Method 1: Yahoo Finance (Free, No API Key Required)
    def get_price_yahoo(self, symbol: str) -> Optional[StockPrice]:
        """Get stock price from Yahoo Finance"""
        try:
            # Convert Indian symbols to Yahoo format
            yahoo_symbol = self._convert_to_yahoo_symbol(symbol)
            
            # Check cache first
            if self._is_cache_valid(yahoo_symbol):
                cached = self.price_cache[yahoo_symbol]
                return StockPrice(**cached['data'])
            
            # Fetch from Yahoo Finance
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return None
                
            current_price = hist['Close'].iloc[-1]
            prev_close = info.get('previousClose', current_price)
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0
            
            stock_price = StockPrice(
                symbol=symbol,
                price=float(current_price),
                change=float(change),
                change_percent=float(change_percent),
                volume=int(hist['Volume'].iloc[-1]) if not hist['Volume'].empty else 0,
                market_cap=info.get('marketCap'),
                timestamp=datetime.now()
            )
            
            # Cache the result
            self.price_cache[yahoo_symbol] = {
                'data': stock_price.__dict__,
                'timestamp': datetime.now()
            }
            
            return stock_price
            
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance data for {symbol}: {e}")
            return None
    
    # Method 2: Alpha Vantage (Free tier: 5 calls/minute, 500 calls/day)
    def get_price_alpha_vantage(self, symbol: str) -> Optional[StockPrice]:
        """Get stock price from Alpha Vantage"""
        if not self.alpha_vantage_key:
            logger.warning("Alpha Vantage API key not configured")
            return None
            
        if not self._should_make_request('alpha_vantage'):
            return None
            
        try:
            # Check cache first
            if self._is_cache_valid(symbol):
                cached = self.price_cache[symbol]
                return StockPrice(**cached['data'])
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Global Quote' not in data:
                return None
                
            quote = data['Global Quote']
            
            stock_price = StockPrice(
                symbol=symbol,
                price=float(quote['05. price']),
                change=float(quote['09. change']),
                change_percent=float(quote['10. change percent'].replace('%', '')),
                volume=int(quote['06. volume']),
                timestamp=datetime.now()
            )
            
            # Cache and rate limit
            self.price_cache[symbol] = {
                'data': stock_price.__dict__,
                'timestamp': datetime.now()
            }
            self.last_request_time['alpha_vantage'] = datetime.now()
            
            return stock_price
            
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data for {symbol}: {e}")
            return None
    
    # Method 3: IEX Cloud (Paid, but very reliable)
    def get_price_iex(self, symbol: str) -> Optional[StockPrice]:
        """Get stock price from IEX Cloud"""
        if not self.iex_token:
            logger.warning("IEX Cloud token not configured")
            return None
            
        try:
            # Check cache first
            if self._is_cache_valid(symbol):
                cached = self.price_cache[symbol]
                return StockPrice(**cached['data'])
            
            url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote"
            params = {'token': self.iex_token}
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            stock_price = StockPrice(
                symbol=symbol,
                price=float(data['latestPrice']),
                change=float(data['change']),
                change_percent=float(data['changePercent'] * 100),
                volume=int(data['latestVolume']),
                market_cap=data.get('marketCap'),
                timestamp=datetime.now()
            )
            
            # Cache the result
            self.price_cache[symbol] = {
                'data': stock_price.__dict__,
                'timestamp': datetime.now()
            }
            
            return stock_price
            
        except Exception as e:
            logger.error(f"Error fetching IEX data for {symbol}: {e}")
            return None
    
    # Method 4: Financial Modeling Prep (Good for Indian stocks)
    def get_price_fmp(self, symbol: str) -> Optional[StockPrice]:
        """Get stock price from Financial Modeling Prep"""
        if not self.fmp_key:
            logger.warning("FMP API key not configured")
            return None
            
        try:
            # Check cache first
            if self._is_cache_valid(symbol):
                cached = self.price_cache[symbol]
                return StockPrice(**cached['data'])
            
            # For Indian stocks, add .NS suffix
            fmp_symbol = f"{symbol}.NS" if not symbol.endswith('.NS') else symbol
            
            url = f"https://financialmodelingprep.com/api/v3/quote/{fmp_symbol}"
            params = {'apikey': self.fmp_key}
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if not data or len(data) == 0:
                return None
                
            quote = data[0]
            
            stock_price = StockPrice(
                symbol=symbol,
                price=float(quote['price']),
                change=float(quote['change']),
                change_percent=float(quote['changesPercentage']),
                volume=int(quote['volume']),
                market_cap=quote.get('marketCap'),
                timestamp=datetime.now()
            )
            
            # Cache the result
            self.price_cache[symbol] = {
                'data': stock_price.__dict__,
                'timestamp': datetime.now()
            }
            
            return stock_price
            
        except Exception as e:
            logger.error(f"Error fetching FMP data for {symbol}: {e}")
            return None
    
    # Main method with fallback strategy
    def get_live_price(self, symbol: str) -> Optional[StockPrice]:
        """
        Get live stock price with fallback strategy
        Tries multiple APIs in order of preference
        """
        # Try APIs in order of preference
        apis = [
            ('yahoo', self.get_price_yahoo),
            ('fmp', self.get_price_fmp),
            ('alpha_vantage', self.get_price_alpha_vantage),
            ('iex', self.get_price_iex)
        ]
        
        for api_name, api_func in apis:
            try:
                price = api_func(symbol)
                if price:
                    logger.info(f"Successfully fetched price for {symbol} from {api_name}")
                    return price
            except Exception as e:
                logger.warning(f"Failed to fetch from {api_name} for {symbol}: {e}")
                continue
        
        logger.error(f"Failed to fetch price for {symbol} from all APIs")
        return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, StockPrice]:
        """Get prices for multiple symbols"""
        results = {}
        
        for symbol in symbols:
            price = self.get_live_price(symbol)
            if price:
                results[symbol] = price
                
        return results
    
    def _convert_to_yahoo_symbol(self, symbol: str) -> str:
        """Convert Indian stock symbols to Yahoo Finance format"""
        # Add .NS for NSE stocks, .BO for BSE stocks
        if not symbol.endswith(('.NS', '.BO')):
            return f"{symbol}.NS"  # Default to NSE
        return symbol
    
    def clear_cache(self):
        """Clear price cache"""
        self.price_cache = {}
        logger.info("Price cache cleared")

# Global instance
market_data_service = MarketDataService()
