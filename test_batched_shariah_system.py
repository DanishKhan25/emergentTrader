#!/usr/bin/env python3
"""
Test Batched Shariah Compliance System
Demonstrates the new batch processing system with rate limiting protection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

import logging
from datetime import datetime
from services.yfinance_fetcher import YFinanceFetcher
from core.enhanced_shariah_filter_batched import BatchedShariahFilter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_batched_shariah_compliance():
    """Test the batched Shariah compliance system"""
    
    print("🕌 Testing Batched Shariah Compliance System")
    print("=" * 55)
    
    # Initialize components
    fetcher = YFinanceFetcher()
    batched_filter = BatchedShariahFilter(batch_size=50)  # 50 stocks per batch
    
    # Create test stock universe (simulating NSE stocks)
    test_stocks = [
        {'symbol': 'TCS', 'company_name': 'Tata Consultancy Services'},
        {'symbol': 'HDFCBANK', 'company_name': 'HDFC Bank'},
        {'symbol': 'RELIANCE', 'company_name': 'Reliance Industries'},
        {'symbol': 'WIPRO', 'company_name': 'Wipro Limited'},
        {'symbol': 'INFY', 'company_name': 'Infosys Limited'},
        {'symbol': 'ICICIBANK', 'company_name': 'ICICI Bank'},
        {'symbol': 'KOTAKBANK', 'company_name': 'Kotak Mahindra Bank'},
        {'symbol': 'SBIN', 'company_name': 'State Bank of India'},
        {'symbol': 'BHARTIARTL', 'company_name': 'Bharti Airtel'},
        {'symbol': 'HINDUNILVR', 'company_name': 'Hindustan Unilever'},
        {'symbol': 'ITC', 'company_name': 'ITC Limited'},
        {'symbol': 'MARUTI', 'company_name': 'Maruti Suzuki'},
        {'symbol': 'ASIANPAINT', 'company_name': 'Asian Paints'},
        {'symbol': 'NESTLEIND', 'company_name': 'Nestle India'},
        {'symbol': 'HCLTECH', 'company_name': 'HCL Technologies'}
    ]
    
    print(f"\n📊 Processing {len(test_stocks)} stocks using batch system...")
    print(f"Batch size: 50 stocks per batch")
    print(f"Expected batches: {(len(test_stocks) + 49) // 50}")  # Ceiling division
    
    # Record start time
    start_time = datetime.now()
    
    # Process stocks using batched system
    try:
        results = batched_filter.get_shariah_universe_batched(
            test_stocks, fetcher, force_refresh=False
        )
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Display results
        print(f"\n📈 Batched Processing Results")
        print("=" * 40)
        
        summary = results['summary']
        batch_stats = results['batch_stats']
        
        print(f"Total processing time: {total_time:.1f}s")
        print(f"Stocks processed: {summary['total_processed']}")
        print(f"✅ Compliant: {summary['compliant_count']}")
        print(f"❓ Unknown/Review: {summary['unknown_count']}")
        print(f"⚠️  Errors: {summary['error_count']}")
        print(f"🔄 Used cached data: {summary['cached_used_count']} ({summary['cache_usage_rate']:.1f}%)")
        print(f"⚡ Rate limited: {summary['rate_limited_count']}")
        print(f"📊 Success rate: {summary['success_rate']:.1f}%")
        
        print(f"\n🔄 Batch Processing Stats:")
        print(f"Total batches: {batch_stats['total_batches']}")
        print(f"Successful batches: {batch_stats['successful_batches']}")
        print(f"Rate limited batches: {batch_stats['rate_limited_batches']}")
        print(f"Average batch time: {batch_stats['average_batch_time']:.1f}s")
        print(f"Circuit breaker activations: {batch_stats['circuit_breaker_activations']}")
        
        # Show detailed results
        if results['compliant_stocks']:
            print(f"\n✅ Compliant Stocks:")
            for stock in results['compliant_stocks'][:5]:  # Show first 5
                confidence = stock.get('confidence_level', 'unknown')
                score = stock.get('compliance_score', 0)
                source = stock.get('data_source', 'unknown')
                print(f"  • {stock['symbol']}: {confidence} confidence, score: {score:.2f} ({source})")
            
            if len(results['compliant_stocks']) > 5:
                print(f"  ... and {len(results['compliant_stocks']) - 5} more")
        
        if results['unknown_stocks']:
            print(f"\n❓ Stocks Needing Review:")
            for stock in results['unknown_stocks'][:5]:  # Show first 5
                confidence = stock.get('confidence_level', 'unknown')
                source = stock.get('data_source', 'unknown')
                print(f"  • {stock['symbol']}: {confidence} confidence ({source})")
            
            if len(results['unknown_stocks']) > 5:
                print(f"  ... and {len(results['unknown_stocks']) - 5} more")
        
        if results['cached_stocks']:
            print(f"\n🔄 Cached Data Usage:")
            cache_sources = {}
            for cached_stock in results['cached_stocks']:
                source = cached_stock.get('cache_source', 'unknown')
                cache_sources[source] = cache_sources.get(source, 0) + 1
            
            for source, count in cache_sources.items():
                print(f"  • {source}: {count} stocks")
        
        # Show batch processor stats
        processor_stats = batched_filter.get_batch_processor_stats()
        print(f"\n📊 Batch Processor Statistics:")
        print(f"Circuit breaker status: {'OPEN' if processor_stats['circuit_breaker_open'] else 'CLOSED'}")
        print(f"Total items processed: {processor_stats['total_items_processed']}")
        print(f"Successful batches: {processor_stats['successful_batches']}")
        print(f"Rate limited batches: {processor_stats['rate_limited_batches']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during batched processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_batch_configuration():
    """Test different batch configurations"""
    
    print(f"\n🔧 Testing Different Batch Configurations")
    print("=" * 45)
    
    configurations = [
        {'batch_size': 10, 'delay': 15.0, 'name': 'Conservative (10 stocks, 15s delay)'},
        {'batch_size': 25, 'delay': 20.0, 'name': 'Balanced (25 stocks, 20s delay)'},
        {'batch_size': 50, 'delay': 30.0, 'name': 'Aggressive (50 stocks, 30s delay)'}
    ]
    
    test_stocks = [
        {'symbol': 'TCS'}, {'symbol': 'HDFCBANK'}, {'symbol': 'RELIANCE'},
        {'symbol': 'WIPRO'}, {'symbol': 'INFY'}
    ]
    
    for config in configurations:
        print(f"\n🔍 Testing {config['name']}:")
        
        # Create filter with specific configuration
        batched_filter = BatchedShariahFilter(batch_size=config['batch_size'])
        
        # Update batch configuration
        batched_filter.batch_config.delay_between_batches = config['delay']
        
        expected_batches = (len(test_stocks) + config['batch_size'] - 1) // config['batch_size']
        estimated_time = expected_batches * config['delay'] + len(test_stocks) * 2  # 2s per stock
        
        print(f"  Expected batches: {expected_batches}")
        print(f"  Estimated time: {estimated_time:.0f}s")
        print(f"  Rate limiting protection: {'High' if config['batch_size'] <= 25 else 'Medium'}")

def demonstrate_rate_limiting_resilience():
    """Demonstrate how the system handles rate limiting"""
    
    print(f"\n⚡ Demonstrating Rate Limiting Resilience")
    print("=" * 45)
    
    batched_filter = BatchedShariahFilter(batch_size=50)
    
    print("Key features of the batched system:")
    print("1. 🔄 Processes stocks in batches of 50 with 30s delays")
    print("2. ⚡ Circuit breaker opens after 3 consecutive failures")
    print("3. 🔄 Falls back to cached compliance data during rate limiting")
    print("4. 📊 Provides comprehensive statistics and monitoring")
    print("5. 🕐 Intelligent delays: 2s between stocks, 30s between batches")
    print("6. 🔁 Automatic retries with exponential backoff")
    print("7. 📈 Tracks cache usage and success rates")
    
    # Show current batch processor status
    stats = batched_filter.get_batch_processor_stats()
    
    print(f"\nCurrent batch processor status:")
    print(f"  Circuit breaker: {'OPEN' if stats['circuit_breaker_open'] else 'CLOSED'}")
    print(f"  Configuration: {stats['config']['batch_size']} stocks per batch")
    print(f"  Delays: {stats['config']['delay_between_items']}s between stocks, {stats['config']['delay_between_batches']}s between batches")
    print(f"  Rate limit delay: {stats['config']['rate_limit_delay']}s when rate limited")

def show_usage_examples():
    """Show usage examples for the batched system"""
    
    print(f"\n💡 Usage Examples")
    print("=" * 20)
    
    print("1. Basic usage with default settings (50 stocks per batch):")
    print("```python")
    print("from core.enhanced_shariah_filter_batched import BatchedShariahFilter")
    print("from services.yfinance_fetcher import YFinanceFetcher")
    print("")
    print("fetcher = YFinanceFetcher()")
    print("filter = BatchedShariahFilter(batch_size=50)")
    print("results = filter.get_shariah_universe_batched(stock_universe, fetcher)")
    print("```")
    
    print("\n2. Conservative processing (smaller batches, longer delays):")
    print("```python")
    print("filter = BatchedShariahFilter(batch_size=25)")
    print("filter.batch_config.delay_between_batches = 45.0  # 45 seconds")
    print("filter.batch_config.delay_between_items = 3.0     # 3 seconds")
    print("```")
    
    print("\n3. Monitoring batch processing:")
    print("```python")
    print("results = filter.get_shariah_universe_batched(stocks, fetcher)")
    print("print(f\"Cache usage: {results['summary']['cache_usage_rate']:.1f}%\")")
    print("print(f\"Success rate: {results['summary']['success_rate']:.1f}%\")")
    print("```")

if __name__ == "__main__":
    try:
        # Test batched Shariah compliance system
        results = test_batched_shariah_compliance()
        
        # Test different configurations
        test_batch_configuration()
        
        # Demonstrate rate limiting resilience
        demonstrate_rate_limiting_resilience()
        
        # Show usage examples
        show_usage_examples()
        
        print(f"\n✅ Batched Shariah Compliance System Test Completed")
        print(f"The system now processes stocks in batches of 50 with intelligent delays")
        print(f"to prevent rate limiting while maintaining high throughput and reliability.")
        
    except Exception as e:
        print(f"❌ Error during batched system test: {str(e)}")
        import traceback
        traceback.print_exc()
