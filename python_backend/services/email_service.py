"""
Email Notification Service for EmergentTrader
Sends trading signals and performance reports via email
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Dict, List, Optional
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        """Initialize email service with credentials from environment"""
        self.smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.email = os.getenv('EMAIL_ADDRESS')
        self.password = os.getenv('EMAIL_PASSWORD')
        self.recipient_emails = os.getenv('EMAIL_RECIPIENTS', '').split(',')
        
        if not self.email or not self.password:
            logger.warning("Email credentials not configured")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"Email service initialized for {self.email}")
    
    def send_email(self, subject: str, body: str, html_body: str = None, 
                   recipients: List[str] = None, attachments: List[str] = None) -> bool:
        """
        Send email with optional HTML body and attachments
        
        Args:
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            recipients: List of recipient emails (defaults to configured recipients)
            attachments: List of file paths to attach
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Email service not enabled - missing credentials")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['Subject'] = subject
            
            # Use provided recipients or default
            if recipients:
                to_emails = recipients
            else:
                to_emails = [email.strip() for email in self.recipient_emails if email.strip()]
            
            if not to_emails:
                logger.error("No recipient emails configured")
                return False
            
            msg['To'] = ', '.join(to_emails)
            
            # Add plain text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_signal_alert(self, signal: Dict) -> bool:
        """Send trading signal alert email"""
        try:
            symbol = signal.get('symbol', 'N/A')
            strategy = signal.get('strategy', 'Unknown')
            entry_price = signal.get('entry_price', 0)
            target_price = signal.get('target_price', 0)
            stop_loss = signal.get('stop_loss', 0)
            confidence = signal.get('confidence_score', 0)
            
            returns_potential = ((target_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
            
            subject = f"🚨 New Trading Signal: {symbol} ({strategy.upper()})"
            
            # Plain text body
            body = f"""
NEW TRADING SIGNAL ALERT
========================

Stock: {symbol}
Strategy: {strategy.upper()}
Entry Price: ₹{entry_price:.2f}
Target Price: ₹{target_price:.2f} (+{returns_potential:.1f}%)
Stop Loss: ₹{stop_loss:.2f}
Confidence: {confidence:.1%}

Signal Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

IMPORTANT DISCLAIMER:
This is an automated trading signal generated by EmergentTrader AI system.
Please conduct your own research before making any investment decisions.
Past performance does not guarantee future results.

Happy Trading!
EmergentTrader Team
            """
            
            # HTML body
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        🚨 New Trading Signal Alert
                    </h2>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #2980b9; margin-top: 0;">{symbol} - {strategy.upper()}</h3>
                        
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px; font-weight: bold; color: #34495e;">Entry Price:</td>
                                <td style="padding: 8px; color: #27ae60; font-weight: bold;">₹{entry_price:.2f}</td>
                            </tr>
                            <tr style="background: #ecf0f1;">
                                <td style="padding: 8px; font-weight: bold; color: #34495e;">Target Price:</td>
                                <td style="padding: 8px; color: #27ae60; font-weight: bold;">₹{target_price:.2f} (+{returns_potential:.1f}%)</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold; color: #34495e;">Stop Loss:</td>
                                <td style="padding: 8px; color: #e74c3c; font-weight: bold;">₹{stop_loss:.2f}</td>
                            </tr>
                            <tr style="background: #ecf0f1;">
                                <td style="padding: 8px; font-weight: bold; color: #34495e;">Confidence:</td>
                                <td style="padding: 8px; color: #8e44ad; font-weight: bold;">{confidence:.1%}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h4 style="color: #856404; margin-top: 0;">⚠️ Important Disclaimer</h4>
                        <p style="margin-bottom: 0; color: #856404;">
                            This is an automated trading signal generated by EmergentTrader AI system.
                            Please conduct your own research before making any investment decisions.
                            Past performance does not guarantee future results.
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #bdc3c7;">
                        <p style="color: #7f8c8d; font-size: 14px;">
                            Signal Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                            Happy Trading!<br>
                            <strong>EmergentTrader Team</strong>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self.send_email(subject, body, html_body)
            
        except Exception as e:
            logger.error(f"Error sending signal alert email: {str(e)}")
            return False
    
    def send_daily_report(self, signals: List[Dict], performance: Dict) -> bool:
        """Send daily trading report"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            subject = f"📊 Daily Trading Report - {today}"
            
            # Plain text body
            body = f"""
DAILY TRADING REPORT - {today}
===============================

SIGNALS GENERATED TODAY: {len(signals)}

"""
            
            if signals:
                body += "TODAY'S SIGNALS:\n"
                body += "-" * 50 + "\n"
                
                for i, signal in enumerate(signals, 1):
                    symbol = signal.get('symbol', 'N/A')
                    strategy = signal.get('strategy', 'Unknown')
                    entry_price = signal.get('entry_price', 0)
                    target_price = signal.get('target_price', 0)
                    confidence = signal.get('confidence_score', 0)
                    
                    returns_potential = ((target_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
                    
                    body += f"""
{i}. {symbol} ({strategy.upper()})
   Entry: ₹{entry_price:.2f}
   Target: ₹{target_price:.2f} (+{returns_potential:.1f}%)
   Confidence: {confidence:.1%}
"""
            else:
                body += "No signals generated today.\n"
            
            # Add performance summary
            body += f"""

PERFORMANCE SUMMARY:
-------------------
Total Active Signals: {performance.get('active_signals', 0)}
Success Rate: {performance.get('success_rate', 0):.1%}
Average Return: {performance.get('avg_return', 0):.1f}%

Best Performing Strategy: {performance.get('best_strategy', 'N/A')}

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EmergentTrader Team
            """
            
            # HTML version
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        📊 Daily Trading Report - {today}
                    </h2>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #2980b9; margin-top: 0;">Signals Generated Today: {len(signals)}</h3>
                        
                        {self._generate_signals_html_table(signals) if signals else '<p>No signals generated today.</p>'}
                    </div>
                    
                    <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #27ae60; margin-top: 0;">📈 Performance Summary</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li style="padding: 5px 0;"><strong>Active Signals:</strong> {performance.get('active_signals', 0)}</li>
                            <li style="padding: 5px 0;"><strong>Success Rate:</strong> {performance.get('success_rate', 0):.1%}</li>
                            <li style="padding: 5px 0;"><strong>Average Return:</strong> {performance.get('avg_return', 0):.1f}%</li>
                            <li style="padding: 5px 0;"><strong>Best Strategy:</strong> {performance.get('best_strategy', 'N/A')}</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #bdc3c7;">
                        <p style="color: #7f8c8d; font-size: 14px;">
                            Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                            <strong>EmergentTrader Team</strong>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self.send_email(subject, body, html_body)
            
        except Exception as e:
            logger.error(f"Error sending daily report: {str(e)}")
            return False
    
    def _generate_signals_html_table(self, signals: List[Dict]) -> str:
        """Generate HTML table for signals"""
        if not signals:
            return "<p>No signals to display.</p>"
        
        html = """
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <thead>
                <tr style="background: #3498db; color: white;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Symbol</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Strategy</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Entry</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Target</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Potential</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Confidence</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for i, signal in enumerate(signals):
            symbol = signal.get('symbol', 'N/A')
            strategy = signal.get('strategy', 'Unknown')
            entry_price = signal.get('entry_price', 0)
            target_price = signal.get('target_price', 0)
            confidence = signal.get('confidence_score', 0)
            
            returns_potential = ((target_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
            
            row_style = "background: #f8f9fa;" if i % 2 == 0 else "background: white;"
            
            html += f"""
                <tr style="{row_style}">
                    <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">{symbol}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{strategy.upper()}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">₹{entry_price:.2f}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">₹{target_price:.2f}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: #27ae60; font-weight: bold;">+{returns_potential:.1f}%</td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: #8e44ad; font-weight: bold;">{confidence:.1%}</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        """
        
        return html
    
    def send_performance_alert(self, alert_type: str, message: str) -> bool:
        """Send performance-related alerts"""
        try:
            subject = f"⚠️ EmergentTrader Alert: {alert_type}"
            
            body = f"""
EMERGENT TRADER ALERT
====================

Alert Type: {alert_type}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Message:
{message}

Please review the system status and take appropriate action if needed.

EmergentTrader Team
            """
            
            return self.send_email(subject, body)
            
        except Exception as e:
            logger.error(f"Error sending performance alert: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()

if __name__ == "__main__":
    # Test email service
    test_signal = {
        'symbol': 'RELIANCE',
        'strategy': 'multibagger',
        'entry_price': 2500.00,
        'target_price': 5000.00,
        'stop_loss': 2000.00,
        'confidence_score': 0.87
    }
    
    email_service.send_signal_alert(test_signal)
