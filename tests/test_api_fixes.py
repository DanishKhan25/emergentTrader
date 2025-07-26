#!/usr/bin/env python3
"""
Test script to validate the EmergentTrader API fixes
Tests the stocks/refresh endpoint and signal tracking functionality
"""

import sys
import os
import json
import requests
import time
from datetime import datetime

# Add the python_backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

def test_python_api_directly():
    """Test the Python API handler directly"""
    print("=" * 60)
    print("TESTING PYTHON API DIRECTLY")
    print("=" * 60)
    
    try:
        from python_backend.api_handler import handle_api_request
        
        # Test 1: Get all stocks
        print("\n1. Testing stocks/all endpoint...")
        result = handle_api_request('stocks/all', 'GET')
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            stock_count = len(result.get('data', {}).get('stocks', []))
            print(f"   Stock count: {stock_count}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        # Test 2: Refresh stock data
        print("\n2. Testing stocks/refresh endpoint...")
        test_symbols = ['RELIANCE', 'TCS', 'HDFCBANK']
        result = handle_api_request('stocks/refresh', 'POST', {'symbols': test_symbols})
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            data = result.get('data', {})
            print(f"   Refreshed: {data.get('successful_count', 0)} stocks")
            print(f"   Failed: {data.get('failed_count', 0)} stocks")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        # Test 3: Generate signals
        print("\n3. Testing signal generation...")
        result = handle_api_request('signals/generate', 'POST', {
            'strategy': 'momentum',
            'symbols': ['RELIANCE', 'TCS']
        })
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            signals = result.get('data', {}).get('signals', [])
            print(f"   Generated signals: {len(signals)}")
            
            # Test signal tracking if we have signals
            if signals:
                signal_id = signals[0].get('signal_id')
                if signal_id:
                    print(f"\n4. Testing signal tracking with ID: {signal_id}")
                    track_result = handle_api_request('signals/track', 'POST', {'signal_id': signal_id})
                    print(f"   Tracking success: {track_result.get('success', False)}")
                    if not track_result.get('success'):
                        print(f"   Tracking error: {track_result.get('error', 'Unknown error')}")
                else:
                    print("\n4. Signal tracking test skipped - no signal_id found")
            else:
                print("\n4. Signal tracking test skipped - no signals generated")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        # Test 5: Test empty signal_id tracking (should fail gracefully)
        print("\n5. Testing signal tracking with empty signal_id...")
        result = handle_api_request('signals/track', 'POST', {'signal_id': ''})
        print(f"   Success: {result.get('success', False)} (should be False)")
        print(f"   Error message: {result.get('error', 'No error message')}")
        
    except Exception as e:
        print(f"Error testing Python API: {str(e)}")
        import traceback
        traceback.print_exc()

def test_next_js_api():
    """Test the Next.js API endpoints (requires server to be running)"""
    print("\n" + "=" * 60)
    print("TESTING NEXT.JS API ENDPOINTS")
    print("=" * 60)
    
    base_url = "http://localhost:3000/api"
    
    # Test if server is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Server status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Server not accessible: {str(e)}")
        print("Please start the Next.js server with 'npm run dev' or 'yarn dev'")
        return
    
    # Test endpoints
    endpoints_to_test = [
        ("GET", "/stocks/all", None),
        ("POST", "/stocks/refresh", {"symbols": ["RELIANCE", "TCS"]}),
        ("POST", "/signals/generate", {"strategy": "momentum", "symbols": ["RELIANCE"]}),
        ("POST", "/signals/track", {"signal_id": "test-signal-123"}),
        ("GET", "/signals/today", None),
    ]
    
    for method, endpoint, payload in endpoints_to_test:
        print(f"\nTesting {method} {endpoint}...")
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=payload, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success', False)}")
                if not data.get('success'):
                    print(f"   Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   HTTP Error: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   Request failed: {str(e)}")

def main():
    """Run all tests"""
    print("EmergentTrader API Fix Validation")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Test Python API directly
    test_python_api_directly()
    
    # Test Next.js API (if server is running)
    test_next_js_api()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("1. stocks/refresh endpoint has been added")
    print("2. Signal tracking improved with better error handling")
    print("3. Signal IDs are now generated for all signals")
    print("4. Empty signal_id requests are handled gracefully")
    print("\nIf any tests failed, check the error messages above.")
    print("Make sure MongoDB is running and the Next.js server is started.")

if __name__ == "__main__":
    main()
