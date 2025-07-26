"""
Enhanced Shariah Filter with Smart Batch Processing
Uses intelligent delays - no delays for cached data, normal delays for fresh API calls
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .enhanced_shariah_filter import EnhancedShariahFilter, ComplianceStatus
from .smart_batch_processor import SmartBatchProcessor, BatchConfig

logger = logging.getLogger(__name__)

class SmartShariahFilter(EnhancedShariahFilter):
    """Enhanced Shariah Filter with smart batch processing that optimizes for cached data"""
    
    def __init__(self, config_path: Optional[str] = None, batch_size: int = 50):
        super().__init__(config_path)
        self.batch_size = batch_size
        self.name = "Smart Enhanced Shariah Compliance Filter"
        
        # Cache for universe results to avoid reprocessing
        self._cached_universe = None
        self._cached_universe_timestamp = None
        self._universe_cache_duration = 3600  # 1 hour cache
        
        # Configure smart batch processor
        self.batch_config = BatchConfig(
            batch_size=batch_size,
            delay_between_items=1.0,      # Will be 0 for cached data
            delay_between_batches=15.0,   # Will be 0 for cached data
            max_retries=2,
            rate_limit_delay=30.0,
            circuit_breaker_threshold=3
        )
        
        self.smart_processor = SmartBatchProcessor(self.batch_config)
        
        logger.info(f"Initialized Smart Shariah Filter with intelligent delay management")
    
    def _is_universe_cache_valid(self) -> bool:
        """Check if the cached universe is still valid"""
        if self._cached_universe is None or self._cached_universe_timestamp is None:
            return False
        
        from datetime import datetime, timedelta
        cache_age = datetime.now() - self._cached_universe_timestamp
        return cache_age.total_seconds() < self._universe_cache_duration
    
    def _get_cached_universe_symbols(self) -> Optional[List[str]]:
        """Get cached Shariah compliant symbols if cache is valid"""
        if self._is_universe_cache_valid():
            logger.info(f"Using cached Shariah universe with {len(self._cached_universe)} stocks")
            return self._cached_universe
        return None
    
    def _cache_universe_symbols(self, symbols: List[str]):
        """Cache the Shariah compliant symbols"""
        from datetime import datetime
        self._cached_universe = symbols
        self._cached_universe_timestamp = datetime.now()
        logger.info(f"Cached Shariah universe with {len(symbols)} stocks")
    
    def get_shariah_universe_smart_cached(self, nse_stocks: List[Dict], 
                                        data_fetcher, 
                                        force_refresh: bool = False) -> List[str]:
        """
        Get Shariah compliant universe with intelligent caching
        Returns only symbols for faster processing
        """
        try:
            # Check cache first unless force refresh
            if not force_refresh:
                cached_symbols = self._get_cached_universe_symbols()
                if cached_symbols is not None:
                    return cached_symbols
            
            # If cache miss or force refresh, process normally
            logger.info("Cache miss or force refresh - processing Shariah compliance")
            compliant_result = self.get_shariah_universe_smart(nse_stocks, data_fetcher, force_refresh)
            
            # Extract symbols correctly from the result dictionary
            symbols = []
            if isinstance(compliant_result, dict) and 'compliant_stocks' in compliant_result:
                compliant_stocks = compliant_result['compliant_stocks']
                symbols = [stock['symbol'] for stock in compliant_stocks if isinstance(stock, dict) and 'symbol' in stock]
            elif isinstance(compliant_result, list):
                # Fallback for list format
                symbols = [stock['symbol'] for stock in compliant_result if isinstance(stock, dict) and 'symbol' in stock]
            
            # Cache the extracted symbols
            self._cache_universe_symbols(symbols)
            
            logger.info(f"Extracted and cached {len(symbols)} Shariah compliant symbols")
            return symbols
            
        except Exception as e:
            logger.error(f"Error in smart cached universe: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_shariah_universe_smart(self, 
                                 stock_universe: List[Dict], 
                                 stock_fetcher, 
                                 force_refresh: bool = False) -> Dict[str, Any]:
        """
        Smart Shariah universe filtering with intelligent delay management
        
        Args:
            stock_universe: List of stock dictionaries from NSE universe
            stock_fetcher: YFinanceFetcher instance to get stock data
            force_refresh: Force refresh of all cached compliance data
            
        Returns:
            Dictionary with comprehensive results and smart processing stats
        """
        logger.info(f"Starting SMART Shariah compliance check for {len(stock_universe)} stocks")
        logger.info(f"Force refresh: {force_refresh} (will use {'fresh API calls' if force_refresh else 'cached data when available'})")
        
        # Extract symbols from stock universe
        symbols = []
        for stock_dict in stock_universe:
            if isinstance(stock_dict, dict):
                symbol = stock_dict.get('symbol', '')
            else:
                symbol = str(stock_dict)
            
            if symbol:
                symbols.append(symbol)
        
        if not symbols:
            logger.warning("No valid symbols found in stock universe")
            return self._create_empty_result()
        
        # Process stocks using smart batch processing
        batch_results = self._process_stocks_with_smart_batching(symbols, stock_fetcher, force_refresh)
        
        # Aggregate results
        aggregated_results = self._aggregate_smart_batch_results(batch_results, stock_universe)
        
        # Cache summary
        self._cache_smart_summary(aggregated_results)
        
        return aggregated_results
    
    def _process_stocks_with_smart_batching(self, 
                                          symbols: List[str], 
                                          stock_fetcher, 
                                          force_refresh: bool) -> List:
        """Process stocks using smart batch processing with cache detection"""
        
        def process_single_stock_smart(symbol: str) -> Dict[str, Any]:
            """Process a single stock with smart caching detection"""
            processing_start = datetime.now()
            
            try:
                # Check if we have cached compliance data first
                if not force_refresh:
                    cached_compliance = self.get_cached_compliance(symbol, force_refresh=False)
                    if cached_compliance:
                        processing_time = (datetime.now() - processing_start).total_seconds()
                        logger.debug(f"Using cached compliance for {symbol} ({processing_time:.3f}s)")
                        
                        return {
                            'symbol': symbol,
                            'status': 'cached_compliance',
                            'compliance_result': cached_compliance,
                            'data_source': 'cached_compliance',
                            'processing_time': processing_time
                        }
                
                # Get stock information (may be cached or fresh)
                stock_info = stock_fetcher.get_stock_info(symbol)
                
                if not stock_info or not stock_info.get('symbol'):
                    # Try cached compliance as fallback
                    cached_compliance = self.get_cached_compliance(symbol, force_refresh=False)
                    if cached_compliance:
                        processing_time = (datetime.now() - processing_start).total_seconds()
                        logger.info(f"Using cached compliance for {symbol} (no fresh stock info)")
                        
                        return {
                            'symbol': symbol,
                            'status': 'cached_fallback',
                            'compliance_result': cached_compliance,
                            'data_source': 'cached_fallback',
                            'processing_time': processing_time
                        }
                    else:
                        processing_time = (datetime.now() - processing_start).total_seconds()
                        return {
                            'symbol': symbol,
                            'status': 'no_data',
                            'error': 'No stock info or cached compliance available',
                            'processing_time': processing_time
                        }
                
                # Enhanced compliance check
                compliance_result = self.is_shariah_compliant_enhanced(
                    stock_info, symbol, force_refresh
                )
                
                processing_time = (datetime.now() - processing_start).total_seconds()
                
                # Determine data source based on processing time and stock_info source
                data_source = 'cached_data' if processing_time < 0.5 else 'fresh_api'
                if stock_info.get('data_source') == 'yahoo_finance':
                    data_source = 'fresh_api'
                
                return {
                    'symbol': symbol,
                    'status': 'processed',
                    'compliance_result': compliance_result,
                    'stock_info': stock_info,
                    'data_source': data_source,
                    'processing_time': processing_time
                }
                
            except Exception as e:
                processing_time = (datetime.now() - processing_start).total_seconds()
                error_msg = str(e).lower()
                
                # Check if it's a rate limiting error
                if any(phrase in error_msg for phrase in ['rate limit', 'too many requests', '429']):
                    # Try cached compliance data during rate limiting
                    cached_compliance = self.get_cached_compliance(symbol, force_refresh=False)
                    if cached_compliance:
                        logger.info(f"Rate limited - using cached compliance for {symbol}")
                        return {
                            'symbol': symbol,
                            'status': 'rate_limited_cached',
                            'compliance_result': cached_compliance,
                            'data_source': 'cached_due_to_rate_limit',
                            'processing_time': processing_time
                        }
                
                logger.error(f"Error processing {symbol}: {str(e)}")
                return {
                    'symbol': symbol,
                    'status': 'error',
                    'error': str(e),
                    'processing_time': processing_time
                }
        
        # Use smart batch processor with cache detection
        batch_results = self.smart_processor.process_batch_smart(
            symbols, process_single_stock_smart, "smart_shariah_compliance", detect_data_source=True
        )
        
        return batch_results
    
    def _aggregate_smart_batch_results(self, batch_results: List, stock_universe: List[Dict]) -> Dict[str, Any]:
        """Aggregate smart batch processing results"""
        
        compliant_stocks = []
        unknown_stocks = []
        error_stocks = []
        cached_stocks = []
        
        # Create symbol to stock_dict mapping
        symbol_to_stock = {}
        for stock_dict in stock_universe:
            if isinstance(stock_dict, dict):
                symbol = stock_dict.get('symbol', '')
                if symbol:
                    symbol_to_stock[symbol] = stock_dict
        
        # Process all batch results
        total_processed = 0
        total_rate_limited = 0
        total_cached_used = 0
        total_api_calls = 0
        total_processing_time = 0
        
        for batch_result in batch_results:
            total_processed += batch_result.processed_count
            total_rate_limited += batch_result.rate_limited_count
            total_processing_time += batch_result.processing_time
            
            # Track cache usage from smart processor
            if hasattr(batch_result, 'cache_hits'):
                total_cached_used += batch_result.cache_hits
            if hasattr(batch_result, 'api_calls'):
                total_api_calls += batch_result.api_calls
            
            # Process successful results
            for result_item in batch_result.results:
                if result_item['status'] == 'success':
                    stock_result = result_item['result']
                    symbol = stock_result['symbol']
                    
                    self._categorize_stock_result(
                        stock_result, symbol_to_stock.get(symbol, {}),
                        compliant_stocks, unknown_stocks, error_stocks, cached_stocks
                    )
            
            # Process errors
            for error_item in batch_result.errors:
                if error_item['status'] == 'rate_limited':
                    symbol = error_item['item']
                    cached_compliance = self.get_cached_compliance(symbol, force_refresh=False)
                    
                    if cached_compliance:
                        stock_result = {
                            'symbol': symbol,
                            'compliance_result': cached_compliance,
                            'data_source': 'cached_due_to_rate_limit'
                        }
                        
                        self._categorize_stock_result(
                            stock_result, symbol_to_stock.get(symbol, {}),
                            compliant_stocks, unknown_stocks, error_stocks, cached_stocks
                        )
                        total_cached_used += 1
                    else:
                        error_stocks.append({
                            'symbol': symbol,
                            'error': 'Rate limited and no cached data available',
                            'error_type': 'rate_limited_no_cache'
                        })
                else:
                    symbol = error_item.get('item', 'unknown')
                    error_stocks.append({
                        'symbol': symbol,
                        'error': error_item.get('error', 'Unknown error'),
                        'error_type': 'processing_error'
                    })
        
        # Sort results
        compliant_stocks.sort(key=lambda x: (-x.get('compliance_score', 0), -x.get('market_cap', 0)))
        
        # Calculate performance metrics
        cache_usage_rate = (total_cached_used / total_processed * 100) if total_processed > 0 else 0
        processing_speed = total_processed / total_processing_time if total_processing_time > 0 else 0
        
        # Create comprehensive results
        results = {
            'compliant_stocks': compliant_stocks,
            'unknown_stocks': unknown_stocks,
            'error_stocks': error_stocks,
            'cached_stocks': cached_stocks,
            'summary': {
                'total_processed': total_processed,
                'compliant_count': len(compliant_stocks),
                'unknown_count': len(unknown_stocks),
                'error_count': len(error_stocks),
                'cached_used_count': total_cached_used,
                'api_calls_count': total_api_calls,
                'rate_limited_count': total_rate_limited,
                'cache_usage_rate': cache_usage_rate,
                'success_rate': ((len(compliant_stocks) + len(unknown_stocks)) / total_processed * 100) if total_processed > 0 else 0,
                'processing_date': datetime.now().isoformat(),
                'total_processing_time': total_processing_time,
                'processing_speed_per_second': processing_speed
            },
            'smart_batch_stats': {
                'total_batches': len(batch_results),
                'successful_batches': len([br for br in batch_results if br.status.value == 'completed']),
                'rate_limited_batches': len([br for br in batch_results if br.status.value == 'rate_limited']),
                'average_batch_time': sum(br.processing_time for br in batch_results) / len(batch_results) if batch_results else 0,
                'circuit_breaker_activations': self.smart_processor.circuit_breaker_failures,
                'smart_optimization_used': True,
                'cache_hit_rate': cache_usage_rate
            }
        }
        
        # Log smart summary
        self._log_smart_compliance_summary(results)
        
        return results
    
    def _categorize_stock_result(self, stock_result: Dict, stock_dict: Dict,
                               compliant_stocks: List, unknown_stocks: List, 
                               error_stocks: List, cached_stocks: List):
        """Categorize a single stock result (same as parent class)"""
        
        symbol = stock_result['symbol']
        compliance_result = stock_result.get('compliance_result', {})
        
        if not compliance_result:
            error_stocks.append({
                'symbol': symbol,
                'error': 'No compliance result available',
                'error_type': 'no_compliance_data'
            })
            return
        
        compliance_status = compliance_result.get('compliance_status', 'unknown')
        confidence_level = compliance_result.get('confidence_level', 'unknown')
        
        # Get additional stock info
        stock_info = stock_result.get('stock_info', {})
        
        base_stock_data = {
            'symbol': symbol,
            'company_name': stock_info.get('company_name', stock_dict.get('company_name', '')),
            'sector': stock_info.get('sector', stock_dict.get('sector', 'Unknown')),
            'market_cap': stock_info.get('market_cap', stock_dict.get('market_cap', 0)),
            'compliance_score': compliance_result.get('compliance_score', 0),
            'confidence_level': confidence_level,
            'compliance_details': compliance_result,
            'data_source': stock_result.get('data_source', 'unknown')
        }
        
        if compliance_status == ComplianceStatus.COMPLIANT.value:
            compliant_stocks.append(base_stock_data)
        elif compliance_status == ComplianceStatus.UNKNOWN.value:
            unknown_stocks.append({
                **base_stock_data,
                'review_required': True,
                'review_reason': compliance_result.get('review_reason', 'Insufficient data for definitive compliance')
            })
        elif compliance_status == ComplianceStatus.ERROR.value:
            error_stocks.append({
                'symbol': symbol,
                'error': compliance_result.get('error', 'Compliance check error'),
                'error_type': 'compliance_error',
                'compliance_details': compliance_result
            })
        
        # Track cached usage
        if stock_result.get('data_source') in ['cached_compliance', 'cached_fallback', 'cached_due_to_rate_limit', 'cached_data']:
            cached_stocks.append({
                'symbol': symbol,
                'cache_source': stock_result.get('data_source'),
                'compliance_status': compliance_status
            })
    
    def _log_smart_compliance_summary(self, results: Dict):
        """Log smart compliance processing summary"""
        summary = results['summary']
        batch_stats = results['smart_batch_stats']
        
        logger.info("=" * 75)
        logger.info("SMART SHARIAH COMPLIANCE SUMMARY")
        logger.info("=" * 75)
        logger.info(f"Total stocks processed: {summary['total_processed']}")
        logger.info(f"✅ Compliant stocks: {summary['compliant_count']} ({summary['compliant_count']/summary['total_processed']*100:.1f}%)")
        logger.info(f"❓ Unknown/Review needed: {summary['unknown_count']} ({summary['unknown_count']/summary['total_processed']*100:.1f}%)")
        logger.info(f"⚠️  Errors: {summary['error_count']} ({summary['error_count']/summary['total_processed']*100:.1f}%)")
        logger.info(f"🔄 Cached data used: {summary['cached_used_count']} ({summary['cache_usage_rate']:.1f}%)")
        logger.info(f"📡 API calls made: {summary['api_calls_count']}")
        logger.info(f"⚡ Rate limited: {summary['rate_limited_count']}")
        logger.info(f"📊 Overall success rate: {summary['success_rate']:.1f}%")
        logger.info(f"⏱️  Total processing time: {summary['total_processing_time']:.1f}s")
        logger.info(f"🚀 Processing speed: {summary['processing_speed_per_second']:.1f} stocks/second")
        logger.info("")
        logger.info("SMART BATCH PROCESSING STATS:")
        logger.info(f"Total batches: {batch_stats['total_batches']}")
        logger.info(f"Successful batches: {batch_stats['successful_batches']}")
        logger.info(f"Rate limited batches: {batch_stats['rate_limited_batches']}")
        logger.info(f"Average batch time: {batch_stats['average_batch_time']:.1f}s")
        logger.info(f"Cache hit rate: {batch_stats['cache_hit_rate']:.1f}%")
        logger.info(f"Smart optimization: {'ENABLED' if batch_stats['smart_optimization_used'] else 'DISABLED'}")
        logger.info("=" * 75)
    
    def _cache_smart_summary(self, results: Dict):
        """Cache the smart processing summary"""
        try:
            cache_summary = {
                **results['summary'],
                'smart_batch_processing': True,
                'batch_size_used': self.batch_size,
                'smart_batch_stats': results['smart_batch_stats']
            }
            
            self.set_cached_compliance('shariah_summary', 'latest_smart', cache_summary)
            logger.debug("Cached smart processing summary")
            
        except Exception as e:
            logger.error(f"Error caching smart summary: {str(e)}")
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create empty result structure"""
        return {
            'compliant_stocks': [],
            'unknown_stocks': [],
            'error_stocks': [],
            'cached_stocks': [],
            'summary': {
                'total_processed': 0,
                'compliant_count': 0,
                'unknown_count': 0,
                'error_count': 0,
                'cached_used_count': 0,
                'api_calls_count': 0,
                'rate_limited_count': 0,
                'cache_usage_rate': 0,
                'success_rate': 0,
                'processing_date': datetime.now().isoformat(),
                'total_processing_time': 0,
                'processing_speed_per_second': 0
            },
            'smart_batch_stats': {
                'total_batches': 0,
                'successful_batches': 0,
                'rate_limited_batches': 0,
                'average_batch_time': 0,
                'circuit_breaker_activations': 0,
                'smart_optimization_used': True,
                'cache_hit_rate': 0
            }
        }
    
    def get_smart_processor_stats(self) -> Dict[str, Any]:
        """Get smart processor statistics"""
        return self.smart_processor.get_processing_stats()
    
    def reset_smart_processor(self):
        """Reset smart processor state"""
        self.smart_processor.reset_circuit_breaker()
        logger.info("Smart processor state reset")

# Backward compatibility
SmartBatchedShariahFilter = SmartShariahFilter
