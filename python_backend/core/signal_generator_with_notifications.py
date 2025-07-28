"""
Enhanced Signal Generator with Telegram Notifications
Integrates signal generation with real-time notifications
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.enhanced_signal_engine import EnhancedSignalEngine
from services.enhanced_notification_service import notification_service
from services.signal_management_service import signal_manager

logger = logging.getLogger(__name__)

class SignalGeneratorWithNotifications:
    def __init__(self):
        """Initialize enhanced signal generator"""
        self.signal_engine = EnhancedSignalEngine()
        logger.info("Signal Generator with Notifications initialized")
    
    async def generate_and_notify_signals(self, 
                                        strategy: str = "multibagger",
                                        shariah_only: bool = True,
                                        min_confidence: float = 0.6,
                                        force_refresh: bool = False) -> Dict:
        """Generate signals and send notifications"""
        try:
            logger.info(f"🎯 Starting signal generation with notifications...")
            
            # Clear old signals first
            clear_result = signal_manager.clear_all_signals()
            if clear_result['success']:
                logger.info(f"Cleared {clear_result['count_cleared']} old signals")
                
                # Send clearing notification
                await notification_service.send_telegram_message(
                    f"🧹 <b>Signal Database Cleared</b>\n\n"
                    f"Removed {clear_result['count_cleared']} old signals\n"
                    f"Preparing for fresh signal generation...\n"
                    f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                )
            
            # Generate signals using the enhanced engine
            result = self.signal_engine.generate_signals(
                strategy=strategy,
                shariah_only=shariah_only,
                min_confidence=min_confidence,
                force_refresh=force_refresh
            )
            
            if not result.get('success'):
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"❌ Signal generation failed: {error_msg}")
                
                # Send error notification
                await notification_service.send_telegram_message(
                    f"❌ <b>Signal Generation Failed</b>\n\n"
                    f"Error: {error_msg}\n"
                    f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                )
                
                return result
            
            # Get generated signals
            signals = result.get('data', {}).get('signals', [])
            logger.info(f"✅ Generated {len(signals)} signals")
            
            # Process each signal
            successful_notifications = 0
            for signal in signals:
                try:
                    # Add to signal tracking database
                    add_result = signal_manager.add_signal(signal)
                    
                    if add_result['success']:
                        # Send individual signal notification
                        notification_id = await notification_service.notify_signal_generated(signal)
                        
                        if notification_id:
                            successful_notifications += 1
                            logger.info(f"✅ Notified signal for {signal.get('symbol')}")
                        else:
                            logger.warning(f"⚠️ Failed to notify signal for {signal.get('symbol')}")
                    
                except Exception as e:
                    logger.error(f"Error processing signal {signal.get('symbol', 'Unknown')}: {e}")
                    continue
            
            # Send summary notification
            summary_message = self._create_summary_message(signals, successful_notifications)
            await notification_service.send_telegram_message(summary_message)
            
            # Update result with notification info
            result['notifications'] = {
                'total_signals': len(signals),
                'successful_notifications': successful_notifications,
                'failed_notifications': len(signals) - successful_notifications
            }
            
            logger.info(f"🎉 Signal generation complete: {len(signals)} signals, {successful_notifications} notifications sent")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in signal generation with notifications: {e}")
            
            # Send error notification
            try:
                await notification_service.send_telegram_message(
                    f"🚨 <b>Signal Generation System Error</b>\n\n"
                    f"Error: {str(e)}\n"
                    f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                    f"<i>Please check system logs for details.</i>"
                )
            except:
                pass  # Don't fail if notification fails
            
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_summary_message(self, signals: List[Dict], successful_notifications: int) -> str:
        """Create summary message for signal generation"""
        try:
            total_signals = len(signals)
            
            # Calculate statistics
            strategies = {}
            total_potential_return = 0
            high_confidence_count = 0
            
            for signal in signals:
                strategy = signal.get('strategy', 'Unknown')
                confidence = signal.get('confidence', 0)
                entry_price = signal.get('entry_price', 0)
                target_price = signal.get('target_price', 0)
                
                # Count by strategy
                strategies[strategy] = strategies.get(strategy, 0) + 1
                
                # Calculate potential return
                if entry_price and target_price:
                    potential_return = ((target_price - entry_price) / entry_price) * 100
                    total_potential_return += potential_return
                
                # Count high confidence signals
                if confidence >= 0.8:
                    high_confidence_count += 1
            
            avg_potential_return = total_potential_return / total_signals if total_signals > 0 else 0
            
            # Create strategy breakdown
            strategy_breakdown = ""
            for strategy, count in strategies.items():
                strategy_breakdown += f"• {strategy.title()}: {count} signals\n"
            
            # Get top 5 signals for preview
            top_signals = sorted(signals, key=lambda x: x.get('confidence', 0), reverse=True)[:5]
            signals_preview = ""
            
            for signal in top_signals:
                symbol = signal.get('symbol', 'N/A')
                confidence = signal.get('confidence', 0)
                entry_price = signal.get('entry_price', 0)
                target_price = signal.get('target_price', 0)
                
                potential_return = 0
                if entry_price and target_price:
                    potential_return = ((target_price - entry_price) / entry_price) * 100
                
                signals_preview += f"• {symbol} - {confidence:.0%} confidence, +{potential_return:.1f}% potential\n"
            
            summary_message = f"""🎯 <b>SIGNAL GENERATION COMPLETE!</b>

