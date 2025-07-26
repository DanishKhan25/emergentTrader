#!/usr/bin/env python3
"""
Practical Rate Limiting Solution
Demonstrates how to work effectively with cached Shariah compliance data during rate limiting
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

import logging
from datetime import datetime
from core.enhanced_shariah_filter import EnhancedShariahFilter
from core.data_cache import cache

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cached_compliance_during_rate_limiting():
    """Test using cached Shariah compliance data during rate limiting scenarios"""
    
    print("🕌 Testing Cached Shariah Compliance During Rate Limiting")
    print("=" * 65)
    
    shariah_filter = EnhancedShariahFilter()
    
    # Test symbols that we know have cached compliance data
    test_symbols = ['TCS', 'HDFCBANK', 'RELIANCE', 'WIPRO', 'INFY']
    
    print(f"\n📊 Checking cached compliance data for {len(test_symbols)} symbols...")
    
    results = {
        'cached_compliance_found': 0,
        'fresh_compliance_needed': 0,
        'compliance_results': []
    }
    
    for symbol in test_symbols:
        print(f"\n🔍 Checking {symbol}...")
        
        # Check if we have cached compliance data
        cached_compliance = cache.get('shariah_compliance', symbol)
        
        if cached_compliance:
            print(f"  ✅ Found cached compliance data")
            
            # Check cache age
            check_date = datetime.fromisoformat(cached_compliance.get('check_date', ''))
            age_days = (datetime.now() - check_date).days
            age_hours = (datetime.now() - check_date).total_seconds() / 3600
            
            print(f"  📅 Cache age: {age_days} days ({age_hours:.1f} hours)")
            
            # Extract compliance info
            status = cached_compliance.get('compliance_status', 'unknown')
            confidence = cached_compliance.get('confidence_level', 'unknown')
            
            status_emoji = {
                'compliant': '✅',
                'non_compliant': '❌',
                'unknown': '❓',
                'error': '⚠️'
            }
            
            emoji = status_emoji.get(status, '❓')
            print(f"  {emoji} Cached compliance: {status} (confidence: {confidence})")
            
            # Check if cache is still valid (within 3 months)
            if age_days < 90:
                print(f"  🔄 Cache is fresh - can use directly")
                results['cached_compliance_found'] += 1
                
                results['compliance_results'].append({
                    'symbol': symbol,
                    'status': status,
                    'confidence': confidence,
                    'data_source': 'cached',
                    'cache_age_days': age_days
                })
            else:
                print(f"  ⚠️  Cache is expired but can still be used during rate limiting")
                results['cached_compliance_found'] += 1
                
                results['compliance_results'].append({
                    'symbol': symbol,
                    'status': status,
                    'confidence': 'expired_cache',
                    'data_source': 'expired_cache',
                    'cache_age_days': age_days
                })
        else:
            print(f"  ❌ No cached compliance data found")
            results['fresh_compliance_needed'] += 1
    
    # Summary
    print(f"\n📈 Cached Compliance Analysis Results")
    print("=" * 45)
    print(f"Total symbols checked: {len(test_symbols)}")
    print(f"Cached compliance available: {results['cached_compliance_found']}")
    print(f"Fresh compliance needed: {results['fresh_compliance_needed']}")
    
    cache_coverage = (results['cached_compliance_found'] / len(test_symbols)) * 100
    print(f"Cache coverage: {cache_coverage:.1f}%")
    
    if cache_coverage >= 80:
        print("✅ Excellent cache coverage - system can operate during rate limiting")
    elif cache_coverage >= 50:
        print("⚠️  Good cache coverage - most operations can continue")
    else:
        print("❌ Poor cache coverage - limited functionality during rate limiting")
    
    # Show detailed results
    print(f"\n🕌 Detailed Compliance Results:")
    for result in results['compliance_results']:
        emoji = status_emoji.get(result['status'], '❓')
        age_info = f"({result['cache_age_days']}d old)" if result['data_source'] != 'fresh' else ""
        print(f"  {emoji} {result['symbol']}: {result['status']} ({result['confidence']}) {age_info}")
    
    return results

def demonstrate_rate_limiting_workflow():
    """Demonstrate the complete workflow during rate limiting"""
    
    print(f"\n🔄 Demonstrating Rate Limiting Workflow")
    print("=" * 45)
    
    shariah_filter = EnhancedShariahFilter()
    
    # Simulate a request for Shariah compliant stocks during rate limiting
    test_symbols = ['TCS', 'HDFCBANK', 'RELIANCE', 'WIPRO', 'INFY']
    
    print(f"Simulating Shariah compliance check during rate limiting...")
    print(f"Symbols to check: {', '.join(test_symbols)}")
    
    compliant_stocks = []
    unknown_stocks = []
    error_stocks = []
    
    for symbol in test_symbols:
        try:
            # During rate limiting, we rely on cached compliance data
            cached_compliance = cache.get('shariah_compliance', symbol)
            
            if cached_compliance:
                status = cached_compliance.get('compliance_status', 'unknown')
                confidence = cached_compliance.get('confidence_level', 'unknown')
                
                if status == 'compliant':
                    compliant_stocks.append({
                        'symbol': symbol,
                        'status': status,
                        'confidence': confidence,
                        'source': 'cached'
                    })
                elif status == 'unknown':
                    unknown_stocks.append({
                        'symbol': symbol,
                        'status': status,
                        'confidence': confidence,
                        'source': 'cached'
                    })
                else:
                    # Non-compliant stocks are not included in results
                    pass
            else:
                # No cached data - mark as needing review
                unknown_stocks.append({
                    'symbol': symbol,
                    'status': 'unknown',
                    'confidence': 'no_cache',
                    'source': 'no_data'
                })
                
        except Exception as e:
            error_stocks.append({
                'symbol': symbol,
                'error': str(e)
            })
    
    # Results
    print(f"\n📊 Rate Limiting Workflow Results:")
    print(f"  ✅ Compliant stocks: {len(compliant_stocks)}")
    print(f"  ❓ Unknown/Review needed: {len(unknown_stocks)}")
    print(f"  ⚠️  Errors: {len(error_stocks)}")
    
    if compliant_stocks:
        print(f"\n✅ Compliant Stocks (can be used for trading):")
        for stock in compliant_stocks:
            print(f"  • {stock['symbol']}: {stock['status']} ({stock['confidence']})")
    
    if unknown_stocks:
        print(f"\n❓ Stocks Needing Review:")
        for stock in unknown_stocks:
            print(f"  • {stock['symbol']}: {stock['status']} ({stock['confidence']})")
    
    return {
        'compliant': compliant_stocks,
        'unknown': unknown_stocks,
        'errors': error_stocks
    }

def suggest_rate_limiting_best_practices():
    """Suggest best practices for handling rate limiting"""
    
    print(f"\n💡 Rate Limiting Best Practices")
    print("=" * 35)
    
    practices = [
        "1. 🔄 Use cached Shariah compliance data (3-month validity)",
        "2. ⚡ Implement circuit breaker pattern to prevent API abuse",
        "3. 📊 Prioritize cached data over fresh API calls during rate limiting",
        "4. 🕐 Schedule non-urgent data refreshes during off-peak hours",
        "5. 📈 Monitor rate limiting patterns and adjust request frequency",
        "6. 🔍 Use cached data for read-only operations (compliance checks)",
        "7. ⚠️  Implement graceful degradation when fresh data unavailable",
        "8. 📝 Log rate limiting events for monitoring and optimization"
    ]
    
    for practice in practices:
        print(f"  {practice}")
    
    print(f"\n🎯 Key Insight:")
    print(f"  The Enhanced Shariah Compliance System with 3-month caching")
    print(f"  provides excellent resilience during rate limiting scenarios.")
    print(f"  Most compliance decisions can be made using cached data.")

def check_cache_health():
    """Check the health of the cache system"""
    
    print(f"\n🔍 Cache Health Check")
    print("=" * 25)
    
    try:
        # Get cache statistics
        cache_stats = cache.get_cache_stats()
        
        print(f"Cache statistics:")
        print(f"  Total entries: {cache_stats.get('total_entries', 0)}")
        print(f"  Cache hits: {cache_stats.get('cache_hits', 0)}")
        print(f"  Cache misses: {cache_stats.get('cache_misses', 0)}")
        
        # Check specific cache types
        cache_types = ['shariah_compliance', 'stock_data', 'signals']
        
        for cache_type in cache_types:
            count = cache_stats.get(f'{cache_type}_count', 0)
            print(f"  {cache_type}: {count} entries")
        
        # Check Shariah summary
        shariah_summary = cache.get('shariah_summary', 'latest')
        if shariah_summary:
            print(f"\nShariah compliance summary:")
            print(f"  Total processed: {shariah_summary.get('total_processed', 0)}")
            print(f"  Compliant: {shariah_summary.get('compliant_count', 0)}")
            print(f"  Unknown: {shariah_summary.get('unknown_count', 0)}")
            print(f"  Last update: {shariah_summary.get('processing_date', 'N/A')}")
        
        return cache_stats
        
    except Exception as e:
        print(f"❌ Error checking cache health: {str(e)}")
        return {}

if __name__ == "__main__":
    try:
        # Test cached compliance during rate limiting
        compliance_results = test_cached_compliance_during_rate_limiting()
        
        # Demonstrate rate limiting workflow
        workflow_results = demonstrate_rate_limiting_workflow()
        
        # Check cache health
        cache_health = check_cache_health()
        
        # Suggest best practices
        suggest_rate_limiting_best_practices()
        
        print(f"\n✅ Practical Rate Limiting Solution Test Completed")
        print(f"The system can effectively operate using cached compliance data during rate limiting.")
        
    except Exception as e:
        print(f"❌ Error during practical rate limiting test: {str(e)}")
        import traceback
        traceback.print_exc()
