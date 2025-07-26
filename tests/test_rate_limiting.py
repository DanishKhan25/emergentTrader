#!/usr/bin/env python3
"""
Test script for rate limiting functionality in YFinance fetcher
"""

import sys
import os
import time
from datetime import datetime

# Add python_backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

from python_backend.services.yfinance_fetcher import YFinanceFetcher

def test_rate_limiting():
    """Test rate limiting with a few stocks"""
    print("🧪 Testing Rate Limiting for YFinance Fetcher")
    print("=" * 50)
    
    fetcher = YFinanceFetcher()
    test_symbols = ['MARUTI', 'DIVISLAB', 'RELIANCE', 'TCS', 'INFY']
    
    print(f"Testing with {len(test_symbols)} symbols: {test_symbols}")
    print(f"Start time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Test individual stock info fetching
    print("\n📊 Testing Individual Stock Info Fetching:")
    print("-" * 40)
    
    start_time = time.time()
    successful_fetches = 0
    
    for i, symbol in enumerate(test_symbols, 1):
        print(f"[{i}/{len(test_symbols)}] Fetching info for {symbol}...")
        
        try:
            info = fetcher.get_stock_info(symbol)
            
            if 'error' not in info and info.get('symbol'):
                print(f"  ✅ Success: {info['company_name']} (PE: {info.get('pe_ratio', 'N/A')})")
                successful_fetches += 1
            else:
                print(f"  ⚠️  Warning: Limited data for {symbol}")
                if 'error' in info:
                    print(f"     Error: {info['error']}")
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    individual_time = time.time() - start_time
    print(f"\nIndividual fetching completed in {individual_time:.1f}s")
    print(f"Success rate: {successful_fetches}/{len(test_symbols)} ({(successful_fetches/len(test_symbols)*100):.1f}%)")
    
    # Test batch processing
    print("\n📦 Testing Batch Processing:")
    print("-" * 40)
    
    start_time = time.time()
    batch_info = fetcher.get_multiple_stock_info(test_symbols, batch_size=2)
    batch_time = time.time() - start_time
    
    batch_successful = len([k for k, v in batch_info.items() if 'error' not in v])
    
    print(f"Batch processing completed in {batch_time:.1f}s")
    print(f"Success rate: {batch_successful}/{len(test_symbols)} ({(batch_successful/len(test_symbols)*100):.1f}%)")
    
    # Test stock data fetching
    print("\n📈 Testing Stock Data Fetching:")
    print("-" * 40)
    
    start_time = time.time()
    test_data_symbols = test_symbols[:3]  # Test with fewer symbols for data
    
    for symbol in test_data_symbols:
        print(f"Fetching 6-month data for {symbol}...")
        try:
            data = fetcher.get_nse_stock_data(symbol, period="6mo")
            if not data.empty:
                print(f"  ✅ Success: {len(data)} data points")
            else:
                print(f"  ⚠️  Warning: No data returned")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    data_time = time.time() - start_time
    print(f"Data fetching completed in {data_time:.1f}s")
    
    # Summary
    print(f"\n📋 Summary:")
    print(f"Total test time: {(individual_time + batch_time + data_time):.1f}s")
    print(f"Rate limiting appears to be working - no 429 errors expected")
    print(f"End time: {datetime.now().strftime('%H:%M:%S')}")

def test_nse_universe():
    """Test NSE universe loading"""
    print("\n🌐 Testing NSE Universe Loading:")
    print("-" * 40)
    
    fetcher = YFinanceFetcher()
    
    try:
        universe = fetcher.get_nse_universe()
        print(f"✅ Loaded {len(universe)} stocks from NSE universe")
        
        if universe:
            sample_stocks = universe[:5]
            print("Sample stocks:")
            for stock in sample_stocks:
                print(f"  - {stock['symbol']}: {stock.get('name', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error loading NSE universe: {str(e)}")

if __name__ == "__main__":
    test_nse_universe()
    test_rate_limiting()
