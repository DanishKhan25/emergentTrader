"""
Enhanced API Handler with Batched Processing
Adds batched endpoints to prevent rate limiting while maintaining all existing functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from flask import Flask, request, jsonify
import logging
from datetime import datetime
import traceback

# Import existing components
from services.yfinance_fetcher import YFinanceFetcher
from core.enhanced_shariah_filter import EnhancedShariahFilter
from core.enhanced_shariah_filter_batched import BatchedShariahFilter
from core.optimized_signal_generator import OptimizedSignalGenerator
from core.signal_engine import SignalEngine
from core.data_cache import cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize components
fetcher = YFinanceFetcher()
shariah_filter = EnhancedShariahFilter()
batched_shariah_filter = BatchedShariahFilter(batch_size=50)  # 50 stocks per batch
optimized_generator = OptimizedSignalGenerator()
signal_engine = SignalEngine()

# Load NSE stock universe
def load_nse_universe():
    """Load NSE stock universe from CSV"""
    try:
        import pandas as pd
        df = pd.read_csv('data/nse_raw.csv')
        
        stocks = []
        for _, row in df.iterrows():
            stocks.append({
                'symbol': row.get('SYMBOL', ''),
                'company_name': row.get('NAME OF COMPANY', ''),
                'series': row.get('SERIES', ''),
                'listing_date': row.get('DATE OF LISTING', ''),
                'paid_up_value': row.get('PAID UP VALUE', 0),
                'market_lot': row.get('MARKET LOT', 0),
                'isin_number': row.get('ISIN NUMBER', ''),
                'face_value': row.get('FACE VALUE', 0)
            })
        
        logger.info(f"Loaded {len(stocks)} stocks from NSE universe")
        return stocks
        
    except Exception as e:
        logger.error(f"Error loading NSE universe: {str(e)}")
        return []

nse_universe = load_nse_universe()

# ============================================================================
# EXISTING ENDPOINTS (maintained for backward compatibility)
# ============================================================================

@app.route('/api/stocks/shariah', methods=['GET'])
def get_shariah_compliant_stocks():
    """Get Shariah compliant stocks (original endpoint)"""
    try:
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        
        # Use original enhanced filter
        compliant_stocks = shariah_filter.get_shariah_universe_enhanced(
            nse_universe[:200], fetcher, force_refresh
        )
        
        # Limit results
        limited_stocks = compliant_stocks[:limit]
        
        return jsonify({
            'success': True,
            'data': limited_stocks,
            'total_count': len(compliant_stocks),
            'returned_count': len(limited_stocks),
            'force_refresh_used': force_refresh,
            'processing_method': 'original_enhanced'
        })
        
    except Exception as e:
        logger.error(f"Error in get_shariah_compliant_stocks: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# ============================================================================
# NEW BATCHED ENDPOINTS
# ============================================================================

@app.route('/api/stocks/shariah/batched', methods=['GET'])
def get_shariah_compliant_stocks_batched():
    """Get Shariah compliant stocks using batch processing"""
    try:
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 200))
        batch_size = int(request.args.get('batch_size', 50))
        
        logger.info(f"Starting batched Shariah compliance check (batch_size={batch_size}, limit={limit})")
        
        # Update batch size if requested
        if batch_size != batched_shariah_filter.batch_size:
            batched_shariah_filter.batch_size = batch_size
            batched_shariah_filter.batch_config.batch_size = batch_size
        
        # Use batched processing
        results = batched_shariah_filter.get_shariah_universe_batched(
            nse_universe[:limit], fetcher, force_refresh
        )
        
        # Format response
        response_data = {
            'success': True,
            'compliant_stocks': results['compliant_stocks'],
            'unknown_stocks': results['unknown_stocks'],
            'summary': results['summary'],
            'batch_stats': results['batch_stats'],
            'processing_method': 'batched_enhanced',
            'batch_configuration': {
                'batch_size': batch_size,
                'delay_between_batches': batched_shariah_filter.batch_config.delay_between_batches,
                'delay_between_items': batched_shariah_filter.batch_config.delay_between_items,
                'rate_limit_delay': batched_shariah_filter.batch_config.rate_limit_delay
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_shariah_compliant_stocks_batched: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/stocks/shariah/batch-status', methods=['GET'])
def get_batch_processing_status():
    """Get current batch processing status"""
    try:
        stats = batched_shariah_filter.get_batch_processor_stats()
        
        return jsonify({
            'success': True,
            'batch_processor_stats': stats,
            'circuit_breaker_status': {
                'open': stats['circuit_breaker_open'],
                'failures': stats['circuit_breaker_failures'],
                'recommendation': 'Wait for circuit breaker to close' if stats['circuit_breaker_open'] else 'Normal operation'
            },
            'performance_metrics': {
                'total_batches_processed': stats['total_batches'],
                'success_rate': (stats['successful_batches'] / stats['total_batches'] * 100) if stats['total_batches'] > 0 else 0,
                'average_processing_time': stats['total_processing_time'] / stats['total_batches'] if stats['total_batches'] > 0 else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_batch_processing_status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stocks/shariah/batch-config', methods=['GET', 'POST'])
def manage_batch_configuration():
    """Get or update batch processing configuration"""
    try:
        if request.method == 'GET':
            # Return current configuration
            config = batched_shariah_filter.batch_config
            
            return jsonify({
                'success': True,
                'current_config': {
                    'batch_size': config.batch_size,
                    'delay_between_items': config.delay_between_items,
                    'delay_between_batches': config.delay_between_batches,
                    'max_retries': config.max_retries,
                    'rate_limit_delay': config.rate_limit_delay,
                    'circuit_breaker_threshold': config.circuit_breaker_threshold
                },
                'recommendations': {
                    'conservative': {'batch_size': 25, 'delay_between_batches': 45.0},
                    'balanced': {'batch_size': 50, 'delay_between_batches': 30.0},
                    'aggressive': {'batch_size': 100, 'delay_between_batches': 20.0}
                }
            })
        
        elif request.method == 'POST':
            # Update configuration
            data = request.get_json()
            
            if 'batch_size' in data:
                batched_shariah_filter.batch_size = int(data['batch_size'])
                batched_shariah_filter.batch_config.batch_size = int(data['batch_size'])
            
            if 'delay_between_items' in data:
                batched_shariah_filter.batch_config.delay_between_items = float(data['delay_between_items'])
            
            if 'delay_between_batches' in data:
                batched_shariah_filter.batch_config.delay_between_batches = float(data['delay_between_batches'])
            
            if 'rate_limit_delay' in data:
                batched_shariah_filter.batch_config.rate_limit_delay = float(data['rate_limit_delay'])
            
            return jsonify({
                'success': True,
                'message': 'Batch configuration updated successfully',
                'updated_config': {
                    'batch_size': batched_shariah_filter.batch_config.batch_size,
                    'delay_between_items': batched_shariah_filter.batch_config.delay_between_items,
                    'delay_between_batches': batched_shariah_filter.batch_config.delay_between_batches,
                    'rate_limit_delay': batched_shariah_filter.batch_config.rate_limit_delay
                }
            })
            
    except Exception as e:
        logger.error(f"Error in manage_batch_configuration: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stocks/shariah/reset-circuit-breaker', methods=['POST'])
def reset_circuit_breaker():
    """Reset the circuit breaker (manual intervention)"""
    try:
        batched_shariah_filter.reset_batch_processor()
        
        return jsonify({
            'success': True,
            'message': 'Circuit breaker reset successfully',
            'new_status': batched_shariah_filter.get_batch_processor_stats()
        })
        
    except Exception as e:
        logger.error(f"Error in reset_circuit_breaker: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ENHANCED SIGNAL ENDPOINTS WITH BATCHING
# ============================================================================

@app.route('/api/signals/batched', methods=['GET'])
def get_signals_batched():
    """Get trading signals using batch processing"""
    try:
        strategy = request.args.get('strategy', 'mean_reversion')
        symbols_param = request.args.get('symbols', '')
        batch_size = int(request.args.get('batch_size', 25))  # Smaller batches for signals
        
        # Parse symbols
        if symbols_param:
            symbols = [s.strip() for s in symbols_param.split(',')]
        else:
            # Use top compliant stocks
            compliant_results = batched_shariah_filter.get_shariah_universe_batched(
                nse_universe[:100], fetcher, force_refresh=False
            )
            symbols = [stock['symbol'] for stock in compliant_results['compliant_stocks'][:20]]
        
        if not symbols:
            return jsonify({
                'success': False,
                'error': 'No symbols provided or found'
            }), 400
        
        logger.info(f"Generating {strategy} signals for {len(symbols)} symbols using batch processing")
        
        # Use batch processing for signal generation
        from core.batch_processor import batch_process_stocks
        
        def generate_signal_for_stock(symbol):
            """Generate signal for a single stock"""
            try:
                if strategy == 'mean_reversion':
                    signals = optimized_generator.generate_mean_reversion_signals([symbol])
                elif strategy == 'momentum':
                    signals = optimized_generator.generate_momentum_signals([symbol])
                elif strategy == 'breakout':
                    signals = optimized_generator.generate_breakout_signals([symbol])
                elif strategy == 'value_investing':
                    signals = optimized_generator.generate_value_investing_signals([symbol])
                else:
                    return {'symbol': symbol, 'error': f'Unknown strategy: {strategy}'}
                
                return {
                    'symbol': symbol,
                    'signals': signals,
                    'signal_count': len(signals)
                }
                
            except Exception as e:
                return {
                    'symbol': symbol,
                    'error': str(e)
                }
        
        # Process in batches
        batch_results = batch_process_stocks(
            symbols, generate_signal_for_stock, 
            batch_size=batch_size, delay_between_batches=20.0
        )
        
        # Aggregate results
        all_signals = []
        errors = []
        
        for batch_result in batch_results:
            for result_item in batch_result.results:
                if result_item['status'] == 'success':
                    stock_result = result_item['result']
                    if 'signals' in stock_result:
                        all_signals.extend(stock_result['signals'])
                    elif 'error' in stock_result:
                        errors.append(stock_result)
            
            for error_item in batch_result.errors:
                errors.append({
                    'symbol': error_item.get('item', 'unknown'),
                    'error': error_item.get('error', 'Unknown error')
                })
        
        return jsonify({
            'success': True,
            'strategy': strategy,
            'signals': all_signals,
            'signal_count': len(all_signals),
            'symbols_processed': len(symbols),
            'errors': errors,
            'batch_stats': {
                'total_batches': len(batch_results),
                'batch_size_used': batch_size,
                'total_processing_time': sum(br.processing_time for br in batch_results)
            },
            'processing_method': 'batched_signals'
        })
        
    except Exception as e:
        logger.error(f"Error in get_signals_batched: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# ============================================================================
# MONITORING AND HEALTH ENDPOINTS
# ============================================================================

@app.route('/api/health/batch-system', methods=['GET'])
def get_batch_system_health():
    """Get comprehensive health status of the batch processing system"""
    try:
        # Get batch processor stats
        batch_stats = batched_shariah_filter.get_batch_processor_stats()
        
        # Get cache stats
        cache_stats = cache.get_cache_stats()
        
        # Calculate health score
        health_score = 100
        issues = []
        
        if batch_stats['circuit_breaker_open']:
            health_score -= 30
            issues.append("Circuit breaker is open")
        
        if batch_stats['rate_limited_batches'] > batch_stats['successful_batches']:
            health_score -= 20
            issues.append("High rate limiting detected")
        
        cache_hit_rate = (cache_stats.get('cache_hits', 0) / 
                         max(cache_stats.get('cache_hits', 0) + cache_stats.get('cache_misses', 0), 1)) * 100
        
        if cache_hit_rate < 70:
            health_score -= 15
            issues.append(f"Low cache hit rate: {cache_hit_rate:.1f}%")
        
        health_status = "excellent" if health_score >= 90 else "good" if health_score >= 70 else "fair" if health_score >= 50 else "poor"
        
        return jsonify({
            'success': True,
            'health_score': health_score,
            'health_status': health_status,
            'issues': issues,
            'batch_processor': {
                'circuit_breaker_open': batch_stats['circuit_breaker_open'],
                'total_batches': batch_stats['total_batches'],
                'successful_batches': batch_stats['successful_batches'],
                'rate_limited_batches': batch_stats['rate_limited_batches'],
                'success_rate': (batch_stats['successful_batches'] / max(batch_stats['total_batches'], 1)) * 100
            },
            'cache_system': {
                'hit_rate': cache_hit_rate,
                'total_entries': cache_stats.get('total_entries', 0),
                'cache_hits': cache_stats.get('cache_hits', 0),
                'cache_misses': cache_stats.get('cache_misses', 0)
            },
            'recommendations': [
                "Use batch processing for large operations",
                "Monitor circuit breaker status regularly",
                "Maintain cache hit rate above 80%",
                "Schedule non-urgent operations during off-peak hours"
            ]
        })
        
    except Exception as e:
        logger.error(f"Error in get_batch_system_health: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# EXISTING ENDPOINTS (maintained for backward compatibility)
# ============================================================================

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get trading signals (original endpoint)"""
    try:
        strategy = request.args.get('strategy', 'mean_reversion')
        symbols_param = request.args.get('symbols', '')
        
        if symbols_param:
            symbols = [s.strip() for s in symbols_param.split(',')]
        else:
            symbols = ['TCS', 'HDFCBANK', 'RELIANCE', 'WIPRO', 'INFY']
        
        signals = signal_engine.generate_signals(strategy, symbols)
        
        return jsonify({
            'success': True,
            'strategy': strategy,
            'signals': signals,
            'signal_count': len(signals),
            'processing_method': 'original'
        })
        
    except Exception as e:
        logger.error(f"Error in get_signals: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting Enhanced API Handler with Batch Processing")
    logger.info("Available endpoints:")
    logger.info("  GET  /api/stocks/shariah/batched - Batched Shariah compliance")
    logger.info("  GET  /api/stocks/shariah/batch-status - Batch processing status")
    logger.info("  GET  /api/signals/batched - Batched signal generation")
    logger.info("  GET  /api/health/batch-system - Batch system health")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
