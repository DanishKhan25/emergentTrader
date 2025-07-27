"""
INTEGRATION GUIDE: Critical Trading Notifications
How to add buy signal, target hit, and stop loss notifications to your existing system
"""

# ============================================================================
# 1. INTEGRATION WITH SIGNAL GENERATION
# ============================================================================

"""
Add this to your existing api_handler.py in the generate_signals() method:
"""

# In api_handler.py - generate_signals() method
async def generate_signals_with_notifications(self, strategy='momentum', symbols=None):
    """Enhanced signal generation with automatic notifications"""
    
    # Your existing signal generation code
    result = self.generate_signals(strategy, symbols)
    
    if result.get('success') and result.get('data'):
        signals = result['data']
        
        # Import the critical notifications
        from services.critical_notifications import send_buy_signal_alert
        
        # Send notification for each BUY signal
        for signal in signals:
            if signal.get('action') == 'BUY' or signal.get('signal_type') == 'buy':
                try:
                    # Send critical notification
                    notification_result = await send_buy_signal_alert(signal)
                    
                    if notification_result.get('success'):
                        print(f"✅ Buy signal notification sent for {signal.get('symbol')}")
                    else:
                        print(f"❌ Notification failed for {signal.get('symbol')}")
                        
                except Exception as e:
                    print(f"Notification error: {e}")
    
    return result

# ============================================================================
# 2. INTEGRATION WITH PRICE MONITORING
# ============================================================================

"""
Add this to your existing system for target/stop loss monitoring:
"""

async def monitor_positions_with_notifications(self):
    """Enhanced position monitoring with target/stop loss notifications"""
    
    from services.critical_notifications import send_target_hit_alert, send_stop_loss_alert
    
    # Get all active positions
    positions = self.get_portfolio_positions()
    
    for position_id, position in positions.items():
        if position.get('status') != 'active':
            continue
            
        symbol = position.get('symbol')
        current_price = self.get_current_price(symbol)  # Your existing price fetching
        target_price = position.get('target_price')
        stop_loss = position.get('stop_loss')
        
        # Check for target hit
        if current_price and target_price and current_price >= target_price:
            try:
                # Send target hit notification
                await send_target_hit_alert({
                    'symbol': symbol,
                    'target_price': target_price,
                    'current_price': current_price,
                    'entry_price': position.get('entry_price'),
                    'quantity': position.get('quantity'),
                    'position_id': position_id
                })
                
                # Update position status
                position['status'] = 'target_hit'
                print(f"🎯 Target hit notification sent for {symbol}")
                
            except Exception as e:
                print(f"Target hit notification error: {e}")
        
        # Check for stop loss hit
        elif current_price and stop_loss and current_price <= stop_loss:
            try:
                # Send stop loss notification
                await send_stop_loss_alert({
                    'symbol': symbol,
                    'stop_loss': stop_loss,
                    'current_price': current_price,
                    'entry_price': position.get('entry_price'),
                    'quantity': position.get('quantity'),
                    'position_id': position_id
                })
                
                # Update position status
                position['status'] = 'stop_loss_hit'
                print(f"🛑 Stop loss notification sent for {symbol}")
                
            except Exception as e:
                print(f"Stop loss notification error: {e}")

# ============================================================================
# 3. INTEGRATION WITH BUY_SIGNAL METHOD
# ============================================================================

"""
Enhance your existing buy_signal() method:
"""

async def buy_signal_with_notification(self, signal_id: str, buy_data: Dict) -> Dict:
    """Enhanced buy signal execution with notification"""
    
    # Your existing buy_signal logic
    result = self.buy_signal(signal_id, buy_data)
    
    if result.get('success'):
        # Extract signal data for notification
        signal_data = {
            'symbol': buy_data.get('symbol'),
            'strategy': buy_data.get('strategy', 'manual'),
            'confidence': buy_data.get('confidence', 0.8),
            'entry_price': buy_data.get('entry_price'),
            'target_price': buy_data.get('target_price'),
            'stop_loss': buy_data.get('stop_loss'),
            'quantity': buy_data.get('quantity')
        }
        
        # Send buy signal notification
        from services.critical_notifications import send_buy_signal_alert
        
        try:
            notification_result = await send_buy_signal_alert(signal_data)
            result['notification_sent'] = notification_result.get('success', False)
        except Exception as e:
            print(f"Buy signal notification error: {e}")
            result['notification_sent'] = False
    
    return result

# ============================================================================
# 4. SCHEDULED PRICE MONITORING
# ============================================================================

