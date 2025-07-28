"""
Scheduler Service for EmergentTrader
Handles automated tasks like signal generation, ML training, and data updates
"""

import asyncio
import schedule
import logging
from datetime import datetime, time
from typing import Dict, List, Callable
import threading
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.enhanced_notification_service import notification_service
from services.signal_management_service import signal_manager
from services.telegram_command_bot import telegram_bot
from api_handler import EmergentTraderAPI

# Import new services
try:
    from core.signal_generator_with_notifications import signal_generator_with_notifications
    from services.ml_training_service import ml_training_service
    from services.strategy_validation_service import strategy_validation_service
    ENHANCED_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced services not available: {e}")
    ENHANCED_SERVICES_AVAILABLE = False

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        """Initialize scheduler service"""
        self.api = EmergentTraderAPI()
        self.running = False
        self.scheduler_thread = None
        self.telegram_thread = None
        
        # Market hours (IST)
        self.market_open = time(9, 15)  # 9:15 AM
        self.market_close = time(15, 30)  # 3:30 PM
        
        logger.info("Scheduler Service initialized")
    
    def is_market_hours(self) -> bool:
        """Check if current time is within market hours"""
        now = datetime.now().time()
        return self.market_open <= now <= self.market_close
    
    def is_weekday(self) -> bool:
        """Check if today is a weekday (Monday-Friday)"""
        return datetime.now().weekday() < 5
    
    async def generate_signals_task(self):
        """Generate trading signals with notifications"""
        try:
            logger.info("🎯 Starting scheduled signal generation task...")
            
            if ENHANCED_SERVICES_AVAILABLE:
                # Use enhanced signal generator with notifications
                result = await signal_generator_with_notifications.generate_and_notify_signals(
                    strategy="multibagger",
                    shariah_only=True,
                    min_confidence=0.6,
                    force_refresh=True
                )
            else:
                # Fallback to basic signal generation
                result = self.api.generate_signals(force_refresh=True)
                
                if result.get('success'):
                    signals = result.get('data', {}).get('signals', [])
                    
                    # Send basic notification
                    await notification_service.send_telegram_message(
                        f"🎯 <b>Signals Generated</b>\n\n"
                        f"Generated {len(signals)} new signals\n"
                        f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                    )
            
            if result.get('success'):
                logger.info(f"✅ Signal generation completed successfully")
            else:
                logger.error(f"❌ Signal generation failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error in signal generation task: {e}")
            await notification_service.send_telegram_message(
                f"🚨 <b>Signal Generation Error</b>\n\n"
                f"Error: {str(e)}\n"
                f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
    
    async def update_stock_data_task(self):
        """Update stock data and check signal targets"""
        try:
            logger.info("📈 Starting stock data update task...")
            
            # Update NSE stock list
            result = self.api.refresh_stock_prices()
            
            if result.get('success'):
                updated_count = result.get('updated_count', 0)
                logger.info(f"✅ Updated {updated_count} stock prices")
                
                if ENHANCED_SERVICES_AVAILABLE:
                    # Check signal targets and send notifications
                    check_result = await signal_generator_with_notifications.check_and_notify_targets()
                    
                    if check_result.get('success'):
                        target_hits = check_result.get('target_hits', 0)
                        stop_losses = check_result.get('stop_losses', 0)
                        
                        if target_hits > 0 or stop_losses > 0:
                            logger.info(f"🎯 Target monitoring: {target_hits} hits, {stop_losses} stop losses")
                
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"❌ Stock data update failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error in stock data update task: {e}")
    
    async def train_ml_models_task(self):
        """Train ML models after market hours"""
        try:
            logger.info("🤖 Starting ML model training task...")
            
            if ENHANCED_SERVICES_AVAILABLE:
                # Use enhanced ML training service
                result = await ml_training_service.daily_training_task()
                
                if result.get('success'):
                    logger.info("✅ ML model training completed successfully")
                else:
                    logger.error(f"❌ ML training failed: {result.get('error')}")
            else:
                # Fallback notification
                await notification_service.send_telegram_message(
                    f"🤖 <b>ML Training Scheduled</b>\n\n"
                    f"Enhanced ML training service not available\n"
                    f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                )
                
        except Exception as e:
            logger.error(f"Error in ML training task: {e}")
    
    async def validate_strategies_task(self):
        """Validate trading strategies"""
        try:
            logger.info("🔍 Starting strategy validation task...")
            
            if ENHANCED_SERVICES_AVAILABLE:
                # Use strategy validation service
                result = await strategy_validation_service.validate_all_strategies()
                
                if result.get('success'):
                    logger.info("✅ Strategy validation completed successfully")
                else:
                    logger.error(f"❌ Strategy validation failed: {result.get('error')}")
            else:
                # Basic validation notification
                stats = signal_manager.get_signal_statistics()
                
                if stats.get('success'):
                    overall = stats.get('overall', {})
                    success_rate = overall.get('success_rate', 0)
                    
                    await notification_service.send_telegram_message(
                        f"🔍 <b>Strategy Check</b>\n\n"
                        f"Overall Success Rate: {success_rate:.1f}%\n"
                        f"Total Signals: {overall.get('total_signals', 0)}\n"
                        f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                    )
                
        except Exception as e:
            logger.error(f"Error in strategy validation task: {e}")
    
    async def daily_summary_task(self):
        """Send daily summary"""
        try:
            logger.info("📊 Generating daily summary...")
            
            # Get signal statistics
            stats = signal_manager.get_signal_statistics()
            
            if stats['success']:
                overall = stats['overall']
                
                summary_msg = f"""📊 <b>DAILY TRADING SUMMARY</b>

📈 <b>Signal Performance:</b>
• Total Signals: {overall['total_signals']}
• Active Signals: {overall['active_signals']}
• Targets Hit: {overall['target_hits']}
• Stop Losses: {overall['stop_losses']}

🎯 <b>Success Metrics:</b>
• Success Rate: {overall['success_rate']:.1f}%
• Avg Profit: +{overall['avg_profit_percent']:.2f}%
• Avg Loss: {overall['avg_loss_percent']:.2f}%
• Total P&L: ₹{overall['total_pnl']:.2f}

📅 <b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}

<i>Keep trading smart! 📈</i>"""
                
                await notification_service.send_telegram_message(summary_msg)
                
        except Exception as e:
            logger.error(f"Error in daily summary task: {e}")
    
    async def health_check_task(self):
        """Perform system health check"""
        try:
            # Check API health
            health = self.api.get_health_status()
            
            if not health.get('success'):
                await notification_service.send_telegram_message(
                    f"⚠️ <b>System Health Alert</b>\n\n"
                    f"API health check failed\n"
                    f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                )
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
    
    def setup_schedules(self):
        """Setup all scheduled tasks"""
        logger.info("Setting up scheduled tasks...")
        
        # Signal generation - 3 times a day during market hours
        schedule.every().day.at("09:30").do(self.run_conditional_task, 
                                          self.generate_signals_task, 
                                          condition=self.is_weekday)  # Market open
        schedule.every().day.at("12:30").do(self.run_conditional_task, 
                                          self.generate_signals_task, 
                                          condition=self.is_weekday)  # Mid-day
        schedule.every().day.at("15:00").do(self.run_conditional_task, 
                                          self.generate_signals_task, 
                                          condition=self.is_weekday)  # Before close
        
        # Stock data updates - Every 30 minutes during market hours
        schedule.every(30).minutes.do(self.run_conditional_task, 
                                    self.update_stock_data_task, 
                                    condition=lambda: self.is_market_hours() and self.is_weekday())
        
        # ML model training - After market hours (6 PM)
        schedule.every().day.at("18:00").do(self.run_conditional_task,
                                          self.train_ml_models_task,
                                          condition=self.is_weekday)
        
        # Strategy validation - Weekly on Sunday at 10 AM
        schedule.every().sunday.at("10:00").do(self.run_async_task, self.validate_strategies_task)
        
        # Daily summary - End of day (7 PM)
        schedule.every().day.at("19:00").do(self.run_conditional_task,
                                          self.daily_summary_task,
                                          condition=self.is_weekday)
        
        # Health check - Every 2 hours
        schedule.every(2).hours.do(self.run_async_task, self.health_check_task)
        
        logger.info("✅ All scheduled tasks configured")
    
    def run_async_task(self, task_func):
        """Run async task in sync context"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(task_func())
            loop.close()
        except Exception as e:
            logger.error(f"Error running async task: {e}")
    
    def run_conditional_task(self, task_func, condition):
        """Run task only if condition is met"""
        if condition():
            self.run_async_task(task_func)
        else:
            logger.debug(f"Skipping task {task_func.__name__} - condition not met")
    
    def start_telegram_bot(self):
        """Start Telegram bot in separate thread"""
        if not telegram_bot.bot_token or not telegram_bot.chat_id:
            logger.warning("Telegram bot not configured, skipping bot startup")
            return
        
        def run_telegram_bot():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(telegram_bot.start_polling())
            except Exception as e:
                logger.error(f"Telegram bot error: {e}")
        
        self.telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        self.telegram_thread.start()
        logger.info("✅ Telegram bot started")
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.setup_schedules()
        self.running = True
        
        # Start Telegram bot
        self.start_telegram_bot()
        
        def run_scheduler():
            logger.info("🚀 Scheduler started")
            while self.running:
                schedule.run_pending()
                asyncio.sleep(1)
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("✅ Scheduler service started successfully")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        logger.info("🛑 Scheduler stopped")
    
    def get_status(self) -> Dict:
        """Get scheduler status"""
        return {
            'running': self.running,
            'scheduled_jobs': len(schedule.jobs),
            'next_run': str(schedule.next_run()) if schedule.jobs else None,
            'market_hours': self.is_market_hours(),
            'is_weekday': self.is_weekday(),
            'telegram_bot_active': telegram_bot.bot_token and telegram_bot.chat_id,
            'enhanced_services': ENHANCED_SERVICES_AVAILABLE
        }

# Global instance
scheduler_service = SchedulerService()
