"""
Critical Trading Notifications
Handles the 3 most important trading alerts:
1. Buy Signal Generated
2. Target Hit 
3. Stop Loss Hit
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
from .email_service import EmailService
from .telegram_bot import EmergentTraderBot

logger = logging.getLogger(__name__)

class CriticalNotifications:
    def __init__(self):
        """Initialize critical notification services"""
        self.email_service = EmailService()
        self.telegram_bot = EmergentTraderBot()
        
        # Load user settings from environment
        self.user_email = os.getenv('EMAIL_USER')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        logger.info("Critical notifications initialized")
    
    async def notify_buy_signal(self, signal_data: Dict) -> Dict:
        """
        Send immediate notification for every BUY signal
        This is called whenever a new buy signal is generated
        """
        try:
            symbol = signal_data.get('symbol', 'N/A')
            strategy = signal_data.get('strategy', 'Unknown')
            confidence = signal_data.get('confidence', 0)
            entry_price = signal_data.get('entry_price', 0)
            target_price = signal_data.get('target_price', 0)
            stop_loss = signal_data.get('stop_loss', 0)
            
            # Calculate potential return
            potential_return = 0
            if entry_price and target_price:
                potential_return = ((target_price - entry_price) / entry_price) * 100
            
            logger.info(f"🚨 CRITICAL: Buy signal for {symbol} - {confidence:.0%} confidence")
            
            results = {'email': None, 'telegram': None}
            
            # 📧 Send Email Notification
            if self.user_email:
                try:
                    email_sent = self.email_service.send_signal_alert(signal_data)
                    results['email'] = {
                        'success': email_sent,
                        'timestamp': datetime.now().isoformat()
                    }
                    if email_sent:
                        logger.info(f"✅ Buy signal email sent for {symbol}")
                    else:
                        logger.warning(f"❌ Buy signal email failed for {symbol}")
                except Exception as e:
                    logger.error(f"Email error for buy signal {symbol}: {e}")
                    results['email'] = {'success': False, 'error': str(e)}
            
            # 📱 Send Telegram Notification
            if self.telegram_chat_id:
                try:
                    telegram_message = self._format_buy_signal_telegram(signal_data, potential_return)
                    
                    # Send via your existing telegram bot
                    telegram_sent = await self.telegram_bot.send_signal_notification(signal_data)
                    results['telegram'] = {
                        'success': telegram_sent,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    if telegram_sent:
                        logger.info(f"✅ Buy signal Telegram sent for {symbol}")
                    else:
                        logger.warning(f"❌ Buy signal Telegram failed for {symbol}")
                        
                except Exception as e:
                    logger.error(f"Telegram error for buy signal {symbol}: {e}")
                    results['telegram'] = {'success': False, 'error': str(e)}
            
            return {
                'success': True,
                'signal': symbol,
                'type': 'buy_signal',
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Critical error in buy signal notification: {e}")
            return {'success': False, 'error': str(e)}
    
    async def notify_target_hit(self, position_data: Dict) -> Dict:
        """
        Send URGENT notification when target price is hit
        This is called when monitoring detects target reached
        """
        try:
            symbol = position_data.get('symbol', 'N/A')
            target_price = position_data.get('target_price', 0)
            current_price = position_data.get('current_price', 0)
            entry_price = position_data.get('entry_price', 0)
            quantity = position_data.get('quantity', 0)
            
            # Calculate profit
            profit_per_share = current_price - entry_price if entry_price else 0
            total_profit = profit_per_share * quantity if quantity else 0
            profit_percent = (profit_per_share / entry_price * 100) if entry_price else 0
            
            logger.info(f"🎯 URGENT: Target hit for {symbol} - ₹{total_profit:,.0f} profit!")
            
            results = {'email': None, 'telegram': None}
            
            # 📧 Send URGENT Email
            if self.user_email:
                try:
                    subject = f"🎯 TARGET HIT! {symbol} - ₹{total_profit:,.0f} Profit"
                    
                    email_body = f"""
🎯 TARGET PRICE HIT!

Symbol: {symbol}
Target Price: ₹{target_price:,.2f}
Current Price: ₹{current_price:,.2f}
Entry Price: ₹{entry_price:,.2f}

💰 PROFIT DETAILS:
• Profit per share: ₹{profit_per_share:,.2f}
• Total profit: ₹{total_profit:,.2f}
• Return: +{profit_percent:.1f}%
• Quantity: {quantity:,} shares

