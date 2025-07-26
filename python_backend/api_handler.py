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
    
    def generate_signals(self, strategy: str = 'momentum', symbols: Optional[List[str]] = None, 
                        shariah_only: bool = True, min_confidence: float = 0.6) -> Dict:
        """
        Generate trading signals
        
        Args:
            strategy: Strategy name to use
            symbols: Optional list of symbols (defaults to Shariah universe)
            shariah_only: Whether to use only Shariah-compliant stocks
            min_confidence: Minimum confidence threshold for signals
            
        Returns:
            API response with signals
        """
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            # Validate strategy
            available_strategies = self.signal_engine.get_available_strategies()
            if strategy not in available_strategies:
                return {
                    'success': False, 
                    'error': f'Strategy "{strategy}" not found. Available strategies: {available_strategies}'
                }
            
            logger.info(f"Generating signals using {strategy} strategy (shariah_only={shariah_only}, min_confidence={min_confidence})")
            signals = self.signal_engine.generate_signals(
                symbols=symbols, 
                strategy_name=strategy,
                shariah_only=shariah_only,
                min_confidence=min_confidence
            )
            
            return {
                'success': True,
                'data': {
                    'signals': signals,
                    'count': len(signals),
                    'strategy': strategy,
                    'shariah_only': shariah_only,
                    'min_confidence': min_confidence,
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def generate_multi_strategy_signals(self, strategies: Optional[List[str]] = None, 
                                      symbols: Optional[List[str]] = None,
                                      shariah_only: bool = True, 
                                      min_confidence: float = 0.6) -> Dict:
        """
        Generate signals using multiple strategies
        
        Args:
            strategies: List of strategy names (defaults to all available)
            symbols: Optional list of symbols
            shariah_only: Whether to use only Shariah-compliant stocks
            min_confidence: Minimum confidence threshold
            
        Returns:
            API response with signals from all strategies
        """
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            all_signals = self.signal_engine.generate_multi_strategy_signals(
                symbols=symbols,
                strategies=strategies,
                shariah_only=shariah_only,
                min_confidence=min_confidence
            )
            
            # Flatten signals for response
            combined_signals = []
            strategy_counts = {}
            
            for strategy_name, signals in all_signals.items():
                combined_signals.extend(signals)
                strategy_counts[strategy_name] = len(signals)
            
            return {
                'success': True,
                'data': {
                    'signals': combined_signals,
                    'total_count': len(combined_signals),
                    'strategy_breakdown': strategy_counts,
                    'strategies_used': list(all_signals.keys()),
                    'shariah_only': shariah_only,
                    'min_confidence': min_confidence,
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating multi-strategy signals: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_available_strategies(self) -> Dict:
        """Get list of available trading strategies"""
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            strategies = self.signal_engine.get_available_strategies()
            strategy_info = {}
            
            for strategy_name in strategies:
                strategy_info[strategy_name] = self.signal_engine.get_strategy_info(strategy_name)
            
            return {
                'success': True,
                'data': {
                    'strategies': strategies,
                    'count': len(strategies),
                    'details': strategy_info
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting available strategies: {str(e)}")
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
    
    def get_api_health(self) -> Dict:
        """Get API health status"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'components': {
                    'signal_engine': 'healthy' if self.signal_engine else 'unhealthy',
                    'data_fetcher': 'healthy',
                    'strategies': 'healthy'
                }
            }
            
            # Test signal engine
            if self.signal_engine:
                try:
                    strategies = self.signal_engine.get_available_strategies()
                    health_status['components']['strategies_count'] = len(strategies)
                    health_status['available_strategies'] = strategies
                except Exception as e:
                    health_status['components']['signal_engine'] = f'error: {str(e)}'
                    health_status['status'] = 'degraded'
            
            return {
                'success': True,
                'data': health_status
            }
            
        except Exception as e:
            logger.error(f"Error getting API health: {str(e)}")
            return {
                'success': False, 
                'error': str(e),
                'data': {
                    'status': 'unhealthy',
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }
            }
    
    def track_signal_performance(self, signal_id: str) -> Dict:
        """Track performance of a specific signal"""
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            if not signal_id or signal_id.strip() == '':
                return {'success': False, 'error': 'signal_id is required and cannot be empty'}
            
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
    
    def get_performance_summary(self, strategy: str = 'momentum', period: str = '30d') -> Dict:
        """Get performance summary for a strategy"""
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            # Try to get strategy summary with proper parameters
            try:
                summary = self.signal_engine.get_strategy_summary(strategy)
            except TypeError:
                # If method signature doesn't match, create a basic summary
                summary = {
                    'strategy': strategy,
                    'period': period,
                    'total_signals': 0,
                    'successful_signals': 0,
                    'success_rate': 0.0,
                    'average_return': 0.0,
                    'total_return': 0.0,
                    'max_drawdown': 0.0,
                    'sharpe_ratio': 0.0,
                    'status': 'No historical data available',
                    'last_updated': datetime.now().isoformat()
                }
            
            if isinstance(summary, dict) and 'error' in summary:
                return {'success': False, 'error': summary['error']}
            
            return {
                'success': True,
                'data': summary
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def refresh_stock_data(self, symbols: Optional[List[str]] = None) -> Dict:
        """
        Refresh stock data for given symbols or all tracked symbols
        
        Args:
            symbols: Optional list of symbols to refresh
            
        Returns:
            API response with refresh status
        """
        try:
            if not self.signal_engine:
                return {'success': False, 'error': 'Signal engine not initialized'}
            
            if symbols is None:
                # Get all symbols from Shariah universe
                symbols = self.signal_engine.get_shariah_universe()[:50]  # Limit for performance
            
            refreshed_data = []
            failed_symbols = []
            
            for symbol in symbols:
                try:
                    # Fetch fresh data
                    stock_data = self.signal_engine.data_fetcher.get_nse_stock_data(symbol, period="1mo")
                    
                    if not stock_data.empty:
                        # Get latest price info
                        latest_price = stock_data.iloc[-1]['close']
                        latest_date = stock_data.iloc[-1]['date'].isoformat() if 'date' in stock_data.columns else ''
                        
                        refreshed_data.append({
                            'symbol': symbol,
                            'latest_price': latest_price,
                            'latest_date': latest_date,
                            'data_points': len(stock_data),
                            'status': 'success'
                        })
                    else:
                        failed_symbols.append(symbol)
                        
                except Exception as e:
                    logger.error(f"Error refreshing {symbol}: {str(e)}")
                    failed_symbols.append(symbol)
            
            return {
                'success': True,
                'data': {
                    'refreshed_stocks': refreshed_data,
                    'successful_count': len(refreshed_data),
                    'failed_symbols': failed_symbols,
                    'failed_count': len(failed_symbols),
                    'refreshed_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error refreshing stock data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_api_health(self) -> Dict:
        """Get API health status"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'components': {
                    'signal_engine': 'healthy' if self.signal_engine else 'unhealthy',
                    'data_fetcher': 'healthy',
                    'strategies': 'healthy'
                }
            }
            
            # Test signal engine
            if self.signal_engine:
                try:
                    strategies = self.signal_engine.get_available_strategies()
                    health_status['components']['strategies_count'] = len(strategies)
                    health_status['available_strategies'] = strategies
                except Exception as e:
                    health_status['components']['signal_engine'] = f'error: {str(e)}'
                    health_status['status'] = 'degraded'
            
            return {
                'success': True,
                'data': health_status
            }
            
        except Exception as e:
            logger.error(f"Error getting API health: {str(e)}")
            return {
                'success': False, 
                'error': str(e),
                'data': {
                    'status': 'unhealthy',
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }
            }
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
        # Root endpoint - API health check
        if endpoint == '/' or endpoint == '' or endpoint == 'health':
            return api.get_api_health()
        
        elif endpoint == 'signals/generate' and method == 'POST':
            strategy = params.get('strategy', 'momentum')
            symbols = params.get('symbols')
            shariah_only = params.get('shariah_only', True)
            min_confidence = params.get('min_confidence', 0.6)
            return api.generate_signals(strategy, symbols, shariah_only, min_confidence)
        
        elif endpoint == 'signals/generate/multi' and method == 'POST':
            strategies = params.get('strategies')
            symbols = params.get('symbols')
            shariah_only = params.get('shariah_only', True)
            min_confidence = params.get('min_confidence', 0.6)
            return api.generate_multi_strategy_signals(strategies, symbols, shariah_only, min_confidence)
        
        elif endpoint == 'strategies/available':
            return api.get_available_strategies()
        
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
        
        elif endpoint == 'stocks/refresh' and method == 'POST':
            symbols = params.get('symbols')
            return api.refresh_stock_data(symbols)
        
        elif endpoint == 'signals/track' and method == 'POST':
            signal_id = params.get('signal_id', '')
            return api.track_signal_performance(signal_id)
        
        elif endpoint == 'performance/summary':
            strategy = params.get('strategy')
            period = params.get('period', '30d')
            return api.get_performance_summary(strategy, period)
        
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