"""
Enhanced API Endpoints for EmergentTrader
Add these endpoints to your main.py
"""

from fastapi import HTTPException
from services.logging_service import get_logger_service, get_logger
from services.position_sizing import get_position_sizer
from services.market_regime import get_regime_filter

# Add these imports to your main.py:
"""
from services.logging_service import get_logger_service, get_logger
from services.position_sizing import get_position_sizer
from services.market_regime import get_regime_filter
"""

# =============================================================================
# LOGGING ENDPOINTS
# =============================================================================

@app.get("/logging/status")
async def get_logging_status():
    """Get current logging status and configuration"""
    try:
        logger_service = get_logger_service()
        
        return {
            'success': True,
            'data': {
                'current_level': logger_service.get_log_level(),
                'available_levels': list(logger_service.log_levels.keys()),
                'log_directory': str(logger_service.log_dir),
                'stats': logger_service.get_log_stats()
            }
        }
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting logging status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logging/level")
async def set_log_level(request: dict):
    """Set logging level dynamically"""
    try:
        level = request.get('level', 'INFO')
        logger_service = get_logger_service()
        
        result = logger_service.set_log_level(level)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error setting log level: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logging/files")
async def get_log_files():
    """Get list of available log files"""
    try:
        logger_service = get_logger_service()
        
        return {
            'success': True,
            'data': logger_service.get_log_files()
        }
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting log files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logging/recent/{component}")
async def get_recent_logs(component: str, lines: int = 100):
    """Get recent log entries from specific component"""
    try:
        logger_service = get_logger_service()
        
        return {
            'success': True,
            'data': {
                'component': component,
                'lines': lines,
                'logs': logger_service.get_recent_logs(component, lines)
            }
        }
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting recent logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logging/search")
async def search_logs(request: dict):
    """Search logs for specific patterns"""
    try:
        query = request.get('query', '')
        component = request.get('component')
        days = request.get('days', 7)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        logger_service = get_logger_service()
        results = logger_service.search_logs(query, component, days)
        
        return {
            'success': True,
            'data': {
                'query': query,
                'component': component,
                'results_count': len(results),
                'results': results
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error searching logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logging/cleanup")
async def cleanup_old_logs(request: dict):
    """Clean up old log files"""
    try:
        days = request.get('days', 30)
        logger_service = get_logger_service()
        
        result = logger_service.cleanup_old_logs(days)
        
        return result
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error cleaning up logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logging/stats")
async def get_logging_stats():
    """Get detailed logging statistics"""
    try:
        logger_service = get_logger_service()
        
        return {
            'success': True,
            'data': logger_service.get_log_stats()
        }
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting logging stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# POSITION SIZING ENDPOINTS
# =============================================================================

@app.post("/position-sizing/calculate")
async def calculate_position_size(request: dict):
    """Calculate optimal position size for a signal"""
    try:
        signal_data = request.get('signal_data', {})
        portfolio_data = request.get('portfolio_data', {})
        sizing_method = request.get('sizing_method', 'kelly')
        
        if not signal_data:
            raise HTTPException(status_code=400, detail="Signal data is required")
        
        position_sizer = get_position_sizer()
        result = position_sizer.calculate_optimal_position_size(
            signal_data, portfolio_data, sizing_method
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error calculating position size: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/position-sizing/recommendations")
async def get_sizing_recommendations(request: dict):
    """Get position sizing recommendations using multiple methods"""
    try:
        signal_data = request.get('signal_data', {})
        portfolio_data = request.get('portfolio_data', {})
        
        if not signal_data:
            raise HTTPException(status_code=400, detail="Signal data is required")
        
        position_sizer = get_position_sizer()
        result = position_sizer.get_sizing_recommendations(signal_data, portfolio_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting sizing recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/position-sizing/parameters")
async def update_sizing_parameters(request: dict):
    """Update position sizing parameters"""
    try:
        parameters = request.get('parameters', {})
        
        position_sizer = get_position_sizer()
        result = position_sizer.update_sizing_parameters(parameters)
        
        return result
        
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error updating sizing parameters: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/position-sizing/parameters")
async def get_sizing_parameters():
    """Get current position sizing parameters"""
    try:
        position_sizer = get_position_sizer()
        result = position_sizer.get_current_parameters()
        
        return result
        
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting sizing parameters: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# MARKET REGIME ENDPOINTS
# =============================================================================

@app.get("/market-regime/detect")
async def detect_market_regime():
    """Detect current market regime"""
    try:
        regime_filter = get_regime_filter()
        result = regime_filter.detect_market_regime()
        
        return result
        
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error detecting market regime: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/market-regime/filter-strategies")
async def filter_strategies_by_regime(request: dict):
    """Filter strategies based on current market regime"""
    try:
        strategies = request.get('strategies', [])
        
        if not strategies:
            raise HTTPException(status_code=400, detail="Strategies list is required")
        
        regime_filter = get_regime_filter()
        result = regime_filter.filter_strategies_by_regime(strategies)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error filtering strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/market-regime/timing-score")
async def get_timing_score(request: dict):
    """Get timing score for a signal based on market regime"""
    try:
        signal_data = request.get('signal_data', {})
        
        if not signal_data:
            raise HTTPException(status_code=400, detail="Signal data is required")
        
        regime_filter = get_regime_filter()
        result = regime_filter.get_optimal_timing_score(signal_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting timing score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-regime/summary")
async def get_regime_summary():
    """Get comprehensive market regime summary"""
    try:
        regime_filter = get_regime_filter()
        result = regime_filter.get_regime_summary()
        
        return result
        
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting regime summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# ENHANCED SIGNAL GENERATION ENDPOINT
# =============================================================================

@app.post("/signals/generate-all")
async def generate_all_signals():
    """Generate signals using all strategies across all stocks"""
    try:
        logger = get_logger('signals')
        logger.info("Starting multi-strategy signal generation")
        
        # Get available strategies
        strategies_result = api_handler.get_available_strategies()
        if not strategies_result.get('success'):
            raise HTTPException(status_code=500, detail="Failed to get available strategies")
        
        strategies = strategies_result.get('data', [])
        
        # Get market regime for strategy filtering
        regime_filter = get_regime_filter()
        regime_result = regime_filter.detect_market_regime()
        
        if regime_result.get('success'):
            # Filter strategies based on market regime
            filter_result = regime_filter.filter_strategies_by_regime(
                [s.get('name', s) for s in strategies]
            )
            
            if filter_result.get('success'):
                recommended_strategies = filter_result['recommendations']['use']
                logger.info(f"Market regime filtering: using {len(recommended_strategies)} strategies")
            else:
                recommended_strategies = [s.get('name', s) for s in strategies]
        else:
            recommended_strategies = [s.get('name', s) for s in strategies]
        
        # Generate signals for each recommended strategy
        all_results = []
        total_signals = 0
        
        for strategy in recommended_strategies:
            try:
                logger.info(f"Generating signals for strategy: {strategy}")
                
                result = api_handler.generate_signals(
                    strategy=strategy,
                    symbols=None,  # All stocks
                    shariah_only=True,
                    min_confidence=0.7
                )
                
                if result.get('success') and result.get('data'):
                    signals = result['data']
                    
                    # Apply position sizing to each signal
                    position_sizer = get_position_sizer()
                    portfolio_data = api_handler.get_portfolio_summary().get('data', {})
                    
                    enhanced_signals = []
                    for signal in signals:
                        # Calculate optimal position size
                        sizing_result = position_sizer.calculate_optimal_position_size(
                            signal, portfolio_data, 'kelly'
                        )
                        
                        if sizing_result.get('success'):
                            signal['position_sizing'] = {
                                'recommended_size': sizing_result['position_size'],
                                'position_value': sizing_result['position_value'],
                                'portfolio_risk_percent': sizing_result['portfolio_risk_percent']
                            }
                        
                        # Get timing score
                        timing_result = regime_filter.get_optimal_timing_score(signal)
                        if timing_result.get('success'):
                            signal['timing'] = {
                                'score': timing_result['timing_score'],
                                'category': timing_result['timing_category'],
                                'recommendation': timing_result['recommendation']
                            }
                        
                        enhanced_signals.append(signal)
                    
                    all_results.append({
                        'strategy': strategy,
                        'success': True,
                        'signals': enhanced_signals,
                        'count': len(enhanced_signals)
                    })
                    
                    total_signals += len(enhanced_signals)
                    
                else:
                    all_results.append({
                        'strategy': strategy,
                        'success': False,
                        'signals': [],
                        'count': 0,
                        'error': result.get('error', 'No signals generated')
                    })
                    
            except Exception as e:
                logger.error(f"Error generating signals for {strategy}: {str(e)}")
                all_results.append({
                    'strategy': strategy,
                    'success': False,
                    'signals': [],
                    'count': 0,
                    'error': str(e)
                })
        
        # Compile final results
        successful_strategies = len([r for r in all_results if r['success']])
        high_confidence_signals = sum([
            len([s for s in r['signals'] if s.get('confidence', 0) >= 0.85])
            for r in all_results if r['success']
        ])
        
        unique_symbols = set()
        for result in all_results:
            if result['success']:
                for signal in result['signals']:
                    unique_symbols.add(signal.get('symbol'))
        
        logger.info(
            f"Multi-strategy generation complete: {total_signals} signals "
            f"from {successful_strategies} strategies"
        )
        
        return {
            'success': True,
            'data': {
                'total_strategies': len(recommended_strategies),
                'successful_strategies': successful_strategies,
                'total_signals': total_signals,
                'high_confidence_signals': high_confidence_signals,
                'unique_symbols': len(unique_symbols),
                'market_regime': regime_result.get('regime') if regime_result.get('success') else 'unknown',
                'results': all_results,
                'timestamp': datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error in multi-strategy signal generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# INTEGRATION INSTRUCTIONS
# =============================================================================

def integrate_enhanced_endpoints():
    """
    Instructions for integrating these endpoints into your main.py:
    
    1. Add the imports at the top of main.py:
    
    from services.logging_service import get_logger_service, get_logger
    from services.position_sizing import get_position_sizer
    from services.market_regime import get_regime_filter
    
    2. Copy all the endpoint functions above into your main.py
    
    3. Update your existing generate_signals method to use logging:
    
    def generate_signals(self, strategy='momentum', symbols=None):
        logger = get_logger('signals')
        logger.info(f"Starting signal generation with strategy: {strategy}")
        
        try:
            # Your existing code
            result = self.signal_engine.generate_signals(...)
            
            if result.get('success'):
                signal_count = len(result.get('data', []))
                logger.info(f"Successfully generated {signal_count} signals")
            
            return result
            
        except Exception as e:
            logger.error(f"Signal generation failed: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    4. Update your portfolio methods to use position sizing:
    
    def add_position_with_sizing(self, signal_data):
        # Get optimal position size
        position_sizer = get_position_sizer()
        portfolio_data = self.get_portfolio_summary().get('data', {})
        
        sizing_result = position_sizer.calculate_optimal_position_size(
            signal_data, portfolio_data
        )
        
        if sizing_result.get('success'):
            # Use recommended position size
            signal_data['quantity'] = sizing_result['position_size']
        
        # Your existing add_position code
        return self.add_position(signal_data)
    
    5. Test the new endpoints:
    
    # Test logging
    curl http://localhost:8000/logging/status
    
    # Test position sizing
    curl -X POST http://localhost:8000/position-sizing/calculate -d '{
        "signal_data": {"symbol": "RELIANCE", "confidence": 0.9, "entry_price": 2450, "target_price": 2800, "stop_loss": 2200},
        "portfolio_data": {"total_value": 1000000, "available_funds": 500000}
    }'
    
    # Test market regime
    curl http://localhost:8000/market-regime/detect
    
    # Test enhanced signal generation
    curl -X POST http://localhost:8000/signals/generate-all
    """
    pass

print("""
🚀 ENHANCED ENDPOINTS READY FOR INTEGRATION

Add these endpoints to your main.py to enable:

📊 Advanced Logging System:
- Dynamic log level control
- Component-specific logging
- Log search and analysis
- Automatic log rotation

💰 Position Sizing Optimization:
- Kelly Criterion sizing
- Risk-based position sizing
- Portfolio constraint management
- Multiple sizing methods

📈 Market Regime Filtering:
- Bull/Bear/Sideways detection
- Strategy filtering by market conditions
- Optimal timing analysis
- Regime-based recommendations

🎯 Enhanced Signal Generation:
- Multi-strategy generation in one call
- Automatic position sizing integration
- Market regime filtering
- Comprehensive results analysis

Follow the integration instructions in the integrate_enhanced_endpoints() function!
""")
