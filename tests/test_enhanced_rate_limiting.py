#!/usr/bin/env python3
"""
Test Enhanced Rate Limiting Resilience
Demonstrates the improved circuit breaker pattern and aggressive cache fallback
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

import logging
from datetime import datetime
from services.yfinance_fetcher_enhanced import EnhancedYFinanceFetcher
from core.enhanced_shariah_filter import EnhancedShariahFilter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_rate_limiting():
    """Test the enhanced rate limiting system with circuit breaker"""
    
    print("🔄 Testing Enhanced Rate Limiting with Circuit Breaker")
    print("=" * 60)
    
    # Initialize enhanced components
    fetcher = EnhancedYFinanceFetcher()
    shariah_filter = EnhancedShariahFilter()
    
    # Test symbols
    test_symbols = ['TCS', 'HDFCBANK', 'RELIANCE', 'WIPRO', 'INFY']
    
    print(f"\n📊 Testing {len(test_symbols)} symbols with enhanced rate limiting...")
    
    results = {
        'successful_fetches': 0,
        'cache_hits': 0,
        'circuit_breaker_activations': 0,
        'fallback_data_used': 0,
        'compliance_results': []
    }
    
    for i, symbol in enumerate(test_symbols):
        print(f"\n🔍 Testing {symbol} ({i+1}/{len(test_symbols)})...")
        
        # Check rate limiting status
        rate_status = fetcher.get_rate_limiting_status()
        if rate_status['circuit_open']:
            print(f"  ⚡ Circuit breaker is OPEN - using cache-only mode")
            results['circuit_breaker_activations'] += 1
        
        try:
            # Attempt to get stock info
            stock_info = fetcher.get_stock_info(symbol)
            
            if stock_info and stock_info.get('symbol'):
                data_source = stock_info.get('data_source', 'unknown')
                if data_source == 'yahoo_finance':
                    print(f"  ✅ Fresh data from Yahoo Finance")
                    results['successful_fetches'] += 1
                elif 'cache' in data_source or 'fallback' in data_source:
                    print(f"  🔄 Using cached/fallback data ({data_source})")
                    results['cache_hits'] += 1
                else:
                    print(f"  📊 Data from: {data_source}")
                    results['cache_hits'] += 1
                
                # Test Shariah compliance
                print(f"  🕌 Testing Shariah compliance...")
                compliance_result = shariah_filter.is_shariah_compliant_enhanced(
                    stock_info, symbol, force_refresh=False
                )
                
                status = compliance_result.get('compliance_status', 'unknown')
                confidence = compliance_result.get('confidence_level', 'unknown')
                
                status_emoji = {
                    'compliant': '✅',
                    'non_compliant': '❌',
                    'unknown': '❓',
                    'error': '⚠️'
                }
                
                emoji = status_emoji.get(status, '❓')
                print(f"  {emoji} Compliance: {status} (confidence: {confidence})")
                
                results['compliance_results'].append({
                    'symbol': symbol,
                    'status': status,
                    'confidence': confidence,
                    'data_source': data_source
                })
                
            else:
                print(f"  ❌ No data available for {symbol}")
                results['fallback_data_used'] += 1
                
        except Exception as e:
            print(f"  ❌ Error testing {symbol}: {str(e)}")
            results['fallback_data_used'] += 1
        
        # Show current rate limiting status
        rate_status = fetcher.get_rate_limiting_status()
        print(f"  📊 Rate limiting status: failures={rate_status['consecutive_failures']}, circuit_open={rate_status['circuit_open']}")
    
    # Final results
    print(f"\n📈 Enhanced Rate Limiting Test Results")
    print("=" * 50)
    print(f"Total symbols tested: {len(test_symbols)}")
    print(f"Fresh API fetches: {results['successful_fetches']}")
    print(f"Cache/fallback hits: {results['cache_hits']}")
    print(f"Circuit breaker activations: {results['circuit_breaker_activations']}")
    print(f"Fallback data used: {results['fallback_data_used']}")
    
    # Calculate success rate
    total_processed = len([r for r in results['compliance_results']])
    success_rate = (total_processed / len(test_symbols)) * 100 if test_symbols else 0
    
    print(f"\n🎯 Data Availability Success Rate: {success_rate:.1f}%")
    
    # Show final rate limiting status
    final_status = fetcher.get_rate_limiting_status()
    print(f"\n⚡ Final Rate Limiting Status:")
    print(f"  Circuit breaker open: {final_status['circuit_open']}")
    print(f"  Consecutive failures: {final_status['consecutive_failures']}")
    print(f"  Cache-only mode: {final_status['cache_only_mode']}")
    
    if final_status['circuit_open']:
        print(f"  🔄 System is in cache-only mode to prevent further rate limiting")
    else:
        print(f"  ✅ System is operating normally")
    
    # Show compliance results
    print(f"\n🕌 Shariah Compliance Results:")
    for result in results['compliance_results']:
        emoji = status_emoji.get(result['status'], '❓')
        print(f"  {emoji} {result['symbol']}: {result['status']} ({result['confidence']}) - {result['data_source']}")
    
    return results

def test_circuit_breaker_recovery():
    """Test circuit breaker recovery mechanism"""
    
    print(f"\n🔄 Testing Circuit Breaker Recovery")
    print("=" * 40)
    
    fetcher = EnhancedYFinanceFetcher()
    
    # Check initial status
    status = fetcher.get_rate_limiting_status()
    print(f"Initial circuit breaker status: {status['circuit_open']}")
    
    if status['circuit_open']:
        print("Circuit breaker is currently open")
        print("In production, this would automatically close after 5 minutes")
        print("For testing, we can manually reset it:")
        
        # Reset for demonstration
        fetcher.reset_rate_limiting_state()
        new_status = fetcher.get_rate_limiting_status()
        print(f"After reset: {new_status['circuit_open']}")
    else:
        print("Circuit breaker is currently closed - system operating normally")
    
    return status

def demonstrate_cache_fallback():
    """Demonstrate the aggressive cache fallback mechanism"""
    
    print(f"\n🔄 Demonstrating Aggressive Cache Fallback")
    print("=" * 45)
    
    fetcher = EnhancedYFinanceFetcher()
    
    # Test with a symbol that might have cached data
    test_symbol = 'TCS'
    
    print(f"Testing cache fallback for {test_symbol}...")
    
    try:
        # This will use the enhanced fallback logic
        stock_info = fetcher.get_stock_info(test_symbol)
        
        if stock_info:
            data_source = stock_info.get('data_source', 'unknown')
            print(f"✅ Retrieved data from: {data_source}")
            
            if 'cache' in data_source or 'fallback' in data_source:
                print("🔄 Successfully used cache fallback mechanism")
            else:
                print("📊 Retrieved fresh data from API")
                
            # Show key data points
            print(f"  Company: {stock_info.get('company_name', 'N/A')}")
            print(f"  Sector: {stock_info.get('sector', 'N/A')}")
            print(f"  Market Cap: {stock_info.get('market_cap', 0):,}")
            
        else:
            print("❌ No data available even with fallback")
            
    except Exception as e:
        print(f"❌ Error in cache fallback test: {str(e)}")

if __name__ == "__main__":
    try:
        # Test enhanced rate limiting
        results = test_enhanced_rate_limiting()
        
        # Test circuit breaker recovery
        circuit_status = test_circuit_breaker_recovery()
        
        # Demonstrate cache fallback
        demonstrate_cache_fallback()
        
        print(f"\n✅ Enhanced Rate Limiting Test Completed")
        print(f"The system now has improved resilience during rate limiting scenarios.")
        
    except Exception as e:
        print(f"❌ Error during enhanced rate limiting test: {str(e)}")
        import traceback
        traceback.print_exc()
