"""
Telegram Command Bot for EmergentTrader
Handles health checks and manual signal generation via Telegram commands
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests
import json
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api_handler import EmergentTraderAPI
from services.enhanced_notification_service import notification_service
from services.signal_management_service import signal_manager

logger = logging.getLogger(__name__)

class TelegramCommandBot:
    def __init__(self):
        """Initialize Telegram command bot"""
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.api = EmergentTraderAPI()
        
        # Command handlers
        self.commands = {
            '/health': self.handle_health_check,
            '/generate': self.handle_generate_signals,
            '/status': self.handle_status,
            '/stats': self.handle_statistics,
            '/help': self.handle_help,
            '/clear': self.handle_clear_signals
        }
        
        logger.info("Telegram Command Bot initialized")
    
    async def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send message via Telegram"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    async def handle_health_check(self, message_text: str) -> str:
        """Handle /health command"""
        try:
            # Check API health
            api_health = self.api.get_health_status()
            
            # Check signal manager
            signal_stats = signal_manager.get_signal_statistics()
            
            # Check scheduler status
            try:
                from services.scheduler_service import scheduler_service
                scheduler_status = scheduler_service.get_status()
            except:
                scheduler_status = {'running': False}
            
            # Get system info
            active_signals = signal_manager.get_active_signals()
            
            health_msg = f"""🏥 <b>SYSTEM HEALTH CHECK</b>

🔧 <b>Services Status:</b>
• API: {'✅ Healthy' if api_health.get('success') else '❌ Error'}
• Signal Manager: {'✅ Active' if signal_stats.get('success') else '❌ Error'}
• Scheduler: {'✅ Running' if scheduler_status.get('running') else '❌ Stopped'}
• Notifications: ✅ Active

📊 <b>Current Stats:</b>
• Active Signals: {active_signals.get('count', 0)}
• Total Signals: {signal_stats.get('overall', {}).get('total_signals', 0)}
• Success Rate: {signal_stats.get('overall', {}).get('success_rate', 0):.1f}%

⏰ <b>Time:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<i>System is operational! 🚀</i>"""
            
            return health_msg
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return f"❌ <b>Health Check Failed</b>\n\nError: {str(e)}"
    
    async def handle_generate_signals(self, message_text: str) -> str:
        """Handle /generate command"""
        try:
            # Clear old signals first
            clear_result = signal_manager.clear_all_signals()
            
            # Generate new signals
            result = self.api.generate_signals(force_refresh=True)
            
            if result.get('success'):
                signals = result.get('data', {}).get('signals', [])
                
                # Add signals to tracking
                for signal in signals:
                    signal_manager.add_signal(signal)
                    # Send individual signal notification
                    await notification_service.notify_signal_generated(signal)
                
                return f"""🎯 <b>SIGNAL GENERATION COMPLETE</b>

✅ <b>Results:</b>
• Cleared: {clear_result.get('count_cleared', 0)} old signals
• Generated: {len(signals)} new signals

📈 <b>New Signals:</b>
{self._format_signals_summary(signals[:5])}

⏰ <b>Generated at:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<i>Check your dashboard for full details! 📊</i>"""
            
            else:
                error_msg = result.get('error', 'Unknown error')
                return f"❌ <b>Signal Generation Failed</b>\n\nError: {error_msg}"
                
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return f"❌ <b>Signal Generation Error</b>\n\nError: {str(e)}"
    
    async def handle_status(self, message_text: str) -> str:
        """Handle /status command"""
        try:
            stats = signal_manager.get_signal_statistics()
            active_signals = signal_manager.get_active_signals()
            
            if not stats.get('success'):
                return "❌ Could not retrieve status"
            
            overall = stats.get('overall', {})
            
            status_msg = f"""📊 <b>CURRENT STATUS</b>

📈 <b>Signal Overview:</b>
• Total Signals: {overall.get('total_signals', 0)}
• Active Signals: {overall.get('active_signals', 0)}
• Target Hits: {overall.get('target_hits', 0)}
• Stop Losses: {overall.get('stop_losses', 0)}

🎯 <b>Performance:</b>
• Success Rate: {overall.get('success_rate', 0):.1f}%
• Avg Profit: +{overall.get('avg_profit_percent', 0):.2f}%
• Avg Loss: {overall.get('avg_loss_percent', 0):.2f}%
• Total P&L: ₹{overall.get('total_pnl', 0):.2f}

