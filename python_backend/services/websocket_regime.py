"""
WebSocket Service for Real-time Market Regime Updates
Provides live market regime updates to frontend clients
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from services.logging_service import get_logger
from services.market_regime_realtime import get_realtime_regime_filter
from services.realtime_market_data import get_market_data_service

logger = get_logger('websocket')

class MarketRegimeWebSocketManager:
    def __init__(self):
        self.logger = get_logger('websocket')
        self.active_connections: Set[WebSocket] = set()
        self.regime_filter = get_realtime_regime_filter()
        self.market_data_service = get_market_data_service()
        
        # Update intervals
        self.regime_update_interval = 300  # 5 minutes for regime updates
        self.market_data_interval = 60     # 1 minute for market data
        self.intraday_interval = 30        # 30 seconds for intraday updates
        
        # Background tasks
        self.regime_task = None
        self.market_data_task = None
        self.intraday_task = None
        
        # Last update tracking
        self.last_regime_update = None
        self.last_market_data = None
        self.last_regime_data = None
        
        # Update flags
        self.is_running = False
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        try:
            await websocket.accept()
            self.active_connections.add(websocket)
            self.logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
            
            # Send initial data
            await self._send_initial_data(websocket)
            
            # Start background tasks if not running
            if not self.is_running:
                await self._start_background_tasks()
            
        except Exception as e:
            self.logger.error(f"Error connecting WebSocket: {e}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        try:
            self.active_connections.discard(websocket)
            self.logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
            
            # Stop background tasks if no connections
            if not self.active_connections and self.is_running:
                await self._stop_background_tasks()
                
        except Exception as e:
            self.logger.error(f"Error disconnecting WebSocket: {e}")
    
    async def _send_initial_data(self, websocket: WebSocket):
        """Send initial market regime data to new connection"""
        try:
            # Get current regime
            regime_result = await self.regime_filter.detect_market_regime(use_cache=True)
            
            # Get market status
            market_data_result = await self.market_data_service.get_live_market_data(period_days=1)
            market_status = {}
            if market_data_result.get('success'):
                market_status = market_data_result['data'].get('market_status', {})
            
            initial_data = {
                'type': 'initial_data',
                'regime': regime_result if regime_result.get('success') else None,
                'market_status': market_status,
                'timestamp': datetime.now().isoformat(),
                'connection_id': id(websocket)
            }
            
            await websocket.send_text(json.dumps(initial_data))
            self.logger.debug("Initial data sent to new WebSocket connection")
            
        except Exception as e:
            self.logger.error(f"Error sending initial data: {e}")
    
    async def _start_background_tasks(self):
        """Start background tasks for real-time updates"""
        try:
            self.is_running = True
            self.logger.info("Starting WebSocket background tasks")
            
            # Start regime update task
            self.regime_task = asyncio.create_task(self._regime_update_loop())
            
            # Start market data task
            self.market_data_task = asyncio.create_task(self._market_data_loop())
            
            # Start intraday task (only during market hours)
            self.intraday_task = asyncio.create_task(self._intraday_update_loop())
            
        except Exception as e:
            self.logger.error(f"Error starting background tasks: {e}")
    
    async def _stop_background_tasks(self):
        """Stop background tasks"""
        try:
            self.is_running = False
            self.logger.info("Stopping WebSocket background tasks")
            
            # Cancel tasks
            if self.regime_task:
                self.regime_task.cancel()
            if self.market_data_task:
                self.market_data_task.cancel()
            if self.intraday_task:
                self.intraday_task.cancel()
                
        except Exception as e:
            self.logger.error(f"Error stopping background tasks: {e}")
    
    async def _regime_update_loop(self):
        """Background loop for regime updates"""
        while self.is_running:
            try:
                # Get updated regime
                regime_result = await self.regime_filter.detect_market_regime(use_cache=False)
                
                if regime_result.get('success'):
                    # Check if regime has changed
                    current_regime = regime_result.get('regime')
                    current_confidence = regime_result.get('confidence')
                    
                    should_update = False
                    
                    if self.last_regime_data is None:
                        should_update = True
                    else:
                        last_regime = self.last_regime_data.get('regime')
                        last_confidence = self.last_regime_data.get('confidence', 0)
                        
                        # Update if regime changed or confidence changed significantly
                        if (current_regime != last_regime or 
                            abs(current_confidence - last_confidence) > 0.05):
                            should_update = True
                    
                    if should_update:
                        self.last_regime_data = regime_result
                        
                        update_data = {
                            'type': 'regime_update',
                            'regime': regime_result,
                            'timestamp': datetime.now().isoformat(),
                            'update_reason': 'regime_change' if current_regime != self.last_regime_data.get('regime') else 'confidence_change'
                        }
                        
                        await self._broadcast_to_all(update_data)
                        self.logger.info(f"Regime update broadcasted: {current_regime} ({current_confidence:.1%})")
                
                # Wait for next update
                await asyncio.sleep(self.regime_update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in regime update loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _market_data_loop(self):
        """Background loop for market data updates"""
        while self.is_running:
            try:
                # Get market status and basic data
                market_data_result = await self.market_data_service.get_live_market_data(period_days=1)
                
                if market_data_result.get('success'):
                    market_data = market_data_result['data']
                    current_snapshot = market_data.get('current_snapshot', {})
                    market_status = market_data.get('market_status', {})
                    
                    # Check if significant market data change
                    should_update = False
                    
                    if self.last_market_data is None:
                        should_update = True
                    else:
                        # Check for significant price changes in major indices
                        for index_name, current_data in current_snapshot.items():
                            last_data = self.last_market_data.get('current_snapshot', {}).get(index_name, {})
                            
                            current_change = abs(current_data.get('change_pct', 0))
                            last_change = abs(last_data.get('change_pct', 0))
                            
                            # Update if change is significant (>0.5% difference)
                            if abs(current_change - last_change) > 0.5:
                                should_update = True
                                break
                    
                    if should_update:
                        self.last_market_data = market_data
                        
                        update_data = {
                            'type': 'market_data_update',
                            'current_snapshot': current_snapshot,
                            'market_status': market_status,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        await self._broadcast_to_all(update_data)
                        self.logger.debug("Market data update broadcasted")
                
                # Wait for next update
                await asyncio.sleep(self.market_data_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in market data loop: {e}")
                await asyncio.sleep(60)
    
    async def _intraday_update_loop(self):
        """Background loop for intraday updates (during market hours)"""
        while self.is_running:
            try:
                # Check if market is open
                market_data_result = await self.market_data_service.get_live_market_data(period_days=1)
                
                if market_data_result.get('success'):
                    market_status = market_data_result['data'].get('market_status', {})
                    is_market_open = market_status.get('is_open', False)
                    
                    if is_market_open:
                        # Get intraday data
                        intraday_result = await self.market_data_service.get_intraday_data()
                        
                        if intraday_result.get('success'):
                            intraday_data = intraday_result['data']
                            
                            # Get regime with intraday updates
                            regime_result = await self.regime_filter.get_regime_with_intraday_update()
                            
                            if regime_result.get('success'):
                                update_data = {
                                    'type': 'intraday_update',
                                    'regime': regime_result,
                                    'intraday_data': {
                                        'current_price': intraday_data['prices'][-1] if intraday_data['prices'] else None,
                                        'intraday_change': ((intraday_data['prices'][-1] - intraday_data['prices'][0]) / intraday_data['prices'][0] * 100) if len(intraday_data['prices']) > 1 else 0,
                                        'last_update': intraday_data.get('last_updated')
                                    },
                                    'timestamp': datetime.now().isoformat()
                                }
                                
                                await self._broadcast_to_all(update_data)
                                self.logger.debug("Intraday update broadcasted")
                
                # Wait for next update (shorter interval during market hours)
                await asyncio.sleep(self.intraday_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in intraday update loop: {e}")
                await asyncio.sleep(60)
    
    async def _broadcast_to_all(self, data: Dict):
        """Broadcast data to all connected clients"""
        if not self.active_connections:
            return
        
        message = json.dumps(data)
        disconnected = set()
        
        for websocket in self.active_connections.copy():
            try:
                await websocket.send_text(message)
            except WebSocketDisconnect:
                disconnected.add(websocket)
            except Exception as e:
                self.logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            self.active_connections.discard(websocket)
        
        if disconnected:
            self.logger.info(f"Removed {len(disconnected)} disconnected WebSocket connections")
    
    async def send_custom_update(self, update_type: str, data: Dict):
        """Send custom update to all connected clients"""
        try:
            update_data = {
                'type': update_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            await self._broadcast_to_all(update_data)
            self.logger.info(f"Custom update broadcasted: {update_type}")
            
        except Exception as e:
            self.logger.error(f"Error sending custom update: {e}")
    
    def get_connection_stats(self) -> Dict:
        """Get WebSocket connection statistics"""
        return {
            'active_connections': len(self.active_connections),
            'is_running': self.is_running,
            'last_regime_update': self.last_regime_update.isoformat() if self.last_regime_update else None,
            'tasks_running': {
                'regime_task': self.regime_task is not None and not self.regime_task.done(),
                'market_data_task': self.market_data_task is not None and not self.market_data_task.done(),
                'intraday_task': self.intraday_task is not None and not self.intraday_task.done()
            }
        }

# Global WebSocket manager instance
_websocket_manager = None

def get_websocket_manager() -> MarketRegimeWebSocketManager:
    """Get global WebSocket manager instance"""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = MarketRegimeWebSocketManager()
    return _websocket_manager

# WebSocket endpoint for main.py:
"""
Add this WebSocket endpoint to your main.py:

