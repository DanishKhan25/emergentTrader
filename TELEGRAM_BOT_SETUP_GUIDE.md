# 🤖 Telegram Bot Setup Guide for EmergentTrader

## 📋 Overview

Your EmergentTrader now includes **Telegram notifications** for all 3 daily scans! You'll receive instant notifications with trading signals, updates, and alerts directly in Telegram.

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Your Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather
3. **Send command**: `/newbot`
4. **Choose a name**: `EmergentTrader Bot` (or any name you like)
5. **Choose a username**: `emergenttrader_yourname_bot` (must end with 'bot')
6. **Copy the bot token** - you'll need this!

Example:
```
BotFather: Congratulations! You have just created a new bot.
Token: 123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

### Step 2: Get Your Chat ID

1. **Start a chat** with your new bot
2. **Send any message** to the bot (like "Hello")
3. **Open this URL** in your browser (replace YOUR_BOT_TOKEN):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. **Find your chat ID** in the response:
   ```json
   {
     "result": [{
       "message": {
         "chat": {
           "id": 123456789,  // This is your CHAT_ID
           "type": "private"
         }
       }
     }]
   }
   ```

### Step 3: Set Environment Variables in Render

Add these to your Render services:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_CHAT_ID=123456789
TELEGRAM_CHANNEL_ID=@your_channel  # Optional
```

## 📱 What You'll Receive

### 🌅 Morning Scan (9:00 AM IST)
```
🌅 Morning Market Scan
📅 03 Aug 2025, 09:00 IST
📈 5 Trading Signals Generated

🔥 Top Signals:

1. 🚀 RELIANCE
   📋 Strategy: Multibagger
   🎯 Confidence: 85.0%
   💰 Entry: ₹2,500.00
   🎯 Target: ₹2,750.00
   📈 Potential: +10.0%

2. 📈 TCS
   📋 Strategy: Momentum
   🎯 Confidence: 78.0%
   💰 Entry: ₹3,200.00
   🎯 Target: ₹3,500.00
   📈 Potential: +9.4%

🔍 Strategies Used:
   🚀 Multibagger
   📈 Momentum
   💥 Breakout

🌐 View Dashboard
📊 API Status

⚠️ Disclaimer: These are algorithmic signals for educational purposes.
```

### ☀️ Afternoon Scan (2:00 PM IST)
- Swing trading opportunities
- Mean reversion signals
- Value investment picks

### 🌆 Evening Scan (6:00 PM IST)
- Sector rotation analysis
- Low volatility stocks
- Fundamental growth opportunities

### 📊 Signal Updates
```
📊 Signal Update

📊 RELIANCE
📈 Status: Target Hit
🟢 Returns: +12.5%
💰 Current Price: ₹2,812.50
⏰ Updated: 14:30 IST
```

### 🚨 Error Alerts
```
🚨 EmergentTrader Alert

❌ Error in Morning Scan
⏰ Time: 2025-08-03T09:00:00
📝 Error Details: [Error message]
🔧 Please check the application logs
```

## 🔧 Advanced Setup (Optional)

### Create a Telegram Channel for Broadcasting

1. **Create a new channel** in Telegram
2. **Add your bot as admin** to the channel
3. **Get the channel ID**:
   - Forward a message from the channel to `@userinfobot`
   - Copy the channel ID (starts with `-100`)
4. **Set environment variable**:
   ```bash
   TELEGRAM_CHANNEL_ID=-1001234567890
   ```

### Customize Notifications

You can customize the notification settings by modifying the `telegram_service.py` file:

```python
# Disable specific notification types
self.config = {
    "send_scan_start": True,      # Scan starting notifications
    "send_signal_updates": True,  # Individual signal updates
    "send_error_alerts": True,    # Error notifications
    "send_daily_summary": True    # End of day summary
}
```

## 🛠️ Environment Variables Reference