"""
Add this to your scheduler.py for continuous monitoring:
"""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class EnhancedScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.api_handler = EmergentTraderAPI()
    
    def start_monitoring(self):
        """Start continuous price monitoring"""
        
        # Monitor positions every 5 minutes during market hours
        self.scheduler.add_job(
            self.monitor_positions_with_notifications,
            'interval',
            minutes=5,
            id='position_monitoring'
        )
        
        # Generate morning signals with notifications
        self.scheduler.add_job(
            self.generate_morning_signals_with_notifications,
            'cron',
            hour=9,
            minute=15,
            id='morning_signals'
        )
        
        self.scheduler.start()
        print("📊 Enhanced monitoring started with notifications!")
    
    async def monitor_positions_with_notifications(self):
        """Wrapper for position monitoring"""
        await monitor_positions_with_notifications(self.api_handler)
    
    async def generate_morning_signals_with_notifications(self):
        """Generate morning signals with notifications"""
        strategies = ['multibagger', 'momentum', 'swing']
        
        for strategy in strategies:
            await self.api_handler.generate_signals_with_notifications(strategy)

# ============================================================================
# 5. TESTING YOUR NOTIFICATIONS
# ============================================================================

"""
Test script to verify all notifications work:
"""

async def test_critical_notifications():
    """Test all 3 critical notifications"""
    
    from services.critical_notifications import CriticalNotifications
    
    notifier = CriticalNotifications()
    
    print("🧪 Testing critical notifications...")
    
    # Test all notifications
    test_result = await notifier.test_all_notifications()
    
    if test_result.get('success'):
        print("✅ All notification tests completed!")
        
        tests = test_result.get('tests', {})
        
        # Check buy signal test
        if tests.get('buy_signal', {}).get('success'):
            print("   📊 Buy signal notification: ✅")
        else:
            print("   📊 Buy signal notification: ❌")
        
        # Check target hit test
        if tests.get('target_hit', {}).get('success'):
            print("   🎯 Target hit notification: ✅")
        else:
            print("   🎯 Target hit notification: ❌")
        
        # Check stop loss test
        if tests.get('stop_loss_hit', {}).get('success'):
            print("   🛑 Stop loss notification: ✅")
        else:
            print("   🛑 Stop loss notification: ❌")
    else:
        print(f"❌ Test failed: {test_result.get('error')}")

# ============================================================================
# 6. QUICK SETUP COMMANDS
# ============================================================================

"""
Run these commands to set up critical notifications:
"""

# 1. Test your environment setup
# python3 -c "
# import os
# print('Email configured:', bool(os.getenv('EMAIL_USER')))
# print('Telegram configured:', bool(os.getenv('TELEGRAM_CHAT_ID')))
# "

# 2. Test critical notifications
# python3 -c "
# import asyncio
# from integration_guide import test_critical_notifications
# asyncio.run(test_critical_notifications())
# "

# 3. Start enhanced monitoring
# python3 -c "
# from integration_guide import EnhancedScheduler
# scheduler = EnhancedScheduler()
# scheduler.start_monitoring()
# "

# ============================================================================
# 7. MANUAL TRIGGER EXAMPLES
# ============================================================================

"""
Manual ways to trigger notifications for testing:
"""

# Trigger buy signal notification
async def manual_buy_signal_test():
    from services.critical_notifications import send_buy_signal_alert
    
    test_signal = {
        'symbol': 'RELIANCE',
        'strategy': 'multibagger',
        'confidence': 0.94,
        'entry_price': 2450.0,
        'target_price': 2800.0,
        'stop_loss': 2200.0
    }
    
    result = await send_buy_signal_alert(test_signal)
    print(f"Buy signal notification result: {result}")

# Trigger target hit notification
async def manual_target_hit_test():
    from services.critical_notifications import send_target_hit_alert
    
    test_position = {
        'symbol': 'TCS',
        'target_price': 4000.0,
        'current_price': 4000.0,
        'entry_price': 3500.0,
        'quantity': 100
    }
    
    result = await send_target_hit_alert(test_position)
    print(f"Target hit notification result: {result}")

# Trigger stop loss notification
async def manual_stop_loss_test():
    from services.critical_notifications import send_stop_loss_alert
    
    test_position = {
        'symbol': 'HDFCBANK',
        'stop_loss': 1400.0,
        'current_price': 1400.0,
        'entry_price': 1600.0,
        'quantity': 50
    }
    
    result = await send_stop_loss_alert(test_position)
    print(f"Stop loss notification result: {result}")

print("""
🎯 CRITICAL NOTIFICATIONS INTEGRATION COMPLETE!

Your system will now send notifications for:
1. 📊 Every BUY signal generated
2. 🎯 Every target price hit
3. 🛑 Every stop loss triggered

Next steps:
1. Test notifications: python3 integration_guide.py
2. Integrate with your existing methods
3. Start continuous monitoring
4. Enjoy real-time trading alerts!
""")