⏰ <b>Updated:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""
            
            return status_msg
            
        except Exception as e:
            logger.error(f"Status error: {e}")
            return f"❌ <b>Status Error</b>\n\nError: {str(e)}"
    
    async def handle_statistics(self, message_text: str) -> str:
        """Handle /stats command"""
        try:
            stats = signal_manager.get_signal_statistics()
            
            if not stats.get('success'):
                return "❌ Could not retrieve statistics"
            
            overall = stats.get('overall', {})
            by_strategy = stats.get('by_strategy', [])
            
            stats_msg = f"""📈 <b>DETAILED STATISTICS</b>

🎯 <b>Overall Performance:</b>
• Total Signals: {overall.get('total_signals', 0)}
• Success Rate: {overall.get('success_rate', 0):.1f}%
• Target Hits: {overall.get('target_hits', 0)}
• Stop Losses: {overall.get('stop_losses', 0)}
• Total P&L: ₹{overall.get('total_pnl', 0):.2f}

📊 <b>By Strategy:</b>"""
            
            for strategy in by_strategy[:5]:  # Top 5 strategies
                stats_msg += f"""
• <b>{strategy['strategy'].title()}:</b>
  - Signals: {strategy['total']}
  - Success: {strategy['success_rate']:.1f}%
  - Avg Profit: +{strategy['avg_profit_percent']:.2f}%"""
            
            stats_msg += f"\n\n⏰ <b>Generated:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            
            return stats_msg
            
        except Exception as e:
            logger.error(f"Statistics error: {e}")
            return f"❌ <b>Statistics Error</b>\n\nError: {str(e)}"
    
    async def handle_clear_signals(self, message_text: str) -> str:
        """Handle /clear command"""
        try:
            result = signal_manager.clear_all_signals()
            
            if result.get('success'):
                return f"""🧹 <b>SIGNALS CLEARED</b>

✅ Cleared {result.get('count_cleared', 0)} signals from database

⏰ <b>Time:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<i>Ready for fresh signals! 🚀</i>"""
            else:
                return f"❌ <b>Clear Failed</b>\n\nError: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Clear signals error: {e}")
            return f"❌ <b>Clear Error</b>\n\nError: {str(e)}"
    
    async def handle_help(self, message_text: str) -> str:
        """Handle /help command"""
        return """🤖 <b>EMERGENTTRADER BOT COMMANDS</b>

📋 <b>Available Commands:</b>

🏥 <b>/health</b> - System health check
🎯 <b>/generate</b> - Generate new signals
📊 <b>/status</b> - Current status overview
📈 <b>/stats</b> - Detailed statistics
🧹 <b>/clear</b> - Clear all signals
❓ <b>/help</b> - Show this help message

💡 <b>Usage:</b>
Just send any command to get instant updates about your trading system!

🚀 <i>Happy Trading!</i>"""
    
    def _format_signals_summary(self, signals: List[Dict]) -> str:
        """Format signals for summary display"""
        if not signals:
            return "No signals generated"
        
        summary = ""
        for signal in signals:
            symbol = signal.get('symbol', 'N/A')
            strategy = signal.get('strategy', 'Unknown')
            confidence = signal.get('confidence', 0)
            entry_price = signal.get('entry_price', 0)
            target_price = signal.get('target_price', 0)
            
            potential_return = 0
            if entry_price and target_price:
                potential_return = ((target_price - entry_price) / entry_price) * 100
            
            summary += f"• {symbol} ({strategy}) - {confidence:.0%} confidence, +{potential_return:.1f}% potential\n"
        
        if len(signals) > 5:
            summary += f"... and {len(signals) - 5} more signals"
        
        return summary
    
    async def get_updates(self, offset: int = 0) -> List[Dict]:
        """Get updates from Telegram"""
        if not self.bot_token:
            return []
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {'offset': offset, 'timeout': 10}
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('result', [])
            
        except Exception as e:
            logger.error(f"Error getting Telegram updates: {e}")
        
        return []
    
    async def process_message(self, message: Dict) -> bool:
        """Process incoming Telegram message"""
        try:
            text = message.get('text', '').strip()
            chat_id = str(message.get('chat', {}).get('id', ''))
            
            # Only respond to configured chat
            if chat_id != self.chat_id:
                return False
            
            # Check if it's a command
            if text.startswith('/'):
                command = text.split()[0].lower()
                
                if command in self.commands:
                    response = await self.commands[command](text)
                    await self.send_message(response)
                    return True
                else:
                    await self.send_message("❓ Unknown command. Send /help for available commands.")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    async def start_polling(self):
        """Start polling for Telegram messages"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram bot not configured, skipping polling")
            return
        
        logger.info("Starting Telegram bot polling...")
        offset = 0
        
        # Send startup message
        await self.send_message(
            "🤖 <b>EmergentTrader Bot Started</b>\n\n"
            "Send /help for available commands\n"
            f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )
        
        while True:
            try:
                updates = await self.get_updates(offset)
                
                for update in updates:
                    offset = update.get('update_id', 0) + 1
                    
                    if 'message' in update:
                        await self.process_message(update['message'])
                
                await asyncio.sleep(1)  # Small delay between polls
                
            except Exception as e:
                logger.error(f"Polling error: {e}")
                await asyncio.sleep(5)  # Wait longer on error

# Global instance
telegram_bot = TelegramCommandBot()
