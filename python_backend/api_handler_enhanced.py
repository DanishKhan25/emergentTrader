"""
Enhanced API Handler with Integrated Critical Notifications
This file shows the exact changes to add to your existing api_handler.py
"""

# ============================================================================
# 1. ADD THESE IMPORTS TO THE TOP OF YOUR api_handler.py
# ============================================================================

import asyncio
from typing import Dict, List, Optional
import logging
from datetime import datetime

# Add this import for notifications
try:
    from services.critical_notifications import (
        send_buy_signal_alert,
        send_target_hit_alert, 
        send_stop_loss_alert
    )
    NOTIFICATIONS_AVAILABLE = True
    print("✅ Critical notifications imported successfully")
except ImportError as e:
    NOTIFICATIONS_AVAILABLE = False
    print(f"⚠️ Critical notifications not available: {e}")

logger = logging.getLogger(__name__)

# ============================================================================
# 2. ENHANCE YOUR EXISTING generate_signals() METHOD
# ============================================================================

def enhance_generate_signals_method():
    """
    Add this code to your existing generate_signals() method in api_handler.py
    """
    
    # Your existing generate_signals code...
    # Then add this at the end before returning:
    
    async def send_signal_notifications(signals_data):
        """Send notifications for generated signals"""
        if not NOTIFICATIONS_AVAILABLE:
            return
            
        try:
            if signals_data and isinstance(signals_data, list):
                for signal in signals_data:
                    # Only notify for BUY signals
                    if (signal.get('action') == 'BUY' or 
                        signal.get('signal_type') == 'buy' or
                        signal.get('recommendation') == 'BUY'):
                        
                        # Send critical notification
                        notification_result = await send_buy_signal_alert(signal)
                        
                        if notification_result.get('success'):
                            logger.info(f"✅ Buy signal notification sent for {signal.get('symbol')}")
                        else:
                            logger.warning(f"❌ Notification failed for {signal.get('symbol')}")
                            
        except Exception as e:
            logger.error(f"Error sending signal notifications: {e}")
    
    # Add this to your generate_signals method:
    """
    # Your existing signal generation code...
    result = self.signal_engine.generate_signals(...)
    
    # ADD THIS BLOCK:
    if result.get('success') and result.get('data'):
        # Send notifications asynchronously
        try:
            asyncio.create_task(send_signal_notifications(result['data']))
        except Exception as e:
            logger.error(f"Error creating notification task: {e}")
    
    return result
    """

# ============================================================================
# 3. ENHANCE YOUR EXISTING buy_signal() METHOD
# ============================================================================

def enhance_buy_signal_method():
    """
    Add this code to your existing buy_signal() method in api_handler.py
    """
    
    # Your existing buy_signal code...
    # Then add this before returning the result:
    
    async def send_buy_notification(signal_data):
        """Send notification for buy signal execution"""
        if not NOTIFICATIONS_AVAILABLE:
            return
            
        try:
            notification_result = await send_buy_signal_alert(signal_data)
            
            if notification_result.get('success'):
                logger.info(f"✅ Buy execution notification sent for {signal_data.get('symbol')}")
            else:
                logger.warning(f"❌ Buy notification failed for {signal_data.get('symbol')}")
                
        except Exception as e:
            logger.error(f"Error sending buy notification: {e}")
    
    # Add this to your buy_signal method:
    """
    # Your existing buy_signal code...
    result = {'success': True, 'message': 'Position added successfully', ...}
    
    # ADD THIS BLOCK:
    if result.get('success'):
        # Prepare signal data for notification
        signal_data = {
            'symbol': buy_data.get('symbol'),
            'strategy': buy_data.get('strategy', 'manual'),
            'confidence': buy_data.get('confidence', 0.8),
            'entry_price': buy_data.get('entry_price'),
            'target_price': buy_data.get('target_price'),
            'stop_loss': buy_data.get('stop_loss'),
            'quantity': buy_data.get('quantity'),
            'action': 'BUY'
        }
        
        # Send notification asynchronously
        try:
            asyncio.create_task(send_buy_notification(signal_data))
        except Exception as e:
            logger.error(f"Error creating buy notification task: {e}")
    
    return result
    """

# ============================================================================
# 4. ADD NEW POSITION MONITORING METHOD
# ============================================================================

