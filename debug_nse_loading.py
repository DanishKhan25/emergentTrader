#!/usr/bin/env python3
"""
Debug NSE Data Loading - Show detailed logs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

import logging
import pandas as pd
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_nse_data_loading():
    """Debug the NSE data loading process with detailed logs"""
    
    print("🔍 Debug: NSE Data Loading Process")
    print("=" * 50)
    
    try:
        print("📊 Step 1: Loading CSV file...")
        df = pd.read_csv('data/nse_raw.csv')
        logger.info(f"CSV loaded successfully: {len(df)} rows")
        
        print(f"✅ Loaded {len(df)} rows from CSV")
        
        print("\n📋 Step 2: Analyzing data structure...")
        print("Columns:", df.columns.tolist())
        print("Data types:", df.dtypes.to_dict())
        
        print("\n📊 Step 3: Sample data (first 3 rows):")
        print(df.head(3).to_string())
        
        print("\n📈 Step 4: Series distribution:")
        series_counts = df[' SERIES'].value_counts()
        print(series_counts.head(10))
        
        print("\n🔍 Step 5: Processing stocks...")
        stocks = []
        valid_stocks = []
        
        for idx, row in df.iterrows():
            symbol = row.get('SYMBOL', '').strip()
            series = row.get(' SERIES', '').strip()
            face_value = row.get(' FACE VALUE', 0)
            
            if symbol and len(symbol) > 0:
                stock_data = {
                    'symbol': symbol,
                    'company_name': row.get('NAME OF COMPANY', '').strip(),
                    'series': series,
                    'listing_date': row.get(' DATE OF LISTING', ''),
                    'paid_up_value': row.get(' PAID UP VALUE', 0),
                    'market_lot': row.get(' MARKET LOT', 0),
                    'isin_number': row.get(' ISIN NUMBER', '').strip(),
                    'face_value': face_value
                }
                stocks.append(stock_data)
                
                # Apply filtering logic
                if (series.upper() in ['EQ', 'BE', 'SM', 'BZ', 'BL'] and 
                    len(symbol) > 0 and 
                    not symbol.startswith('$') and
                    face_value > 0):
                    valid_stocks.append(stock_data)
                    
                # Show first few valid stocks
                if len(valid_stocks) <= 5:
                    logger.debug(f"Valid stock {len(valid_stocks)}: {symbol} ({series}) - {stock_data['company_name']}")
        
        print(f"\n📊 Step 6: Filtering results:")
        print(f"Total stocks processed: {len(stocks)}")
        print(f"Valid stocks after filtering: {len(valid_stocks)}")
        
        if len(valid_stocks) == 0:
            print("\n❌ No valid stocks found! Debugging filtering criteria...")
            
            # Debug filtering criteria
            print("\n🔍 Debugging filtering issues:")
            sample_stocks = stocks[:10]
            
            for stock in sample_stocks:
                symbol = stock['symbol']
                series = stock['series']
                face_value = stock['face_value']
                
                print(f"\nStock: {symbol}")
                print(f"  Series: '{series}' (upper: '{series.upper()}')")
                print(f"  Face value: {face_value} (type: {type(face_value)})")
                print(f"  Series check: {series.upper() in ['EQ', 'BE', 'SM', 'BZ', 'BL']}")
                print(f"  Symbol check: {len(symbol) > 0 and not symbol.startswith('$')}")
                print(f"  Face value check: {face_value > 0}")
                
                # Try to fix face value issue
                try:
                    face_val_num = float(face_value) if face_value else 0
                    print(f"  Face value as float: {face_val_num}")
                except:
                    print(f"  Face value conversion failed")
        
        else:
            print(f"\n✅ Successfully loaded {len(valid_stocks)} valid stocks")
            print("\nFirst 10 valid stocks:")
            for i, stock in enumerate(valid_stocks[:10], 1):
                print(f"{i:2d}. {stock['symbol']:12} | {stock['series']:3} | {stock['company_name'][:40]:40}")
        
        return valid_stocks
        
    except Exception as e:
        logger.error(f"Error in debug process: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def test_batch_processing_setup():
    """Test if batch processing components work"""
    
    print(f"\n🔧 Testing Batch Processing Components")
    print("=" * 45)
    
    try:
        from services.yfinance_fetcher import YFinanceFetcher
        from core.enhanced_shariah_filter_batched import BatchedShariahFilter
        
        print("✅ Successfully imported YFinanceFetcher")
        print("✅ Successfully imported BatchedShariahFilter")
        
        # Test initialization
        fetcher = YFinanceFetcher()
        batched_filter = BatchedShariahFilter(batch_size=50)
        
        print("✅ Successfully initialized components")
        print(f"   Batch size: {batched_filter.batch_size}")
        print(f"   Delay between batches: {batched_filter.batch_config.delay_between_batches}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing batch components: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting NSE Data Loading Debug")
    print("=" * 40)
    
    # Debug NSE data loading
    valid_stocks = debug_nse_data_loading()
    
    # Test batch processing setup
    batch_ready = test_batch_processing_setup()
    
    print(f"\n📋 Debug Summary:")
    print(f"   Valid stocks loaded: {len(valid_stocks)}")
    print(f"   Batch processing ready: {batch_ready}")
    
    if len(valid_stocks) > 0 and batch_ready:
        print(f"\n✅ System is ready for full NSE processing!")
        print(f"   Estimated processing time: {len(valid_stocks) * 2.5 / 60:.1f} minutes")
    else:
        print(f"\n❌ Issues found that need to be resolved before processing")
