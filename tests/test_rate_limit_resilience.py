#!/usr/bin/env python3
"""
Test Rate Limiting Resilience - Enhanced caching during rate limiting scenarios
Tests the system's ability to gracefully handle Yahoo Finance rate limits
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

import logging
from datetime import datetime, timedelta
from services.yfinance_fetcher import YFinanceFetcher
from core.enhanced_shariah_filter import EnhancedShariahFilter
from core.data_cache import cache

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rate_limit_resilience():
    """Test system resilience during rate limiting scenarios"""
    
    print("🔄 Testing Rate Limiting Resilience System")
    print("=" * 60)
    
    # Initialize components
    fetcher = YFinanceFetcher()
    shariah_filter = EnhancedShariahFilter()
    
    # Test symbols that are likely to trigger rate limits
    test_symbols = ['TCS', 'HDFCBANK', 'RELIANCE', 'WIPRO', 'INFY']
    
    print(f"\n📊 Testing {len(test_symbols)} symbols for rate limit resilience...")
    
    results = {
        'successful_fetches': 0,
        'cache_hits': 0,
        'rate_limited': 0,
        'fallback_used': 0,
        'compliance_results': []
    }
    
    for symbol in test_symbols:
        print(f"\n🔍 Testing {symbol}...")
        
        try:
            # Check if we have cached data
            cached_info = cache.get('stock_info', symbol)
            if cached_info:
                print(f"  ✅ Found cached stock info for {symbol}")
                results['cache_hits'] += 1
                stock_info = cached_info
            else:
                print(f"  🔄 Fetching fresh data for {symbol}...")
                stock_info = fetcher.get_stock_info(symbol)
                
                if stock_info and stock_info.get('symbol'):
                    print(f"  ✅ Successfully fetched data for {symbol}")
                    results['successful_fetches'] += 1
                else:
                    print(f"  ⚠️  Rate limited or no data for {symbol}")
                    results['rate_limited'] += 1
                    
                    # Try to use any available cached data, even if expired
                    cached_info = cache.get('stock_info', symbol, ignore_ttl=True)
                    if cached_info:
                        print(f"  🔄 Using expired cached data for {symbol}")
                        stock_info = cached_info
                        results['fallback_used'] += 1
                    else:
                        print(f"  ❌ No cached data available for {symbol}")
                        continue
            
            # Test Shariah compliance with available data
            print(f"  🕌 Testing Shariah compliance for {symbol}...")
            compliance_result = shariah_filter.is_shariah_compliant_enhanced(
                stock_info, symbol, force_refresh=False
            )
            
            status_emoji = {
                'compliant': '✅',
                'non_compliant': '❌', 
                'unknown': '❓',
                'error': '⚠️'
            }
            
            status = compliance_result.get('compliance_status', 'unknown')
            confidence = compliance_result.get('confidence_level', 'unknown')
            emoji = status_emoji.get(status, '❓')
            
            print(f"  {emoji} Compliance: {status} (confidence: {confidence})")
            
            results['compliance_results'].append({
                'symbol': symbol,
                'status': status,
                'confidence': confidence,
                'data_source': 'cached' if cached_info else 'fresh'
            })
            
        except Exception as e:
            print(f"  ❌ Error testing {symbol}: {str(e)}")
            results['rate_limited'] += 1
    
    # Print comprehensive results
    print(f"\n📈 Rate Limiting Resilience Test Results")
    print("=" * 50)
    print(f"Total symbols tested: {len(test_symbols)}")
    print(f"Successful fresh fetches: {results['successful_fetches']}")
    print(f"Cache hits: {results['cache_hits']}")
    print(f"Rate limited: {results['rate_limited']}")
    print(f"Fallback data used: {results['fallback_used']}")
    
    # Calculate resilience score
    total_processed = len([r for r in results['compliance_results'] if r['status'] != 'error'])
    resilience_score = (total_processed / len(test_symbols)) * 100 if test_symbols else 0
    
    print(f"\n🎯 System Resilience Score: {resilience_score:.1f}%")
    
    if resilience_score >= 80:
        print("✅ Excellent resilience - system handles rate limiting well")
    elif resilience_score >= 60:
        print("⚠️  Good resilience - some improvements possible")
    else:
        print("❌ Poor resilience - system needs improvement")
    
    # Show compliance results
    print(f"\n🕌 Shariah Compliance Results:")
    for result in results['compliance_results']:
        emoji = status_emoji.get(result['status'], '❓')
        print(f"  {emoji} {result['symbol']}: {result['status']} ({result['confidence']}) - {result['data_source']} data")
    
    return results

def test_cache_fallback_mechanism():
    """Test the cache fallback mechanism specifically"""
    
    print(f"\n🔄 Testing Cache Fallback Mechanism")
    print("=" * 40)
    
    # Test with a symbol that might be rate limited
    test_symbol = 'TCS'
    
    print(f"Testing cache fallback for {test_symbol}...")
    
    # Check current cache status
    cached_info = cache.get('stock_info', test_symbol)
    cached_compliance = cache.get('shariah_compliance', test_symbol)
    
    print(f"Stock info cached: {'Yes' if cached_info else 'No'}")
    print(f"Compliance cached: {'Yes' if cached_compliance else 'No'}")
    
    if cached_compliance:
        check_date = datetime.fromisoformat(cached_compliance.get('check_date', ''))
        age_days = (datetime.now() - check_date).days
        print(f"Compliance cache age: {age_days} days")
        
        if age_days < 90:  # Within 3-month window
            print("✅ Compliance cache is fresh (within 3 months)")
        else:
            print("⚠️  Compliance cache is expired (>3 months)")
    
    return {
        'stock_info_cached': bool(cached_info),
        'compliance_cached': bool(cached_compliance),
        'cache_age_days': age_days if cached_compliance else None
    }

def suggest_improvements():
    """Suggest improvements for rate limiting resilience"""
    
    print(f"\n💡 Suggested Improvements for Rate Limiting Resilience")
    print("=" * 55)
    
    improvements = [
        "1. Implement progressive cache TTL extension during rate limiting",
        "2. Add circuit breaker pattern to temporarily stop API calls",
        "3. Implement batch processing with intelligent delays",
        "4. Add alternative data sources for basic company information",
        "5. Implement queue-based processing for non-urgent requests",
        "6. Add rate limiting detection and automatic fallback modes",
        "7. Implement data freshness scoring to prioritize cache usage",
        "8. Add manual data override capabilities for critical stocks"
    ]
    
    for improvement in improvements:
        print(f"  {improvement}")
    
    print(f"\n🔧 Immediate Actions:")
    print("  • Use cached data more aggressively during rate limiting")
    print("  • Extend cache TTL temporarily when rate limits are detected")
    print("  • Implement smarter retry logic with exponential backoff")
    print("  • Add rate limiting status monitoring and alerts")

if __name__ == "__main__":
    try:
        # Test rate limiting resilience
        resilience_results = test_rate_limit_resilience()
        
        # Test cache fallback mechanism
        cache_results = test_cache_fallback_mechanism()
        
        # Suggest improvements
        suggest_improvements()
        
        print(f"\n✅ Rate Limiting Resilience Test Completed")
        print(f"Check the results above to assess system performance during rate limiting scenarios.")
        
    except Exception as e:
        print(f"❌ Error during rate limiting resilience test: {str(e)}")
        import traceback
        traceback.print_exc()
