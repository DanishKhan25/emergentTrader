"""
Batch Processor - Intelligent batching system to prevent rate limiting
Implements batch processing with configurable delays and circuit breaker integration
"""

import logging
import time
import random
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BatchStatus(Enum):
    """Batch processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"

@dataclass
class BatchConfig:
    """Configuration for batch processing"""
    batch_size: int = 50
    delay_between_items: float = 1.0  # seconds
    delay_between_batches: float = 30.0  # seconds
    max_retries: int = 3
    backoff_multiplier: float = 2.0
    rate_limit_delay: float = 60.0  # seconds to wait when rate limited
    circuit_breaker_threshold: int = 3  # failures before opening circuit

@dataclass
class BatchResult:
    """Result of batch processing"""
    batch_id: str
    status: BatchStatus
    processed_count: int
    success_count: int
    error_count: int
    rate_limited_count: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    processing_time: float
    start_time: datetime
    end_time: Optional[datetime] = None

class BatchProcessor:
    """Intelligent batch processor with rate limiting protection"""
    
    def __init__(self, config: Optional[BatchConfig] = None):
        self.config = config or BatchConfig()
        self.name = "Batch Processor"
        self.circuit_breaker_failures = 0
        self.circuit_breaker_open = False
        self.circuit_breaker_open_time = None
        self.processing_stats = {
            'total_batches': 0,
            'successful_batches': 0,
            'failed_batches': 0,
            'rate_limited_batches': 0,
            'total_items_processed': 0,
            'total_processing_time': 0.0
        }
        
        logger.info(f"Initialized Batch Processor with batch_size={self.config.batch_size}")
    
    def _should_process_batch(self) -> bool:
        """Check if we should process batch or wait due to circuit breaker"""
        if not self.circuit_breaker_open:
            return True
        
        # Try to close circuit breaker after 5 minutes
        if (self.circuit_breaker_open_time and 
            (datetime.now() - self.circuit_breaker_open_time).seconds > 300):
            logger.info("Attempting to close circuit breaker")
            self.circuit_breaker_open = False
            self.circuit_breaker_failures = 0
            return True
        
        return False
    
    def _record_batch_success(self):
        """Record successful batch processing"""
        self.circuit_breaker_failures = 0
        self.circuit_breaker_open = False
        self.circuit_breaker_open_time = None
    
    def _record_batch_failure(self):
        """Record failed batch processing"""
        self.circuit_breaker_failures += 1
        
        if self.circuit_breaker_failures >= self.config.circuit_breaker_threshold:
            self.circuit_breaker_open = True
            self.circuit_breaker_open_time = datetime.now()
            logger.warning(f"Circuit breaker opened after {self.circuit_breaker_failures} failures")
    
    def process_batch(self, 
                     items: List[Any], 
                     processor_func: Callable,
                     batch_name: str = "batch") -> List[BatchResult]:
        """
        Process items in batches with rate limiting protection
        
        Args:
            items: List of items to process
            processor_func: Function to process each item
            batch_name: Name for logging purposes
            
        Returns:
            List of BatchResult objects
        """
        if not items:
            logger.warning("No items to process")
            return []
        
        logger.info(f"Starting batch processing: {len(items)} items in batches of {self.config.batch_size}")
        
        # Split items into batches
        batches = [items[i:i + self.config.batch_size] 
                  for i in range(0, len(items), self.config.batch_size)]
        
        batch_results = []
        
        for batch_index, batch_items in enumerate(batches):
            batch_id = f"{batch_name}_{batch_index + 1}"
            
            # Check circuit breaker
            if not self._should_process_batch():
                logger.warning(f"Circuit breaker open - skipping batch {batch_id}")
                batch_results.append(BatchResult(
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
                ))
                continue
            
            # Process batch with retries
            batch_result = self._process_single_batch(
                batch_items, processor_func, batch_id, batch_index + 1, len(batches)
            )
            
            batch_results.append(batch_result)
            
            # Update circuit breaker state
            if batch_result.status == BatchStatus.COMPLETED:
                self._record_batch_success()
            elif batch_result.status in [BatchStatus.FAILED, BatchStatus.RATE_LIMITED]:
                self._record_batch_failure()
            
            # Delay between batches (except for last batch)
            if batch_index < len(batches) - 1:
                delay = self.config.delay_between_batches
                
                # Increase delay if rate limited
                if batch_result.rate_limited_count > 0:
                    delay = self.config.rate_limit_delay
                    logger.warning(f"Rate limiting detected - extending delay to {delay}s")
                
                logger.info(f"Waiting {delay}s before processing next batch...")
                time.sleep(delay)
        
        # Update processing stats
        self._update_processing_stats(batch_results)
        
        # Log summary
        self._log_batch_summary(batch_results)
        
        return batch_results
    
    def _process_single_batch(self, 
                            batch_items: List[Any], 
                            processor_func: Callable,
                            batch_id: str,
                            batch_num: int,
                            total_batches: int) -> BatchResult:
        """Process a single batch with retries"""
        
        start_time = datetime.now()
        logger.info(f"Processing batch {batch_num}/{total_batches} ({batch_id}): {len(batch_items)} items")
        
        results = []
        errors = []
        rate_limited_count = 0
        
        for item_index, item in enumerate(batch_items):
            item_result = self._process_single_item(
                item, processor_func, batch_id, item_index + 1, len(batch_items)
            )
            
            if item_result['status'] == 'success':
                results.append(item_result)
            elif item_result['status'] == 'rate_limited':
                rate_limited_count += 1
                errors.append(item_result)
            else:
                errors.append(item_result)
            
            # Delay between items within batch
            if item_index < len(batch_items) - 1:
                delay = self.config.delay_between_items
                
                # Add jitter to prevent thundering herd
                jitter = random.uniform(0.5, 1.5)
                delay *= jitter
                
                time.sleep(delay)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Determine batch status
        if rate_limited_count > len(batch_items) * 0.5:  # More than 50% rate limited
            status = BatchStatus.RATE_LIMITED
        elif len(errors) > len(batch_items) * 0.8:  # More than 80% errors
            status = BatchStatus.FAILED
        else:
            status = BatchStatus.COMPLETED
        
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
        
        logger.info(f"Batch {batch_id} completed: {len(results)} success, {len(errors)} errors, {rate_limited_count} rate limited")
        
        return batch_result
    
    def _process_single_item(self, 
                           item: Any, 
                           processor_func: Callable,
                           batch_id: str,
                           item_num: int,
                           batch_size: int) -> Dict[str, Any]:
        """Process a single item with error handling"""
        
        for attempt in range(self.config.max_retries + 1):
            try:
                # Add attempt delay for retries
                if attempt > 0:
                    delay = self.config.delay_between_items * (self.config.backoff_multiplier ** attempt)
                    logger.debug(f"Retry {attempt} for item {item_num} after {delay:.1f}s delay")
                    time.sleep(delay)
                
                # Process the item
                result = processor_func(item)
                
                return {
                    'status': 'success',
                    'item': item,
                    'result': result,
                    'batch_id': batch_id,
                    'attempts': attempt + 1,
                    'processing_time': time.time()
                }
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check for rate limiting
                if any(phrase in error_msg for phrase in ['rate limit', 'too many requests', '429']):
                    if attempt < self.config.max_retries:
                        backoff_delay = self.config.rate_limit_delay * (attempt + 1)
                        logger.warning(f"Rate limited processing item {item_num} - backing off {backoff_delay:.1f}s")
                        time.sleep(backoff_delay)
                        continue
                    else:
                        return {
                            'status': 'rate_limited',
                            'item': item,
                            'error': str(e),
                            'batch_id': batch_id,
                            'attempts': attempt + 1
                        }
                
                # For other errors, don't retry
                else:
                    return {
                        'status': 'error',
                        'item': item,
                        'error': str(e),
                        'batch_id': batch_id,
                        'attempts': attempt + 1
                    }
        
        # If we get here, all retries failed
        return {
            'status': 'error',
            'item': item,
            'error': 'Max retries exceeded',
            'batch_id': batch_id,
            'attempts': self.config.max_retries + 1
        }
    
    def _update_processing_stats(self, batch_results: List[BatchResult]):
        """Update processing statistics"""
        self.processing_stats['total_batches'] += len(batch_results)
        
        for batch_result in batch_results:
            if batch_result.status == BatchStatus.COMPLETED:
                self.processing_stats['successful_batches'] += 1
            elif batch_result.status == BatchStatus.FAILED:
                self.processing_stats['failed_batches'] += 1
            elif batch_result.status == BatchStatus.RATE_LIMITED:
                self.processing_stats['rate_limited_batches'] += 1
            
            self.processing_stats['total_items_processed'] += batch_result.processed_count
            self.processing_stats['total_processing_time'] += batch_result.processing_time
    
    def _log_batch_summary(self, batch_results: List[BatchResult]):
        """Log comprehensive batch processing summary"""
        total_items = sum(br.processed_count for br in batch_results)
        total_success = sum(br.success_count for br in batch_results)
        total_errors = sum(br.error_count for br in batch_results)
        total_rate_limited = sum(br.rate_limited_count for br in batch_results)
        total_time = sum(br.processing_time for br in batch_results)
        
        logger.info("=" * 60)
        logger.info("BATCH PROCESSING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total batches: {len(batch_results)}")
        logger.info(f"Total items processed: {total_items}")
        logger.info(f"Successful: {total_success} ({total_success/total_items*100:.1f}%)")
        logger.info(f"Errors: {total_errors} ({total_errors/total_items*100:.1f}%)")
        logger.info(f"Rate limited: {total_rate_limited} ({total_rate_limited/total_items*100:.1f}%)")
        logger.info(f"Total processing time: {total_time:.1f}s")
        logger.info(f"Average time per item: {total_time/total_items:.2f}s")
        logger.info(f"Circuit breaker status: {'OPEN' if self.circuit_breaker_open else 'CLOSED'}")
        logger.info("=" * 60)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        return {
            **self.processing_stats,
            'circuit_breaker_open': self.circuit_breaker_open,
            'circuit_breaker_failures': self.circuit_breaker_failures,
            'config': {
                'batch_size': self.config.batch_size,
                'delay_between_items': self.config.delay_between_items,
                'delay_between_batches': self.config.delay_between_batches,
                'rate_limit_delay': self.config.rate_limit_delay
            }
        }
    
    def reset_circuit_breaker(self):
        """Reset circuit breaker (for manual intervention)"""
        self.circuit_breaker_open = False
        self.circuit_breaker_failures = 0
        self.circuit_breaker_open_time = None
        logger.info("Circuit breaker manually reset")

# Convenience functions for common batch operations

def batch_process_stocks(stocks: List[str], 
                        processor_func: Callable,
                        batch_size: int = 50,
                        delay_between_batches: float = 30.0) -> List[BatchResult]:
    """
    Convenience function to batch process stocks
    
    Args:
        stocks: List of stock symbols
        processor_func: Function to process each stock
        batch_size: Number of stocks per batch
        delay_between_batches: Delay between batches in seconds
        
    Returns:
        List of BatchResult objects
    """
    config = BatchConfig(
        batch_size=batch_size,
        delay_between_items=2.0,  # 2 seconds between stocks
        delay_between_batches=delay_between_batches,
        rate_limit_delay=60.0  # 1 minute when rate limited
    )
    
    processor = BatchProcessor(config)
    return processor.process_batch(stocks, processor_func, "stock_processing")

def batch_process_shariah_compliance(stocks: List[str], 
                                   shariah_filter,
                                   stock_fetcher,
                                   batch_size: int = 50) -> List[BatchResult]:
    """
    Batch process Shariah compliance checks
    
    Args:
        stocks: List of stock symbols
        shariah_filter: EnhancedShariahFilter instance
        stock_fetcher: YFinanceFetcher instance
        batch_size: Number of stocks per batch
        
    Returns:
        List of BatchResult objects
    """
    def process_stock_compliance(symbol: str) -> Dict[str, Any]:
        """Process single stock for Shariah compliance"""
        try:
            # Get stock info (with caching)
            stock_info = stock_fetcher.get_stock_info(symbol)
            
            if not stock_info:
                return {
                    'symbol': symbol,
                    'compliance_status': 'error',
                    'error': 'No stock info available'
                }
            
            # Check Shariah compliance
            compliance_result = shariah_filter.is_shariah_compliant_enhanced(
                stock_info, symbol, force_refresh=False
            )
            
            return {
                'symbol': symbol,
                'compliance_status': compliance_result.get('compliance_status'),
                'confidence_level': compliance_result.get('confidence_level'),
                'compliance_score': compliance_result.get('compliance_score', 0),
                'compliance_details': compliance_result
            }
            
        except Exception as e:
            return {
                'symbol': symbol,
                'compliance_status': 'error',
                'error': str(e)
            }
    
    config = BatchConfig(
        batch_size=batch_size,
        delay_between_items=3.0,  # 3 seconds between compliance checks
        delay_between_batches=45.0,  # 45 seconds between batches
        rate_limit_delay=120.0  # 2 minutes when rate limited
    )
    
    processor = BatchProcessor(config)
    return processor.process_batch(stocks, process_stock_compliance, "shariah_compliance")
