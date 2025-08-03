"""
Production FastAPI Main Application - EmergentTrader Backend
Optimized for Render deployment with health checks and monitoring
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import our modules
from api_handler import EmergentTraderAPI

# Import AI prediction endpoints
try:
    from ai_prediction_endpoints import router as ai_router
    AI_PREDICTIONS_AVAILABLE = True
except ImportError as e:
    print(f"AI Predictions not available: {e}")
    AI_PREDICTIONS_AVAILABLE = False

# Import AI-enhanced signal endpoints
try:
    from ai_enhanced_endpoints import router as ai_enhanced_router
    AI_ENHANCED_SIGNALS_AVAILABLE = True
except ImportError as e:
    print(f"AI Enhanced Signals not available: {e}")
    AI_ENHANCED_SIGNALS_AVAILABLE = False

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EmergentTrader API",
    description="Production-grade trading signal system with automated signal generation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for production
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://emergenttrader.onrender.com")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API handler
api_handler = EmergentTraderAPI()

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Health check endpoint for Render
@app.get("/health")
async def health_check():
    """Health check endpoint for Render deployment"""
    try:
        # Test database connection
        test_result = api_handler.test_database_connection()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected" if test_result else "disconnected",
            "version": "2.0.0",
            "environment": os.getenv("PYTHON_ENV", "development")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "EmergentTrader API v2.0 - Production Ready",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/health"
    }

# Signal generation endpoints
@app.post("/api/signals/generate")
async def generate_signals(request: dict, background_tasks: BackgroundTasks):
    """Generate trading signals"""
    try:
        logger.info(f"Signal generation request: {request}")
        
        # Add background task for signal broadcasting
        background_tasks.add_task(broadcast_signal_update, "signal_generation_started")
        
        result = api_handler.generate_signals(request)
        
        # Broadcast completion
        background_tasks.add_task(broadcast_signal_update, "signal_generation_completed", result)
        
        return result
    except Exception as e:
        logger.error(f"Error generating signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/signals/active")
async def get_active_signals(days: int = 7):
    """Get active signals"""
    try:
        result = api_handler.get_active_signals({"days": days})
        return result
    except Exception as e:
        logger.error(f"Error getting active signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/signals/performance")
async def get_signal_performance():
    """Get signal performance metrics"""
    try:
        result = api_handler.get_signal_performance()
        return result
    except Exception as e:
        logger.error(f"Error getting signal performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/signals/track")
async def track_signal_progress(background_tasks: BackgroundTasks):
    """Track progress of existing signals"""
    try:
        background_tasks.add_task(run_signal_tracking)
        return {"message": "Signal tracking started", "status": "success"}
    except Exception as e:
        logger.error(f"Error starting signal tracking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Portfolio endpoints
@app.get("/api/portfolio")
async def get_portfolio():
    """Get portfolio data"""
    try:
        result = api_handler.get_portfolio()
        return result
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/portfolio/position")
async def add_position(position: dict):
    """Add position to portfolio"""
    try:
        result = api_handler.add_portfolio_position(position)
        return result
    except Exception as e:
        logger.error(f"Error adding position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio")
async def get_portfolio_root():
    """Get portfolio data (root endpoint)"""
    try:
        result = api_handler.get_portfolio()
        return result
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/positions")
async def get_portfolio_positions():
    """Get portfolio positions"""
    try:
        result = api_handler.get_portfolio()
        return result.get('positions', [])
    except Exception as e:
        logger.error(f"Error getting portfolio positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/allocation")
async def get_portfolio_allocation():
    """Get portfolio allocation"""
    try:
        result = api_handler.get_portfolio()
        return result.get('allocation', {})
    except Exception as e:
        logger.error(f"Error getting portfolio allocation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/strategies")
async def get_strategies():
    """Get available trading strategies"""
    try:
        strategies = [
            {"id": "multibagger", "name": "Multibagger", "description": "High-growth potential stocks"},
            {"id": "momentum", "name": "Momentum", "description": "Stocks with strong price momentum"},
            {"id": "breakout", "name": "Breakout", "description": "Stocks breaking resistance levels"},
            {"id": "swing_trading", "name": "Swing Trading", "description": "Short to medium-term opportunities"},
            {"id": "mean_reversion", "name": "Mean Reversion", "description": "Oversold stocks likely to bounce"},
            {"id": "value_investing", "name": "Value Investing", "description": "Undervalued stocks with strong fundamentals"}
        ]
        return {"success": True, "strategies": strategies}
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals")
async def get_signals_root():
    """Get signals (root endpoint)"""
    try:
        result = api_handler.get_active_signals()
        return result
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals/today")
async def get_signals_today():
    """Get today's signals"""
    try:
        result = api_handler.get_active_signals(days=1)
        return result
    except Exception as e:
        logger.error(f"Error getting today's signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals/open")
async def get_signals_open():
    """Get open signals"""
    try:
        result = api_handler.get_active_signals()
        return result
    except Exception as e:
        logger.error(f"Error getting open signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance")
