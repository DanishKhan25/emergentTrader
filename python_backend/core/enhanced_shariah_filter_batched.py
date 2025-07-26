"""
Enhanced Shariah Filter with Batch Processing
Integrates batch processing to prevent rate limiting while maintaining all existing functionality
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .enhanced_shariah_filter import EnhancedShariahFilter, ComplianceStatus
from .batch_processor import BatchProcessor, BatchConfig, batch_process_shariah_compliance

logger = logging.getLogger(__name__)

class BatchedShariahFilter(EnhancedShariahFilter):
    """Enhanced Shariah Filter with integrated batch processing"""
    
    def __init__(self, config_path: Optional[str] = None, batch_size: int = 50):
        super().__init__(config_path)
        self.batch_size = batch_size
        self.name = "Batched Enhanced Shariah Compliance Filter"
        
        # Configure batch processor for Shariah compliance
        self.batch_config = BatchConfig(
            batch_size=batch_size,
            delay_between_items=2.0,  # 2 seconds between stocks
            delay_between_batches=30.0,  # 30 seconds between batches
            max_retries=2,
            rate_limit_delay=60.0,  # 1 minute when rate limited
            circuit_breaker_threshold=3
        )
        
        self.batch_processor = BatchProcessor(self.batch_config)
        
        logger.info(f"Initialized Batched Shariah Filter with batch_size={batch_size}")
    
    def get_shariah_universe_batched(self, 
                                   stock_universe: List[Dict], 
                                   stock_fetcher, 
                                   force_refresh: bool = False) -> Dict[str, Any]:
        """
        Enhanced Shariah universe filtering with batch processing
        
        Args:
            stock_universe: List of stock dictionaries from NSE universe
            stock_fetcher: YFinanceFetcher instance to get stock data
            force_refresh: Force refresh of all cached compliance data
            
        Returns:
            Dictionary with comprehensive results including batch processing stats
        """
        logger.info(f"Starting batched Shariah compliance check for {len(stock_universe)} stocks")
        logger.info(f"Batch configuration: size={self.batch_size}, delay_between_batches={self.batch_config.delay_between_batches}s")
        
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
        
        # Process stocks in batches
        batch_results = self._process_stocks_in_batches(symbols, stock_fetcher, force_refresh)
        
        # Aggregate results
        aggregated_results = self._aggregate_batch_results(batch_results, stock_universe)
        
        # Cache summary
        self._cache_batch_summary(aggregated_results)
        
        return aggregated_results
    
    def _process_stocks_in_batches(self, 
                                 symbols: List[str], 
                                 stock_fetcher, 
                                 force_refresh: bool) -> List:
        """Process stocks in batches with rate limiting protection"""
        
        def process_single_stock(symbol: str) -> Dict[str, Any]:
            """Process a single stock for Shariah compliance"""
            try:
                # Get stock information (with caching)
                stock_info = stock_fetcher.get_stock_info(symbol)
                
                if not stock_info or not stock_info.get('symbol'):
                    # Try to use cached compliance data if stock info fails
                    cached_compliance = self.get_cached_compliance(symbol, force_refresh=False)
                    if cached_compliance:
                        logger.info(f"Using cached compliance for {symbol} (no fresh stock info)")
                        return {
                            'symbol': symbol,
                            'status': 'cached_compliance',
                            'compliance_result': cached_compliance,
                            'data_source': 'cached_only'
                        }
                    else:
                        return {
                            'symbol': symbol,
                            'status': 'no_data',
                            'error': 'No stock info or cached compliance available'
                        }
                
                # Enhanced compliance check
                compliance_result = self.is_shariah_compliant_enhanced(
                    stock_info, symbol, force_refresh
                )
                
                return {
                    'symbol': symbol,
                    'status': 'processed',
                    'compliance_result': compliance_result,
                    'stock_info': stock_info,
                    'data_source': 'fresh_and_compliance'
                }
                
            except Exception as e:
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
                            'data_source': 'cached_due_to_rate_limit'
                        }
                
                logger.error(f"Error processing {symbol}: {str(e)}")
                return {
                    'symbol': symbol,
                    'status': 'error',
                    'error': str(e)
                }
        
        # Use batch processor
        batch_results = self.batch_processor.process_batch(
            symbols, process_single_stock, "shariah_compliance_batch"
        )
        
        return batch_results
    
    def _aggregate_batch_results(self, batch_results: List, stock_universe: List[Dict]) -> Dict[str, Any]:
        """Aggregate batch processing results into final compliance results"""
        
        compliant_stocks = []
        unknown_stocks = []
        error_stocks = []
        cached_stocks = []
        
        # Create symbol to stock_dict mapping for additional info
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
        
        for batch_result in batch_results:
            total_processed += batch_result.processed_count
            total_rate_limited += batch_result.rate_limited_count
            
            # Process successful results
            for result_item in batch_result.results:
                if result_item['status'] == 'success':
                    stock_result = result_item['result']
                    symbol = stock_result['symbol']
                    
                    self._categorize_stock_result(
                        stock_result, symbol_to_stock.get(symbol, {}),
                        compliant_stocks, unknown_stocks, error_stocks, cached_stocks
                    )
                    
                    if stock_result.get('data_source') in ['cached_only', 'cached_due_to_rate_limit']:
                        total_cached_used += 1
            
            # Process errors (including rate limited items)
            for error_item in batch_result.errors:
                if error_item['status'] == 'rate_limited':
                    # Try to get cached compliance for rate limited items
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
                    # Regular errors
                    symbol = error_item.get('item', 'unknown')
                    error_stocks.append({
                        'symbol': symbol,
                        'error': error_item.get('error', 'Unknown error'),
                        'error_type': 'processing_error'
                    })
        
        # Sort results
        compliant_stocks.sort(key=lambda x: (-x.get('compliance_score', 0), -x.get('market_cap', 0)))
        
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
                'rate_limited_count': total_rate_limited,
                'cache_usage_rate': (total_cached_used / total_processed * 100) if total_processed > 0 else 0,
                'success_rate': ((len(compliant_stocks) + len(unknown_stocks)) / total_processed * 100) if total_processed > 0 else 0,
                'processing_date': datetime.now().isoformat()
            },
            'batch_stats': {
                'total_batches': len(batch_results),
                'successful_batches': len([br for br in batch_results if br.status.value == 'completed']),
                'rate_limited_batches': len([br for br in batch_results if br.status.value == 'rate_limited']),
                'total_processing_time': sum(br.processing_time for br in batch_results),
                'average_batch_time': sum(br.processing_time for br in batch_results) / len(batch_results) if batch_results else 0,
                'circuit_breaker_activations': self.batch_processor.circuit_breaker_failures
            }
        }
        
        # Log comprehensive summary
        self._log_batch_compliance_summary(results)
        
        return results
    
    def _categorize_stock_result(self, stock_result: Dict, stock_dict: Dict,
                               compliant_stocks: List, unknown_stocks: List, 
                               error_stocks: List, cached_stocks: List):
        """Categorize a single stock result"""
        
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
        # Non-compliant stocks are not included in results (filtered out)
        
        # Track cached usage
        if stock_result.get('data_source') in ['cached_only', 'cached_due_to_rate_limit']:
            cached_stocks.append({
                'symbol': symbol,
                'cache_source': stock_result.get('data_source'),
                'compliance_status': compliance_status
            })
    
    def _log_batch_compliance_summary(self, results: Dict):
        """Log comprehensive batch compliance summary"""
        summary = results['summary']
        batch_stats = results['batch_stats']
        
        logger.info("=" * 70)
        logger.info("BATCHED SHARIAH COMPLIANCE SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total stocks processed: {summary['total_processed']}")
        logger.info(f"✅ Compliant stocks: {summary['compliant_count']} ({summary['compliant_count']/summary['total_processed']*100:.1f}%)")
        logger.info(f"❓ Unknown/Review needed: {summary['unknown_count']} ({summary['unknown_count']/summary['total_processed']*100:.1f}%)")
        logger.info(f"⚠️  Errors: {summary['error_count']} ({summary['error_count']/summary['total_processed']*100:.1f}%)")
        logger.info(f"🔄 Cached data used: {summary['cached_used_count']} ({summary['cache_usage_rate']:.1f}%)")
        logger.info(f"⚡ Rate limited: {summary['rate_limited_count']} ({summary['rate_limited_count']/summary['total_processed']*100:.1f}%)")
        logger.info(f"📊 Overall success rate: {summary['success_rate']:.1f}%")
        logger.info("")
        logger.info("BATCH PROCESSING STATS:")
        logger.info(f"Total batches: {batch_stats['total_batches']}")
        logger.info(f"Successful batches: {batch_stats['successful_batches']}")
        logger.info(f"Rate limited batches: {batch_stats['rate_limited_batches']}")
        logger.info(f"Total processing time: {batch_stats['total_processing_time']:.1f}s")
        logger.info(f"Average batch time: {batch_stats['average_batch_time']:.1f}s")
        logger.info(f"Circuit breaker activations: {batch_stats['circuit_breaker_activations']}")
        logger.info("=" * 70)
    
    def _cache_batch_summary(self, results: Dict):
        """Cache the batch processing summary"""
        try:
            cache_summary = {
                **results['summary'],
                'batch_processing': True,
                'batch_size_used': self.batch_size,
                'batch_stats': results['batch_stats']
            }
            
            self.set_cached_compliance('shariah_summary', 'latest_batched', cache_summary)
            logger.debug("Cached batch processing summary")
            
        except Exception as e:
            logger.error(f"Error caching batch summary: {str(e)}")
    
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
                'rate_limited_count': 0,
                'cache_usage_rate': 0,
                'success_rate': 0,
                'processing_date': datetime.now().isoformat()
            },
            'batch_stats': {
                'total_batches': 0,
                'successful_batches': 0,
                'rate_limited_batches': 0,
                'total_processing_time': 0,
                'average_batch_time': 0,
                'circuit_breaker_activations': 0
            }
        }
    
    def get_batch_processor_stats(self) -> Dict[str, Any]:
        """Get batch processor statistics"""
        return self.batch_processor.get_processing_stats()
    
    def reset_batch_processor(self):
        """Reset batch processor state"""
        self.batch_processor.reset_circuit_breaker()
        logger.info("Batch processor state reset")

# Backward compatibility
BatchedEnhancedShariahFilter = BatchedShariahFilter
