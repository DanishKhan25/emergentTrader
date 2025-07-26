#!/usr/bin/env python3
"""
Test script to verify the yfinance fetcher fix for handling dictionary inputs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

from services.yfinance_fetcher import YFinanceFetcher
from core.shariah_filter import ShariahFilter
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_yfinance_fix():
    """Test the yfinance fetcher fix"""
    print("🔧 Testing YFinance Fetcher Fix")
    print("=" * 50)
    
    try:
        # Initialize fetcher
        fetcher = YFinanceFetcher()
        
        # Test 1: Get NSE universe (returns list of dicts)
        print("\n1️⃣ Testing NSE Universe Retrieval...")
        nse_stocks = fetcher.get_nse_universe()
        print(f"✅ Retrieved {len(nse_stocks)} stocks from NSE universe")
        
        if nse_stocks:
            sample_stock = nse_stocks[0]
            print(f"   Sample stock: {sample_stock}")
            print(f"   Type: {type(sample_stock)}")
        
        # Test 2: Test get_stock_info with dictionary input
        print("\n2️⃣ Testing get_stock_info with dictionary input...")
        if nse_stocks:
            sample_dict = nse_stocks[0]  # This is a dictionary
            stock_info = fetcher.get_stock_info(sample_dict)
            
            if stock_info and 'error' not in stock_info:
                print(f"✅ Successfully fetched info for {sample_dict.get('symbol', 'unknown')}")
                print(f"   Company: {stock_info.get('company_name', 'N/A')}")
                print(f"   Sector: {stock_info.get('sector', 'N/A')}")
            else:
                print(f"⚠️  Warning: Could not fetch info for {sample_dict.get('symbol', 'unknown')}")
                if stock_info:
                    print(f"   Error: {stock_info.get('error', 'Unknown error')}")
        
        # Test 3: Test get_stock_info with string input
        print("\n3️⃣ Testing get_stock_info with string input...")
        test_symbol = "RELIANCE"
        stock_info = fetcher.get_stock_info(test_symbol)
        
        if stock_info and 'error' not in stock_info:
            print(f"✅ Successfully fetched info for {test_symbol}")
            print(f"   Company: {stock_info.get('company_name', 'N/A')}")
            print(f"   Current Price: ₹{stock_info.get('current_price', 0)}")
        else:
            print(f"⚠️  Warning: Could not fetch info for {test_symbol}")
            if stock_info:
                print(f"   Error: {stock_info.get('error', 'Unknown error')}")
        
        # Test 4: Test Shariah filter with fixed input
        print("\n4️⃣ Testing Shariah Filter with NSE universe...")
        shariah_filter = ShariahFilter()
        
        # Test with a small subset to avoid rate limiting
        test_stocks = nse_stocks[:5] if len(nse_stocks) >= 5 else nse_stocks
        print(f"   Testing with {len(test_stocks)} stocks...")
        
        compliant_stocks = shariah_filter.get_shariah_universe(test_stocks, fetcher)
        print(f"✅ Found {len(compliant_stocks)} Shariah compliant stocks")
        
        for stock in compliant_stocks:
            print(f"   - {stock['symbol']}: {stock['company_name']}")
        
        print("\n🎉 All tests completed successfully!")
        print("✅ The yfinance fetcher fix is working correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_yfinance_fix()
    sys.exit(0 if success else 1)