✅ <b>Generation Summary:</b>
• Total Signals: {total_signals}
• Notifications Sent: {successful_notifications}
• High Confidence (80%+): {high_confidence_count}
• Avg Potential Return: +{avg_potential_return:.1f}%

📊 <b>By Strategy:</b>
{strategy_breakdown}

🔥 <b>Top Signals:</b>
{signals_preview}

⏰ <b>Generated at:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<i>Check your dashboard for complete details! 📈</i>"""
            
            return summary_message
            
        except Exception as e:
            logger.error(f"Error creating summary message: {e}")
            return f"""🎯 <b>SIGNAL GENERATION COMPLETE!</b>

✅ Generated {len(signals)} signals
📱 Sent {successful_notifications} notifications

⏰ Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

<i>Check your dashboard for details!</i>"""
    
    async def check_and_notify_targets(self) -> Dict:
        """Check active signals for target hits and stop losses"""
        try:
            logger.info("🎯 Checking signals for target hits and stop losses...")
            
            # Get active signals
            active_signals_result = signal_manager.get_active_signals()
            
            if not active_signals_result['success']:
                return {
                    'success': False,
                    'error': 'Could not retrieve active signals'
                }
            
            active_signals = active_signals_result['signals']
            
            if not active_signals:
                logger.info("No active signals to check")
                return {
                    'success': True,
                    'message': 'No active signals to check',
                    'checked_count': 0
                }
            
            # Get current prices for all symbols
            symbols = [signal['symbol'] for signal in active_signals]
            current_prices = await signal_manager.fetch_current_prices(symbols)
            
            if not current_prices:
                logger.warning("Could not fetch current prices")
                return {
                    'success': False,
                    'error': 'Could not fetch current prices'
                }
            
            # Update signal prices and check targets
            update_result = signal_manager.update_signal_prices(current_prices)
            
            if update_result['success']:
                target_hits = update_result.get('target_hits', [])
                stop_losses = update_result.get('stop_losses', [])
                
                # Send notifications for target hits
                for target_hit in target_hits:
                    await notification_service.notify_target_hit(
                        target_hit, 
                        target_hit['current_price'], 
                        target_hit['profit_percent']
                    )
                
                # Send notifications for stop losses
                for stop_loss in stop_losses:
                    await notification_service.notify_stop_loss_hit(
                        stop_loss,
                        stop_loss['current_price'], 
                        stop_loss['loss_percent']
                    )
                
                logger.info(f"✅ Checked {len(active_signals)} signals: {len(target_hits)} targets hit, {len(stop_losses)} stop losses")
                
                return {
                    'success': True,
                    'checked_count': len(active_signals),
                    'target_hits': len(target_hits),
                    'stop_losses': len(stop_losses),
                    'updated_count': update_result.get('updated_count', 0)
                }
            
            else:
                return {
                    'success': False,
                    'error': update_result.get('error', 'Update failed')
                }
                
        except Exception as e:
            logger.error(f"Error checking targets: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
signal_generator_with_notifications = SignalGeneratorWithNotifications()
