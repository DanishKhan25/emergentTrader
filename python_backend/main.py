"""
FastAPI Main Application - EmergentTrader Backend
Production-ready API server with all trading endpoints
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import sys
from datetime import datetime
import logging

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import our modules
from api_handler import EmergentTraderAPI
from core.enhanced_signal_engine import EnhancedSignalEngine
from core.enhanced_shariah_filter import EnhancedShariahFilter
from core.backtest_engine import BacktestEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EmergentTrader API",
    description="Production-grade trading signal system with ML-enhanced multibagger strategies",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API handler
api_handler = EmergentTraderAPI()

# Pydantic models for request/response
class SignalRequest(BaseModel):
    strategy: str = "multibagger"
    symbols: Optional[List[str]] = None
    shariah_only: bool = True
    min_confidence: float = 0.6

class BacktestRequest(BaseModel):
    strategy: str = "multibagger"
    start_date: str = "2019-01-01"
    end_date: str = "2025-01-27"
    symbols: Optional[List[str]] = None

class StockRequest(BaseModel):
    symbols: Optional[List[str]] = None
    shariah_only: bool = True

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "EmergentTrader API",
        "version": "1.1.0",
        "status": "active",
        "features": [
            "10 Trading Strategies",
            "ML-Enhanced Signals (87% success rate)",
            "Shariah Compliance Filter",
            "Real-time Signal Generation",
            "Comprehensive Backtesting",
            "Risk Management"
        ],
        "endpoints": {
            "signals": "/signals",
            "stocks": "/stocks",
            "shariah": "/shariah-stocks",
            "backtest": "/backtest",
            "performance": "/performance",
            "strategies": "/strategies"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test signal engine
        if api_handler.signal_engine:
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        else:
            return {"status": "unhealthy", "error": "Signal engine not initialized"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/signals")
async def generate_signals(request: SignalRequest):
    """Generate trading signals using specified strategy"""
    try:
        result = api_handler.generate_signals(
            strategy=request.strategy,
            symbols=request.symbols,
            shariah_only=request.shariah_only,
            min_confidence=request.min_confidence
        )
        return result
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/signals/generate")
async def generate_signals_alt(request: SignalRequest):
    """Generate trading signals (alternative endpoint for frontend compatibility)"""
    try:
        result = api_handler.generate_signals(
            strategy=request.strategy,
            symbols=request.symbols,
            shariah_only=request.shariah_only,
            min_confidence=request.min_confidence
        )
        return result
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals/open")
async def get_open_signals():
    """Get currently open trading signals"""
    try:
        result = api_handler.get_active_signals()
        return result
    except Exception as e:
        logger.error(f"Error getting open signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals/today")
async def get_today_signals():
    """Get today's generated signals"""
    try:
        result = api_handler.get_todays_signals()
        return result
    except Exception as e:
        logger.error(f"Error getting today's signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/signals/track")
async def track_signals(request: dict):
    """Track signal performance"""
    try:
        signal_ids = request.get('signal_ids', [])
        results = []
        
        for signal_id in signal_ids:
            result = api_handler.track_signal_performance(signal_id)
            if result.get('success'):
                results.append(result.get('data', {}))
        
        return {
            'success': True,
            'data': {
                'results': results
            }
        }
    except Exception as e:
        logger.error(f"Error tracking signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks")
async def get_stocks(shariah_only: bool = True, limit: int = 100):
    """Get stock universe (with optional Shariah filter)"""
    try:
        result = api_handler.get_all_stocks() if not shariah_only else api_handler.get_shariah_stocks()
        return result
    except Exception as e:
        logger.error(f"Error getting stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/all")
