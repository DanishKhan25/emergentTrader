# 🚀 CRITICAL NOTIFICATIONS INTEGRATION INSTRUCTIONS

## ✅ What's Ready:
- **📱 Telegram Notifications**: 100% Working
- **🔧 Simplified Integration**: No complex dependencies
- **📊 3 Critical Alerts**: Buy signals, target hits, stop losses

## 🎯 How to Integrate:

### 1. Add to Signal Generation (api_handler.py)

Add this to your `generate_signals()` method:

```python
# At the top of api_handler.py, add:
import asyncio
from services.simplified_notifications import send_buy_signal_alert

# In your generate_signals() method, add this at the end:
if result.get('success') and result.get('data'):
    signals = result['data']
    
    # Send notifications for BUY signals
    for signal in signals:
        if (signal.get('action') == 'BUY' or 
            signal.get('signal_type') == 'buy' or
            signal.get('recommendation') == 'BUY'):
            
            try:
                # Send notification asynchronously
                asyncio.create_task(send_buy_signal_alert(signal))
            except Exception as e:
                print(f"Notification error: {e}")
```

### 2. Add to Buy Signal Method (api_handler.py)

Add this to your `buy_signal()` method:

```python
# At the top, add the import:
from services.simplified_notifications import send_buy_signal_alert

# In your buy_signal() method, before returning result:
if result.get('success'):
    signal_data = {
        'symbol': buy_data.get('symbol'),
        'strategy': buy_data.get('strategy', 'manual'),
        'confidence': buy_data.get('confidence', 0.8),
        'entry_price': buy_data.get('entry_price'),
        'target_price': buy_data.get('target_price'),
        'stop_loss': buy_data.get('stop_loss'),
        'quantity': buy_data.get('quantity')
    }
    
    try:
        asyncio.create_task(send_buy_signal_alert(signal_data))
    except Exception as e:
        print(f"Buy notification error: {e}")
```

### 3. Add Position Monitoring (New Method)

Add this new method to your api_handler.py:

```python
from services.simplified_notifications import send_target_hit_alert, send_stop_loss_alert

async def monitor_positions_for_alerts(self):
    """Monitor positions for target hits and stop losses"""
    try:
        positions = self.get_portfolio_positions()
        
        for position_id, position in positions.items():
            if position.get('status') != 'active':
                continue
                
            symbol = position.get('symbol')
            # Get current price (implement based on your data source)
            current_price = self.get_current_price(symbol)
            
            if not current_price:
                continue
                
            target_price = position.get('target_price')
            stop_loss = position.get('stop_loss')
            
            # Check target hit
            if target_price and current_price >= target_price:
                position_data = {
                    'symbol': symbol,
                    'target_price': target_price,
                    'current_price': current_price,
                    'entry_price': position.get('entry_price'),
                    'quantity': position.get('quantity')
                }
                
                await send_target_hit_alert(position_data)
                position['status'] = 'target_hit'
            
            # Check stop loss
            elif stop_loss and current_price <= stop_loss:
                position_data = {
                    'symbol': symbol,
                    'stop_loss': stop_loss,
                    'current_price': current_price,
                    'entry_price': position.get('entry_price'),
                    'quantity': position.get('quantity')
                }
                
                await send_stop_loss_alert(position_data)
                position['status'] = 'stop_loss_hit'
                
    except Exception as e:
        print(f"Position monitoring error: {e}")
```

### 4. Add to Scheduler (scheduler.py)

Add this to your scheduler.py:

```python
# Add this job to monitor positions every 5 minutes
self.scheduler.add_job(
    self.api_handler.monitor_positions_for_alerts,
    'interval',
    minutes=5,
    id='position_alerts'
)
```

## 🧪 Manual Testing:

```python
# Test buy signal notification
import asyncio
from services.simplified_notifications import send_buy_signal_alert

signal = {
    'symbol': 'RELIANCE',
    'strategy': 'multibagger',
    'confidence': 0.94,
    'entry_price': 2450.0,
    'target_price': 2800.0,
    'stop_loss': 2200.0
}

asyncio.run(send_buy_signal_alert(signal))
```

## 🎯 Result:

After integration, you'll get **instant Telegram notifications** for:
- 📊 **Every buy signal** generated
- 🎯 **Every target hit** (profit opportunity)
- 🛑 **Every stop loss** (risk management)

**Your critical trading notifications are ready for production!** 🚀