class EnhancedPositionMonitoring:
    """Add this class to your api_handler.py or create as separate method"""
    
    def __init__(self, api_handler):
        self.api_handler = api_handler
        
    async def monitor_positions_for_targets_and_stops(self):
        """Monitor all positions for target hits and stop losses"""
        if not NOTIFICATIONS_AVAILABLE:
            return
            
        try:
            # Get all active positions
            positions = self.api_handler.get_portfolio_positions()
            
            if not positions or not isinstance(positions, dict):
                return
                
            for position_id, position in positions.items():
                if position.get('status') != 'active':
                    continue
                    
                symbol = position.get('symbol')
                if not symbol:
                    continue
                    
                # Get current price (you'll need to implement this)
                current_price = await self.get_current_price(symbol)
                if not current_price:
                    continue
                    
                target_price = position.get('target_price')
                stop_loss = position.get('stop_loss')
                
                # Check for target hit
                if target_price and current_price >= target_price:
                    await self.handle_target_hit(position_id, position, current_price)
                
                # Check for stop loss hit
                elif stop_loss and current_price <= stop_loss:
                    await self.handle_stop_loss_hit(position_id, position, current_price)
                    
        except Exception as e:
            logger.error(f"Error monitoring positions: {e}")
    
    async def handle_target_hit(self, position_id, position, current_price):
        """Handle target price hit"""
        try:
            # Prepare position data for notification
            position_data = {
                'symbol': position.get('symbol'),
                'target_price': position.get('target_price'),
                'current_price': current_price,
                'entry_price': position.get('entry_price'),
                'quantity': position.get('quantity'),
                'position_id': position_id
            }
            
            # Send target hit notification
            notification_result = await send_target_hit_alert(position_data)
            
            if notification_result.get('success'):
                logger.info(f"🎯 Target hit notification sent for {position.get('symbol')}")
                
                # Update position status
                position['status'] = 'target_hit'
                position['target_hit_date'] = datetime.now().isoformat()
                
                # Save updated position (implement based on your storage)
                self.api_handler.update_position(position_id, position)
                
            else:
                logger.warning(f"❌ Target hit notification failed for {position.get('symbol')}")
                
        except Exception as e:
            logger.error(f"Error handling target hit: {e}")
    
    async def handle_stop_loss_hit(self, position_id, position, current_price):
        """Handle stop loss hit"""
        try:
            # Prepare position data for notification
            position_data = {
                'symbol': position.get('symbol'),
                'stop_loss': position.get('stop_loss'),
                'current_price': current_price,
                'entry_price': position.get('entry_price'),
                'quantity': position.get('quantity'),
                'position_id': position_id
            }
            
            # Send stop loss notification
            notification_result = await send_stop_loss_alert(position_data)
            
            if notification_result.get('success'):
                logger.warning(f"🛑 Stop loss notification sent for {position.get('symbol')}")
                
                # Update position status
                position['status'] = 'stop_loss_hit'
                position['stop_loss_hit_date'] = datetime.now().isoformat()
                
                # Save updated position (implement based on your storage)
                self.api_handler.update_position(position_id, position)
                
            else:
                logger.warning(f"❌ Stop loss notification failed for {position.get('symbol')}")
                
        except Exception as e:
            logger.error(f"Error handling stop loss hit: {e}")
    
    async def get_current_price(self, symbol):
        """Get current price for symbol - implement based on your data source"""
        try:
            # This is a placeholder - implement based on your price data source
            # You might use yfinance, your existing price fetching, or market data API
            
            # Example implementation:
            # return self.api_handler.get_live_price(symbol)
            # or
            # return await self.api_handler.fetch_current_price(symbol)
            
            # For now, return None to avoid errors
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None

# ============================================================================
# 5. ADD SCHEDULED MONITORING TO YOUR SCHEDULER
# ============================================================================

def enhance_scheduler_with_monitoring():
    """
    Add this to your existing scheduler.py
    """
    
    # Add this import to your scheduler.py:
    """
    from api_handler_enhanced import EnhancedPositionMonitoring
    """
    
    # Add this method to your scheduler class:
    """
    async def monitor_positions_continuously(self):
        '''Monitor positions every 5 minutes during market hours'''
        try:
            position_monitor = EnhancedPositionMonitoring(self.api_handler)
            await position_monitor.monitor_positions_for_targets_and_stops()
            
        except Exception as e:
            logger.error(f"Error in continuous position monitoring: {e}")
    
    def start_position_monitoring(self):
        '''Start continuous position monitoring'''
        # Add this job to your scheduler
        self.scheduler.add_job(
            self.monitor_positions_continuously,
            'interval',
            minutes=5,  # Check every 5 minutes
            id='position_monitoring_with_notifications'
        )
        
        logger.info("📊 Position monitoring with notifications started")
    """

# ============================================================================
# 6. INTEGRATION TESTING FUNCTIONS
# ============================================================================

