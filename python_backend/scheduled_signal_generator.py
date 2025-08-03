#!/usr/bin/env python3
"""
Scheduled Signal Generator for EmergentTrader
Runs automated signal generation 3 times daily on Render
"""

import os
import sys
import json
import logging
import argparse
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Import our modules
from api_handler import EmergentTraderAPI
from core.enhanced_signal_engine import EnhancedSignalEngine
from core.ml_enhanced_signal_engine import MLEnhancedSignalEngine
from services.notification_service import NotificationService
from services.email_service import EmailService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduled_signals.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ScheduledSignalGenerator:
    def __init__(self, run_time="morning"):
        self.run_time = run_time
        self.api = EmergentTraderAPI()
        self.signal_engine = EnhancedSignalEngine()
        self.ml_engine = MLEnhancedSignalEngine()
        self.notification_service = NotificationService()
        self.email_service = EmailService()
        
        # Configure based on run time
        self.config = self.get_run_config(run_time)
        
    def get_run_config(self, run_time):
        """Get configuration based on run time"""
        configs = {
            "morning": {
                "name": "Morning Market Scan",
                "time": "09:00",
                "strategies": ["multibagger", "momentum", "breakout"],
                "min_confidence": 0.7,
                "max_signals": 20,
                "email_subject": "🌅 Morning Trading Signals - EmergentTrader"
            },
            "afternoon": {
                "name": "Midday Market Analysis",
                "time": "14:00", 
                "strategies": ["swing_trading", "mean_reversion", "value_investing"],
                "min_confidence": 0.75,
                "max_signals": 15,
                "email_subject": "☀️ Afternoon Market Update - EmergentTrader"
            },
            "evening": {
                "name": "End of Day Review",
                "time": "18:00",
                "strategies": ["sector_rotation", "low_volatility", "fundamental_growth"],
                "min_confidence": 0.8,
                "max_signals": 10,
                "email_subject": "🌆 Evening Market Summary - EmergentTrader"
            }
        }
        return configs.get(run_time, configs["morning"])
    
    async def run_full_scan(self):
        """Run complete market scan and generate signals"""
        logger.info(f"Starting {self.config['name']} at {datetime.now()}")
        
        try:
            # Step 1: Generate signals using multiple strategies
            all_signals = []
            
            for strategy in self.config["strategies"]:
                logger.info(f"Running {strategy} strategy...")
                
                try:
                    # Generate signals for this strategy
                    strategy_signals = await self.generate_strategy_signals(strategy)
                    all_signals.extend(strategy_signals)
                    logger.info(f"Generated {len(strategy_signals)} signals from {strategy}")
                    
                except Exception as e:
                    logger.error(f"Error in {strategy} strategy: {e}")
                    continue
            
            # Step 2: Enhance signals with ML
            logger.info("Enhancing signals with ML predictions...")
            enhanced_signals = await self.enhance_signals_with_ml(all_signals)
            
            # Step 3: Filter and rank signals
            logger.info("Filtering and ranking signals...")
            final_signals = self.filter_and_rank_signals(enhanced_signals)
            
            # Step 4: Save signals to database
            logger.info("Saving signals to database...")
            saved_count = await self.save_signals(final_signals)
            
            # Step 5: Track signal progress
            logger.info("Tracking signal progress...")
            await self.track_signal_progress()
            
            # Step 6: Send notifications
            logger.info("Sending notifications...")
            await self.send_notifications(final_signals)
            
            # Step 7: Generate report
            report = self.generate_run_report(final_signals, saved_count)
            logger.info(f"Scan completed successfully. Generated {len(final_signals)} signals")
            
            return report
            
        except Exception as e:
            logger.error(f"Error in scheduled scan: {e}")
            await self.send_error_notification(str(e))
            raise
    
    async def generate_strategy_signals(self, strategy_name):
        """Generate signals for a specific strategy"""
        try:
            # Use the API handler to generate signals
            response = await asyncio.to_thread(
                self.api.generate_signals,
                {
                    "strategy": strategy_name,
                    "min_confidence": self.config["min_confidence"],
                    "shariah_compliant": True,
                    "limit": self.config["max_signals"]
                }
            )
            
            if response.get("success"):
                return response.get("signals", [])
            else:
                logger.warning(f"Strategy {strategy_name} returned no signals")
                return []
                
        except Exception as e:
            logger.error(f"Error generating {strategy_name} signals: {e}")
            return []
    
    async def enhance_signals_with_ml(self, signals):
        """Enhance signals with ML predictions"""
        enhanced_signals = []
        
        for signal in signals:
            try:
                # Get ML enhancement
                ml_data = await asyncio.to_thread(
                    self.ml_engine.enhance_signal,
                    signal
                )
                
                # Merge ML data with original signal
                enhanced_signal = {**signal, **ml_data}
                enhanced_signals.append(enhanced_signal)
                
            except Exception as e:
                logger.warning(f"ML enhancement failed for {signal.get('symbol', 'unknown')}: {e}")
                # Keep original signal if ML fails
                enhanced_signals.append(signal)
        
        return enhanced_signals
    
    def filter_and_rank_signals(self, signals):
        """Filter and rank signals based on criteria"""
        # Filter by confidence
        filtered_signals = [
            s for s in signals 
            if s.get("confidence", 0) >= self.config["min_confidence"]
        ]
        
        # Sort by confidence and ML score
        filtered_signals.sort(
            key=lambda x: (
                x.get("confidence", 0) * 0.6 + 
                x.get("ml_score", 0) * 0.4
            ),
            reverse=True
        )
        
        # Limit to max signals
        return filtered_signals[:self.config["max_signals"]]
    
    async def save_signals(self, signals):
        """Save signals to database"""
        saved_count = 0
        
        for signal in signals:
            try:
                # Add metadata
                signal.update({
                    "generated_at": datetime.now().isoformat(),
                    "run_type": self.run_time,
                    "scan_id": f"{self.run_time}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                })
                
                # Save via API
                result = await asyncio.to_thread(
                    self.api.save_signal,
                    signal
                )
                
                if result.get("success"):
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"Error saving signal for {signal.get('symbol')}: {e}")
        
        return saved_count
    
    async def track_signal_progress(self):
        """Track progress of existing signals"""
        try:
            # Get active signals from last 30 days
            active_signals = await asyncio.to_thread(
                self.api.get_active_signals,
                {"days": 30}
            )
            
            if not active_signals.get("success"):
                logger.warning("Could not retrieve active signals for tracking")
                return
            
            signals = active_signals.get("signals", [])
            logger.info(f"Tracking progress for {len(signals)} active signals")
            
            # Update each signal's progress
            for signal in signals:
                try:
                    # Get current price and calculate performance
                    current_data = await self.get_current_market_data(signal["symbol"])
                    
                    if current_data:
                        # Calculate performance metrics
                        performance = self.calculate_signal_performance(signal, current_data)
                        
                        # Update signal in database
                        await asyncio.to_thread(
                            self.api.update_signal_progress,
                            signal["id"],
                            performance
                        )
                        
                except Exception as e:
                    logger.error(f"Error tracking signal {signal.get('symbol')}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in signal tracking: {e}")
    
    async def get_current_market_data(self, symbol):
        """Get current market data for a symbol"""
        try:
            # Use yfinance fetcher
            from services.yfinance_fetcher import YFinanceFetcher
            fetcher = YFinanceFetcher()
            
            data = await asyncio.to_thread(
                fetcher.get_current_price,
                symbol
            )
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return None
    
    def calculate_signal_performance(self, signal, current_data):
        """Calculate signal performance metrics"""
        try:
            entry_price = signal.get("entry_price", 0)
            current_price = current_data.get("current_price", 0)
            
            if entry_price and current_price:
                # Calculate returns
                returns = ((current_price - entry_price) / entry_price) * 100
                
                # Determine status
                target_price = signal.get("target_price", 0)
                stop_loss = signal.get("stop_loss", 0)
                
                status = "active"
                if target_price and current_price >= target_price:
                    status = "target_hit"
                elif stop_loss and current_price <= stop_loss:
                    status = "stop_loss_hit"
                
                return {
                    "current_price": current_price,
                    "returns": returns,
                    "status": status,
                    "last_updated": datetime.now().isoformat()
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error calculating performance: {e}")
            return {}
    
    async def send_notifications(self, signals):
        """Send notifications about new signals"""
        try:
            if not signals:
                logger.info("No signals to notify about")
                return
            
            # Prepare notification content
            notification_data = {
                "run_type": self.run_time,
                "run_name": self.config["name"],
                "signal_count": len(signals),
                "signals": signals[:5],  # Top 5 signals
                "timestamp": datetime.now().isoformat()
            }
            
            # Send email notification
            await self.send_email_notification(notification_data)
            
            # Send in-app notifications
            await self.send_app_notifications(notification_data)
            
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    async def send_email_notification(self, data):
        """Send email notification"""
        try:
            # Create email content
            subject = self.config["email_subject"]
            
            # Generate HTML email content
            html_content = self.generate_email_html(data)
            
            # Send email
            await asyncio.to_thread(
                self.email_service.send_signal_notification,
                subject,
                html_content,
                data["signals"]
            )
            
            logger.info("Email notification sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def generate_email_html(self, data):
        """Generate HTML content for email"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <h2 style="color: #2563eb;">{data['run_name']}</h2>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Total Signals:</strong> {data['signal_count']}</p>
            
            <h3 style="color: #059669;">Top Signals:</h3>
            <table style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f3f4f6;">
                    <th style="border: 1px solid #d1d5db; padding: 8px;">Symbol</th>
                    <th style="border: 1px solid #d1d5db; padding: 8px;">Strategy</th>
                    <th style="border: 1px solid #d1d5db; padding: 8px;">Confidence</th>
                    <th style="border: 1px solid #d1d5db; padding: 8px;">Entry Price</th>
                    <th style="border: 1px solid #d1d5db; padding: 8px;">Target</th>
                </tr>
        """
        
        for signal in data["signals"]:
            html += f"""
                <tr>
                    <td style="border: 1px solid #d1d5db; padding: 8px;">{signal.get('symbol', 'N/A')}</td>
                    <td style="border: 1px solid #d1d5db; padding: 8px;">{signal.get('strategy', 'N/A')}</td>
                    <td style="border: 1px solid #d1d5db; padding: 8px;">{signal.get('confidence', 0):.2f}</td>
                    <td style="border: 1px solid #d1d5db; padding: 8px;">₹{signal.get('entry_price', 0):.2f}</td>
                    <td style="border: 1px solid #d1d5db; padding: 8px;">₹{signal.get('target_price', 0):.2f}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <p style="margin-top: 20px;">
                <a href="https://emergenttrader.onrender.com/signals" 
                   style="background-color: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                   View All Signals
                </a>
            </p>
            
            <p style="color: #6b7280; font-size: 12px; margin-top: 30px;">
                This is an automated message from EmergentTrader. 
                <br>Generated by scheduled signal scanner.
            </p>
        </body>
        </html>
        """
        
        return html
    
    async def send_app_notifications(self, data):
        """Send in-app notifications"""
        try:
            notification = {
                "title": f"New {data['run_name']} Signals",
                "message": f"Generated {data['signal_count']} new trading signals",
                "type": "signal_update",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            await asyncio.to_thread(
                self.notification_service.send_notification,
                notification
            )
            
            logger.info("In-app notification sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending in-app notification: {e}")
    
    async def send_error_notification(self, error_message):
        """Send error notification"""
        try:
            subject = f"🚨 EmergentTrader {self.config['name']} - Error Alert"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 20px;">
                <h2 style="color: #dc2626;">Error in {self.config['name']}</h2>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Error:</strong></p>
                <div style="background-color: #fef2f2; border: 1px solid #fecaca; padding: 10px; border-radius: 5px;">
                    <code>{error_message}</code>
                </div>
                
                <p style="margin-top: 20px;">
                    Please check the application logs for more details.
                </p>
            </body>
            </html>
            """
            
            await asyncio.to_thread(
                self.email_service.send_error_notification,
                subject,
                html_content
            )
            
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
    
    def generate_run_report(self, signals, saved_count):
        """Generate run report"""
        report = {
            "run_type": self.run_time,
            "run_name": self.config["name"],
            "timestamp": datetime.now().isoformat(),
            "total_signals_generated": len(signals),
            "signals_saved": saved_count,
            "strategies_used": self.config["strategies"],
            "min_confidence": self.config["min_confidence"],
            "success": True
        }
        
        # Save report to file
        report_file = f"reports/scheduled_run_{self.run_time}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("reports", exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Run report saved to {report_file}")
        return report

async def main():
    """Main function for scheduled execution"""
    parser = argparse.ArgumentParser(description='Scheduled Signal Generator')
    parser.add_argument('--time', choices=['morning', 'afternoon', 'evening'], 
                       default='morning', help='Time of day for signal generation')
    
    args = parser.parse_args()
    
    logger.info(f"Starting scheduled signal generation for {args.time}")
    
    try:
        generator = ScheduledSignalGenerator(args.time)
        report = await generator.run_full_scan()
        
        logger.info("Scheduled signal generation completed successfully")
        logger.info(f"Report: {json.dumps(report, indent=2)}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Scheduled signal generation failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