async def get_performance():
    """Get performance data"""
    try:
        # Mock performance data
        performance = {
            "total_return": 15.2,
            "daily_return": 0.8,
            "win_rate": 68.5,
            "total_trades": 45,
            "winning_trades": 31,
            "losing_trades": 14
        }
        return {"success": True, "performance": performance}
    except Exception as e:
        logger.error(f"Error getting performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance/summary")
async def get_performance_summary(period: str = "30d"):
    """Get performance summary"""
    try:
        # Mock performance summary
        summary = {
            "period": period,
            "total_return": 15.2,
            "sharpe_ratio": 1.8,
            "max_drawdown": -5.2,
            "volatility": 12.5,
            "trades_count": 45
        }
        return {"success": True, "summary": summary}
    except Exception as e:
        logger.error(f"Error getting performance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/all")
async def get_all_stocks():
    """Get all stocks"""
    try:
        # Mock stock data
        stocks = [
            {"symbol": "RELIANCE", "name": "Reliance Industries", "price": 2450.50, "change": 1.2},
            {"symbol": "TCS", "name": "Tata Consultancy Services", "price": 3650.75, "change": -0.8},
            {"symbol": "INFY", "name": "Infosys", "price": 1580.25, "change": 2.1}
        ]
        return {"success": True, "stocks": stocks}
    except Exception as e:
        logger.error(f"Error getting all stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/shariah")
async def get_shariah_stocks():
    """Get Shariah-compliant stocks"""
    try:
        # Mock Shariah stock data
        stocks = [
            {"symbol": "TCS", "name": "Tata Consultancy Services", "price": 3650.75, "change": -0.8, "shariah_compliant": True},
            {"symbol": "INFY", "name": "Infosys", "price": 1580.25, "change": 2.1, "shariah_compliant": True}
        ]
        return {"success": True, "stocks": stocks}
    except Exception as e:
        logger.error(f"Error getting Shariah stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Market data endpoints
@app.get("/api/market/data/{symbol}")
async def get_market_data(symbol: str):
    """Get market data for symbol"""
    try:
        result = api_handler.get_market_data(symbol)
        return result
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/status")
async def get_market_status():
    """Get market status"""
    try:
        result = api_handler.get_market_status()
        return result
    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Scheduled job status endpoint
@app.get("/api/scheduled/status")
async def get_scheduled_status():
    """Get status of scheduled jobs"""
    try:
        # Read recent job reports
        reports_dir = Path("reports")
        if not reports_dir.exists():
            return {"scheduled_jobs": [], "last_run": None}
        
        # Get recent reports
        report_files = sorted(reports_dir.glob("scheduled_run_*.json"), 
                            key=lambda x: x.stat().st_mtime, reverse=True)
        
        recent_reports = []
        for report_file in report_files[:10]:  # Last 10 runs
            try:
                with open(report_file, 'r') as f:
                    report = json.load(f)
                    recent_reports.append(report)
            except Exception as e:
                logger.error(f"Error reading report {report_file}: {e}")
        
        return {
            "scheduled_jobs": recent_reports,
            "last_run": recent_reports[0] if recent_reports else None,
            "total_runs": len(recent_reports)
        }
    except Exception as e:
        logger.error(f"Error getting scheduled status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Echo back for heartbeat
            await manager.send_personal_message(
                json.dumps({"type": "heartbeat", "timestamp": datetime.now().isoformat()}),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Background tasks
async def broadcast_signal_update(event_type: str, data: dict = None):
    """Broadcast signal updates to connected clients"""
    message = {
        "type": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    await manager.broadcast(json.dumps(message))

async def run_signal_tracking():
    """Background task for signal tracking"""
    try:
        from scheduled_signal_generator import ScheduledSignalGenerator
        
        generator = ScheduledSignalGenerator("tracking")
        await generator.track_signal_progress()
        
        # Broadcast update
        await broadcast_signal_update("signal_tracking_completed")
        
    except Exception as e:
        logger.error(f"Error in background signal tracking: {e}")

# Include AI routers if available
if AI_PREDICTIONS_AVAILABLE:
    app.include_router(ai_router, prefix="/api/ai", tags=["AI Predictions"])
    logger.info("AI Predictions endpoints enabled")

if AI_ENHANCED_SIGNALS_AVAILABLE:
    app.include_router(ai_enhanced_router, prefix="/api/enhanced", tags=["Enhanced Signals"])
    logger.info("AI Enhanced Signals endpoints enabled")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("EmergentTrader API starting up...")
    
    # Test database connection
    try:
        api_handler.test_database_connection()
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    
    # Create necessary directories
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    logger.info("EmergentTrader API startup complete")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("EmergentTrader API shutting down...")
    
    # Close all WebSocket connections
    for connection in manager.active_connections:
        try:
            await connection.close()
        except Exception as e:
            logger.error(f"Error closing WebSocket connection: {e}")
    
    logger.info("EmergentTrader API shutdown complete")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

if __name__ == "__main__":
    # Production server configuration
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting EmergentTrader API on {host}:{port}")
    
    uvicorn.run(
        "main_production:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=False  # Disable reload in production
    )