⚡ ACTION REQUIRED:
Consider taking profits or trailing stop loss.

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                    
                    email_sent = self.email_service.send_email(
                        subject=subject,
                        body=email_body,
                        recipients=[self.user_email]
                    )
                    
                    results['email'] = {
                        'success': email_sent,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    if email_sent:
                        logger.info(f"✅ Target hit email sent for {symbol}")
                    
                except Exception as e:
                    logger.error(f"Email error for target hit {symbol}: {e}")
                    results['email'] = {'success': False, 'error': str(e)}
            
            # 📱 Send URGENT Telegram
            if self.telegram_chat_id:
                try:
                    telegram_message = f"""
🎯 <b>TARGET HIT!</b> 🎯

📈 <b>{symbol}</b>
💰 Target: ₹{target_price:,.2f}
📊 Current: ₹{current_price:,.2f}

🏆 <b>PROFIT ACHIEVED:</b>
💵 Total Profit: <b>₹{total_profit:,.0f}</b>
📈 Return: <b>+{profit_percent:.1f}%</b>
📊 Quantity: {quantity:,} shares

⚡ <b>ACTION REQUIRED:</b>
Consider taking profits now!

🕐 {datetime.now().strftime('%H:%M:%S')}
"""
                    
                    # Use your existing telegram bot method
                    telegram_sent = await self.telegram_bot.send_portfolio_update({
                        'message': telegram_message,
                        'type': 'target_hit',
                        'symbol': symbol,
                        'profit': total_profit
                    })
                    
                    results['telegram'] = {
                        'success': telegram_sent,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    if telegram_sent:
                        logger.info(f"✅ Target hit Telegram sent for {symbol}")
                        
                except Exception as e:
                    logger.error(f"Telegram error for target hit {symbol}: {e}")
                    results['telegram'] = {'success': False, 'error': str(e)}
            
            return {
                'success': True,
                'symbol': symbol,
                'type': 'target_hit',
                'profit': total_profit,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Critical error in target hit notification: {e}")
            return {'success': False, 'error': str(e)}
    
    async def notify_stop_loss_hit(self, position_data: Dict) -> Dict:
        """
        Send URGENT notification when stop loss is hit
        This is called when monitoring detects stop loss triggered
        """
        try:
            symbol = position_data.get('symbol', 'N/A')
            stop_loss = position_data.get('stop_loss', 0)
            current_price = position_data.get('current_price', 0)
            entry_price = position_data.get('entry_price', 0)
            quantity = position_data.get('quantity', 0)
            
            # Calculate loss
            loss_per_share = entry_price - current_price if entry_price else 0
            total_loss = loss_per_share * quantity if quantity else 0
            loss_percent = (loss_per_share / entry_price * 100) if entry_price else 0
            
            logger.warning(f"🛑 URGENT: Stop loss hit for {symbol} - ₹{total_loss:,.0f} loss!")
            
            results = {'email': None, 'telegram': None}
            
            # 📧 Send URGENT Email
            if self.user_email:
                try:
                    subject = f"🛑 STOP LOSS HIT! {symbol} - ₹{total_loss:,.0f} Loss"
                    
                    email_body = f"""
🛑 STOP LOSS TRIGGERED!

Symbol: {symbol}
Stop Loss: ₹{stop_loss:,.2f}
Current Price: ₹{current_price:,.2f}
Entry Price: ₹{entry_price:,.2f}

💸 LOSS DETAILS:
• Loss per share: ₹{loss_per_share:,.2f}
• Total loss: ₹{total_loss:,.2f}
• Loss: -{loss_percent:.1f}%
• Quantity: {quantity:,} shares

🛡️ RISK MANAGEMENT:
Position automatically protected by stop loss.

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                    
                    email_sent = self.email_service.send_email(
                        subject=subject,
                        body=email_body,
                        recipients=[self.user_email]
                    )
                    
                    results['email'] = {
                        'success': email_sent,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    if email_sent:
                        logger.info(f"✅ Stop loss email sent for {symbol}")
                    
                except Exception as e:
                    logger.error(f"Email error for stop loss {symbol}: {e}")
                    results['email'] = {'success': False, 'error': str(e)}
            
            # 📱 Send URGENT Telegram
            if self.telegram_chat_id:
                try:
                    telegram_message = f"""
🛑 <b>STOP LOSS HIT!</b> 🛑

📉 <b>{symbol}</b>
🛑 Stop Loss: ₹{stop_loss:,.2f}
📊 Current: ₹{current_price:,.2f}

💸 <b>LOSS INCURRED:</b>
💰 Total Loss: <b>₹{total_loss:,.0f}</b>
📉 Loss: <b>-{loss_percent:.1f}%</b>
📊 Quantity: {quantity:,} shares

🛡️ <b>RISK MANAGED:</b>
Position protected by stop loss.

🕐 {datetime.now().strftime('%H:%M:%S')}
"""
                    
                    # Use your existing telegram bot method
                    telegram_sent = await self.telegram_bot.send_portfolio_update({
                        'message': telegram_message,
                        'type': 'stop_loss_hit',
                        'symbol': symbol,
                        'loss': total_loss
                    })
                    
                    results['telegram'] = {
                        'success': telegram_sent,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    if telegram_sent:
                        logger.info(f"✅ Stop loss Telegram sent for {symbol}")
                        
                except Exception as e:
                    logger.error(f"Telegram error for stop loss {symbol}: {e}")
                    results['telegram'] = {'success': False, 'error': str(e)}
            
            return {
                'success': True,
                'symbol': symbol,
                'type': 'stop_loss_hit',
                'loss': total_loss,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Critical error in stop loss notification: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_buy_signal_telegram(self, signal_data: Dict, potential_return: float) -> str:
        """Format buy signal for Telegram"""
        symbol = signal_data.get('symbol', 'N/A')
        strategy = signal_data.get('strategy', 'Unknown')
        confidence = signal_data.get('confidence', 0)
        entry_price = signal_data.get('entry_price', 0)
        target_price = signal_data.get('target_price', 0)
        stop_loss = signal_data.get('stop_loss', 0)
        
        return f"""
🚨 <b>BUY SIGNAL GENERATED!</b>

📈 <b>Symbol:</b> {symbol}
🎯 <b>Strategy:</b> {strategy.title()}
🔥 <b>Confidence:</b> {confidence:.0%}

💰 <b>Price Levels:</b>
• Entry: ₹{entry_price:,.2f}
• Target: ₹{target_price:,.2f}
• Stop Loss: ₹{stop_loss:,.2f}

📊 <b>Potential Return:</b> +{potential_return:.1f}%

🕐 {datetime.now().strftime('%H:%M:%S')}
"""
    
    async def test_all_notifications(self) -> Dict:
        """Test all 3 critical notifications"""
        try:
            logger.info("🧪 Testing all critical notifications...")
            
            # Test buy signal
            test_signal = {
                'symbol': 'RELIANCE',
                'strategy': 'multibagger',
                'confidence': 0.94,
                'entry_price': 2450.0,
                'target_price': 2800.0,
                'stop_loss': 2200.0
            }
            
            buy_result = await self.notify_buy_signal(test_signal)
            
            # Test target hit
            test_target = {
                'symbol': 'TCS',
                'target_price': 4000.0,
                'current_price': 4000.0,
                'entry_price': 3500.0,
                'quantity': 100
            }
            
            target_result = await self.notify_target_hit(test_target)
            
            # Test stop loss
            test_stop_loss = {
                'symbol': 'HDFCBANK',
                'stop_loss': 1400.0,
                'current_price': 1400.0,
                'entry_price': 1600.0,
                'quantity': 50
            }
            
            stop_loss_result = await self.notify_stop_loss_hit(test_stop_loss)
            
            return {
                'success': True,
                'tests': {
                    'buy_signal': buy_result,
                    'target_hit': target_result,
                    'stop_loss_hit': stop_loss_result
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error testing notifications: {e}")
            return {'success': False, 'error': str(e)}

# Convenience functions for easy integration
async def send_buy_signal_alert(signal_data: Dict) -> Dict:
    """Quick function to send buy signal notification"""
    notifier = CriticalNotifications()
    return await notifier.notify_buy_signal(signal_data)

async def send_target_hit_alert(position_data: Dict) -> Dict:
    """Quick function to send target hit notification"""
    notifier = CriticalNotifications()
    return await notifier.notify_target_hit(position_data)

async def send_stop_loss_alert(position_data: Dict) -> Dict:
    """Quick function to send stop loss notification"""
    notifier = CriticalNotifications()
    return await notifier.notify_stop_loss_hit(position_data)
