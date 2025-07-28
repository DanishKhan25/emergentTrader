#!/usr/bin/env python3
"""
Full NSE Shariah Compliance Processing
Process ALL NSE stocks with fresh data using batch processing to prevent rate limiting
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

import logging
import pandas as pd
from datetime import datetime
from services.yfinance_fetcher import YFinanceFetcher
from core.enhanced_shariah_filter_batched import BatchedShariahFilter
from core.data_cache import cache

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('full_nse_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_full_nse_universe():
    """Load complete NSE stock universe"""
    try:
        # Try to load from the data file
        df = pd.read_csv('data/nse_raw.csv')
        
        stocks = []
        for _, row in df.iterrows():
            symbol = row.get('SYMBOL', '').strip()
            if symbol and len(symbol) > 0:  # Only valid symbols
                stocks.append({
                    'symbol': symbol,
                    'company_name': row.get('NAME OF COMPANY', '').strip(),
                    'series': row.get(' SERIES', '').strip(),  # Note the space in column name
                    'listing_date': row.get(' DATE OF LISTING', ''),
                    'paid_up_value': row.get(' PAID UP VALUE', 0),
                    'market_lot': row.get(' MARKET LOT', 0),
                    'isin_number': row.get(' ISIN NUMBER', '').strip(),
                    'face_value': row.get(' FACE VALUE', 0)
                })
        
        # Filter for valid stocks (include EQ, BE, SM series and others)
        valid_stocks = []
        for stock in stocks:
            series = stock['series'].strip().upper()
            symbol = stock['symbol'].strip()
            
            # Include major series types and exclude penny stocks/suspended stocks
            if (series in ['EQ', 'BE', 'SM', 'BZ', 'BL'] and 
                len(symbol) > 0 and 
                not symbol.startswith('$') and
                stock['face_value'] > 0):
                valid_stocks.append(stock)
        
        logger.info(f"Loaded {len(stocks)} total stocks from NSE universe")
        logger.info(f"Filtered to {len(valid_stocks)} valid stocks for processing")
        
        return valid_stocks
        
    except Exception as e:
        logger.error(f"Error loading NSE universe: {str(e)}")
        
        # Fallback to a comprehensive list of major NSE stocks
        fallback_stocks = [
            {'symbol': 'TCS', 'company_name': 'Tata Consultancy Services', 'series': 'EQ'},
            {'symbol': 'RELIANCE', 'company_name': 'Reliance Industries', 'series': 'EQ'},
            {'symbol': 'HDFCBANK', 'company_name': 'HDFC Bank', 'series': 'EQ'},
            {'symbol': 'INFY', 'company_name': 'Infosys', 'series': 'EQ'},
            {'symbol': 'HINDUNILVR', 'company_name': 'Hindustan Unilever', 'series': 'EQ'},
            {'symbol': 'ICICIBANK', 'company_name': 'ICICI Bank', 'series': 'EQ'},
            {'symbol': 'KOTAKBANK', 'company_name': 'Kotak Mahindra Bank', 'series': 'EQ'},
            {'symbol': 'SBIN', 'company_name': 'State Bank of India', 'series': 'EQ'},
            {'symbol': 'BHARTIARTL', 'company_name': 'Bharti Airtel', 'series': 'EQ'},
            {'symbol': 'ITC', 'company_name': 'ITC Limited', 'series': 'EQ'},
            {'symbol': 'MARUTI', 'company_name': 'Maruti Suzuki', 'series': 'EQ'},
            {'symbol': 'ASIANPAINT', 'company_name': 'Asian Paints', 'series': 'EQ'},
            {'symbol': 'NESTLEIND', 'company_name': 'Nestle India', 'series': 'EQ'},
            {'symbol': 'HCLTECH', 'company_name': 'HCL Technologies', 'series': 'EQ'},
            {'symbol': 'WIPRO', 'company_name': 'Wipro', 'series': 'EQ'},
            {'symbol': 'AXISBANK', 'company_name': 'Axis Bank', 'series': 'EQ'},
            {'symbol': 'LT', 'company_name': 'Larsen & Toubro', 'series': 'EQ'},
            {'symbol': 'ULTRACEMCO', 'company_name': 'UltraTech Cement', 'series': 'EQ'},
            {'symbol': 'TITAN', 'company_name': 'Titan Company', 'series': 'EQ'},
            {'symbol': 'SUNPHARMA', 'company_name': 'Sun Pharmaceutical', 'series': 'EQ'},
            {'symbol': 'POWERGRID', 'company_name': 'Power Grid Corporation', 'series': 'EQ'},
            {'symbol': 'NTPC', 'company_name': 'NTPC Limited', 'series': 'EQ'},
            {'symbol': 'ONGC', 'company_name': 'Oil & Natural Gas Corporation', 'series': 'EQ'},
            {'symbol': 'TECHM', 'company_name': 'Tech Mahindra', 'series': 'EQ'},
            {'symbol': 'BAJFINANCE', 'company_name': 'Bajaj Finance', 'series': 'EQ'},
            {'symbol': 'HDFCLIFE', 'company_name': 'HDFC Life Insurance', 'series': 'EQ'},
            {'symbol': 'SBILIFE', 'company_name': 'SBI Life Insurance', 'series': 'EQ'},
            {'symbol': 'DIVISLAB', 'company_name': 'Divis Laboratories', 'series': 'EQ'},
            {'symbol': 'DRREDDY', 'company_name': 'Dr Reddys Laboratories', 'series': 'EQ'},
            {'symbol': 'CIPLA', 'company_name': 'Cipla Limited', 'series': 'EQ'},
            {'symbol': 'BRITANNIA', 'company_name': 'Britannia Industries', 'series': 'EQ'},
            {'symbol': 'COALINDIA', 'company_name': 'Coal India', 'series': 'EQ'},
            {'symbol': 'TATASTEEL', 'company_name': 'Tata Steel', 'series': 'EQ'},
            {'symbol': 'JSWSTEEL', 'company_name': 'JSW Steel', 'series': 'EQ'},
            {'symbol': 'HINDALCO', 'company_name': 'Hindalco Industries', 'series': 'EQ'},
            {'symbol': 'ADANIPORTS', 'company_name': 'Adani Ports and SEZ', 'series': 'EQ'},
            {'symbol': 'GRASIM', 'company_name': 'Grasim Industries', 'series': 'EQ'},
            {'symbol': 'BAJAJFINSV', 'company_name': 'Bajaj Finserv', 'series': 'EQ'},
            {'symbol': 'EICHERMOT', 'company_name': 'Eicher Motors', 'series': 'EQ'},
            {'symbol': 'HEROMOTOCO', 'company_name': 'Hero MotoCorp', 'series': 'EQ'},
            {'symbol': 'BAJAJ-AUTO', 'company_name': 'Bajaj Auto', 'series': 'EQ'},
            {'symbol': 'TATACONSUM', 'company_name': 'Tata Consumer Products', 'series': 'EQ'},
            {'symbol': 'INDUSINDBK', 'company_name': 'IndusInd Bank', 'series': 'EQ'},
            {'symbol': 'SHREECEM', 'company_name': 'Shree Cement', 'series': 'EQ'},
            {'symbol': 'APOLLOHOSP', 'company_name': 'Apollo Hospitals', 'series': 'EQ'},
            {'symbol': 'TATAMOTORS', 'company_name': 'Tata Motors', 'series': 'EQ'},
            {'symbol': 'M&M', 'company_name': 'Mahindra & Mahindra', 'series': 'EQ'},
            {'symbol': 'BPCL', 'company_name': 'Bharat Petroleum', 'series': 'EQ'},
            {'symbol': 'IOC', 'company_name': 'Indian Oil Corporation', 'series': 'EQ'},
            {'symbol': 'ADANIENT', 'company_name': 'Adani Enterprises', 'series': 'EQ'},
            {'symbol': 'GODREJCP', 'company_name': 'Godrej Consumer Products', 'series': 'EQ'}
        ]
        
        logger.warning(f"Using fallback list of {len(fallback_stocks)} major NSE stocks")
        return fallback_stocks

def clear_cache_for_fresh_data():
    """Clear relevant cache to ensure fresh data"""
    try:
        logger.info("Clearing cache to ensure fresh data...")
        
        # Clear stock info cache
        cache.clear_cache_type('stock_info')
        
        # Clear Shariah compliance cache  
        cache.clear_cache_type('shariah_compliance')
        
        # Clear stock data cache
        cache.clear_cache_type('stock_data')
        
        logger.info("✅ Cache cleared successfully - will fetch fresh data")
        
    except Exception as e:
        logger.warning(f"Could not clear cache: {str(e)} - will use force_refresh instead")

def process_full_nse_with_batching():
    """Process full NSE universe with batch processing and fresh data"""
    
    print("🚀 Starting Full NSE Shariah Compliance Processing")
    print("=" * 65)
    
    # Load full NSE universe
    print("📊 Loading NSE stock universe...")
    nse_stocks = load_full_nse_universe()
    
    if not nse_stocks:
        print("❌ No stocks loaded. Exiting.")
        return
    
    print(f"✅ Loaded {len(nse_stocks)} stocks for processing")
    
    # Clear cache for fresh data
    print("\n🔄 Clearing cache for fresh data...")
    clear_cache_for_fresh_data()
    
    # Initialize components
    print("\n⚙️  Initializing batch processing system...")
    fetcher = YFinanceFetcher()
    
    # Configure for comprehensive processing
    batched_filter = BatchedShariahFilter(batch_size=50)
    
    # Adjust configuration for large-scale processing
    batched_filter.batch_config.delay_between_items = 0.01      # 2 seconds between stocks
    batched_filter.batch_config.delay_between_batches = 1.0  # 45 seconds between batches
    batched_filter.batch_config.rate_limit_delay = 5.0       # 2 minutes when rate limited
    batched_filter.batch_config.max_retries = 3               # More retries for reliability
    
    print(f"✅ Batch configuration:")
    print(f"   • Batch size: {batched_filter.batch_size} stocks")
    print(f"   • Delay between stocks: {batched_filter.batch_config.delay_between_items}s")
    print(f"   • Delay between batches: {batched_filter.batch_config.delay_between_batches}s")
    print(f"   • Rate limit delay: {batched_filter.batch_config.rate_limit_delay}s")
    
    # Calculate estimated processing time
    total_batches = (len(nse_stocks) + batched_filter.batch_size - 1) // batched_filter.batch_size
    estimated_time = (total_batches * batched_filter.batch_config.delay_between_batches + 
                     len(nse_stocks) * batched_filter.batch_config.delay_between_items)
    
    print(f"\n📈 Processing estimates:")
    print(f"   • Total stocks: {len(nse_stocks)}")
    print(f"   • Expected batches: {total_batches}")
    print(f"   • Estimated time: {estimated_time/60:.1f} minutes ({estimated_time/3600:.1f} hours)")
    
    # Confirm before starting
    response = input(f"\n🤔 This will process {len(nse_stocks)} stocks and take approximately {estimated_time/60:.1f} minutes. Continue? (y/N): ")
    if response.lower() != 'y':
        print("❌ Processing cancelled by user")
        return
    
    # Start processing
    print(f"\n🚀 Starting batch processing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Process with force_refresh=True to ensure fresh data
        results = batched_filter.get_shariah_universe_batched(
            nse_stocks, fetcher, force_refresh=True
        )
        
        end_time = datetime.now()
        total_processing_time = (end_time - start_time).total_seconds()
        
        # Display comprehensive results
        print("\n" + "=" * 80)
        print("🎉 FULL NSE PROCESSING COMPLETED!")
        print("=" * 80)
        
        summary = results['summary']
        batch_stats = results['batch_stats']
        
        print(f"⏱️  Total processing time: {total_processing_time/60:.1f} minutes ({total_processing_time/3600:.1f} hours)")
        print(f"📊 Stocks processed: {summary['total_processed']}")
        print(f"✅ Compliant stocks: {summary['compliant_count']} ({summary['compliant_count']/summary['total_processed']*100:.1f}%)")
        print(f"❓ Unknown/Review needed: {summary['unknown_count']} ({summary['unknown_count']/summary['total_processed']*100:.1f}%)")
        print(f"⚠️  Errors: {summary['error_count']} ({summary['error_count']/summary['total_processed']*100:.1f}%)")
        print(f"⚡ Rate limited: {summary['rate_limited_count']} ({summary['rate_limited_count']/summary['total_processed']*100:.1f}%)")
        print(f"📈 Overall success rate: {summary['success_rate']:.1f}%")
        
        print(f"\n🔄 Batch Processing Statistics:")
        print(f"   • Total batches: {batch_stats['total_batches']}")
        print(f"   • Successful batches: {batch_stats['successful_batches']}")
        print(f"   • Rate limited batches: {batch_stats['rate_limited_batches']}")
        print(f"   • Average batch time: {batch_stats['average_batch_time']:.1f}s")
        print(f"   • Circuit breaker activations: {batch_stats['circuit_breaker_activations']}")
        
        # Show top compliant stocks
        if results['compliant_stocks']:
            print(f"\n✅ TOP SHARIAH COMPLIANT STOCKS:")
            print("-" * 50)
            for i, stock in enumerate(results['compliant_stocks'][:20], 1):  # Top 20
                score = stock.get('compliance_score', 0)
                confidence = stock.get('confidence_level', 'unknown')
                market_cap = stock.get('market_cap', 0)
                print(f"{i:2d}. {stock['symbol']:12} | {stock['company_name'][:30]:30} | Score: {score:.2f} | {confidence:6} | ₹{market_cap:,}")
            
            if len(results['compliant_stocks']) > 20:
                print(f"    ... and {len(results['compliant_stocks']) - 20} more compliant stocks")
        
        # Save results to file
        save_results_to_file(results, total_processing_time)
        
        # Show summary statistics
        print(f"\n📊 FINAL SUMMARY:")
        print(f"   • Processing completed successfully")
        print(f"   • {summary['compliant_count']} Shariah compliant stocks identified")
        print(f"   • Results saved to 'nse_shariah_compliance_results.json'")
        print(f"   • Processing log saved to 'full_nse_processing.log'")
        
        return results
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Processing interrupted by user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Partial results may be available in cache")
        return None
        
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        logger.error(f"Processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def save_results_to_file(results, processing_time):
    """Save results to JSON file for later analysis"""
    try:
        import json
        
        # Prepare results for JSON serialization
        json_results = {
            'processing_metadata': {
                'processing_date': datetime.now().isoformat(),
                'processing_time_seconds': processing_time,
                'processing_time_minutes': processing_time / 60,
                'force_refresh_used': True,
                'batch_processing': True
            },
            'summary': results['summary'],
            'batch_stats': results['batch_stats'],
            'compliant_stocks': results['compliant_stocks'],
            'unknown_stocks': results['unknown_stocks'][:100],  # Limit to first 100 for file size
            'error_summary': {
                'total_errors': len(results['error_stocks']),
                'error_types': {}
            }
        }
        
        # Analyze error types
        for error in results['error_stocks']:
            error_type = error.get('error_type', 'unknown')
            json_results['error_summary']['error_types'][error_type] = json_results['error_summary']['error_types'].get(error_type, 0) + 1
        
        # Save to file
        with open('nse_shariah_compliance_results.json', 'w') as f:
            json.dump(json_results, f, indent=2, default=str)
        
        print(f"💾 Results saved to 'nse_shariah_compliance_results.json'")
        
    except Exception as e:
        logger.error(f"Error saving results to file: {str(e)}")

if __name__ == "__main__":
    try:
        results = process_full_nse_with_batching()
        
        if results:
            print(f"\n🎉 Full NSE Shariah compliance processing completed successfully!")
            print(f"Check 'nse_shariah_compliance_results.json' for detailed results.")
        else:
            print(f"\n⚠️  Processing was not completed successfully.")
            
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
