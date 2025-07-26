"""
YFinance Data Fetcher - Handles all market data retrieval using yfinance
Provides clean, consistent data for trading strategies and backtesting
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YFinanceFetcher:
    def __init__(self):
        self.nse_suffix = ".NS"  # NSE suffix for Indian stocks
        
    def get_nse_stock_data(self, symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch stock data for NSE listed stocks
        
        Args:
            symbol: Stock symbol (will add .NS suffix)
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Add NSE suffix if not present
            if not symbol.endswith(self.nse_suffix):
                symbol += self.nse_suffix
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data found for symbol: {symbol}")
                return pd.DataFrame()
            
            # Clean column names
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            data.reset_index(inplace=True)
            data['symbol'] = symbol.replace(self.nse_suffix, "")
            
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
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        Get fundamental information about a stock
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with stock information
        """
        try:
            if not symbol.endswith(self.nse_suffix):
                symbol += self.nse_suffix
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract key fundamental metrics
            fundamental_data = {
                'symbol': symbol.replace(self.nse_suffix, ""),
                'company_name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'roe': info.get('returnOnEquity', 0),
                'current_price': info.get('currentPrice', 0),
                'beta': info.get('beta', 0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                'revenue_growth': info.get('revenueGrowth', 0)
            }
            
            return fundamental_data
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {str(e)}")
            return {}
    
    def get_nse_universe(self) -> List[str]:
        """
        Get list of popular NSE stocks for screening
        This is a curated list of liquid stocks across sectors
        
        Returns:
            List of stock symbols
        """
        # Popular NSE stocks across sectors
        nse_stocks = [
            # Large Cap
            'RELIANCE', 'TCS', 'HDFCBANK', 'BHARTIARTL', 'ICICIBANK',
            'SBIN', 'LICI', 'ITC', 'HINDUNILVR', 'LT',
            
            # IT Sector
            'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTIM',
            
            # Banking & Finance
            'KOTAKBANK', 'AXISBANK', 'BAJFINANCE', 'HDFCLIFE', 'SBILIFE',
            
            # Auto Sector
            'MARUTI', 'MAHINDRAM', 'TATAMOTORS', 'BAJAJ-AUTO', 'HEROMOTOCO',
            
            # Pharma
            'SUNPHARMA', 'DRREDDY', 'CIPLA', 'APOLLOHOSP', 'DIVISLAB',
            
            # FMCG
            'NESTLEIND', 'BRITANNIA', 'DABUR', 'GODREJCP', 'MARICO',
            
            # Metals & Mining
            'TATASTEEL', 'JSWSTEEL', 'HINDALCO', 'VEDL', 'COALINDIA',
            
            # Energy & Power
            'NTPC', 'POWERGRID', 'ONGC', 'GAIL', 'IOC',
            
            # Telecom
            'AIRTEL', 'JIO', 'INDUSINDBK',
            
            # Mid Cap Growth
            'ADANIPORTS', 'ULTRACEMCO', 'ASIANPAINT', 'BAJAJFINSV', 'TITAN'
        ]
        
        return nse_stocks
    
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