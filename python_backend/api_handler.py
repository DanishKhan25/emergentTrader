"""
API Handler - Python backend interface for Next.js API routes
Handles all trading-related API calls and returns JSON responses
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

# Add the python_backend directory to the path
sys.path.append(os.path.dirname(__file__))

from core.signal_engine import SignalEngine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmergentTraderAPI:
    def __init__(self):
        """Initialize the trading API"""
        try:
            self.signal_engine = SignalEngine()
            logger.info("EmergentTrader API initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing API: {str(e)}")
            self.signal_engine = None
    
    def generate_signals(self, strategy: str = 'momentum', symbols: Optional[List[str]] = None) -> Dict:
        """
        Generate trading signals
        
        Args:
            strategy: Strategy name to use
            symbols: Optional list of symbols (defaults to Shariah universe)
            
        Returns:
            API response with signals
        """
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            logger.info(f"Generating signals using {strategy} strategy")
            signals = self.signal_engine.generate_signals(symbols, strategy)
            
            return {
                'success': True,
                'data': {
                    'signals': signals,
                    'count': len(signals),
                    'strategy': strategy,
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_active_signals(self, strategy: Optional[str] = None) -> Dict:
        """Get currently active signals"""
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            signals = self.signal_engine.get_active_signals(strategy)
            
            return {
                'success': True,
                'data': {
                    'signals': signals,
                    'count': len(signals),
                    'filter_strategy': strategy,
                    'retrieved_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting active signals: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_todays_signals(self) -> Dict:
        """Get signals generated today"""
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            today = datetime.now().date().isoformat()
            all_signals = self.signal_engine.get_active_signals()
            
            todays_signals = [
                signal for signal in all_signals 
                if signal.get('generated_at', signal.get('timestamp', ''))[:10] == today
            ]
            
            return {
                'success': True,
                'data': {
                    'signals': todays_signals,
                    'count': len(todays_signals),
                    'date': today,
                    'retrieved_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting today's signals: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def run_backtest(self, 
                    strategy: str = 'momentum',
                    start_date: str = "2012-01-01",
                    end_date: str = "2018-12-31",
                    symbols: Optional[List[str]] = None) -> Dict:
        """Run strategy backtest"""
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            logger.info(f"Running backtest for {strategy} from {start_date} to {end_date}")
            results = self.signal_engine.backtest_strategy(strategy, start_date, end_date, symbols)
            
            if 'error' in results:
                return {'success': False, 'error': results['error']}
            
            return {
                'success': True,
                'data': results
            }
            
        except Exception as e:
            logger.error(f"Error running backtest: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_backtest_results(self, test_type: str = 'backtest') -> Dict:
        """Get latest backtest results"""
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            if test_type == 'forward_test':
                results = self.signal_engine.forward_test_evaluation()
            else:
                results = self.signal_engine.backtest_strategy()
            
            return {
                'success': True,
                'data': results
            }
            
        except Exception as e:
            logger.error(f"Error getting backtest results: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_shariah_stocks(self) -> Dict:
        """Get Shariah compliant stock universe"""
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            logger.info("Fetching Shariah compliant stocks")
            stocks = self.signal_engine.get_shariah_universe()
            
            # Get additional info for each stock
            stock_details = []
            for symbol in stocks[:20]:  # Limit for performance
                try:
                    info = self.signal_engine.data_fetcher.get_stock_info(symbol)
                    if info:
                        stock_details.append({
                            'symbol': symbol,
                            'company_name': info.get('company_name', ''),
                            'sector': info.get('sector', ''),
                            'market_cap': info.get('market_cap', 0),
                            'current_price': info.get('current_price', 0)
                        })
                except:
                    continue
            
            return {
                'success': True,
                'data': {
                    'stocks': stock_details,
                    'total_symbols': len(stocks),
                    'detailed_count': len(stock_details),
                    'updated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting Shariah stocks: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_all_stocks(self) -> Dict:
        """Get all available stocks in NSE universe"""
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            all_stocks = self.signal_engine.data_fetcher.get_nse_universe()
            
            return {
                'success': True,
                'data': {
                    'stocks': all_stocks,
                    'count': len(all_stocks),
                    'market': 'NSE',
                    'updated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting all stocks: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def track_signal_performance(self, signal_id: str) -> Dict:
        """Track performance of a specific signal"""
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            performance = self.signal_engine.get_signal_performance(signal_id)
            
            if 'error' in performance:
                return {'success': False, 'error': performance['error']}
            
            return {
                'success': True,
                'data': performance
            }
            
        except Exception as e:
            logger.error(f"Error tracking signal performance: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_performance_summary(self, strategy: str = 'momentum') -> Dict:
        """Get performance summary for a strategy"""
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            summary = self.signal_engine.get_strategy_summary(strategy)
            
            if 'error' in summary:
                return {'success': False, 'error': summary['error']}
            
            return {
                'success': True,
                'data': summary
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_report(self, report_type: str = 'daily', recipients: Optional[List[str]] = None) -> Dict:
        """Send trading report via email/telegram"""
        try:
            # For now, just return a mock response
            # TODO: Implement actual email/telegram sending
            return {
                'success': True,
                'data': {
                    'message': f'{report_type} report sent successfully',
                    'recipients': recipients or ['default@example.com'],
                    'sent_at': datetime.now().isoformat(),
                    'report_type': report_type
                }
            }
            
        except Exception as e:
            logger.error(f"Error sending report: {str(e)}")
            return {'success': False, 'error': str(e)}


def handle_api_request(endpoint: str, method: str = 'GET', params: Optional[Dict] = None) -> Dict:
    """
    Main API handler function called from Next.js
    
    Args:
        endpoint: API endpoint path
        method: HTTP method
        params: Request parameters
        
    Returns:
        API response dictionary
    """
    try:
        api = EmergentTraderAPI()
        params = params or {}
        
        # Route to appropriate handler based on endpoint
        if endpoint == 'signals/generate' and method == 'POST':
            strategy = params.get('strategy', 'momentum')
            symbols = params.get('symbols')
            return api.generate_signals(strategy, symbols)
        
        elif endpoint == 'signals/active' or endpoint == 'signals/open':
            strategy = params.get('strategy')
            return api.get_active_signals(strategy)
        
        elif endpoint == 'signals/today':
            return api.get_todays_signals()
        
        elif endpoint == 'backtest' and method == 'POST':
            strategy = params.get('strategy', 'momentum')
            start_date = params.get('start_date', '2012-01-01')
            end_date = params.get('end_date', '2018-12-31')
            symbols = params.get('symbols')
            return api.run_backtest(strategy, start_date, end_date, symbols)
        
        elif endpoint == 'backtest/results':
            test_type = params.get('type', 'backtest')
            return api.get_backtest_results(test_type)
        
        elif endpoint == 'stocks/shariah':
            return api.get_shariah_stocks()
        
        elif endpoint == 'stocks/all':
            return api.get_all_stocks()
        
        elif endpoint == 'signals/track' and method == 'POST':
            signal_id = params.get('signal_id', '')
            return api.track_signal_performance(signal_id)
        
        elif endpoint == 'performance/summary':
            strategy = params.get('strategy', 'momentum')
            return api.get_performance_summary(strategy)
        
        elif endpoint == 'report/send' and method == 'POST':
            report_type = params.get('type', 'daily')
            recipients = params.get('recipients')
            return api.send_report(report_type, recipients)
        
        else:
            return {
                'success': False,
                'error': f'Endpoint {endpoint} not found or method {method} not supported'
            }
            
    except Exception as e:
        logger.error(f"Error handling API request {endpoint}: {str(e)}")
        return {'success': False, 'error': str(e)}


# Test the API
if __name__ == "__main__":
    # Test basic functionality
    print("Testing EmergentTrader API...")
    
    # Test signal generation
    response = handle_api_request('signals/generate', 'POST', {'strategy': 'momentum'})
    print(f"Signal generation test: {response.get('success', False)}")
    
    # Test getting stocks
    response = handle_api_request('stocks/all', 'GET')
    print(f"Get stocks test: {response.get('success', False)}")
    
    print("API tests completed!")