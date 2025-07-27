"""
Real-time Market Regime API Endpoints
Add these endpoints to your main.py for real-time market data integration
"""

from fastapi import HTTPException
from services.logging_service import get_logger
from services.realtime_market_data import get_market_data_service
from services.market_regime_realtime import get_realtime_regime_filter

# Add these endpoints to your main.py:

@app.get("/market-regime/realtime")
async def get_realtime_market_regime():
    """Get real-time market regime using live market data"""
    try:
        logger = get_logger('api')
        logger.info("Fetching real-time market regime")
        
        regime_filter = get_realtime_regime_filter()
        result = await regime_filter.detect_market_regime(use_cache=False)
        
        return result
        
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting real-time market regime: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-regime/realtime-intraday")
async def get_realtime_intraday_regime():
    """Get real-time market regime with intraday updates"""
    try:
        logger = get_logger('api')
        logger.info("Fetching real-time market regime with intraday data")
        
        regime_filter = get_realtime_regime_filter()
        result = await regime_filter.get_regime_with_intraday_update()
        
        return result
        
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting intraday market regime: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-data/live")
async def get_live_market_data(period_days: int = 30):
    """Get live market data for analysis"""
    try:
        logger = get_logger('api')
        logger.info(f"Fetching live market data for {period_days} days")
        
        market_data_service = get_market_data_service()
        result = await market_data_service.get_live_market_data(period_days)
        
        return result
        
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting live market data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-data/intraday")
async def get_intraday_market_data(symbol: str = "^NSEI", interval: str = "5m"):
    """Get intraday market data"""
    try:
        logger = get_logger('api')
        logger.info(f"Fetching intraday data for {symbol}")
        
        market_data_service = get_market_data_service()
        result = await market_data_service.get_intraday_data(symbol, interval)
        
        return result
        
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting intraday data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-data/status")
async def get_market_status():
    """Get current market status (open/closed)"""
    try:
        logger = get_logger('api')
        
        market_data_service = get_market_data_service()
        
        # Get market status from the service
        market_data_result = await market_data_service.get_live_market_data(period_days=1)
        
        if market_data_result.get('success'):
            market_status = market_data_result['data'].get('market_status', {})
            current_snapshot = market_data_result['data'].get('current_snapshot', {})
            
            return {
                'success': True,
                'data': {
                    'market_status': market_status,
                    'current_snapshot': current_snapshot,
                    'timestamp': market_data_result['data'].get('timestamp')
                }
            }
        else:
            return market_data_result
        
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting market status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/market-data/clear-cache")
async def clear_market_data_cache():
    """Clear market data cache to force fresh data fetch"""
    try:
        logger = get_logger('api')
        logger.info("Clearing market data cache")
        
        market_data_service = get_market_data_service()
        market_data_service.clear_cache()
        
        return {
            'success': True,
            'message': 'Market data cache cleared successfully'
        }
        
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-regime/summary-realtime")
async def get_realtime_regime_summary():
    """Get comprehensive real-time market regime summary"""
    try:
        logger = get_logger('api')
        logger.info("Fetching comprehensive real-time regime summary")
        
        regime_filter = get_realtime_regime_filter()
        
        # Get real-time regime
        regime_result = await regime_filter.detect_market_regime(use_cache=False)
        
        if not regime_result.get('success'):
            return regime_result
        
        # Get strategy recommendations
        all_strategies = list(regime_filter.strategy_regime_compatibility.keys())
        filter_result = regime_filter.filter_strategies_by_regime(all_strategies)
        
        # Combine results
        summary = {
            'success': True,
            'data': {
                'current_regime': regime_result['regime'],
                'confidence': regime_result['confidence'],
                'description': regime_result['description'],
                'indicators': regime_result['indicators'],
                'market_status': regime_result.get('market_status', {}),
                'data_source': regime_result.get('data_source', 'real_time'),
                'last_update': regime_result['timestamp'],
                'strategy_recommendations': filter_result.get('recommendations', {}) if filter_result.get('success') else {}
            }
        }
        
        return summary
        
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error getting real-time regime summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/market-regime/filter-strategies-realtime")
async def filter_strategies_realtime(request: dict):
    """Filter strategies based on real-time market regime"""
    try:
        strategies = request.get('strategies', [])
        
        if not strategies:
            raise HTTPException(status_code=400, detail="Strategies list is required")
        
        logger = get_logger('api')
        logger.info(f"Filtering {len(strategies)} strategies using real-time regime")
        
        regime_filter = get_realtime_regime_filter()
        
        # Get current regime with real-time data
        regime_result = await regime_filter.detect_market_regime(use_cache=False)
        
        if not regime_result.get('success'):
            return regime_result
        
        # Filter strategies
        result = regime_filter.filter_strategies_by_regime(strategies)
        
        # Add real-time context
        if result.get('success'):
            result['data']['regime_data_source'] = 'real_time'
            result['data']['regime_timestamp'] = regime_result['timestamp']
            result['data']['market_status'] = regime_result.get('market_status', {})
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error filtering strategies with real-time data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/market-regime/timing-score-realtime")
async def get_timing_score_realtime(request: dict):
    """Get timing score using real-time market regime"""
    try:
        signal_data = request.get('signal_data', {})
        
        if not signal_data:
            raise HTTPException(status_code=400, detail="Signal data is required")
        
        logger = get_logger('api')
        logger.info("Calculating timing score using real-time regime")
        
        regime_filter = get_realtime_regime_filter()
        
        # Get current regime with real-time data
        regime_result = await regime_filter.detect_market_regime(use_cache=False)
        
        if not regime_result.get('success'):
            return regime_result
        
        # Calculate timing score
        result = regime_filter.get_optimal_timing_score(signal_data)
        
        # Add real-time context
        if result.get('success'):
            result['regime_data_source'] = 'real_time'
            result['regime_timestamp'] = regime_result['timestamp']
            result['market_status'] = regime_result.get('market_status', {})
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger = get_logger('api')
        logger.error(f"Error calculating timing score with real-time data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Integration instructions for main.py:
def integrate_realtime_endpoints():
    """
    Instructions for integrating real-time endpoints into your main.py:
    
    1. Add these imports at the top of main.py:
    
    from services.realtime_market_data import get_market_data_service
    from services.market_regime_realtime import get_realtime_regime_filter
    
    2. Copy all the endpoint functions above into your main.py
    
    3. Update your existing market regime endpoints to use real-time data:
    
    # Replace the existing /market-regime/summary endpoint:
    @app.get("/market-regime/summary")
    async def get_regime_summary():
        # Use the new real-time version
        return await get_realtime_regime_summary()
    
    # Replace the existing /market-regime/detect endpoint:
    @app.get("/market-regime/detect")
    async def detect_market_regime():
        # Use the new real-time version
        return await get_realtime_market_regime()
    
    4. Install required dependencies:
    
    pip install yfinance pandas numpy aiohttp
    
    5. Test the new endpoints:
    
    # Test real-time regime detection
    curl http://localhost:8000/market-regime/realtime
    
    # Test live market data
    curl http://localhost:8000/market-data/live?period_days=30
    
    # Test intraday data
    curl http://localhost:8000/market-data/intraday?symbol=^NSEI&interval=5m
    
    # Test market status
    curl http://localhost:8000/market-data/status
    
    6. Frontend Integration:
    
    Update your frontend components to use the new real-time endpoints:
    
    // In your React components, replace:
    fetch('http://localhost:8000/market-regime/summary')
    
    // With:
    fetch('http://localhost:8000/market-regime/summary-realtime')
    
    This will provide real-time market data with:
    - Live NIFTY50, SENSEX, and other index data
    - Real-time regime detection with enhanced accuracy
    - Intraday updates for more responsive regime changes
    - Market status awareness (open/closed)
    - Comprehensive technical indicators
    - Enhanced confidence scoring
    """
    pass

print("""
🚀 REAL-TIME MARKET REGIME ENDPOINTS READY!

New endpoints available:
📊 GET /market-regime/realtime - Real-time regime detection
📈 GET /market-regime/realtime-intraday - Intraday regime updates
📉 GET /market-data/live - Live market data
⏰ GET /market-data/intraday - Intraday price data
🔄 GET /market-data/status - Market open/closed status
🗑️ POST /market-data/clear-cache - Clear data cache
📋 GET /market-regime/summary-realtime - Complete real-time summary

Features:
✅ Live NIFTY50, SENSEX, Bank Nifty data
✅ Real-time regime detection with 60-day analysis
✅ Intraday updates every 5 minutes
✅ Market status awareness (IST market hours)
✅ Enhanced technical indicators (RSI, volatility, momentum)
✅ Improved confidence scoring with data quality assessment
✅ Automatic caching with 5-minute expiry
✅ Error handling and fallback mechanisms

Follow the integration instructions to enable real-time market regime detection!
""")
