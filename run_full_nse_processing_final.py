#!/usr/bin/env python3
"""
Full NSE Shariah Compliance Processing - Final Version
Process all 2,116 NSE stocks with fresh data and comprehensive logging
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
log_filename = f"nse_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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

def run_full_nse_processing():
    """Run the complete NSE processing with detailed logging"""
    
    print("🚀 Full NSE Shariah Compliance Processing")
    print("=" * 50)
    print(f"📝 Logging to: {log_filename}")
    
    # Load stocks
    logger.info("Starting full NSE processing...")
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
    
    # Configure for production processing
    batched_filter.batch_config.delay_between_items = 2.0
    batched_filter.batch_config.delay_between_batches = 30.0
    batched_filter.batch_config.rate_limit_delay = 60.0
    batched_filter.batch_config.max_retries = 3
    
    # Calculate estimates
    total_batches = (len(stocks) + 49) // 50
    estimated_time = (total_batches * 30 + len(stocks) * 2) / 60  # minutes
    
    print(f"⚙️  Configuration:")
    print(f"   • Batch size: 50 stocks")
    print(f"   • Total batches: {total_batches}")
    print(f"   • Estimated time: {estimated_time:.1f} minutes")
    print(f"   • Force refresh: True (fresh data)")
    
    logger.info(f"Processing configuration: {total_batches} batches, estimated {estimated_time:.1f} minutes")
    
    # Start processing
    start_time = datetime.now()
    logger.info(f"Starting batch processing at {start_time}")
    
    print(f"\n🔄 Starting processing at {start_time.strftime('%H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Process with force_refresh=True for fresh data
        results = batched_filter.get_shariah_universe_batched(
            stocks, fetcher, force_refresh=True
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Log completion
        logger.info(f"Processing completed at {end_time}")
        logger.info(f"Total processing time: {processing_time/60:.1f} minutes")
        
        # Display results
        print(f"\n🎉 Processing Completed!")
        print("=" * 30)
        
        summary = results['summary']
        batch_stats = results['batch_stats']
        
        print(f"⏱️  Processing time: {processing_time/60:.1f} minutes")
        print(f"📊 Stocks processed: {summary['total_processed']}")
        print(f"✅ Compliant: {summary['compliant_count']} ({summary['compliant_count']/summary['total_processed']*100:.1f}%)")
        print(f"❓ Unknown/Review: {summary['unknown_count']} ({summary['unknown_count']/summary['total_processed']*100:.1f}%)")
        print(f"⚠️  Errors: {summary['error_count']} ({summary['error_count']/summary['total_processed']*100:.1f}%)")
        print(f"⚡ Rate limited: {summary['rate_limited_count']}")
        print(f"📈 Success rate: {summary['success_rate']:.1f}%")
        
        # Log detailed results
        logger.info("=" * 60)
        logger.info("FINAL PROCESSING RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total processed: {summary['total_processed']}")
        logger.info(f"Compliant stocks: {summary['compliant_count']}")
        logger.info(f"Unknown stocks: {summary['unknown_count']}")
        logger.info(f"Error stocks: {summary['error_count']}")
        logger.info(f"Rate limited: {summary['rate_limited_count']}")
        logger.info(f"Success rate: {summary['success_rate']:.1f}%")
        logger.info(f"Cache usage: {summary['cache_usage_rate']:.1f}%")
        
        # Show top compliant stocks
        if results['compliant_stocks']:
            print(f"\n✅ Top 20 Shariah Compliant Stocks:")
            print("-" * 60)
            
            for i, stock in enumerate(results['compliant_stocks'][:20], 1):
                score = stock.get('compliance_score', 0)
                confidence = stock.get('confidence_level', 'unknown')
                market_cap = stock.get('market_cap', 0)
                
                print(f"{i:2d}. {stock['symbol']:12} | {stock['company_name'][:25]:25} | {confidence:6} | {score:.2f}")
                
                # Log compliant stocks
                if i <= 10:  # Log top 10
                    logger.info(f"Compliant {i:2d}: {stock['symbol']} - {stock['company_name']} (score: {score:.2f})")
        
        # Save results
        save_results(results, processing_time, log_filename)
        
        logger.info("Processing completed successfully")
        return results
        
    except KeyboardInterrupt:
        logger.warning("Processing interrupted by user")
        print(f"\n⚠️  Processing interrupted at {datetime.now().strftime('%H:%M:%S')}")
        return None
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def save_results(results, processing_time, log_filename):
    """Save results to JSON file"""
    try:
        output_file = f"nse_shariah_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Prepare results for JSON
        json_results = {
            'metadata': {
                'processing_date': datetime.now().isoformat(),
                'processing_time_minutes': processing_time / 60,
                'log_file': log_filename,
                'force_refresh_used': True,
                'batch_size': 50
            },
            'summary': results['summary'],
            'batch_stats': results['batch_stats'],
            'compliant_stocks': results['compliant_stocks'],
            'unknown_stocks': results['unknown_stocks'][:50],  # First 50 for file size
            'error_summary': {
                'total_errors': len(results['error_stocks']),
                'sample_errors': results['error_stocks'][:10]  # First 10 errors
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(json_results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {output_file}")
        logger.info(f"Results saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")

if __name__ == "__main__":
    print("🚀 NSE Shariah Compliance Processing - Final Version")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        results = run_full_nse_processing()
        
        if results:
            print(f"\n✅ Processing completed successfully!")
            print(f"📝 Check log file: {log_filename}")
            print(f"📊 Results saved to JSON file")
        else:
            print(f"\n⚠️  Processing was not completed")
            
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        logger.error(f"Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
