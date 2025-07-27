"""
Automated Scheduler for EmergentTrader
Handles periodic tasks like signal generation, monitoring, and notifications
"""

import schedule
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api_handler import EmergentTraderAPI
from services.telegram_bot import EmergentTraderBot
from services.email_service import EmailService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmergentTraderScheduler:
    def __init__(self):
        """Initialize the scheduler with all services"""
        self.api_handler = EmergentTraderAPI()
        self.email_service = EmailService()
        
        # Initialize Telegram bot (optional)
        try:
            self.telegram_bot = EmergentTraderBot()
            self.telegram_enabled = True
        except Exception as e:
            logger.warning(f"Telegram bot not available: {str(e)}")
            self.telegram_bot = None
            self.telegram_enabled = False
        
        self.last_signals = []
        self.monitoring_active = True
        
        logger.info("EmergentTrader Scheduler initialized")
    
    def generate_morning_signals(self):
        """Generate signals every morning at market open"""
        try:
            logger.info("🌅 Generating morning signals...")
            
            # Generate signals for multiple strategies
            strategies = ['multibagger', 'momentum', 'swing', 'breakout']
            all_signals = []
            
            for strategy in strategies:
                result = self.api_handler.generate_signals(
                    strategy=strategy,
                    shariah_only=True,
                    min_confidence=0.7
                )
                
                if result.get('success'):
                    signals = result.get('signals', [])
                    all_signals.extend(signals)
                    logger.info(f"Generated {len(signals)} {strategy} signals")
            
            # Send notifications if new signals found
            if all_signals:
                self.send_signal_notifications(all_signals)
                self.last_signals = all_signals
                logger.info(f"✅ Generated {len(all_signals)} total signals")
            else:
                logger.info("No signals generated this morning")
                
        except Exception as e:
            logger.error(f"Error generating morning signals: {str(e)}")
            self.send_error_notification("Morning Signal Generation Failed", str(e))
    
    def monitor_open_signals(self):
        """Monitor open signals 3 times per day"""
        try:
            logger.info("📊 Monitoring open signals...")
            
            result = self.api_handler.get_active_signals()
            
            if result.get('success'):
                signals = result.get('signals', [])
                
                if signals:
                    # Check for target hits or stop losses
                    alerts = []
                    
                    for signal in signals:
                        symbol = signal.get('symbol')
                        current_price = self.get_current_price(symbol)
                        
                        if current_price:
                            alert = self.check_signal_status(signal, current_price)
                            if alert:
                                alerts.append(alert)
                    
                    # Send alerts if any
                    if alerts:
                        self.send_monitoring_alerts(alerts)
                        logger.info(f"Sent {len(alerts)} monitoring alerts")
                    else:
                        logger.info("All signals within normal range")
                else:
                    logger.info("No active signals to monitor")
            else:
                logger.error(f"Error getting active signals: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error monitoring signals: {str(e)}")
            self.send_error_notification("Signal Monitoring Failed", str(e))
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            import yfinance as yf
            
            # Add .NS suffix for NSE stocks
            ticker = f"{symbol}.NS"
            stock = yf.Ticker(ticker)
            
            # Get current price
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            return current_price
            
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {str(e)}")
            return None
    
    def check_signal_status(self, signal: Dict, current_price: float) -> Dict:
        """Check if signal has hit target or stop loss"""
        try:
            symbol = signal.get('symbol')
            entry_price = signal.get('entry_price', 0)
            target_price = signal.get('target_price', 0)
            stop_loss = signal.get('stop_loss', 0)
            strategy = signal.get('strategy', 'Unknown')
            
            # Check for target hit
            if current_price >= target_price:
                return {
                    'type': 'TARGET_HIT',
                    'symbol': symbol,
                    'strategy': strategy,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'target_price': target_price,
                    'profit_pct': ((current_price - entry_price) / entry_price * 100)
                }
            
            # Check for stop loss hit
            elif current_price <= stop_loss:
                return {
                    'type': 'STOP_LOSS_HIT',
                    'symbol': symbol,
                    'strategy': strategy,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'stop_loss': stop_loss,
                    'loss_pct': ((current_price - entry_price) / entry_price * 100)
                }
            
            # Check for significant moves (>10% up or down)
            elif entry_price > 0:
                move_pct = (current_price - entry_price) / entry_price * 100
                
                if abs(move_pct) > 10:
                    return {
                        'type': 'SIGNIFICANT_MOVE',
                        'symbol': symbol,
                        'strategy': strategy,
                        'entry_price': entry_price,
                        'current_price': current_price,
                        'move_pct': move_pct
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking signal status: {str(e)}")
            return None
    
    def send_signal_notifications(self, signals: List[Dict]):
        """Send notifications for new signals"""
        try:
            # Send email notification
            if self.email_service.enabled:
                performance = self.api_handler.get_performance_summary()
                perf_data = performance.get('performance', {}) if performance.get('success') else {}
                
                self.email_service.send_daily_report(signals, perf_data)
            
            # Send Telegram notifications
            if self.telegram_enabled and self.telegram_bot:
                for signal in signals[:3]:  # Send top 3 signals
                    asyncio.run(self.telegram_bot.send_signal_alert(signal))
            
            logger.info(f"Sent notifications for {len(signals)} signals")
            
        except Exception as e:
            logger.error(f"Error sending signal notifications: {str(e)}")
    
    def send_monitoring_alerts(self, alerts: List[Dict]):
        """Send monitoring alerts"""
        try:
            for alert in alerts:
                alert_type = alert.get('type')
                symbol = alert.get('symbol')
                
                if alert_type == 'TARGET_HIT':
                    message = f"🎯 TARGET HIT: {symbol} reached ₹{alert.get('current_price'):.2f} (+{alert.get('profit_pct'):.1f}%)"
                elif alert_type == 'STOP_LOSS_HIT':
                    message = f"🛡️ STOP LOSS: {symbol} at ₹{alert.get('current_price'):.2f} ({alert.get('loss_pct'):.1f}%)"
                elif alert_type == 'SIGNIFICANT_MOVE':
                    move_pct = alert.get('move_pct')
                    direction = "📈" if move_pct > 0 else "📉"
                    message = f"{direction} SIGNIFICANT MOVE: {symbol} moved {move_pct:.1f}% to ₹{alert.get('current_price'):.2f}"
                
                # Send email alert
                if self.email_service.enabled:
                    self.email_service.send_performance_alert(alert_type, message)
                
                # Send Telegram alert
                if self.telegram_enabled and self.telegram_bot:
                    asyncio.run(self.telegram_bot.send_notification(message))
            
            logger.info(f"Sent {len(alerts)} monitoring alerts")
            
        except Exception as e:
            logger.error(f"Error sending monitoring alerts: {str(e)}")
    
    def send_error_notification(self, error_type: str, error_message: str):
        """Send error notifications"""
        try:
            message = f"❌ EmergentTrader Error: {error_type}\n\nDetails: {error_message}\n\nTime: {datetime.now()}"
            
            # Send email
            if self.email_service.enabled:
                self.email_service.send_performance_alert(error_type, error_message)
            
            # Send Telegram
            if self.telegram_enabled and self.telegram_bot:
                asyncio.run(self.telegram_bot.send_notification(message))
            
            logger.info(f"Sent error notification: {error_type}")
            
        except Exception as e:
            logger.error(f"Error sending error notification: {str(e)}")
    
    def generate_weekly_report(self):
        """Generate weekly performance report"""
        try:
            logger.info("📊 Generating weekly report...")
            
            # Get performance data
            result = self.api_handler.get_performance_summary(period='7d')
            
            if result.get('success'):
                performance = result.get('performance', {})
                
                # Create detailed report
                report = f"""
WEEKLY PERFORMANCE REPORT
========================
Week Ending: {datetime.now().strftime('%Y-%m-%d')}

SIGNAL PERFORMANCE:
- Total Signals: {performance.get('total_signals', 0)}
- Success Rate: {performance.get('success_rate', 0):.1%}
- Average Return: {performance.get('avg_return', 0):.1f}%
- Best Return: {performance.get('best_return', 0):.1f}%
- Worst Return: {performance.get('worst_return', 0):.1f}%

STRATEGY BREAKDOWN:
- Best Strategy: {performance.get('best_strategy', 'N/A')}
- Multibagger Signals: {performance.get('multibagger_signals', 0)}
- Active Signals: {performance.get('active_signals', 0)}

SYSTEM HEALTH:
- Uptime: {performance.get('uptime', 'N/A')}
- Last Update: {performance.get('last_update', 'N/A')}
- Errors: {performance.get('error_count', 0)}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
                
                # Send report
                if self.email_service.enabled:
                    self.email_service.send_email(
                        "📊 Weekly Performance Report",
                        report
                    )
                
                if self.telegram_enabled and self.telegram_bot:
                    asyncio.run(self.telegram_bot.send_notification(
                        f"📊 *Weekly Report Generated*\n\nSignals: {performance.get('total_signals', 0)}\nSuccess Rate: {performance.get('success_rate', 0):.1%}\nAvg Return: {performance.get('avg_return', 0):.1f}%"
                    ))
                
                logger.info("Weekly report sent successfully")
            else:
                logger.error("Failed to generate weekly report")
                
        except Exception as e:
            logger.error(f"Error generating weekly report: {str(e)}")
            self.send_error_notification("Weekly Report Failed", str(e))
    
    def setup_schedule(self):
        """Setup the automated schedule"""
        logger.info("Setting up automated schedule...")
        
        # Morning signal generation (9:15 AM IST - market open)
        schedule.every().monday.at("09:15").do(self.generate_morning_signals)
        schedule.every().tuesday.at("09:15").do(self.generate_morning_signals)
        schedule.every().wednesday.at("09:15").do(self.generate_morning_signals)
        schedule.every().thursday.at("09:15").do(self.generate_morning_signals)
        schedule.every().friday.at("09:15").do(self.generate_morning_signals)
        
        # Signal monitoring (3 times per day during market hours)
        schedule.every().monday.at("11:00").do(self.monitor_open_signals)
        schedule.every().monday.at("14:00").do(self.monitor_open_signals)
        schedule.every().monday.at("15:00").do(self.monitor_open_signals)
        
        schedule.every().tuesday.at("11:00").do(self.monitor_open_signals)
        schedule.every().tuesday.at("14:00").do(self.monitor_open_signals)
        schedule.every().tuesday.at("15:00").do(self.monitor_open_signals)
        
        schedule.every().wednesday.at("11:00").do(self.monitor_open_signals)
        schedule.every().wednesday.at("14:00").do(self.monitor_open_signals)
        schedule.every().wednesday.at("15:00").do(self.monitor_open_signals)
        
        schedule.every().thursday.at("11:00").do(self.monitor_open_signals)
        schedule.every().thursday.at("14:00").do(self.monitor_open_signals)
        schedule.every().thursday.at("15:00").do(self.monitor_open_signals)
        
        schedule.every().friday.at("11:00").do(self.monitor_open_signals)
        schedule.every().friday.at("14:00").do(self.monitor_open_signals)
        schedule.every().friday.at("15:00").do(self.monitor_open_signals)
        
        # Weekly report (Sunday evening)
        schedule.every().sunday.at("18:00").do(self.generate_weekly_report)
        
        logger.info("✅ Schedule configured successfully")
        logger.info("📅 Next jobs:")
        for job in schedule.jobs:
            logger.info(f"   - {job}")
    
    def run(self):
        """Run the scheduler"""
        logger.info("🚀 Starting EmergentTrader Scheduler...")
        
        self.setup_schedule()
        
        logger.info("⏰ Scheduler is running. Press Ctrl+C to stop.")
        
        try:
            while self.monitoring_active:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
            self.monitoring_active = False
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            self.send_error_notification("Scheduler Error", str(e))

if __name__ == "__main__":
    scheduler = EmergentTraderScheduler()
    scheduler.run()