### Required Variables
```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Email Configuration (existing)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
NOTIFICATION_EMAIL=alerts@yourdomain.com
```

### Optional Variables
```bash
# Telegram Channel (for broadcasting)
TELEGRAM_CHANNEL_ID=@your_channel_or_-1001234567890

# Notification Settings
TELEGRAM_SEND_SCAN_START=true
TELEGRAM_SEND_SIGNAL_UPDATES=true
TELEGRAM_SEND_ERROR_ALERTS=true
TELEGRAM_MAX_SIGNALS_PER_MESSAGE=5
```

## 🧪 Testing Your Setup

### Test the Bot Connection

1. **SSH into your Render service** or run locally:
   ```bash
   cd python_backend
   python -c "
   import asyncio
   from services.telegram_service import test_telegram_service
   asyncio.run(test_telegram_service())
   "
   ```

2. **Check for test message** in your Telegram chat

### Manual Test Notification

```bash
# Send a test signal notification
python -c "
import asyncio
from services.telegram_service import send_scan_notification

test_data = {
    'run_type': 'test',
    'run_name': 'Test Notification',
    'signal_count': 1,
    'signals': [{
        'symbol': 'RELIANCE',
        'strategy': 'multibagger',
        'confidence': 0.85,
        'entry_price': 2500.00,
        'target_price': 2750.00
    }]
}

asyncio.run(send_scan_notification(test_data))
"
```

## 📊 Notification Schedule

Your Telegram bot will send notifications:

```
🌅 09:00 AM IST - Morning Scan Results
   ├── Scan start notification
   ├── Signal results (if any)
   └── Error alerts (if issues)

☀️ 02:00 PM IST - Afternoon Scan Results
   ├── Scan start notification
   ├── Signal results (if any)
   └── Signal updates from morning

🌆 06:00 PM IST - Evening Scan Results
   ├── Scan start notification
   ├── Signal results (if any)
   ├── Daily summary
   └── Performance updates

📊 Real-time - Signal Updates
   ├── Target hit notifications
   ├── Stop loss alerts
   └── Significant price movements
```

## 🔒 Security & Privacy

### Bot Security
- Your bot token is private - never share it
- Only you can message your bot (private chat)
- Bot cannot initiate conversations

### Data Privacy
- No personal data is stored by the bot
- Only trading signals and market data are sent
- All communications are encrypted by Telegram

### Best Practices
- Use environment variables for tokens
- Don't commit tokens to version control
- Regularly rotate bot tokens if needed
- Monitor bot usage in BotFather

## 🚨 Troubleshooting

### Bot Not Responding
1. **Check bot token** - ensure it's correct
2. **Verify chat ID** - make sure you got the right ID
3. **Test connection** - use the test script above
4. **Check logs** - look for Telegram service errors

### Messages Not Received
1. **Check if bot is blocked** - unblock in Telegram
2. **Verify environment variables** - ensure they're set in Render
3. **Check internet connectivity** - bot needs internet access
4. **Review Telegram API limits** - check for rate limiting

### Common Errors
```bash
# Invalid bot token
Error: 401 Unauthorized - Bot token is invalid

# Invalid chat ID  
Error: 400 Bad Request - Chat not found

# Rate limiting
Error: 429 Too Many Requests - Slow down API calls
```

## 📞 Support

### Telegram Bot Issues
- Check [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- Contact @BotSupport on Telegram
- Review bot settings with @BotFather

### EmergentTrader Issues
- Check application logs in Render
- Review health check endpoints
- Test individual components

## 🎉 You're All Set!

Once configured, your EmergentTrader will send you:
- ✅ **3 daily scan results** with trading signals
- ✅ **Real-time signal updates** when targets are hit
- ✅ **Error alerts** if anything goes wrong
- ✅ **Performance summaries** at end of day

Your professional trading signal system now includes instant Telegram notifications! 🚀📱

**Next**: Deploy to Render with the updated `render_with_telegram.yaml` configuration!