async def test_integrated_notifications():
    """Test the integrated notification system"""
    
    print("🧪 Testing integrated notification system...")
    
    # Test 1: Signal generation with notification
    print("\n📊 Testing signal generation with notification...")
    
    test_signal = {
        'symbol': 'RELIANCE',
        'strategy': 'multibagger',
        'confidence': 0.94,
        'entry_price': 2450.0,
        'target_price': 2800.0,
        'stop_loss': 2200.0,
        'action': 'BUY',
        'signal_type': 'buy'
    }
    
    if NOTIFICATIONS_AVAILABLE:
        try:
            result = await send_buy_signal_alert(test_signal)
            if result.get('success'):
                print("✅ Signal notification integration working!")
            else:
                print("❌ Signal notification integration failed")
        except Exception as e:
            print(f"❌ Signal notification error: {e}")
    
    # Test 2: Target hit notification
    print("\n🎯 Testing target hit notification...")
    
    test_position = {
        'symbol': 'TCS',
        'target_price': 4000.0,
        'current_price': 4000.0,
        'entry_price': 3500.0,
        'quantity': 100
    }
    
    if NOTIFICATIONS_AVAILABLE:
        try:
            result = await send_target_hit_alert(test_position)
            if result.get('success'):
                print("✅ Target hit notification integration working!")
            else:
                print("❌ Target hit notification integration failed")
        except Exception as e:
            print(f"❌ Target hit notification error: {e}")
    
    # Test 3: Stop loss notification
    print("\n🛑 Testing stop loss notification...")
    
    test_stop_position = {
        'symbol': 'HDFCBANK',
        'stop_loss': 1400.0,
        'current_price': 1400.0,
        'entry_price': 1600.0,
        'quantity': 50
    }
    
    if NOTIFICATIONS_AVAILABLE:
        try:
            result = await send_stop_loss_alert(test_stop_position)
            if result.get('success'):
                print("✅ Stop loss notification integration working!")
            else:
                print("❌ Stop loss notification integration failed")
        except Exception as e:
            print(f"❌ Stop loss notification error: {e}")
    
    print("\n🎯 Integration testing complete!")

# ============================================================================
# 7. MANUAL TRIGGER FUNCTIONS FOR TESTING
# ============================================================================

async def manually_trigger_buy_signal_notification(symbol, strategy='manual', confidence=0.8):
    """Manually trigger a buy signal notification for testing"""
    
    signal_data = {
        'symbol': symbol,
        'strategy': strategy,
        'confidence': confidence,
        'entry_price': 1000.0,  # Example price
        'target_price': 1200.0,  # Example target
        'stop_loss': 900.0,      # Example stop loss
        'action': 'BUY'
    }
    
    if NOTIFICATIONS_AVAILABLE:
        result = await send_buy_signal_alert(signal_data)
        print(f"Buy signal notification for {symbol}: {'✅ Sent' if result.get('success') else '❌ Failed'}")
        return result
    else:
        print("❌ Notifications not available")
        return {'success': False, 'error': 'Notifications not available'}

async def manually_trigger_target_hit_notification(symbol, profit_amount=10000):
    """Manually trigger a target hit notification for testing"""
    
    position_data = {
        'symbol': symbol,
        'target_price': 1200.0,
        'current_price': 1200.0,
        'entry_price': 1000.0,
        'quantity': 50
    }
    
    if NOTIFICATIONS_AVAILABLE:
        result = await send_target_hit_alert(position_data)
        print(f"Target hit notification for {symbol}: {'✅ Sent' if result.get('success') else '❌ Failed'}")
        return result
    else:
        print("❌ Notifications not available")
        return {'success': False, 'error': 'Notifications not available'}

async def manually_trigger_stop_loss_notification(symbol, loss_amount=5000):
    """Manually trigger a stop loss notification for testing"""
    
    position_data = {
        'symbol': symbol,
        'stop_loss': 900.0,
        'current_price': 900.0,
        'entry_price': 1000.0,
        'quantity': 50
    }
    
    if NOTIFICATIONS_AVAILABLE:
        result = await send_stop_loss_alert(position_data)
        print(f"Stop loss notification for {symbol}: {'✅ Sent' if result.get('success') else '❌ Failed'}")
        return result
    else:
        print("❌ Notifications not available")
        return {'success': False, 'error': 'Notifications not available'}

print("""
🎯 INTEGRATION CODE READY!

To integrate notifications into your existing system:

1. Add the imports to your api_handler.py
2. Enhance your generate_signals() method
3. Enhance your buy_signal() method  
4. Add position monitoring
5. Update your scheduler
6. Test the integration

Your critical trading notifications will then be automatically sent for:
📊 Every buy signal generated
🎯 Every target price hit
🛑 Every stop loss triggered

Both Telegram and Email (once Gmail app password is fixed) notifications!
""")
