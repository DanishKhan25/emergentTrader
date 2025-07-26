#!/usr/bin/env python3
"""
Fast NSE Shariah Compliance Processing
Process all 2,116 NSE stocks with minimal delays for faster processing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

import logging
import pandas as pd
import json
from datetime import datetime
from services.yfinance_fetcher import YFinanceFetcher
from core.enhanced_shariah_filter_batched import BatchedShariahFilter
from core.data_cache import cache

# Configure comprehensive logging
log_filename = f"nse_fast_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_nse_stocks():
    """Load all NSE stocks with proper error handling"""
    try:
        df = pd.read_csv('data/nse_raw.csv')
        logger.info(f"Loaded {len(df)} stocks from NSE CSV")
        
        stocks = []
        for _, row in df.iterrows():
            symbol = row.get('SYMBOL', '').strip()
            series = row.get(' SERIES', '').strip()
            face_value = row.get(' FACE VALUE', 0)
            
            if (symbol and len(symbol) > 0 and 
                series.upper() in ['EQ', 'BE', 'SM', 'BZ', 'BL'] and
                face_value > 0):
                
                stocks.append({
                    'symbol': symbol,
                    'company_name': row.get('NAME OF COMPANY', '').strip(),
                    'series': series,
                    'listing_date': row.get(' DATE OF LISTING', ''),
                    'paid_up_value': row.get(' PAID UP VALUE', 0),
                    'market_lot': row.get(' MARKET LOT', 0),
                    'isin_number': row.get(' ISIN NUMBER', '').strip(),
                    'face_value': face_value
                })
        
        logger.info(f"Filtered to {len(stocks)} valid stocks for processing")
        return stocks
        
    except Exception as e:
        logger.error(f"Error loading NSE stocks: {str(e)}")
        return []

def clear_cache_for_fresh_data():
    """Clear cache to ensure fresh data"""
    try:
        logger.info("Clearing cache for fresh data processing...")
        cache.clear_cache_type('stock_info')
        cache.clear_cache_type('shariah_compliance')
        logger.info("✅ Cache cleared successfully")
        return True
    except Exception as e:
        logger.warning(f"Could not clear cache: {str(e)}")
        return False

def run_fast_nse_processing():
    """Run the complete NSE processing with minimal delays for speed"""
    
    print("🚀 Fast NSE Shariah Compliance Processing")
    print("=" * 50)
    print(f"📝 Logging to: {log_filename}")
    
    # Load stocks
    logger.info("Starting fast NSE processing...")
    stocks = load_nse_stocks()
    
    if not stocks:
        logger.error("No stocks loaded. Exiting.")
        return None
    
    print(f"📊 Loaded {len(stocks)} NSE stocks")
    logger.info(f"Loaded {len(stocks)} stocks for processing")
    
    # Clear cache for fresh data
    clear_cache_for_fresh_data()
    
    # Initialize components
    logger.info("Initializing processing components...")
    fetcher = YFinanceFetcher()
    batched_filter = BatchedShariahFilter(batch_size=50)
    
    # Configure for FAST processing - minimal delays
    batched_filter.batch_config.delay_between_items = 0.5      # Reduced from 2.0s to 0.5s
    batched_filter.batch_config.delay_between_batches = 15.0   # Reduced from 30.0s to 15.0s
    batched_filter.batch_config.rate_limit_delay = 30.0        # Reduced from 60.0s to 30.0s
    batched_filter.batch_config.max_retries = 2               # Reduced retries for speed
    batched_filter.batch_config.circuit_breaker_threshold = 5  # More tolerant to avoid stopping
    
    # Calculate estimates with new timing
    total_batches = (len(stocks) + 49) // 50
    estimated_time = (total_batches * 15 + len(stocks) * 0.5) / 60  # minutes
    
    print(f"⚡ FAST Configuration:")
    print(f"   • Batch size: 50 stocks")
    print(f"   • Delay between stocks: 0.5s (reduced from 2s)")
    print(f"   • Delay between batches: 15s (reduced from 30s)")
    print(f"   • Total batches: {total_batches}")
    print(f"   • Estimated time: {estimated_time:.1f} minutes (much faster!)")
    print(f"   • Force refresh: True (fresh data)")
    
    logger.info(f"FAST processing configuration: {total_batches} batches, estimated {estimated_time:.1f} minutes")
    logger.info("Using minimal delays: 0.5s between stocks, 15s between batches")
    
    # Confirm before starting
    response = input(f"\n🤔 Process {len(stocks)} stocks in ~{estimated_time:.1f} minutes with fast settings? (y/N): ")
    if response.lower() != 'y':
        print("❌ Processing cancelled by user")
        return None
    
    # Start processing
    start_time = datetime.now()
    logger.info(f"Starting FAST batch processing at {start_time}")
    
    print(f"\n🔄 Starting FAST processing at {start_time.strftime('%H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Process with force_refresh=True for fresh data
        results = batched_filter.get_shariah_universe_batched(
            stocks, fetcher, force_refresh=True
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Log completion
        logger.info(f"FAST processing completed at {end_time}")
        logger.info(f"Total processing time: {processing_time/60:.1f} minutes")
        
        # Display results
        print(f"\n🎉 FAST Processing Completed!")
        print("=" * 35)
        
        summary = results['summary']
        batch_stats = results['batch_stats']
        
        print(f"⏱️  Processing time: {processing_time/60:.1f} minutes")
        print(f"📊 Stocks processed: {summary['total_processed']}")
        print(f"✅ Compliant: {summary['compliant_count']} ({summary['compliant_count']/summary['total_processed']*100:.1f}%)")
        print(f"❓ Unknown/Review: {summary['unknown_count']} ({summary['unknown_count']/summary['total_processed']*100:.1f}%)")
        print(f"⚠️  Errors: {summary['error_count']} ({summary['error_count']/summary['total_processed']*100:.1f}%)")
        print(f"⚡ Rate limited: {summary['rate_limited_count']}")
        print(f"📈 Success rate: {summary['success_rate']:.1f}%")
        
        # Show batch performance
        print(f"\n🔄 Batch Performance:")
        print(f"   • Total batches: {batch_stats['total_batches']}")
        print(f"   • Successful batches: {batch_stats['successful_batches']}")
        print(f"   • Rate limited batches: {batch_stats['rate_limited_batches']}")
        print(f"   • Average batch time: {batch_stats['average_batch_time']:.1f}s")
        print(f"   • Circuit breaker activations: {batch_stats['circuit_breaker_activations']}")
        
        # Log detailed results
        logger.info("=" * 60)
        logger.info("FAST PROCESSING RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total processed: {summary['total_processed']}")
        logger.info(f"Compliant stocks: {summary['compliant_count']}")
        logger.info(f"Unknown stocks: {summary['unknown_count']}")
        logger.info(f"Error stocks: {summary['error_count']}")
        logger.info(f"Rate limited: {summary['rate_limited_count']}")
        logger.info(f"Success rate: {summary['success_rate']:.1f}%")
        logger.info(f"Cache usage: {summary['cache_usage_rate']:.1f}%")
        logger.info(f"Processing speed: {summary['total_processed']/(processing_time/60):.1f} stocks/minute")
        
        # Show top compliant stocks
        if results['compliant_stocks']:
            print(f"\n✅ Top 15 Shariah Compliant Stocks:")
            print("-" * 65)
            
            for i, stock in enumerate(results['compliant_stocks'][:15], 1):
                score = stock.get('compliance_score', 0)
                confidence = stock.get('confidence_level', 'unknown')
                sector = stock.get('sector', 'Unknown')[:15]
                
                print(f"{i:2d}. {stock['symbol']:12} | {stock['company_name'][:20]:20} | {sector:15} | {confidence:6} | {score:.2f}")
                
                # Log top compliant stocks
                if i <= 10:  # Log top 10
                    logger.info(f"Compliant {i:2d}: {stock['symbol']} - {stock['company_name']} (score: {score:.2f}, sector: {sector})")
        
        # Performance metrics
        stocks_per_minute = summary['total_processed'] / (processing_time / 60)
        print(f"\n📈 Performance Metrics:")
        print(f"   • Processing speed: {stocks_per_minute:.1f} stocks/minute")
        print(f"   • Time saved vs standard: ~{(88.2 - processing_time/60):.1f} minutes")
        print(f"   • Efficiency gain: {((88.2 - processing_time/60) / 88.2 * 100):.1f}%")
        
        # Save results
        save_results(results, processing_time, log_filename, stocks_per_minute)
        
        logger.info("FAST processing completed successfully")
        logger.info(f"Processing speed: {stocks_per_minute:.1f} stocks/minute")
        return results
        
    except KeyboardInterrupt:
        logger.warning("FAST processing interrupted by user")
        print(f"\n⚠️  Processing interrupted at {datetime.now().strftime('%H:%M:%S')}")
        return None
        
    except Exception as e:
        logger.error(f"FAST processing error: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def save_results(results, processing_time, log_filename, stocks_per_minute):
    """Save results to JSON file with performance metrics"""
    try:
        output_file = f"nse_fast_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Prepare results for JSON
        json_results = {
            'metadata': {
                'processing_date': datetime.now().isoformat(),
                'processing_time_minutes': processing_time / 60,
                'processing_speed_stocks_per_minute': stocks_per_minute,
                'log_file': log_filename,
                'force_refresh_used': True,
                'batch_size': 50,
                'fast_mode': True,
                'delays_used': {
                    'between_stocks': '0.5s',
                    'between_batches': '15s',
                    'rate_limit_delay': '30s'
                }
            },
            'summary': results['summary'],
            'batch_stats': results['batch_stats'],
            'compliant_stocks': results['compliant_stocks'],
            'unknown_stocks': results['unknown_stocks'][:50],  # First 50 for file size
            'error_summary': {
                'total_errors': len(results['error_stocks']),
                'sample_errors': results['error_stocks'][:10]  # First 10 errors
            },
            'performance_metrics': {
                'stocks_per_minute': stocks_per_minute,
                'total_processing_time_minutes': processing_time / 60,
                'estimated_time_saved_minutes': 88.2 - (processing_time / 60),
                'efficiency_gain_percent': ((88.2 - processing_time/60) / 88.2 * 100)
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(json_results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {output_file}")
        logger.info(f"Results saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")

if __name__ == "__main__":
    print("⚡ NSE Shariah Compliance Processing - FAST MODE")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        results = run_fast_nse_processing()
        
        if results:
            print(f"\n✅ FAST processing completed successfully!")
            print(f"📝 Check log file: {log_filename}")
            print(f"📊 Results saved to JSON file")
            print(f"⚡ Much faster than standard processing!")
        else:
            print(f"\n⚠️  Processing was not completed")
            
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        logger.error(f"Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
