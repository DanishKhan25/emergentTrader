
"""
Simplified Critical Notifications - Works without telegram module
Uses direct HTTP requests to Telegram API
"""

import os
import requests
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

class SimplifiedNotifications:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.email_user = os.getenv('EMAIL_USER')
        
    async def send_buy_signal_alert(self, signal_data: Dict) -> Dict:
        """Send buy signal notification via Telegram"""
        try:
            if not self.bot_token or not self.chat_id:
                return {'success': False, 'error': 'Telegram not configured'}
            
            symbol = signal_data.get('symbol', 'N/A')
            strategy = signal_data.get('strategy', 'Unknown')
            confidence = signal_data.get('confidence', 0)
            entry_price = signal_data.get('entry_price', 0)
            target_price = signal_data.get('target_price', 0)
            stop_loss = signal_data.get('stop_loss', 0)
            
            potential_return = 0
            if entry_price and target_price:
                potential_return = ((target_price - entry_price) / entry_price) * 100
            
            message = f"""🚨 <b>BUY SIGNAL GENERATED!</b>

📈 <b>Symbol:</b> {symbol}
🎯 <b>Strategy:</b> {strategy.title()}
🔥 <b>Confidence:</b> {confidence:.0%}

💰 <b>Price Levels:</b>
• Entry: ₹{entry_price:,.2f}
• Target: ₹{target_price:,.2f}
• Stop Loss: ₹{stop_loss:,.2f}

📊 <b>Potential Return:</b> +{potential_return:.1f}%

🕐 {datetime.now().strftime('%H:%M:%S')}"""
            
            url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200 and response.json().get('ok'):
                logger.info(f"✅ Buy signal notification sent for {symbol}")
                return {'success': True, 'message_id': response.json()['result']['message_id']}
            else:
                logger.error(f"❌ Telegram API error: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Error sending buy signal notification: {e}")
            return {'success': False, 'error': str(e)}
    
    async def send_target_hit_alert(self, position_data: Dict) -> Dict:
        """Send target hit notification via Telegram"""
        try:
            if not self.bot_token or not self.chat_id:
                return {'success': False, 'error': 'Telegram not configured'}
            
            symbol = position_data.get('symbol', 'N/A')
            target_price = position_data.get('target_price', 0)
            current_price = position_data.get('current_price', 0)
            entry_price = position_data.get('entry_price', 0)
            quantity = position_data.get('quantity', 0)
            
            profit_per_share = current_price - entry_price if entry_price else 0
            total_profit = profit_per_share * quantity if quantity else 0
            profit_percent = (profit_per_share / entry_price * 100) if entry_price else 0
            
            message = f"""🎯 <b>TARGET HIT!</b> 🎯

📈 <b>{symbol}</b>
💰 Target: ₹{target_price:,.2f}
📊 Current: ₹{current_price:,.2f}

🏆 <b>PROFIT ACHIEVED:</b>
💵 Total Profit: <b>₹{total_profit:,.0f}</b>
📈 Return: <b>+{profit_percent:.1f}%</b>
📊 Quantity: {quantity:,} shares

⚡ <b>ACTION REQUIRED:</b>
Consider taking profits now!

🕐 {datetime.now().strftime('%H:%M:%S')}"""
            
            url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200 and response.json().get('ok'):
                logger.info(f"✅ Target hit notification sent for {symbol}")
                return {'success': True, 'profit': total_profit}
            else:
                logger.error(f"❌ Telegram API error: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Error sending target hit notification: {e}")
            return {'success': False, 'error': str(e)}
    
    async def send_stop_loss_alert(self, position_data: Dict) -> Dict:
        """Send stop loss notification via Telegram"""
        try:
            if not self.bot_token or not self.chat_id:
                return {'success': False, 'error': 'Telegram not configured'}
            
            symbol = position_data.get('symbol', 'N/A')
            stop_loss = position_data.get('stop_loss', 0)
            current_price = position_data.get('current_price', 0)
            entry_price = position_data.get('entry_price', 0)
            quantity = position_data.get('quantity', 0)
            
            loss_per_share = entry_price - current_price if entry_price else 0
            total_loss = loss_per_share * quantity if quantity else 0
            loss_percent = (loss_per_share / entry_price * 100) if entry_price else 0
            
            message = f"""🛑 <b>STOP LOSS HIT!</b> 🛑

📉 <b>{symbol}</b>
🛑 Stop Loss: ₹{stop_loss:,.2f}
📊 Current: ₹{current_price:,.2f}

💸 <b>LOSS INCURRED:</b>
💰 Total Loss: <b>₹{total_loss:,.0f}</b>
📉 Loss: <b>-{loss_percent:.1f}%</b>
📊 Quantity: {quantity:,} shares

🛡️ <b>RISK MANAGED:</b>
Position protected by stop loss.

🕐 {datetime.now().strftime('%H:%M:%S')}"""
            
            url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200 and response.json().get('ok'):
                logger.warning(f"✅ Stop loss notification sent for {symbol}")
                return {'success': True, 'loss': total_loss}
            else:
                logger.error(f"❌ Telegram API error: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Error sending stop loss notification: {e}")
            return {'success': False, 'error': str(e)}

# Global instance
_notifier = None

def get_notifier():
    global _notifier
    if _notifier is None:
        _notifier = SimplifiedNotifications()
    return _notifier

# Convenience functions
async def send_buy_signal_alert(signal_data: Dict) -> Dict:
    return await get_notifier().send_buy_signal_alert(signal_data)

async def send_target_hit_alert(position_data: Dict) -> Dict:
    return await get_notifier().send_target_hit_alert(position_data)

async def send_stop_loss_alert(position_data: Dict) -> Dict:
    return await get_notifier().send_stop_loss_alert(position_data)
