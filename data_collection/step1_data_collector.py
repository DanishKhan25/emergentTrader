#!/usr/bin/env python3
"""
Step 1: Simple Historical Data Collector
Downloads 10 years of data for major Indian stocks
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime

def download_10_year_data():
    """Download 10 years of historical data"""
    
    # Major Indian stocks for testing
    symbols = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
        "ICICIBANK.NS", "KOTAKBANK.NS", "BHARTIARTL.NS", "ITC.NS", "SBIN.NS",
        "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS", "AXISBANK.NS"
    ]
    
    print("📊 Downloading 10-year historical data...")
    
    # Create data directory
    os.makedirs("historical_data", exist_ok=True)
    
    successful_downloads = 0
    
    for symbol in symbols:
        try:
            print(f"Downloading {symbol}...")
            
            # Download 2014-2025 data
            ticker = yf.Ticker(symbol)
            data = ticker.history(start="2014-01-01", end="2025-01-01")
            
            if len(data) > 0:
                # Save to CSV
                data.to_csv(f"historical_data/{symbol.replace('.NS', '')}_10year.csv")
                print(f"✅ {symbol}: {len(data)} records saved")
                successful_downloads += 1
            else:
                print(f"❌ {symbol}: No data")
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {str(e)}")
            
    print(f"\n✅ Downloaded data for {successful_downloads}/{len(symbols)} symbols")
    print("📁 Data saved in 'historical_data/' folder")
    
    return successful_downloads > 0

if __name__ == "__main__":
    success = download_10_year_data()
    if success:
        print("\n🚀 Next: Run step2_train_2019.py")
    else:
        print("\n❌ Data download failed")
