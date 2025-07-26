"""
ML-Enhanced API Handler
FastAPI endpoints for ML-enhanced signal generation and management
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import json
from datetime import datetime

# Import the ML-enhanced signal engine
from core.ml_enhanced_signal_engine import MLEnhancedSignalEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EmergentTrader ML-Enhanced API",
    description="ML-powered trading signal generation and management",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML-enhanced signal engine
signal_engine = MLEnhancedSignalEngine(enable_ml=True)

# Pydantic models for request/response
class SignalRequest(BaseModel):
    symbols: Optional[List[str]] = None
    strategy: str = "ml_consensus"
    shariah_only: bool = True
    min_confidence: float = 0.6
    max_symbols: int = 50
    enable_ml_filter: bool = True

class MLSignalRequest(BaseModel):
    symbols: Optional[List[str]] = None
    shariah_only: bool = True
    max_symbols: int = 50
    min_ml_probability: float = 0.6

class SystemStatusResponse(BaseModel):
    system_ready: bool
    ml_enabled: bool
    strategies_available: int
    active_signals: int
    ml_enhanced_signals: int

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "EmergentTrader ML-Enhanced API",
        "version": "2.0.0",
        "features": [
            "ML-enhanced signal generation",
            "Multi-strategy consensus signals",
            "Real-time market context analysis",
            "Signal quality scoring",
            "Shariah compliance filtering"
        ],
        "endpoints": {
            "signals": "/signals/generate",
            "ml_signals": "/signals/ml-enhanced",
            "status": "/system/status",
            "ml_test": "/ml/test",
            "market_context": "/market/context"
        }
    }

@app.post("/signals/generate")
async def generate_signals(request: SignalRequest):
    """
    Generate trading signals with optional ML enhancement
    
    - **strategy**: 'ml_consensus' (recommended), 'consensus', or specific strategy name
    - **shariah_only**: Filter for Shariah compliant stocks only
    - **min_confidence**: Minimum confidence threshold (0.0 to 1.0)
    - **enable_ml_filter**: Apply ML filtering to signals
    """
    try:
        logger.info(f"Generating signals with strategy: {request.strategy}")
        
        signals = signal_engine.generate_signals(
            symbols=request.symbols,
            strategy_name=request.strategy,
            shariah_only=request.shariah_only,
            min_confidence=request.min_confidence,
            enable_ml_filter=request.enable_ml_filter
        )
        
        return {
            "success": True,
            "signals_count": len(signals),
            "signals": signals,
            "strategy_used": request.strategy,
            "ml_enhanced": request.enable_ml_filter and signal_engine.enable_ml,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/signals/ml-enhanced")
async def generate_ml_enhanced_signals(request: MLSignalRequest):
    """
    Generate ML-enhanced consensus signals (recommended endpoint)
    
    This endpoint provides the highest quality signals by:
    1. Generating multi-strategy consensus signals
    2. Applying ML-based quality enhancement
    3. Filtering by ML probability threshold
    """
    try:
        logger.info("Generating ML-enhanced consensus signals")
        
        signals = signal_engine.generate_ml_enhanced_signals(
            symbols=request.symbols,
            shariah_only=request.shariah_only,
            max_symbols=request.max_symbols,
            min_ml_probability=request.min_ml_probability
        )
        
        # Calculate statistics
        if signals:
            avg_ml_prob = sum(s.get('ml_probability', 0) for s in signals) / len(signals)
            avg_confidence_adj = sum(s.get('confidence_adjustment', 0) for s in signals) / len(signals)
            
            recommendations = {}
            for signal in signals:
                rec = signal.get('ml_recommendation', 'UNKNOWN')
                recommendations[rec] = recommendations.get(rec, 0) + 1
        else:
            avg_ml_prob = 0
            avg_confidence_adj = 0
            recommendations = {}
        
        return {
            "success": True,
            "signals_count": len(signals),
            "signals": signals,
            "ml_statistics": {
                "average_ml_probability": avg_ml_prob,
                "average_confidence_adjustment": avg_confidence_adj,
                "recommendation_breakdown": recommendations
            },
            "filter_threshold": request.min_ml_probability,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating ML-enhanced signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals/active")
async def get_active_signals(
    strategy: Optional[str] = Query(None, description="Filter by strategy"),
    ml_enhanced_only: bool = Query(False, description="Show only ML-enhanced signals")
):
    """Get currently active trading signals"""
    try:
        if ml_enhanced_only:
            signals = signal_engine.get_ml_enhanced_signals(days=7)
        else:
            signals = signal_engine.active_signals
            
        if strategy:
            signals = [s for s in signals if s.get('strategy', '').lower() == strategy.lower()]
        
        return {
            "success": True,
            "active_signals_count": len(signals),
            "signals": signals,
            "filter_applied": {
                "strategy": strategy,
                "ml_enhanced_only": ml_enhanced_only
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting active signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/context")
async def get_market_context():
    """Get current market context for ML enhancement"""
    try:
        market_context = signal_engine.get_market_context()
        
        return {
            "success": True,
            "market_context": market_context,
            "interpretation": {
                "regime_description": {
                    "BULL": "Uptrend - favor momentum and growth strategies",
                    "BEAR": "Downtrend - favor defensive and value strategies", 
                    "SIDEWAYS": "Range-bound - favor mean reversion strategies"
                }.get(market_context['regime'], "Unknown regime"),
                "volatility_level": "High" if market_context['volatility'] > 0.25 else "Medium" if market_context['volatility'] > 0.15 else "Low",
                "trend_strength": "Strong" if abs(market_context['trend_20d']) > 0.05 else "Moderate" if abs(market_context['trend_20d']) > 0.02 else "Weak"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting market context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ml/test")
async def test_ml_integration():
    """Test ML integration with sample data"""
    try:
        test_result = signal_engine.test_ml_integration()
        
        return {
            "success": test_result['status'] == 'success',
            "test_result": test_result,
            "ml_available": signal_engine.enable_ml,
            "ml_engine_loaded": signal_engine.ml_engine is not None
        }
        
    except Exception as e:
        logger.error(f"Error testing ML integration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ml/performance")
async def get_ml_performance():
    """Get ML enhancement performance summary"""
    try:
        performance = signal_engine.get_ml_performance_summary()
        
        return {
            "success": True,
            "ml_performance": performance
        }
        
    except Exception as e:
        logger.error(f"Error getting ML performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        status = signal_engine.get_system_status()
        
        return {
            "success": True,
            "system_status": status,
            "api_version": "2.0.0",
            "features_enabled": {
                "ml_enhancement": status.get('ml_status', {}).get('ml_enabled', False),
                "consensus_engine": status.get('consensus_engine_active', False),
                "shariah_filtering": True,
                "database_storage": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/strategies/available")
async def get_available_strategies():
    """Get list of available trading strategies"""
    try:
        strategies = signal_engine.get_available_strategies()
        
        strategy_info = {}
        for strategy_name in strategies:
            strategy_info[strategy_name] = signal_engine.get_strategy_info(strategy_name)
        
        return {
            "success": True,
            "strategies_count": len(strategies),
            "strategies": strategies,
            "strategy_details": strategy_info,
            "recommended_strategies": ["ml_consensus", "consensus"],
            "single_strategies": strategies
        }
        
    except Exception as e:
        logger.error(f"Error getting available strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/shariah/universe")
async def get_shariah_universe(
    force_refresh: bool = Query(False, description="Force refresh of Shariah universe")
):
    """Get list of Shariah compliant stocks"""
    try:
        shariah_stocks = signal_engine.get_shariah_universe(force_refresh=force_refresh)
        
        return {
            "success": True,
            "shariah_stocks_count": len(shariah_stocks),
            "shariah_stocks": shariah_stocks,
            "force_refresh": force_refresh,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Shariah universe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/signals/batch-generate")
async def batch_generate_signals(background_tasks: BackgroundTasks):
    """
    Generate signals for multiple strategies in background
    Useful for comprehensive market analysis
    """
    try:
        def generate_all_strategies():
            """Background task to generate signals for all strategies"""
            strategies = ['ml_consensus', 'consensus'] + signal_engine.get_available_strategies()
            
            results = {}
            for strategy in strategies:
                try:
                    signals = signal_engine.generate_signals(
                        strategy_name=strategy,
                        shariah_only=True,
                        min_confidence=0.6,
                        enable_ml_filter=True
                    )
                    results[strategy] = len(signals)
                    logger.info(f"Generated {len(signals)} signals for {strategy}")
                except Exception as e:
                    logger.error(f"Error generating signals for {strategy}: {str(e)}")
                    results[strategy] = 0
            
            logger.info(f"Batch generation complete: {results}")
        
        # Start background task
        background_tasks.add_task(generate_all_strategies)
        
        return {
            "success": True,
            "message": "Batch signal generation started in background",
            "strategies_to_process": ['ml_consensus', 'consensus'] + signal_engine.get_available_strategies(),
            "estimated_completion": "5-10 minutes",
            "check_status_at": "/system/status"
        }
        
    except Exception as e:
        logger.error(f"Error starting batch generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Quick system check
        status = signal_engine.get_system_status()
        
        return {
            "status": "healthy" if status.get('system_ready', False) else "degraded",
            "timestamp": datetime.now().isoformat(),
            "ml_enabled": status.get('ml_status', {}).get('ml_enabled', False),
            "database_connected": status.get('database_stats', {}).get('connected', False),
            "version": "2.0.0"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting ML-Enhanced EmergentTrader API")
    print("=" * 50)
    print("Features:")
    print("  ✅ ML-enhanced signal generation")
    print("  ✅ Multi-strategy consensus signals")
    print("  ✅ Real-time market context analysis")
    print("  ✅ Signal quality scoring")
    print("  ✅ Shariah compliance filtering")
    print("=" * 50)
    
    uvicorn.run(
        "ml_enhanced_api_handler:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
