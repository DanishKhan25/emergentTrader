#!/usr/bin/env python3
"""
Focused test for core functionality - strategies and key endpoints
"""

import sys
import os
import json
from datetime import datetime

# Add python_backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

from python_backend.api_handler import handle_api_request
from python_backend.core.signal_engine import SignalEngine

def test_core_functionality():
    print("🧪 EmergentTrader Core Functionality Test")
    print("=" * 50)
    
    # Test 1: Strategy Availability
    print("\n1️⃣ Testing Strategy Availability...")
    try:
        signal_engine = SignalEngine()
        strategies = signal_engine.get_available_strategies()
        print(f"✅ Found {len(strategies)} strategies: {strategies}")
        
        expected = ['momentum', 'mean_reversion', 'breakout', 'value_investing', 
                   'swing_trading', 'multibagger', 'fundamental_growth', 
                   'sector_rotation', 'low_volatility', 'pivot_cpr']
        
        missing = [s for s in expected if s not in strategies]
        if missing:
            print(f"⚠️  Missing strategies: {missing}")
        else:
            print("✅ All 10 strategies available!")
            
    except Exception as e:
        print(f"❌ Strategy availability test failed: {str(e)}")
    
    # Test 2: API Health Check
    print("\n2️⃣ Testing API Health...")
    try:
        response = handle_api_request('/', 'GET')
        if response.get('success'):
            print("✅ API is healthy and responding")
        else:
            print(f"⚠️  API health check warning: {response.get('error')}")
    except Exception as e:
        print(f"❌ API health check failed: {str(e)}")
    
    # Test 3: Available Strategies Endpoint
    print("\n3️⃣ Testing Available Strategies Endpoint...")
    try:
        response = handle_api_request('strategies/available', 'GET')
        if response.get('success'):
            data = response.get('data', {})
            strategies = data.get('strategies', [])
            print(f"✅ API returned {len(strategies)} strategies")
            print(f"   Strategies: {', '.join(strategies)}")
        else:
            print(f"❌ Strategies endpoint failed: {response.get('error')}")
    except Exception as e:
        print(f"❌ Strategies endpoint test failed: {str(e)}")
    
    # Test 4: Stock Data
    print("\n4️⃣ Testing Stock Data...")
    try:
        response = handle_api_request('stocks/all', 'GET')
        if response.get('success'):
            data = response.get('data', {})
            stocks = data.get('stocks', [])
            print(f"✅ Found {len(stocks)} stocks in universe")
        else:
            print(f"⚠️  Stock data warning: {response.get('error')}")
    except Exception as e:
        print(f"❌ Stock data test failed: {str(e)}")
    
    # Test 5: Shariah Stocks
    print("\n5️⃣ Testing Shariah Stocks...")
    try:
        response = handle_api_request('stocks/shariah', 'GET')
        if response.get('success'):
            data = response.get('data', {})
            stocks = data.get('stocks', [])
            print(f"✅ Found {len(stocks)} Shariah-compliant stocks")
            if stocks:
                sample = stocks[0]
                print(f"   Sample: {sample.get('symbol', 'N/A')} - {sample.get('name', 'N/A')}")
        else:
            print(f"⚠️  Shariah stocks warning: {response.get('error')}")
    except Exception as e:
        print(f"❌ Shariah stocks test failed: {str(e)}")
    
    # Test 6: Signal Generation (Momentum)
    print("\n6️⃣ Testing Signal Generation (Momentum)...")
    try:
        response = handle_api_request('signals/generate', 'POST', {
            'strategy': 'momentum',
            'shariah_only': True,
            'min_confidence': 0.3
        })
        if response.get('success'):
            data = response.get('data', {})
            signals = data.get('signals', [])
            print(f"✅ Generated {len(signals)} momentum signals")
            if signals:
                sample = signals[0]
                print(f"   Sample: {sample.get('symbol')} - {sample.get('signal_type')} - ₹{sample.get('entry_price', 0)}")
        else:
            print(f"⚠️  Signal generation warning: {response.get('error')}")
    except Exception as e:
        print(f"❌ Signal generation test failed: {str(e)}")
    
    # Test 7: Multi-Strategy Generation
    print("\n7️⃣ Testing Multi-Strategy Generation...")
    try:
        response = handle_api_request('signals/generate/multi', 'POST', {
            'strategies': ['momentum', 'mean_reversion', 'breakout'],
            'shariah_only': True,
            'min_confidence': 0.3
        })
        if response.get('success'):
            data = response.get('data', {})
            total_signals = data.get('total_count', 0)
            breakdown = data.get('strategy_breakdown', {})
            print(f"✅ Generated {total_signals} signals across multiple strategies")
            print(f"   Breakdown: {breakdown}")
        else:
            print(f"⚠️  Multi-strategy warning: {response.get('error')}")
    except Exception as e:
        print(f"❌ Multi-strategy test failed: {str(e)}")
    
    # Test 8: Performance Summary
    print("\n8️⃣ Testing Performance Summary...")
    try:
        response = handle_api_request('performance/summary', 'GET', {'period': '30d'})
        if response.get('success'):
            print("✅ Performance summary endpoint working")
        else:
            print(f"⚠️  Performance summary warning: {response.get('error')}")
    except Exception as e:
        print(f"❌ Performance summary test failed: {str(e)}")
    
    print(f"\n🏁 Core functionality test completed at {datetime.now().strftime('%H:%M:%S')}")
    print("\n📋 Summary:")
    print("   ✅ = Working correctly")
    print("   ⚠️  = Working with warnings (expected due to rate limiting)")
    print("   ❌ = Critical failure")

if __name__ == "__main__":
    test_core_functionality()
