#!/usr/bin/env python3
"""
Telegram Notification Service for EmergentTrader
Sends automated trading signal notifications via Telegram bot
"""

import os
import json
import logging
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.channel_id = os.getenv("TELEGRAM_CHANNEL_ID")  # Optional: for broadcasting
        
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not set. Telegram notifications disabled.")
            self.enabled = False
        elif not self.chat_id:
            logger.warning("TELEGRAM_CHAT_ID not set. Telegram notifications disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Telegram service initialized successfully")
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Emoji mappings for different scan types
        self.scan_emojis = {
            "morning": "🌅",
            "afternoon": "☀️", 
            "evening": "🌆"
        }
        
        # Strategy emojis
        self.strategy_emojis = {
            "multibagger": "🚀",
            "momentum": "📈",
            "breakout": "💥",
            "swing_trading": "🔄",
            "mean_reversion": "↩️",
            "value_investing": "💎",
            "sector_rotation": "🔄",
            "low_volatility": "🛡️",
            "fundamental_growth": "📊"
        }
    
    async def send_signal_notification(self, scan_data: Dict) -> bool:
        """Send signal notification to Telegram"""
        if not self.enabled:
            logger.warning("Telegram service not enabled")
            return False
        
        try:
            # Create message content
            message = self.create_signal_message(scan_data)
            
            # Send to personal chat
            personal_sent = await self.send_message(self.chat_id, message)
            
            # Send to channel if configured
            channel_sent = True
            if self.channel_id:
                channel_sent = await self.send_message(self.channel_id, message)
            
            return personal_sent and channel_sent
            
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False
    
    def create_signal_message(self, scan_data: Dict) -> str:
        """Create formatted message for Telegram"""
        run_type = scan_data.get("run_type", "morning")
        run_name = scan_data.get("run_name", "Market Scan")
        signals = scan_data.get("signals", [])
        signal_count = scan_data.get("signal_count", len(signals))
        
        # Get appropriate emoji
        scan_emoji = self.scan_emojis.get(run_type, "📊")
        
        # Create header
        message = f"{scan_emoji} *{run_name}*\n"
        message += f"📅 {datetime.now().strftime('%d %b %Y, %H:%M IST')}\n"
        message += f"📈 *{signal_count} Trading Signals Generated*\n\n"
        
        if not signals:
            message += "❌ No signals generated in this scan.\n"
            message += "Market conditions may not be favorable.\n\n"
            return message
        
        # Add top signals (limit to 5 for readability)
        message += "🔥 *Top Signals:*\n"
        
        for i, signal in enumerate(signals[:5], 1):
            symbol = signal.get("symbol", "N/A")
            strategy = signal.get("strategy", "unknown")
            confidence = signal.get("confidence", 0)
            entry_price = signal.get("entry_price", 0)
            target_price = signal.get("target_price", 0)
            
            # Get strategy emoji
            strategy_emoji = self.strategy_emojis.get(strategy, "📊")
            
            # Calculate potential return
            potential_return = 0
            if entry_price and target_price:
                potential_return = ((target_price - entry_price) / entry_price) * 100
            
            message += f"\n{i}. {strategy_emoji} *{symbol}*\n"
            message += f"   📋 Strategy: {strategy.replace('_', ' ').title()}\n"
            message += f"   🎯 Confidence: {confidence:.1%}\n"
            message += f"   💰 Entry: ₹{entry_price:.2f}\n"
            message += f"   🎯 Target: ₹{target_price:.2f}\n"
            
            if potential_return > 0:
                message += f"   📈 Potential: +{potential_return:.1f}%\n"
        
        # Add summary if more signals exist
        if len(signals) > 5:
            remaining = len(signals) - 5
            message += f"\n➕ *{remaining} more signals available*\n"
        
        # Add performance metrics if available
        if scan_data.get("strategies_used"):
            strategies = scan_data["strategies_used"]
            message += f"\n🔍 *Strategies Used:*\n"
            for strategy in strategies:
                emoji = self.strategy_emojis.get(strategy, "📊")
                message += f"   {emoji} {strategy.replace('_', ' ').title()}\n"
        
        # Add footer with links
        message += f"\n🌐 [View Dashboard](https://emergenttrader.onrender.com/signals)\n"
        message += f"📊 [API Status](https://emergenttrader-backend.onrender.com/health)\n"
        
        # Add disclaimer
        message += f"\n⚠️ *Disclaimer:* These are algorithmic signals for educational purposes. Please do your own research before trading.\n"
        
        return message
    
    async def send_error_notification(self, error_data: Dict) -> bool:
        """Send error notification to Telegram"""
        if not self.enabled:
            return False
        
        try:
            run_type = error_data.get("run_type", "unknown")
            error_message = error_data.get("error", "Unknown error")
            timestamp = error_data.get("timestamp", datetime.now().isoformat())
            
            message = f"🚨 *EmergentTrader Alert*\n\n"
            message += f"❌ *Error in {run_type.title()} Scan*\n"
            message += f"⏰ Time: {timestamp}\n\n"
            message += f"📝 *Error Details:*\n"
            message += f"```\n{error_message}\n```\n\n"
            message += f"🔧 Please check the application logs for more details.\n"
            message += f"📊 [Check Status](https://emergenttrader-backend.onrender.com/health)"
            
            return await self.send_message(self.chat_id, message)
            
        except Exception as e:
            logger.error(f"Error sending Telegram error notification: {e}")
            return False
    
    async def send_daily_summary(self, summary_data: Dict) -> bool:
        """Send daily summary notification"""
        if not self.enabled:
            return False
        
        try:
            total_signals = summary_data.get("total_signals", 0)
            successful_scans = summary_data.get("successful_scans", 0)
            failed_scans = summary_data.get("failed_scans", 0)
            top_performers = summary_data.get("top_performers", [])
            
            message = f"📊 *Daily Trading Summary*\n"
            message += f"📅 {datetime.now().strftime('%d %b %Y')}\n\n"
            
            message += f"📈 *Scan Results:*\n"
            message += f"   ✅ Successful: {successful_scans}\n"
            message += f"   ❌ Failed: {failed_scans}\n"
            message += f"   📊 Total Signals: {total_signals}\n\n"
            
            if top_performers:
                message += f"🏆 *Top Performing Signals:*\n"
                for performer in top_performers[:3]:
                    symbol = performer.get("symbol", "N/A")
                    returns = performer.get("returns", 0)
                    status_emoji = "🟢" if returns > 0 else "🔴"
                    message += f"   {status_emoji} {symbol}: {returns:+.1f}%\n"
            
            message += f"\n🌐 [View Full Report](https://emergenttrader.onrender.com/analytics)"
            
            return await self.send_message(self.chat_id, message)
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
            return False
    
    async def send_message(self, chat_id: str, message: str, parse_mode: str = "Markdown") -> bool:
        """Send message to Telegram chat"""
        try:
            url = f"{self.base_url}/sendMessage"
            
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("ok"):
                            logger.info(f"Telegram message sent successfully to {chat_id}")
                            return True
                        else:
                            logger.error(f"Telegram API error: {result.get('description')}")
                            return False
                    else:
                        logger.error(f"HTTP error {response.status} sending Telegram message")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    async def send_signal_update(self, signal_data: Dict) -> bool:
        """Send individual signal update"""
        if not self.enabled:
            return False
        
        try:
            symbol = signal_data.get("symbol", "N/A")
            status = signal_data.get("status", "unknown")
            returns = signal_data.get("returns", 0)
            current_price = signal_data.get("current_price", 0)
            
            # Status emojis
            status_emojis = {
                "target_hit": "🎯",
                "stop_loss_hit": "🛑", 
                "active": "⏳",
                "expired": "⏰"
            }
            
            status_emoji = status_emojis.get(status, "📊")
            returns_emoji = "🟢" if returns > 0 else "🔴" if returns < 0 else "⚪"
            
            message = f"{status_emoji} *Signal Update*\n\n"
            message += f"📊 *{symbol}*\n"
            message += f"📈 Status: {status.replace('_', ' ').title()}\n"
            message += f"{returns_emoji} Returns: {returns:+.1f}%\n"
            message += f"💰 Current Price: ₹{current_price:.2f}\n"
            message += f"⏰ Updated: {datetime.now().strftime('%H:%M IST')}\n"
            
            return await self.send_message(self.chat_id, message)
            
        except Exception as e:
            logger.error(f"Error sending signal update: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        if not self.enabled:
            return False
        
        try:
            url = f"{self.base_url}/getMe"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("ok"):
                            bot_info = result.get("result", {})
                            logger.info(f"Telegram bot connected: {bot_info.get('username')}")
                            return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error testing Telegram connection: {e}")
            return False
    
    def get_bot_setup_instructions(self) -> str:
        """Get instructions for setting up Telegram bot"""
        instructions = """
🤖 Telegram Bot Setup Instructions:

1. Create a Telegram Bot:
   - Message @BotFather on Telegram
   - Send /newbot command
   - Choose a name and username for your bot
   - Copy the bot token

2. Get Your Chat ID:
   - Start a chat with your bot
   - Send any message to the bot
   - Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   - Find your chat ID in the response

3. Set Environment Variables:
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   TELEGRAM_CHANNEL_ID=channel_id_here (optional)

4. Test the connection:
   - The bot will send a test message when first initialized
   - Check your Telegram for the test message

5. Optional - Create a Channel:
   - Create a Telegram channel for broadcasting signals
   - Add your bot as an admin
   - Get the channel ID and set TELEGRAM_CHANNEL_ID
        """
        return instructions

# Singleton instance
telegram_service = TelegramService()

async def send_scan_notification(scan_data: Dict) -> bool:
    """Convenience function to send scan notification"""
    return await telegram_service.send_signal_notification(scan_data)

async def send_error_alert(error_data: Dict) -> bool:
    """Convenience function to send error alert"""
    return await telegram_service.send_error_notification(error_data)

async def send_signal_update_notification(signal_data: Dict) -> bool:
    """Convenience function to send signal update"""
    return await telegram_service.send_signal_update(signal_data)

# Test function
async def test_telegram_service():
    """Test the Telegram service"""
    if not telegram_service.enabled:
        print("❌ Telegram service not enabled. Check environment variables.")
        print(telegram_service.get_bot_setup_instructions())
        return False
    
    # Test connection
    if await telegram_service.test_connection():
        print("✅ Telegram bot connection successful")
        
        # Send test message
        test_data = {
            "run_type": "test",
            "run_name": "Test Notification",
            "signal_count": 2,
            "signals": [
                {
                    "symbol": "RELIANCE",
                    "strategy": "multibagger",
                    "confidence": 0.85,
                    "entry_price": 2500.00,
                    "target_price": 2750.00
                },
                {
                    "symbol": "TCS",
                    "strategy": "momentum", 
                    "confidence": 0.78,
                    "entry_price": 3200.00,
                    "target_price": 3500.00
                }
            ]
        }
        
        if await telegram_service.send_signal_notification(test_data):
            print("✅ Test notification sent successfully")
            return True
        else:
            print("❌ Failed to send test notification")
            return False
    else:
        print("❌ Telegram bot connection failed")
        return False

if __name__ == "__main__":
    asyncio.run(test_telegram_service())
