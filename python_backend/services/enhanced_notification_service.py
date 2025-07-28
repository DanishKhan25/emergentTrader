"""
Enhanced Notification Service for EmergentTrader
Handles real-time notifications via multiple channels with proper signal tracking
"""

import os
import asyncio
import logging
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class NotificationConfig:
    """Configuration for notification service"""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    email_enabled: bool = False
    webhook_url: str = ""
    
    def __post_init__(self):
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
        self.webhook_url = os.getenv('WEBHOOK_URL', '')

class EnhancedNotificationService:
    def __init__(self, db_path: str = None):
        """Initialize enhanced notification service"""
        self.config = NotificationConfig()
        self.db_path = db_path or "python_backend/emergent_trader.db"
        self.init_database()
        
        logger.info("Enhanced Notification Service initialized")
        logger.info(f"Telegram configured: {bool(self.config.telegram_bot_token and self.config.telegram_chat_id)}")
    
    def init_database(self):
        """Initialize notification tracking database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create notifications table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        notification_id TEXT UNIQUE NOT NULL,
                        type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        message TEXT NOT NULL,
                        data TEXT,
                        channels TEXT,
                        status TEXT DEFAULT 'pending',
                        created_at TEXT NOT NULL,
                        sent_at TEXT,
                        error_message TEXT
                    )
                ''')
                
                # Create signal tracking table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS signal_tracking (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        signal_id TEXT UNIQUE NOT NULL,
                        symbol TEXT NOT NULL,
                        strategy TEXT NOT NULL,
                        signal_type TEXT NOT NULL,
                        entry_price REAL,
                        target_price REAL,
                        stop_loss REAL,
                        current_price REAL,
                        status TEXT DEFAULT 'active',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        target_hit_at TEXT,
                        stop_loss_hit_at TEXT,
                        profit_loss REAL DEFAULT 0,
                        profit_loss_percent REAL DEFAULT 0
                    )
                ''')
                
                conn.commit()
                logger.info("Notification database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing notification database: {e}")
    
    async def send_telegram_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send message via Telegram"""
        if not self.config.telegram_bot_token or not self.config.telegram_chat_id:
            logger.warning("Telegram not configured - skipping telegram notification")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
            payload = {
                'chat_id': self.config.telegram_chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    async def notify_signal_generated(self, signal_data: Dict) -> str:
        """Send notification when a new signal is generated"""
        try:
            symbol = signal_data.get('symbol', 'N/A')
            strategy = signal_data.get('strategy', 'Unknown')
            signal_type = signal_data.get('signal_type', 'BUY')
            confidence = signal_data.get('confidence', 0)
            entry_price = signal_data.get('entry_price', 0)
            target_price = signal_data.get('target_price', 0)
            stop_loss = signal_data.get('stop_loss', 0)
            
            # Calculate potential return
            potential_return = 0
            if entry_price and target_price and entry_price > 0:
                potential_return = ((target_price - entry_price) / entry_price) * 100
            
            # Create notification message
            message = f"""🚨 <b>NEW {signal_type.upper()} SIGNAL!</b>

📈 <b>Symbol:</b> {symbol}
🎯 <b>Strategy:</b> {strategy.title()}
🔥 <b>Confidence:</b> {confidence:.0%}

💰 <b>Price Levels:</b>
• Entry: ₹{entry_price:,.2f}
• Target: ₹{target_price:,.2f}
• Stop Loss: ₹{stop_loss:,.2f}

📊 <b>Potential Return:</b> +{potential_return:.1f}%
⏰ <b>Generated:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<i>Trade at your own risk. This is not financial advice.</i>"""
            
            # Store notification in database
            notification_id = f"signal_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO notifications 
                    (notification_id, type, title, message, data, channels, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    notification_id,
                    'signal',
                    f'New {signal_type} Signal - {symbol}',
                    message,
                    json.dumps(signal_data),
                    'telegram,websocket',
                    datetime.now().isoformat()
                ))
                conn.commit()
            
            # Send via Telegram
            telegram_success = await self.send_telegram_message(message)
            
            # Update notification status
            status = 'sent' if telegram_success else 'failed'
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE notifications 
                    SET status = ?, sent_at = ?
                    WHERE notification_id = ?
                ''', (status, datetime.now().isoformat(), notification_id))
                conn.commit()
            
            # Track the signal
            await self.track_signal(signal_data)
            
            logger.info(f"Signal notification sent for {symbol} - Status: {status}")
            return notification_id
            
        except Exception as e:
            logger.error(f"Error sending signal notification: {e}")
            return ""
    
    async def track_signal(self, signal_data: Dict):
        """Track signal for target/stop loss monitoring"""
        try:
            signal_id = signal_data.get('signal_id', f"signal_{signal_data.get('symbol')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO signal_tracking 
                    (signal_id, symbol, strategy, signal_type, entry_price, target_price, 
                     stop_loss, current_price, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    signal_id,
                    signal_data.get('symbol'),
                    signal_data.get('strategy'),
                    signal_data.get('signal_type', 'BUY'),
                    signal_data.get('entry_price'),
                    signal_data.get('target_price'),
                    signal_data.get('stop_loss'),
                    signal_data.get('current_price', signal_data.get('entry_price')),
                    'active',
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                conn.commit()
                
            logger.info(f"Signal tracking started for {signal_data.get('symbol')}")
            
        except Exception as e:
            logger.error(f"Error tracking signal: {e}")
    
    async def check_signal_targets(self, current_prices: Dict[str, float]):
        """Check if any tracked signals have hit targets or stop losses"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM signal_tracking 
                    WHERE status = 'active'
                ''')
                
                active_signals = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                for row in active_signals:
                    signal = dict(zip(columns, row))
                    symbol = signal['symbol']
                    
                    if symbol not in current_prices:
                        continue
                    
                    current_price = current_prices[symbol]
                    entry_price = signal['entry_price']
                    target_price = signal['target_price']
                    stop_loss = signal['stop_loss']
                    
                    # Update current price
                    cursor.execute('''
                        UPDATE signal_tracking 
                        SET current_price = ?, updated_at = ?
                        WHERE signal_id = ?
                    ''', (current_price, datetime.now().isoformat(), signal['signal_id']))
                    
                    # Check for target hit
                    if current_price >= target_price:
                        profit = current_price - entry_price
                        profit_percent = (profit / entry_price) * 100
                        
                        cursor.execute('''
                            UPDATE signal_tracking 
                            SET status = 'target_hit', target_hit_at = ?, 
                                profit_loss = ?, profit_loss_percent = ?
                            WHERE signal_id = ?
                        ''', (datetime.now().isoformat(), profit, profit_percent, signal['signal_id']))
                        
                        await self.notify_target_hit(signal, current_price, profit_percent)
                    
                    # Check for stop loss hit
                    elif current_price <= stop_loss:
                        loss = current_price - entry_price
                        loss_percent = (loss / entry_price) * 100
                        
                        cursor.execute('''
                            UPDATE signal_tracking 
                            SET status = 'stop_loss_hit', stop_loss_hit_at = ?, 
                                profit_loss = ?, profit_loss_percent = ?
                            WHERE signal_id = ?
                        ''', (datetime.now().isoformat(), loss, loss_percent, signal['signal_id']))
                        
                        await self.notify_stop_loss_hit(signal, current_price, loss_percent)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error checking signal targets: {e}")
    
    async def notify_target_hit(self, signal: Dict, current_price: float, profit_percent: float):
        """Send notification when target is hit"""
        try:
            message = f"""🎯 <b>TARGET HIT!</b> 🎉

📈 <b>Symbol:</b> {signal['symbol']}
🎯 <b>Strategy:</b> {signal['strategy']}
💰 <b>Entry Price:</b> ₹{signal['entry_price']:,.2f}
🎯 <b>Target Price:</b> ₹{signal['target_price']:,.2f}
📊 <b>Current Price:</b> ₹{current_price:,.2f}

💵 <b>Profit:</b> +{profit_percent:.2f}%
⏰ <b>Time:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<b>Congratulations! 🚀</b>"""
            
            await self.send_telegram_message(message)
            logger.info(f"Target hit notification sent for {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"Error sending target hit notification: {e}")
    
    async def notify_stop_loss_hit(self, signal: Dict, current_price: float, loss_percent: float):
        """Send notification when stop loss is hit"""
        try:
            message = f"""🛑 <b>STOP LOSS HIT</b> ⚠️

📉 <b>Symbol:</b> {signal['symbol']}
🎯 <b>Strategy:</b> {signal['strategy']}
💰 <b>Entry Price:</b> ₹{signal['entry_price']:,.2f}
🛑 <b>Stop Loss:</b> ₹{signal['stop_loss']:,.2f}
📊 <b>Current Price:</b> ₹{current_price:,.2f}

💸 <b>Loss:</b> {loss_percent:.2f}%
⏰ <b>Time:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<i>Risk management in action. Better luck next time!</i>"""
            
            await self.send_telegram_message(message)
            logger.info(f"Stop loss notification sent for {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"Error sending stop loss notification: {e}")
    
    def get_signal_statistics(self) -> Dict:
        """Get statistics about tracked signals"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get overall stats
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_signals,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_signals,
                        COUNT(CASE WHEN status = 'target_hit' THEN 1 END) as target_hits,
                        COUNT(CASE WHEN status = 'stop_loss_hit' THEN 1 END) as stop_losses,
                        AVG(CASE WHEN status = 'target_hit' THEN profit_loss_percent END) as avg_profit,
                        AVG(CASE WHEN status = 'stop_loss_hit' THEN profit_loss_percent END) as avg_loss
                    FROM signal_tracking
                ''')
                
                stats = cursor.fetchone()
                
                return {
                    'total_signals': stats[0] or 0,
                    'active_signals': stats[1] or 0,
                    'target_hits': stats[2] or 0,
                    'stop_losses': stats[3] or 0,
                    'success_rate': (stats[2] / stats[0] * 100) if stats[0] > 0 else 0,
                    'avg_profit_percent': stats[4] or 0,
                    'avg_loss_percent': stats[5] or 0
                }
                
        except Exception as e:
            logger.error(f"Error getting signal statistics: {e}")
            return {}
    
    async def send_daily_summary(self):
        """Send daily summary of signals and performance"""
        try:
            stats = self.get_signal_statistics()
            
            message = f"""📊 <b>DAILY TRADING SUMMARY</b>

📈 <b>Signal Statistics:</b>
• Total Signals: {stats.get('total_signals', 0)}
• Active Signals: {stats.get('active_signals', 0)}
• Targets Hit: {stats.get('target_hits', 0)}
• Stop Losses: {stats.get('stop_losses', 0)}

🎯 <b>Performance:</b>
• Success Rate: {stats.get('success_rate', 0):.1f}%
• Avg Profit: +{stats.get('avg_profit_percent', 0):.2f}%
• Avg Loss: {stats.get('avg_loss_percent', 0):.2f}%

⏰ <b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}

<i>Keep trading smart! 📈</i>"""
            
            await self.send_telegram_message(message)
            logger.info("Daily summary sent")
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")

# Global instance
notification_service = EnhancedNotificationService()
