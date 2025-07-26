"""
Smart Batch Processor - Intelligent delays based on data source
Only applies delays when making fresh API calls, skips delays for cached data
"""

import logging
import time
import random
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .batch_processor import BatchProcessor, BatchConfig, BatchStatus, BatchResult

logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Data source types"""
    CACHED = "cached"
    FRESH_API = "fresh_api"
    MIXED = "mixed"

class SmartBatchProcessor(BatchProcessor):
    """Smart batch processor that adjusts delays based on data source"""
    
    def __init__(self, config: Optional[BatchConfig] = None):
        super().__init__(config)
        self.name = "Smart Batch Processor"
        self.cache_hit_count = 0
        self.api_call_count = 0
        
        logger.info("Initialized Smart Batch Processor with intelligent delay management")
    
    def process_batch_smart(self, 
                           items: List[Any], 
                           processor_func: Callable,
                           batch_name: str = "batch",
                           detect_data_source: bool = True) -> List[BatchResult]:
        """
        Process items with smart delays based on data source detection
        
        Args:
            items: List of items to process
            processor_func: Function to process each item
            batch_name: Name for logging purposes
            detect_data_source: Whether to detect and optimize for data source
            
        Returns:
            List of BatchResult objects
        """
        if not items:
            logger.warning("No items to process")
            return []
        
        logger.info(f"Starting SMART batch processing: {len(items)} items")
        
        # Split items into batches
        batches = [items[i:i + self.config.batch_size] 
                  for i in range(0, len(items), self.config.batch_size)]
        
        batch_results = []
        consecutive_cache_hits = 0
        
        for batch_index, batch_items in enumerate(batches):
            batch_id = f"{batch_name}_{batch_index + 1}"
            
            # Check circuit breaker
            if not self._should_process_batch():
                logger.warning(f"Circuit breaker open - skipping batch {batch_id}")
                batch_results.append(self._create_skipped_batch_result(batch_id, batch_items))
                continue
            
            # Process batch and detect data source
            batch_result = self._process_smart_batch(
                batch_items, processor_func, batch_id, batch_index + 1, len(batches)
            )
            
            batch_results.append(batch_result)
            
            # Update circuit breaker state
            if batch_result.status == BatchStatus.COMPLETED:
                self._record_batch_success()
            elif batch_result.status in [BatchStatus.FAILED, BatchStatus.RATE_LIMITED]:
                self._record_batch_failure()
            
            # Smart delay logic based on data source
            if batch_index < len(batches) - 1:  # Not the last batch
                delay = self._calculate_smart_delay(batch_result, consecutive_cache_hits)
                
                if delay > 0:
                    logger.info(f"Smart delay: {delay}s before next batch (based on data source analysis)")
                    time.sleep(delay)
                else:
                    logger.info("No delay needed - using cached data")
                
                # Track consecutive cache hits
                if batch_result.rate_limited_count == 0 and self._is_mostly_cached(batch_result):
                    consecutive_cache_hits += 1
                else:
                    consecutive_cache_hits = 0
        
        # Update processing stats
        self._update_processing_stats(batch_results)
        
        # Log smart summary
        self._log_smart_batch_summary(batch_results)
        
        return batch_results
    
    def _process_smart_batch(self, 
                            batch_items: List[Any], 
                            processor_func: Callable,
                            batch_id: str,
                            batch_num: int,
                            total_batches: int) -> BatchResult:
        """Process a single batch with smart delay detection"""
        
        start_time = datetime.now()
        logger.info(f"Processing SMART batch {batch_num}/{total_batches} ({batch_id}): {len(batch_items)} items")
        
        results = []
        errors = []
        rate_limited_count = 0
        cache_hits = 0
        api_calls = 0
        
        for item_index, item in enumerate(batch_items):
            item_start_time = time.time()
            
            item_result = self._process_single_item(
                item, processor_func, batch_id, item_index + 1, len(batch_items)
            )
            
            item_processing_time = time.time() - item_start_time
            
            # Analyze data source based on processing time and result
            data_source = self._detect_data_source(item_result, item_processing_time)
            item_result['data_source_detected'] = data_source.value
            
            if item_result['status'] == 'success':
                results.append(item_result)
                if data_source == DataSource.CACHED:
                    cache_hits += 1
                else:
                    api_calls += 1
            elif item_result['status'] == 'rate_limited':
                rate_limited_count += 1
                api_calls += 1
                errors.append(item_result)
            else:
                errors.append(item_result)
            
            # Smart delay between items
            if item_index < len(batch_items) - 1:
                item_delay = self._calculate_smart_item_delay(data_source, consecutive_cache_hits=cache_hits)
                if item_delay > 0:
                    time.sleep(item_delay)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Determine batch status
        if rate_limited_count > len(batch_items) * 0.5:
            status = BatchStatus.RATE_LIMITED
        elif len(errors) > len(batch_items) * 0.8:
            status = BatchStatus.FAILED
        else:
            status = BatchStatus.COMPLETED
        
        # Create enhanced batch result
        batch_result = BatchResult(
            batch_id=batch_id,
            status=status,
            processed_count=len(batch_items),
            success_count=len(results),
            error_count=len(errors) - rate_limited_count,
            rate_limited_count=rate_limited_count,
            results=results,
            errors=errors,
            processing_time=processing_time,
            start_time=start_time,
            end_time=end_time
        )
        
        # Add smart processing metadata
        batch_result.cache_hits = cache_hits
        batch_result.api_calls = api_calls
        batch_result.cache_hit_rate = (cache_hits / len(batch_items)) * 100 if batch_items else 0
        
        logger.info(f"SMART batch {batch_id} completed: {len(results)} success, {cache_hits} cached, {api_calls} API calls")
        
        return batch_result
    
    def _detect_data_source(self, item_result: Dict, processing_time: float) -> DataSource:
        """Detect if data came from cache or fresh API call"""
        
        # Fast processing time usually indicates cached data
        if processing_time < 0.1:  # Less than 100ms
            return DataSource.CACHED
        
        # Check if result indicates cached data
        result_data = item_result.get('result', {})
        if isinstance(result_data, dict):
            data_source = result_data.get('data_source', '')
            if 'cache' in data_source.lower():
                return DataSource.CACHED
        
        # Slow processing time usually indicates API call
        if processing_time > 1.0:  # More than 1 second
            return DataSource.FRESH_API
        
        # Default to fresh API if uncertain
        return DataSource.FRESH_API
    
    def _calculate_smart_delay(self, batch_result: BatchResult, consecutive_cache_hits: int) -> float:
        """Calculate smart delay based on batch result analysis"""
        
        # No delay if mostly cached data
        if hasattr(batch_result, 'cache_hit_rate') and batch_result.cache_hit_rate > 80:
            return 0.0
        
        # No delay for consecutive cache-heavy batches
        if consecutive_cache_hits >= 3:
            return 0.0
        
        # Rate limited - use longer delay
        if batch_result.rate_limited_count > 0:
            return self.config.rate_limit_delay
        
        # Mixed data - use reduced delay
        if hasattr(batch_result, 'cache_hit_rate') and batch_result.cache_hit_rate > 50:
            return self.config.delay_between_batches * 0.3  # 30% of normal delay
        
        # Mostly fresh API calls - use normal delay
        return self.config.delay_between_batches
    
    def _calculate_smart_item_delay(self, data_source: DataSource, consecutive_cache_hits: int) -> float:
        """Calculate smart delay between items"""
        
        # No delay for cached data
        if data_source == DataSource.CACHED:
            return 0.0
        
        # Minimal delay if we've had many cache hits
        if consecutive_cache_hits > 5:
            return 0.1
        
        # Normal delay for fresh API calls
        return self.config.delay_between_items
    
    def _is_mostly_cached(self, batch_result: BatchResult) -> bool:
        """Check if batch result is mostly from cached data"""
        return hasattr(batch_result, 'cache_hit_rate') and batch_result.cache_hit_rate > 70
    
    def _create_skipped_batch_result(self, batch_id: str, batch_items: List[Any]) -> BatchResult:
        """Create result for skipped batch"""
        return BatchResult(
            batch_id=batch_id,
            status=BatchStatus.RATE_LIMITED,
            processed_count=0,
            success_count=0,
            error_count=0,
            rate_limited_count=len(batch_items),
            results=[],
            errors=[{'error': 'Circuit breaker open', 'items': batch_items}],
            processing_time=0.0,
            start_time=datetime.now()
        )
    
    def _log_smart_batch_summary(self, batch_results: List[BatchResult]):
        """Log smart batch processing summary"""
        total_items = sum(br.processed_count for br in batch_results)
        total_success = sum(br.success_count for br in batch_results)
        total_errors = sum(br.error_count for br in batch_results)
        total_rate_limited = sum(br.rate_limited_count for br in batch_results)
        total_time = sum(br.processing_time for br in batch_results)
        
        # Calculate cache statistics
        total_cache_hits = sum(getattr(br, 'cache_hits', 0) for br in batch_results)
        total_api_calls = sum(getattr(br, 'api_calls', 0) for br in batch_results)
        overall_cache_rate = (total_cache_hits / total_items * 100) if total_items > 0 else 0
        
        logger.info("=" * 70)
        logger.info("SMART BATCH PROCESSING SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total batches: {len(batch_results)}")
        logger.info(f"Total items processed: {total_items}")
        logger.info(f"Successful: {total_success} ({total_success/total_items*100:.1f}%)")
        logger.info(f"Errors: {total_errors} ({total_errors/total_items*100:.1f}%)")
        logger.info(f"Rate limited: {total_rate_limited} ({total_rate_limited/total_items*100:.1f}%)")
        logger.info(f"Cache hits: {total_cache_hits} ({overall_cache_rate:.1f}%)")
        logger.info(f"API calls: {total_api_calls}")
        logger.info(f"Total processing time: {total_time:.1f}s")
        logger.info(f"Average time per item: {total_time/total_items:.3f}s")
        logger.info(f"Processing speed: {total_items/total_time:.1f} items/second")
        logger.info(f"Circuit breaker status: {'OPEN' if self.circuit_breaker_open else 'CLOSED'}")
        logger.info("=" * 70)

# Convenience function for smart batch processing
def smart_batch_process_stocks(stocks: List[str], 
                              processor_func: Callable,
                              batch_size: int = 50,
                              detect_cache: bool = True) -> List[BatchResult]:
    """
    Smart batch process stocks with automatic delay optimization
    
    Args:
        stocks: List of stock symbols
        processor_func: Function to process each stock
        batch_size: Number of stocks per batch
        detect_cache: Whether to detect and optimize for cached data
        
    Returns:
        List of BatchResult objects
    """
    config = BatchConfig(
        batch_size=batch_size,
        delay_between_items=1.0,      # Will be reduced to 0 for cached data
        delay_between_batches=15.0,   # Will be reduced to 0 for cached data
        rate_limit_delay=30.0
    )
    
    processor = SmartBatchProcessor(config)
    return processor.process_batch_smart(stocks, processor_func, "smart_stock_processing", detect_cache)
