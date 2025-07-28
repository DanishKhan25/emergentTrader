"""
Enhanced FastAPI Main Application - EmergentTrader Backend
Production-ready API server with enhanced services, authentication, and real-time features
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import asyncio
import logging
from datetime import datetime
import uvicorn
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import our modules
from api_handler import EmergentTraderAPI

# Import enhanced services
try:
    from services.enhanced_notification_service import notification_service
    from services.signal_management_service import signal_manager
    from services.scheduler_service import scheduler_service
    from services.auth_service import auth_service
    ENHANCED_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced services not available: {e}")
    ENHANCED_SERVICES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EmergentTrader Enhanced API",
    description="Production-grade trading system with authentication, real-time notifications, and automated scheduling",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API handler
api_handler = EmergentTraderAPI()

# Security
security = HTTPBearer()

# WebSocket Connection Manager (Enhanced)
class EnhancedConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from user connections
        for user_id, conn in list(self.user_connections.items()):
            if conn == websocket:
                del self.user_connections[user_id]
                break
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            self.disconnect(websocket)

    async def send_to_user(self, user_id: str, message: str):
        if user_id in self.user_connections:
            await self.send_personal_message(message, self.user_connections[user_id])

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_signal(self, signal_data: Dict):
        """Broadcast new signal to all connected clients"""
        message = {
            "type": "signal_generated",
            "data": signal_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(json.dumps(message))

    async def broadcast_target_hit(self, target_data: Dict):
        """Broadcast target hit to all connected clients"""
        message = {
            "type": "target_hit",
            "data": target_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(json.dumps(message))

    async def broadcast_stop_loss(self, stop_loss_data: Dict):
        """Broadcast stop loss hit to all connected clients"""
        message = {
            "type": "stop_loss_hit",
            "data": stop_loss_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(json.dumps(message))

manager = EnhancedConnectionManager()

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class SignalRequest(BaseModel):
    strategy: str = "multibagger"
    symbols: Optional[List[str]] = None
    shariah_only: bool = True
    min_confidence: float = 0.6

class NotificationRequest(BaseModel):
    type: str
    title: str
    message: str
    data: Optional[Dict] = None

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not ENHANCED_SERVICES_AVAILABLE:
        return {"username": "demo", "role": "admin"}  # Fallback for demo
    
    token = credentials.credentials
    result = auth_service.verify_token(token)
    
    if not result['success']:
        raise HTTPException(status_code=401, detail=result['error'])
    
    return result['user']

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting EmergentTrader Enhanced API...")
    
    if ENHANCED_SERVICES_AVAILABLE:
        # Start scheduler service
        scheduler_service.start()
        logger.info("✅ Scheduler service started")
        
        # Send startup notification
        try:
            await notification_service.send_telegram_message(
                "🚀 <b>EmergentTrader System Started</b>\n\n"
                f"API server is now running\n"
                f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                f"<i>Ready for trading! 📈</i>"
            )
        except Exception as e:
            logger.warning(f"Could not send startup notification: {e}")
    
    logger.info("✅ EmergentTrader Enhanced API started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down EmergentTrader Enhanced API...")
    
    if ENHANCED_SERVICES_AVAILABLE:
        scheduler_service.stop()
        logger.info("✅ Scheduler service stopped")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check with service status"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "api": True,
            "websocket": len(manager.active_connections) > 0,
            "enhanced_services": ENHANCED_SERVICES_AVAILABLE
        }
    }
    
    if ENHANCED_SERVICES_AVAILABLE:
        health_data["services"].update({
            "scheduler": scheduler_service.get_status()["running"],
            "notification": True,
            "signal_manager": True,
            "auth": True
        })
    
    return health_data

# Authentication endpoints
@app.post("/auth/login")
async def login(request: LoginRequest):
    """User login endpoint"""
    if not ENHANCED_SERVICES_AVAILABLE:
        return {"success": False, "error": "Authentication service not available"}
    
    result = auth_service.authenticate(request.username, request.password)
    return result

@app.post("/auth/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify JWT token"""
    return {"success": True, "user": current_user}

@app.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """User logout endpoint"""
    if not ENHANCED_SERVICES_AVAILABLE:
        return {"success": True, "message": "Logged out"}
    
    token = credentials.credentials
    result = auth_service.logout(token)
    return result

# Signal management endpoints
@app.get("/signals/active")
async def get_active_signals(current_user: dict = Depends(get_current_user)):
    """Get all active signals"""
    if not ENHANCED_SERVICES_AVAILABLE:
        return {"success": False, "error": "Signal management service not available"}
    
    return signal_manager.get_active_signals()

@app.get("/signals/statistics")
async def get_signal_statistics(current_user: dict = Depends(get_current_user)):
    """Get signal performance statistics"""
    if not ENHANCED_SERVICES_AVAILABLE:
        return {"success": False, "error": "Signal management service not available"}
    
    return signal_manager.get_signal_statistics()

@app.post("/signals/clear")
async def clear_all_signals(current_user: dict = Depends(get_current_user)):
    """Clear all signals from database"""
    if not ENHANCED_SERVICES_AVAILABLE:
        return {"success": False, "error": "Signal management service not available"}
    
    # Only admin can clear signals
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = signal_manager.clear_all_signals()
    
    # Broadcast signal clear event
    if result['success']:
        await manager.broadcast(json.dumps({
            "type": "signals_cleared",
            "data": {"count": result['count_cleared']},
            "timestamp": datetime.now().isoformat()
        }))
    
    return result

