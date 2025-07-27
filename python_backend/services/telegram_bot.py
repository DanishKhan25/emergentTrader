"""
Telegram Bot Service for EmergentTrader
Handles notifications and trading commands via Telegram
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api_handler import EmergentTraderAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmergentTraderBot:
    def __init__(self):
        """Initialize the Telegram bot"""
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            return
            
        self.application = Application.builder().token(self.token).build()
        self.api_handler = EmergentTraderAPI()
        
        # Setup handlers
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup command and callback handlers"""
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("signals", self.signals_command))
        self.application.add_handler(CommandHandler("strategies", self.strategies_command))
        self.application.add_handler(CommandHandler("performance", self.performance_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("backtest", self.backtest_command))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🚀 *Welcome to EmergentTrader Bot!*

I'm your AI-powered trading assistant with:
• 10 Advanced Trading Strategies
• ML-Enhanced Signals (87% success rate)
• Shariah Compliance Filter
• Real-time Notifications

*Available Commands:*
/signals - Get latest trading signals
/strategies - View available strategies  
/performance - Check system performance
/status - System health status
/backtest - Run strategy backtest
/help - Show this help message

Let's start making profitable trades! 📈
        """
        
        await update.message.reply_text(
            welcome_message, 
            parse_mode='Markdown'
        )
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
🤖 *EmergentTrader Bot Commands*

*Signal Commands:*
/signals - Get today's signals
/signals multibagger - Get multibagger signals
/signals momentum - Get momentum signals

*Strategy Commands:*
/strategies - List all strategies
/performance - Overall performance
/backtest <strategy> - Run backtest

*System Commands:*
/status - System health
/help - This help message

*Quick Actions:*
Use the inline buttons for faster access!
        """
        
        await update.message.reply_text(
            help_message,
            parse_mode='Markdown'
        )
        
    async def signals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /signals command"""
        try:
            # Get strategy from command args
            strategy = 'multibagger'  # default
            if context.args:
                strategy = context.args[0].lower()
            
            # Generate signals
            result = self.api_handler.generate_signals(
                strategy=strategy,
                shariah_only=True,
                min_confidence=0.7
            )
            
            if result.get('success'):
                signals = result.get('signals', [])
                
                if not signals:
                    await update.message.reply_text(
                        f"🔍 No {strategy} signals found today.\nTry a different strategy or lower confidence threshold."
                    )
                    return
                
                # Format signals message
                message = f"📊 *{strategy.upper()} SIGNALS* ({len(signals)} found)\n\n"
                
                for i, signal in enumerate(signals[:5], 1):  # Show top 5
                    symbol = signal.get('symbol', 'N/A')
                    entry_price = signal.get('entry_price', 0)
                    target_price = signal.get('target_price', 0)
                    stop_loss = signal.get('stop_loss', 0)
                    confidence = signal.get('confidence_score', 0)
                    
                    returns_potential = ((target_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
                    
                    message += f"""
{i}. *{symbol}*
   💰 Entry: ₹{entry_price:.2f}
   🎯 Target: ₹{target_price:.2f} (+{returns_potential:.1f}%)
   🛡️ Stop Loss: ₹{stop_loss:.2f}
   📈 Confidence: {confidence:.1%}
"""
                
                # Add inline keyboard for actions
                keyboard = [
                    [
                        InlineKeyboardButton("📊 More Signals", callback_data=f"more_signals_{strategy}"),
                        InlineKeyboardButton("📈 Performance", callback_data="performance")
                    ],
                    [
                        InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_signals_{strategy}"),
                        InlineKeyboardButton("⚙️ Strategies", callback_data="strategies")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
            else:
                await update.message.reply_text(
                    f"❌ Error generating signals: {result.get('error', 'Unknown error')}"
                )
                
        except Exception as e:
            logger.error(f"Error in signals command: {str(e)}")
            await update.message.reply_text(
                f"❌ Error: {str(e)}"
            )
            
    async def strategies_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /strategies command"""
        try:
            result = self.api_handler.get_available_strategies()
            
            if result.get('success'):
                strategies = result.get('strategies', [])
                
                message = "🎯 *Available Trading Strategies*\n\n"
                
                for strategy in strategies:
                    name = strategy.get('name', 'Unknown')
                    description = strategy.get('description', 'No description')
                    success_rate = strategy.get('success_rate', 'N/A')
                    
                    message += f"• *{name.upper()}*\n  {description}\n  Success Rate: {success_rate}\n\n"
                
                # Add inline keyboard
                keyboard = [
                    [
                        InlineKeyboardButton("🚀 Multibagger", callback_data="signals_multibagger"),
                        InlineKeyboardButton("⚡ Momentum", callback_data="signals_momentum")
                    ],
                    [
                        InlineKeyboardButton("🔄 Swing", callback_data="signals_swing"),
                        InlineKeyboardButton("💎 Value", callback_data="signals_value_investing")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
            else:
                await update.message.reply_text(
                    f"❌ Error getting strategies: {result.get('error', 'Unknown error')}"
                )
                
        except Exception as e:
            logger.error(f"Error in strategies command: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            
    async def performance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /performance command"""
        try:
            result = self.api_handler.get_performance_summary()
            
            if result.get('success'):
                perf = result.get('performance', {})
                
                message = f"""
📈 *SYSTEM PERFORMANCE*

🎯 *Overall Stats:*
• Total Signals: {perf.get('total_signals', 0)}
• Success Rate: {perf.get('success_rate', 0):.1%}
• Avg Return: {perf.get('avg_return', 0):.1f}%
• Best Return: {perf.get('best_return', 0):.1f}%

🚀 *Multibagger Performance:*
• 2x+ Returns: {perf.get('multibagger_2x', 0)} signals
• 5x+ Returns: {perf.get('multibagger_5x', 0)} signals
• 10x+ Returns: {perf.get('multibagger_10x', 0)} signals

📊 *Recent Activity:*
• Today's Signals: {perf.get('today_signals', 0)}
• Active Signals: {perf.get('active_signals', 0)}
• This Week: {perf.get('week_signals', 0)}
                """
                
                await update.message.reply_text(message, parse_mode='Markdown')
                
            else:
                await update.message.reply_text(
                    f"❌ Error getting performance: {result.get('error', 'Unknown error')}"
                )
                
        except Exception as e:
            logger.error(f"Error in performance command: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            result = self.api_handler.get_api_health()
            
            if result.get('success'):
                status = result.get('status', {})
                
                message = f"""
🔧 *SYSTEM STATUS*

🟢 *API Health:* {status.get('api_status', 'Unknown')}
🟢 *Database:* {status.get('database_status', 'Unknown')}
🟢 *Signal Engine:* {status.get('signal_engine_status', 'Unknown')}

📊 *System Info:*
• Uptime: {status.get('uptime', 'Unknown')}
• Last Update: {status.get('last_update', 'Unknown')}
• Version: {status.get('version', '1.1.0')}

🎯 *Active Features:*
• ML-Enhanced Signals ✅
• Shariah Compliance ✅
• Real-time Monitoring ✅
• Telegram Notifications ✅
                """
                
                await update.message.reply_text(message, parse_mode='Markdown')
                
            else:
                await update.message.reply_text(
                    f"❌ System Status Error: {result.get('error', 'Unknown error')}"
                )
                
        except Exception as e:
            logger.error(f"Error in status command: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            
    async def backtest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /backtest command"""
        try:
            strategy = 'multibagger'
            if context.args:
                strategy = context.args[0].lower()
            
            await update.message.reply_text(
                f"🔄 Running {strategy} backtest... This may take a few minutes."
            )
            
            result = self.api_handler.run_backtest(
                strategy=strategy,
                start_date="2019-01-01",
                end_date="2025-01-27"
            )
            
            if result.get('success'):
                backtest = result.get('results', {})
                
                message = f"""
📊 *{strategy.upper()} BACKTEST RESULTS*

🎯 *Performance:*
• Total Return: {backtest.get('total_return', 0):.1f}%
• Success Rate: {backtest.get('success_rate', 0):.1%}
• Avg Return: {backtest.get('avg_return', 0):.1f}%
• Max Drawdown: {backtest.get('max_drawdown', 0):.1f}%

📈 *Trade Stats:*
• Total Trades: {backtest.get('total_trades', 0)}
• Winning Trades: {backtest.get('winning_trades', 0)}
• Losing Trades: {backtest.get('losing_trades', 0)}

🚀 *Multibagger Stats:*
• 2x Returns: {backtest.get('multibagger_2x', 0)}
• 5x Returns: {backtest.get('multibagger_5x', 0)}
• 10x+ Returns: {backtest.get('multibagger_10x', 0)}
                """
                
                await update.message.reply_text(message, parse_mode='Markdown')
                
            else:
                await update.message.reply_text(
                    f"❌ Backtest Error: {result.get('error', 'Unknown error')}"
                )
                
        except Exception as e:
            logger.error(f"Error in backtest command: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith('signals_'):
            strategy = data.replace('signals_', '')
            # Simulate signals command
            context.args = [strategy]
            await self.signals_command(update, context)
            
        elif data == 'performance':
            await self.performance_command(update, context)
            
        elif data == 'strategies':
            await self.strategies_command(update, context)
            
        elif data.startswith('refresh_signals_'):
            strategy = data.replace('refresh_signals_', '')
            await query.edit_message_text("🔄 Refreshing signals...")
            context.args = [strategy]
            await self.signals_command(update, context)
            
    async def send_notification(self, message: str, parse_mode: str = 'Markdown'):
        """Send notification to configured chat"""
        try:
            if self.chat_id:
                await self.application.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=parse_mode
                )
                logger.info("Notification sent successfully")
            else:
                logger.warning("No chat ID configured for notifications")
                
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            
    async def send_signal_alert(self, signal: Dict):
        """Send trading signal alert"""
        try:
            symbol = signal.get('symbol', 'N/A')
            strategy = signal.get('strategy', 'Unknown')
            entry_price = signal.get('entry_price', 0)
            target_price = signal.get('target_price', 0)
            stop_loss = signal.get('stop_loss', 0)
            confidence = signal.get('confidence_score', 0)
            
            returns_potential = ((target_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
            
            message = f"""
🚨 *NEW TRADING SIGNAL*

📊 *{symbol}* ({strategy.upper()})
💰 Entry: ₹{entry_price:.2f}
🎯 Target: ₹{target_price:.2f} (+{returns_potential:.1f}%)
🛡️ Stop Loss: ₹{stop_loss:.2f}
📈 Confidence: {confidence:.1%}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#TradingSignal #{strategy.upper()} #{symbol}
            """
            
            await self.send_notification(message)
            
        except Exception as e:
            logger.error(f"Error sending signal alert: {str(e)}")
            
    def run(self):
        """Run the Telegram bot"""
        if not self.token:
            logger.error("Cannot start bot - no token provided")
            return
            
        logger.info("Starting EmergentTrader Telegram Bot...")
        self.application.run_polling()

if __name__ == "__main__":
    bot = EmergentTraderBot()
    bot.run()