@app.websocket("/ws/market-regime")
async def websocket_market_regime(websocket: WebSocket):
    manager = get_websocket_manager()
    await manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            
            # Handle client requests
            try:
                message = json.loads(data)
                message_type = message.get('type')
                
                if message_type == 'ping':
                    await websocket.send_text(json.dumps({
                        'type': 'pong',
                        'timestamp': datetime.now().isoformat()
                    }))
                elif message_type == 'request_update':
                    # Force immediate regime update
                    regime_result = await get_realtime_regime_filter().detect_market_regime(use_cache=False)
                    await websocket.send_text(json.dumps({
                        'type': 'requested_update',
                        'regime': regime_result,
                        'timestamp': datetime.now().isoformat()
                    }))
                    
            except json.JSONDecodeError:
                # Ignore invalid JSON
                pass
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)

# Also add this endpoint for WebSocket stats:
@app.get("/ws/market-regime/stats")
async def get_websocket_stats():
    manager = get_websocket_manager()
    return {
        'success': True,
        'data': manager.get_connection_stats()
    }
"""

print("""
🔄 WEBSOCKET SERVICE FOR REAL-TIME MARKET REGIME READY!

Features:
✅ Real-time regime updates every 5 minutes
✅ Market data updates every 1 minute
✅ Intraday updates every 30 seconds (during market hours)
✅ Automatic connection management
✅ Background task management
✅ Error handling and reconnection support
✅ Custom update broadcasting
✅ Connection statistics

WebSocket Endpoint: /ws/market-regime

Client Message Types:
- ping: Keep connection alive
- request_update: Force immediate regime update

Server Message Types:
- initial_data: Initial regime and market data
- regime_update: Regime change notifications
- market_data_update: Market data changes
- intraday_update: Real-time intraday updates
- pong: Response to ping

Add the WebSocket endpoint to your main.py to enable real-time updates!
""")
