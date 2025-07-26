#!/usr/bin/env python3
"""
Historical Data Collection for ML Training
Generate signals as if we were trading in the past
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import pickle
import json
from typing import List, Dict, Optional
import logging

# Add the python_backend directory to the path
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
except NameError:
    parent_dir = os.getcwd()

sys.path.append(parent_dir)

from core.enhanced_signal_engine import EnhancedSignalEngine
from core.enhanced_shariah_filter_smart import SmartShariahFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoricalDataCollector:
    """Collect historical trading signals for ML training"""
    
    def __init__(self, start_date='2012-01-01', end_date='2024-12-31'):
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.shariah_filter = SmartShariahFilter()
        
        # Create directories
        os.makedirs('ml/data', exist_ok=True)
        os.makedirs('ml/models', exist_ok=True)
        
        logger.info(f"Historical data collection: {start_date} to {end_date}")
    
    def get_nse_universe(self) -> List[str]:
        """Get NSE stock universe with proper .NS suffix"""
        try:
            # Get top NSE stocks (liquid and well-traded)
            nse_stocks = [
                'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR',
                'ICICIBANK', 'KOTAKBANK', 'SBIN', 'BHARTIARTL', 'ITC',
                'ASIANPAINT', 'LT', 'AXISBANK', 'MARUTI', 'SUNPHARMA',
                'ULTRACEMCO', 'TITAN', 'WIPRO', 'NESTLEIND', 'POWERGRID',
                'NTPC', 'TECHM', 'HCLTECH', 'BAJFINANCE', 'ONGC',
                'TATASTEEL', 'COALINDIA', 'INDUSINDBK', 'DRREDDY', 'GRASIM',
                'CIPLA', 'EICHERMOT', 'HEROMOTOCO', 'BAJAJFINSV', 'BRITANNIA',
                'DIVISLAB', 'JSWSTEEL', 'ADANIPORTS', 'TATACONSUM', 'HINDALCO',
                'BPCL', 'APOLLOHOSP', 'HDFCLIFE', 'SBILIFE', 'BAJAJ-AUTO',
                'TATAMOTORS', 'SHREECEM', 'PIDILITIND', 'GODREJCP', 'DABUR'
            ]
            
            # Add .NS suffix for NSE stocks
            return [f"{stock}.NS" for stock in nse_stocks]
            
        except Exception as e:
            logger.error(f"Error getting NSE universe: {str(e)}")
            return []
    
    def get_shariah_compliant_stocks(self, date: datetime) -> List[str]:
        """Get Shariah compliant stocks for a specific date"""
        try:
            # For historical purposes, we'll use a subset of known Shariah stocks
            # In production, this would query historical Shariah compliance data
            
            shariah_stocks = [
                'TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS',
                'HINDUNILVR.NS', 'ITC.NS', 'ASIANPAINT.NS', 'TITAN.NS',
                'NESTLEIND.NS', 'SUNPHARMA.NS', 'CIPLA.NS', 'DRREDDY.NS',
                'DIVISLAB.NS', 'BRITANNIA.NS', 'DABUR.NS', 'GODREJCP.NS',
                'MARUTI.NS', 'HEROMOTOCO.NS', 'BAJAJ-AUTO.NS', 'EICHERMOT.NS',
                'ULTRACEMCO.NS', 'SHREECEM.NS', 'COALINDIA.NS', 'NTPC.NS',
                'POWERGRID.NS', 'ONGC.NS', 'BPCL.NS', 'HINDALCO.NS',
                'TATASTEEL.NS', 'JSWSTEEL.NS', 'GRASIM.NS', 'LT.NS'
            ]
            
            return shariah_stocks
            
        except Exception as e:
            logger.error(f"Error getting Shariah stocks for {date}: {str(e)}")
            return []
    
    def get_market_context(self, date: datetime) -> Dict:
        """Get market context for a specific date"""
        try:
            # Get NIFTY data for market context
            nifty_symbol = '^NSEI'
            end_date = date + timedelta(days=1)
            start_date = date - timedelta(days=252)  # 1 year lookback
            
            nifty_data = yf.download(nifty_symbol, start=start_date, end=end_date, progress=False)
            
            if nifty_data.empty:
                return self._default_market_context()
            
            # Calculate market indicators
            current_price = nifty_data['Close'].iloc[-1]
            sma_50 = nifty_data['Close'].rolling(50).mean().iloc[-1]
            sma_200 = nifty_data['Close'].rolling(200).mean().iloc[-1]
            
            # Volatility (20-day)
            returns = nifty_data['Close'].pct_change()
            volatility = returns.rolling(20).std().iloc[-1] * np.sqrt(252)
            
            # Market trend
            trend_20d = (current_price / nifty_data['Close'].iloc[-20] - 1) if len(nifty_data) >= 20 else 0
            trend_50d = (current_price / nifty_data['Close'].iloc[-50] - 1) if len(nifty_data) >= 50 else 0
            
            # Market regime
            if sma_50 > sma_200 and volatility < 0.20:
                regime = 'BULL'
            elif sma_50 < sma_200 and volatility < 0.25:
                regime = 'BEAR'
            elif volatility > 0.25:
                regime = 'HIGH_VOLATILITY'
            else:
                regime = 'SIDEWAYS'
            
            return {
                'date': date.strftime('%Y-%m-%d'),
                'nifty_price': current_price,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'volatility': volatility,
                'trend_20d': trend_20d,
                'trend_50d': trend_50d,
                'regime': regime,
                'bull_market': 1 if regime == 'BULL' else 0,
                'bear_market': 1 if regime == 'BEAR' else 0,
                'high_vol_market': 1 if regime == 'HIGH_VOLATILITY' else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting market context for {date}: {str(e)}")
            return self._default_market_context()
    
    def _default_market_context(self) -> Dict:
        """Default market context when data is unavailable"""
        return {
            'date': '',
            'nifty_price': 10000,
            'sma_50': 10000,
            'sma_200': 10000,
            'volatility': 0.20,
            'trend_20d': 0.0,
            'trend_50d': 0.0,
            'regime': 'SIDEWAYS',
            'bull_market': 0,
            'bear_market': 0,
            'high_vol_market': 0
        }
    
    def generate_historical_signals(self, date: datetime, symbols: List[str]) -> List[Dict]:
        """Generate signals for a specific historical date"""
        try:
            logger.info(f"Generating signals for {date.strftime('%Y-%m-%d')}")
            
            # Get market context
            market_context = self.get_market_context(date)
            
            # Initialize strategies (simplified for historical generation)
            strategies = {
                'momentum': self._momentum_strategy,
                'low_volatility': self._low_volatility_strategy,
                'fundamental_growth': self._fundamental_growth_strategy,
                'mean_reversion': self._mean_reversion_strategy,
                'breakout': self._breakout_strategy
            }
            
            all_signals = []
            
            for strategy_name, strategy_func in strategies.items():
                try:
                    strategy_signals = strategy_func(date, symbols, market_context)
                    
                    for signal in strategy_signals:
                        signal.update({
                            'strategy': strategy_name,
                            'generated_date': date.strftime('%Y-%m-%d'),
                            'market_context': market_context
                        })
                        all_signals.append(signal)
                        
                except Exception as e:
                    logger.error(f"Error in {strategy_name} strategy for {date}: {str(e)}")
                    continue
            
            logger.info(f"Generated {len(all_signals)} signals for {date.strftime('%Y-%m-%d')}")
            return all_signals
            
        except Exception as e:
            logger.error(f"Error generating historical signals for {date}: {str(e)}")
            return []
    
    def _momentum_strategy(self, date: datetime, symbols: List[str], market_context: Dict) -> List[Dict]:
        """Simplified momentum strategy for historical data"""
        signals = []
        
        for symbol in symbols[:10]:  # Limit for performance
            try:
                # Get historical data up to this date
                end_date = date + timedelta(days=1)
                start_date = date - timedelta(days=252)
                
                stock_data = yf.download(symbol, start=start_date, end=end_date, progress=False)
                
                if len(stock_data) < 50:
                    continue
                
                # Calculate momentum indicators
                current_price = stock_data['Close'].iloc[-1]
                sma_20 = stock_data['Close'].rolling(20).mean().iloc[-1]
                sma_50 = stock_data['Close'].rolling(50).mean().iloc[-1]
                
                # Price momentum
                momentum_20d = (current_price / stock_data['Close'].iloc[-20] - 1) if len(stock_data) >= 20 else 0
                momentum_50d = (current_price / stock_data['Close'].iloc[-50] - 1) if len(stock_data) >= 50 else 0
                
                # Volume momentum
                avg_volume = stock_data['Volume'].rolling(20).mean().iloc[-1]
                current_volume = stock_data['Volume'].iloc[-1]
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                
                # RSI
                delta = stock_data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
                
                # Generate signal
                momentum_score = 0
                
                # Price momentum conditions
                if momentum_20d > 0.05:  # 5% gain in 20 days
                    momentum_score += 2
                if momentum_50d > 0.10:  # 10% gain in 50 days
                    momentum_score += 2
                if current_price > sma_20 > sma_50:  # Uptrend
                    momentum_score += 2
                if volume_ratio > 1.5:  # High volume
                    momentum_score += 1
                if 40 < current_rsi < 70:  # Not overbought
                    momentum_score += 1
                
                # Market regime adjustment
                if market_context['regime'] == 'BULL':
                    momentum_score += 1
                elif market_context['regime'] == 'BEAR':
                    momentum_score -= 2
                
                # Generate signal if score is high enough
                if momentum_score >= 5:
                    confidence = min(0.9, momentum_score / 8.0)
                    
                    signal = {
                        'symbol': symbol.replace('.NS', ''),
                        'signal_type': 'BUY',
                        'confidence': confidence,
                        'entry_price': current_price,
                        'momentum_score': momentum_score,
                        'momentum_20d': momentum_20d,
                        'momentum_50d': momentum_50d,
                        'rsi': current_rsi,
                        'volume_ratio': volume_ratio,
                        'price_above_sma20': 1 if current_price > sma_20 else 0,
                        'price_above_sma50': 1 if current_price > sma_50 else 0
                    }
                    
                    signals.append(signal)
                    
            except Exception as e:
                logger.error(f"Error processing {symbol} in momentum strategy: {str(e)}")
                continue
        
        return signals
    
    def _low_volatility_strategy(self, date: datetime, symbols: List[str], market_context: Dict) -> List[Dict]:
        """Simplified low volatility strategy"""
        signals = []
        
        for symbol in symbols[:10]:
            try:
                end_date = date + timedelta(days=1)
                start_date = date - timedelta(days=252)
                
                stock_data = yf.download(symbol, start=start_date, end=end_date, progress=False)
                
                if len(stock_data) < 60:
                    continue
                
                # Calculate volatility metrics
                returns = stock_data['Close'].pct_change()
                volatility_20d = returns.rolling(20).std() * np.sqrt(252)
                volatility_60d = returns.rolling(60).std() * np.sqrt(252)
                
                current_vol = volatility_20d.iloc[-1]
                avg_vol = volatility_60d.iloc[-1]
                
                # Price stability
                current_price = stock_data['Close'].iloc[-1]
                price_range_20d = (stock_data['High'].rolling(20).max() / stock_data['Low'].rolling(20).min()).iloc[-1] - 1
                
                # Generate signal for low volatility stocks
                if current_vol < 0.25 and current_vol < avg_vol and price_range_20d < 0.20:
                    
                    # Additional quality checks
                    sma_20 = stock_data['Close'].rolling(20).mean().iloc[-1]
                    trend = (current_price / sma_20 - 1)
                    
                    if trend > -0.05:  # Not in strong downtrend
                        confidence = max(0.4, 1 - current_vol)  # Lower vol = higher confidence
                        
                        signal = {
                            'symbol': symbol.replace('.NS', ''),
                            'signal_type': 'BUY',
                            'confidence': confidence,
                            'entry_price': current_price,
                            'volatility_20d': current_vol,
                            'volatility_60d': avg_vol,
                            'price_range_20d': price_range_20d,
                            'trend_20d': trend,
                            'low_vol_score': 1 - current_vol
                        }
                        
                        signals.append(signal)
                        
            except Exception as e:
                logger.error(f"Error processing {symbol} in low volatility strategy: {str(e)}")
                continue
        
        return signals
    
    def _fundamental_growth_strategy(self, date: datetime, symbols: List[str], market_context: Dict) -> List[Dict]:
        """Simplified fundamental growth strategy"""
        signals = []
        
        # For historical data, we'll use simplified fundamental screening
        # In production, this would use historical fundamental data
        
        for symbol in symbols[:5]:  # Limited for performance
            try:
                end_date = date + timedelta(days=1)
                start_date = date - timedelta(days=252)
                
                stock_data = yf.download(symbol, start=start_date, end=end_date, progress=False)
                
                if len(stock_data) < 100:
                    continue
                
                current_price = stock_data['Close'].iloc[-1]
                
                # Price-based growth indicators (proxy for fundamental growth)
                price_3m = stock_data['Close'].iloc[-60] if len(stock_data) >= 60 else current_price
                price_6m = stock_data['Close'].iloc[-120] if len(stock_data) >= 120 else current_price
                
                growth_3m = (current_price / price_3m - 1) if price_3m > 0 else 0
                growth_6m = (current_price / price_6m - 1) if price_6m > 0 else 0
                
                # Volume growth (proxy for interest)
                volume_avg = stock_data['Volume'].rolling(60).mean().iloc[-1]
                volume_recent = stock_data['Volume'].rolling(20).mean().iloc[-1]
                volume_growth = (volume_recent / volume_avg - 1) if volume_avg > 0 else 0
                
                # Generate signal for growth stocks
                if growth_3m > 0.05 and growth_6m > 0.10 and volume_growth > 0:
                    
                    confidence = min(0.8, (growth_3m + growth_6m) / 2)
                    
                    signal = {
                        'symbol': symbol.replace('.NS', ''),
                        'signal_type': 'BUY',
                        'confidence': confidence,
                        'entry_price': current_price,
                        'growth_3m': growth_3m,
                        'growth_6m': growth_6m,
                        'volume_growth': volume_growth,
                        'growth_score': (growth_3m + growth_6m) / 2
                    }
                    
                    signals.append(signal)
                    
            except Exception as e:
                logger.error(f"Error processing {symbol} in growth strategy: {str(e)}")
                continue
        
        return signals
    
    def _mean_reversion_strategy(self, date: datetime, symbols: List[str], market_context: Dict) -> List[Dict]:
        """Simplified mean reversion strategy"""
        signals = []
        
        for symbol in symbols[:8]:
            try:
                end_date = date + timedelta(days=1)
                start_date = date - timedelta(days=100)
                
                stock_data = yf.download(symbol, start=start_date, end=end_date, progress=False)
                
                if len(stock_data) < 50:
                    continue
                
                current_price = stock_data['Close'].iloc[-1]
                sma_20 = stock_data['Close'].rolling(20).mean().iloc[-1]
                sma_50 = stock_data['Close'].rolling(50).mean().iloc[-1]
                
                # Bollinger Bands
                bb_std = stock_data['Close'].rolling(20).std().iloc[-1]
                bb_upper = sma_20 + (2 * bb_std)
                bb_lower = sma_20 - (2 * bb_std)
                
                # RSI
                delta = stock_data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
                
                # Mean reversion signal (oversold conditions)
                if (current_price < bb_lower and current_rsi < 35 and 
                    current_price < sma_20 * 0.95):  # 5% below SMA
                    
                    # Check for potential reversal
                    recent_low = stock_data['Low'].rolling(5).min().iloc[-1]
                    if current_price > recent_low * 1.02:  # Bouncing from recent low
                        
                        confidence = max(0.4, (35 - current_rsi) / 35)
                        
                        signal = {
                            'symbol': symbol.replace('.NS', ''),
                            'signal_type': 'BUY',
                            'confidence': confidence,
                            'entry_price': current_price,
                            'rsi': current_rsi,
                            'bb_position': (current_price - bb_lower) / (bb_upper - bb_lower),
                            'price_vs_sma20': current_price / sma_20 - 1,
                            'mean_reversion_score': (35 - current_rsi) / 35
                        }
                        
                        signals.append(signal)
                        
            except Exception as e:
                logger.error(f"Error processing {symbol} in mean reversion strategy: {str(e)}")
                continue
        
        return signals
    
    def _breakout_strategy(self, date: datetime, symbols: List[str], market_context: Dict) -> List[Dict]:
        """Simplified breakout strategy"""
        signals = []
        
        for symbol in symbols[:8]:
            try:
                end_date = date + timedelta(days=1)
                start_date = date - timedelta(days=100)
                
                stock_data = yf.download(symbol, start=start_date, end=end_date, progress=False)
                
                if len(stock_data) < 50:
                    continue
                
                current_price = stock_data['Close'].iloc[-1]
                
                # Resistance levels
                high_20d = stock_data['High'].rolling(20).max().iloc[-1]
                high_50d = stock_data['High'].rolling(50).max().iloc[-1]
                
                # Volume confirmation
                avg_volume = stock_data['Volume'].rolling(20).mean().iloc[-1]
                current_volume = stock_data['Volume'].iloc[-1]
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                
                # Breakout conditions
                if (current_price > high_20d * 1.02 and  # 2% above 20-day high
                    current_price > high_50d * 1.01 and  # 1% above 50-day high
                    volume_ratio > 1.5):  # High volume confirmation
                    
                    # Additional momentum check
                    price_5d_ago = stock_data['Close'].iloc[-5] if len(stock_data) >= 5 else current_price
                    momentum = (current_price / price_5d_ago - 1) if price_5d_ago > 0 else 0
                    
                    if momentum > 0.03:  # 3% gain in 5 days
                        confidence = min(0.8, momentum * 10)  # Scale momentum to confidence
                        
                        signal = {
                            'symbol': symbol.replace('.NS', ''),
                            'signal_type': 'BUY',
                            'confidence': confidence,
                            'entry_price': current_price,
                            'breakout_level': high_20d,
                            'volume_ratio': volume_ratio,
                            'momentum_5d': momentum,
                            'breakout_strength': (current_price / high_20d - 1)
                        }
                        
                        signals.append(signal)
                        
            except Exception as e:
                logger.error(f"Error processing {symbol} in breakout strategy: {str(e)}")
                continue
        
        return signals
    
    def collect_historical_data(self, sample_dates: Optional[List[str]] = None) -> pd.DataFrame:
        """Collect historical signals for ML training"""
        logger.info("Starting historical data collection...")
        
        # Get stock universe
        symbols = self.get_nse_universe()
        logger.info(f"Processing {len(symbols)} symbols")
        
        # Generate sample dates if not provided
        if sample_dates is None:
            # Sample every 30 days from start to end date
            date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='30D')
            sample_dates = [date.strftime('%Y-%m-%d') for date in date_range]
        
        logger.info(f"Processing {len(sample_dates)} dates")
        
        all_historical_signals = []
        
        for date_str in sample_dates:
            try:
                date = pd.to_datetime(date_str)
                
                # Skip weekends
                if date.weekday() >= 5:
                    continue
                
                # Get Shariah compliant stocks for this date
                shariah_symbols = self.get_shariah_compliant_stocks(date)
                
                # Generate signals for this date
                signals = self.generate_historical_signals(date, shariah_symbols)
                
                all_historical_signals.extend(signals)
                
                # Progress update
                if len(all_historical_signals) % 100 == 0:
                    logger.info(f"Collected {len(all_historical_signals)} historical signals...")
                    
            except Exception as e:
                logger.error(f"Error processing date {date_str}: {str(e)}")
                continue
        
        # Convert to DataFrame
        df = pd.DataFrame(all_historical_signals)
        
        logger.info(f"Historical data collection complete: {len(df)} signals")
        
        # Save to file
        output_file = 'ml/data/historical_signals.pkl'
        df.to_pickle(output_file)
        logger.info(f"Historical signals saved to {output_file}")
        
        return df

def main():
    """Run historical data collection"""
    print("🚀 Starting Historical Data Collection for ML Training")
    print("=" * 60)
    
    # Initialize collector
    collector = HistoricalDataCollector(start_date='2020-01-01', end_date='2024-12-31')
    
    # Collect historical data
    historical_df = collector.collect_historical_data()
    
    if len(historical_df) > 0:
        print(f"\n✅ Historical Data Collection Complete!")
        print(f"📊 Total signals collected: {len(historical_df)}")
        print(f"📅 Date range: {historical_df['generated_date'].min()} to {historical_df['generated_date'].max()}")
        print(f"🎯 Strategies: {historical_df['strategy'].unique()}")
        print(f"📈 Signal breakdown:")
        print(historical_df['strategy'].value_counts())
        
        print(f"\n💾 Data saved to: ml/data/historical_signals.pkl")
        print(f"🔄 Next step: Run outcome tracking to calculate returns")
    else:
        print("❌ No historical data collected")

if __name__ == "__main__":
    main()