async def get_all_stocks(include_prices: bool = True, limit: int = None):
    """Get all stocks in universe with optional price data"""
    try:
        result = api_handler.get_all_stocks(include_prices=include_prices, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Error getting all stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/fast")
async def get_stocks_fast(limit: int = 100, include_prices: bool = True):
    """Get limited stocks with price data for better performance"""
    try:
        result = api_handler.get_all_stocks(include_prices=include_prices, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Error getting stocks fast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/shariah")
async def get_shariah_stocks_alt(force_refresh: bool = False, include_prices: bool = True):
    """Get Shariah-compliant stock universe with price data"""
    try:
        result = api_handler.get_shariah_stocks(force_refresh=force_refresh, include_prices=include_prices)
        return result
    except Exception as e:
        logger.error(f"Error getting Shariah stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stocks/refresh")
async def refresh_stock_prices():
    """Refresh stock prices"""
    try:
        result = api_handler.refresh_stock_data()
        return result
    except Exception as e:
        logger.error(f"Error refreshing stock prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/shariah-stocks")
async def get_shariah_stocks():
    """Get Shariah-compliant stock universe"""
    try:
        result = api_handler.get_shariah_stocks()
        return result
    except Exception as e:
        logger.error(f"Error getting Shariah stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest")
async def run_backtest(request: BacktestRequest):
    """Run historical backtest for specified strategy"""
    try:
        result = api_handler.run_backtest(
            strategy=request.strategy,
            start_date=request.start_date,
            end_date=request.end_date,
            symbols=request.symbols
        )
        return result
    except Exception as e:
        logger.error(f"Error running backtest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance")
async def get_performance():
    """Get overall system performance metrics"""
    try:
        result = api_handler.get_performance()
        return result
    except Exception as e:
        logger.error(f"Error getting performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/strategies")
async def get_strategies():
    """Get list of available trading strategies"""
    try:
        strategies = [
            {
                "name": "multibagger",
                "description": "ML-enhanced multibagger strategy (87% success rate)",
                "focus": "2x, 3x, 5x+ returns",
                "holding_period": "6 months to 3 years"
            },
            {
                "name": "momentum",
                "description": "Momentum-based trading strategy",
                "focus": "Trending stocks with strong momentum",
                "holding_period": "1-3 months"
            },
            {
                "name": "swing_trading",
                "description": "Swing trading strategy",
                "focus": "Short to medium-term price swings",
                "holding_period": "1-4 weeks"
            },
            {
                "name": "breakout",
                "description": "Breakout pattern strategy",
                "focus": "Stocks breaking key resistance levels",
                "holding_period": "2-8 weeks"
            },
            {
                "name": "mean_reversion",
                "description": "Mean reversion strategy",
                "focus": "Oversold stocks likely to bounce",
                "holding_period": "1-6 weeks"
            },
            {
                "name": "value_investing",
                "description": "Value investing strategy",
                "focus": "Undervalued stocks with strong fundamentals",
                "holding_period": "6 months to 2 years"
            },
            {
                "name": "fundamental_growth",
                "description": "Fundamental growth strategy",
                "focus": "Companies with strong growth metrics",
                "holding_period": "3 months to 2 years"
            },
            {
                "name": "sector_rotation",
                "description": "Sector rotation strategy",
                "focus": "Rotating between outperforming sectors",
                "holding_period": "1-6 months"
            },
            {
                "name": "low_volatility",
                "description": "Low volatility strategy",
                "focus": "Stable stocks with consistent returns",
                "holding_period": "3-12 months"
            },
            {
                "name": "pivot_cpr",
                "description": "Pivot CPR strategy",
                "focus": "Support/resistance based trading",
                "holding_period": "1-4 weeks"
            }
        ]
        return {"strategies": strategies, "total": len(strategies)}
    except Exception as e:
        logger.error(f"Error getting strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ml/performance")
async def get_ml_performance():
    """Get ML performance metrics for all strategies"""
    try:
        from ml.ml_strategy_enhancer import get_ml_performance_summary
        performance_data = get_ml_performance_summary()
        return {
            "success": True,
            "data": performance_data
        }
    except Exception as e:
        logger.error(f"Error getting ML performance: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/signals/open")
async def get_open_signals():
    """Get currently open trading signals"""
    try:
        result = api_handler.get_open_signals()
        return result
    except Exception as e:
        logger.error(f"Error getting open signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals/today")
async def get_today_signals():
    """Get today's generated signals"""
    try:
        result = api_handler.get_today_signals()
        return result
    except Exception as e:
        logger.error(f"Error getting today's signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/{symbol}")
async def get_stock_details(symbol: str):
    """Get detailed information for a specific stock"""
    try:
        result = api_handler.get_stock_details(symbol)
        return result
    except Exception as e:
        logger.error(f"Error getting stock details for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance")
async def get_performance():
    """Get overall system performance metrics"""
    try:
        result = api_handler.get_performance_summary()
        return result
    except Exception as e:
        logger.error(f"Error getting performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance/summary")
async def get_performance_summary(period: str = "30d"):
    """Get performance summary with period filter"""
    try:
        result = api_handler.get_performance_summary(period=period)
        return result
    except Exception as e:
        logger.error(f"Error getting performance summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest")
async def run_backtest(request: BacktestRequest):
    """Run historical backtest for specified strategy"""
    try:
        result = api_handler.run_backtest(
            strategy=request.strategy,
            start_date=request.start_date,
            end_date=request.end_date,
            symbols=request.symbols
        )
        return result
    except Exception as e:
        logger.error(f"Error running backtest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