@app.post("/signals/generate")
async def generate_signals_manual(
    request: SignalRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger signal generation"""
    if not ENHANCED_SERVICES_AVAILABLE:
        # Fallback to original API
        return api_handler.generate_signals()
    
    # Only admin can manually generate signals
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Run signal generation in background
    background_tasks.add_task(run_signal_generation)
    
    return {
        "success": True,
        "message": "Signal generation started",
        "status": "processing"
    }

async def run_signal_generation():
    """Background task for signal generation"""
    try:
        # Clear old signals
        clear_result = signal_manager.clear_all_signals()
        
        # Generate new signals
        result = api_handler.generate_signals(force_refresh=True)
        
        if result.get('success'):
            signals = result.get('data', {}).get('signals', [])
            
            # Add signals to tracking and send notifications
            for signal in signals:
                signal_manager.add_signal(signal)
                await notification_service.notify_signal_generated(signal)
                await manager.broadcast_signal(signal)
            
            logger.info(f"Generated and broadcasted {len(signals)} signals")
        
    except Exception as e:
        logger.error(f"Error in background signal generation: {e}")

# Notification endpoints
@app.post("/notifications/send")
async def send_notification(
    request: NotificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send custom notification"""
    if not ENHANCED_SERVICES_AVAILABLE:
        return {"success": False, "error": "Notification service not available"}
    
    # Only admin can send custom notifications
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    notification_id = await notification_service.addNotification({
        "type": request.type,
        "title": request.title,
        "message": request.message,
        "data": request.data
    })
    
    return {
        "success": True,
        "notification_id": notification_id,
        "message": "Notification sent"
    }

# Scheduler endpoints
@app.get("/scheduler/status")
async def get_scheduler_status(current_user: dict = Depends(get_current_user)):
    """Get scheduler status"""
    if not ENHANCED_SERVICES_AVAILABLE:
        return {"success": False, "error": "Scheduler service not available"}
    
    return {
        "success": True,
        "data": scheduler_service.get_status()
    }

@app.post("/scheduler/start")
async def start_scheduler(current_user: dict = Depends(get_current_user)):
    """Start scheduler service"""
    if not ENHANCED_SERVICES_AVAILABLE:
        return {"success": False, "error": "Scheduler service not available"}
    
    # Only admin can control scheduler
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    scheduler_service.start()
    return {"success": True, "message": "Scheduler started"}

@app.post("/scheduler/stop")
async def stop_scheduler(current_user: dict = Depends(get_current_user)):
    """Stop scheduler service"""
    if not ENHANCED_SERVICES_AVAILABLE:
        return {"success": False, "error": "Scheduler service not available"}
    
    # Only admin can control scheduler
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    scheduler_service.stop()
    return {"success": True, "message": "Scheduler stopped"}

# Original API endpoints (with authentication)
@app.get("/stocks/all")
async def get_all_stocks(current_user: dict = Depends(get_current_user)):
    """Get all stocks"""
    return api_handler.get_stocks(shariah_only=False, include_prices=True)

@app.get("/stocks/shariah")
async def get_shariah_stocks(current_user: dict = Depends(get_current_user)):
    """Get Shariah compliant stocks"""
    return api_handler.get_shariah_stocks(include_prices=True)

@app.post("/stocks/refresh")
async def refresh_stock_prices(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Refresh stock prices"""
    background_tasks.add_task(update_prices_and_check_signals)
    return {"success": True, "message": "Price refresh started"}

async def update_prices_and_check_signals():
    """Background task to update prices and check signal targets"""
    try:
        # Refresh stock prices
        result = api_handler.refresh_stock_prices()
        
        if ENHANCED_SERVICES_AVAILABLE and result.get('success'):
            # Update signal prices and check targets
            active_signals = signal_manager.get_active_signals()
            if active_signals['success']:
                symbols = [s['symbol'] for s in active_signals['signals']]
                
                if symbols:
                    current_prices = await signal_manager.fetch_current_prices(symbols)
                    update_result = signal_manager.update_signal_prices(current_prices)
                    
                    # Broadcast target hits and stop losses
                    for target_hit in update_result.get('target_hits', []):
                        await notification_service.notify_target_hit(target_hit, 
                            target_hit['current_price'], target_hit['profit_percent'])
                        await manager.broadcast_target_hit(target_hit)
                    
                    for stop_loss in update_result.get('stop_losses', []):
                        await notification_service.notify_stop_loss_hit(stop_loss,
                            stop_loss['current_price'], stop_loss['loss_percent'])
                        await manager.broadcast_stop_loss(stop_loss)
        
    except Exception as e:
        logger.error(f"Error in price update task: {e}")

# WebSocket endpoint (Enhanced)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal_message(json.dumps({
            "type": "connection",
            "message": "Connected to EmergentTrader Enhanced WebSocket",
            "timestamp": datetime.now().isoformat()
        }), websocket)
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "heartbeat":
                    await manager.send_personal_message(json.dumps({
                        "type": "heartbeat_response",
                        "timestamp": datetime.now().isoformat()
                    }), websocket)
                
                elif message.get("type") == "subscribe":
                    # Handle subscription to specific data feeds
                    await manager.send_personal_message(json.dumps({
                        "type": "subscription_confirmed",
                        "data": message.get("data"),
                        "timestamp": datetime.now().isoformat()
                    }), websocket)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket message error: {e}")
                break
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)

# WebSocket status endpoint
@app.get("/websocket/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "websocket_enabled": True,
        "active_connections": len(manager.active_connections),
        "user_connections": len(manager.user_connections)
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
