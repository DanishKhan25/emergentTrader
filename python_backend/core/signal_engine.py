"""
Signal Engine - Core trading signal generation and management system
Orchestrates data fetching, strategy execution, and signal storage
"""

import sys
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add the python_backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.yfinance_fetcher import YFinanceFetcher
from core.shariah_filter import ShariahFilter
from core.strategies.momentum_strategy import MomentumStrategy
from core.strategies.mean_reversion_strategy import MeanReversionStrategy
from core.strategies.breakout_strategy import BreakoutStrategy
from core.strategies.value_investing_strategy import ValueInvestingStrategy
from core.backtest_engine import BacktestEngine

logger = logging.getLogger(__name__)

class SignalEngine:
    def __init__(self):
        self.data_fetcher = YFinanceFetcher()
        self.shariah_filter = ShariahFilter()
        
        # Initialize all available strategies
        self.strategies = {
            'momentum': MomentumStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'breakout': BreakoutStrategy(),
            'value_investing': ValueInvestingStrategy()
        }
        
        self.backtest_engine = BacktestEngine()
        
        # Signal storage
        self.active_signals = []
        self.signal_history = []
        
    def get_available_strategies(self) -> List[str]:
        """Get list of available trading strategies"""
        return list(self.strategies.keys())
        
    def get_strategy_info(self, strategy_name: str) -> Dict:
        """Get information about a specific strategy"""
        if strategy_name in self.strategies:
            strategy = self.strategies[strategy_name]
            return {
                'name': strategy.name,
                'parameters': strategy.get_strategy_params(),
                'description': strategy.__doc__ or f"{strategy.name} trading strategy"
            }
        return {}
    
    def get_shariah_universe(self) -> List[str]:
        """Get list of Shariah compliant stocks"""
        try:
            # Get NSE universe
            nse_stocks = self.data_fetcher.get_nse_universe()
            
            # Filter for Shariah compliance
            compliant_stocks = self.shariah_filter.get_shariah_universe(
                nse_stocks, self.data_fetcher
            )
            
            # Extract symbols
            shariah_symbols = [stock['symbol'] for stock in compliant_stocks]
            
            logger.info(f"Found {len(shariah_symbols)} Shariah compliant stocks")
            return shariah_symbols
            
        except Exception as e:
            logger.error(f"Error getting Shariah universe: {str(e)}")
            return []
    
    def generate_signals(self, symbols: Optional[List[str]] = None, strategy_name: str = 'momentum', 
                        shariah_only: bool = True, min_confidence: float = 0.6) -> List[Dict]:
        """
        Generate trading signals for given symbols using specified strategy
        
        Args:
            symbols: List of stock symbols (defaults to Shariah compliant universe if shariah_only=True)
            strategy_name: Strategy to use for signal generation
            shariah_only: Whether to use only Shariah compliant stocks
            min_confidence: Minimum confidence score for signals
            
        Returns:
            List of generated signals
        """
        try:
            # Determine stock universe
            if symbols is None:
                if shariah_only:
                    symbols = self.get_shariah_universe()
                else:
                    # Get full NSE universe
                    nse_stocks = self.data_fetcher.get_nse_universe()
                    symbols = [stock['symbol'] for stock in nse_stocks]
            
            if strategy_name not in self.strategies:
                logger.error(f"Strategy {strategy_name} not found. Available: {list(self.strategies.keys())}")
                return []
            
            strategy = self.strategies[strategy_name]
            generated_signals = []
            
            logger.info(f"Generating {strategy_name} signals for {len(symbols)} stocks")
            
            for symbol in symbols:
                try:
                    # Get stock data
                    stock_data = self.data_fetcher.get_nse_stock_data(symbol, period="1y")
                    
                    if stock_data.empty:
                        logger.warning(f"No data available for {symbol}")
                        continue
                    
                    # Add technical indicators
                    stock_data = self.data_fetcher.calculate_technical_indicators(stock_data)
                    
                    # Get stock fundamental info
                    stock_info = self.data_fetcher.get_stock_info(symbol)
                    
                    # Add Shariah compliance info
                    if shariah_only:
                        stock_info['shariah_compliant'] = True
                    else:
                        # Check Shariah compliance
                        shariah_stocks = self.get_shariah_universe()
                        stock_info['shariah_compliant'] = symbol in shariah_stocks
                    
                    # Generate signal
                    signal = strategy.generate_signal(symbol, stock_data, stock_info)
                    
                    if signal:
                        # Add unique signal ID if not present
                        if 'signal_id' not in signal:
                            signal['signal_id'] = str(uuid.uuid4())
                        
                        # Add strategy metadata
                        signal['strategy'] = strategy_name
                        signal['generated_at'] = datetime.now().isoformat()
                        signal['shariah_compliant'] = stock_info.get('shariah_compliant', False)
                        signal['status'] = 'ACTIVE'
                        
                        # Filter by confidence score
                        confidence = signal.get('confidence_score', 0)
                        if confidence >= min_confidence:
                            generated_signals.append(signal)
                            logger.info(f"Generated {signal['signal_type']} signal for {symbol} using {strategy_name}")
                        else:
                            logger.debug(f"Signal for {symbol} filtered out due to low confidence: {confidence}")
                    
                except Exception as e:
                    logger.error(f"Error generating signal for {symbol}: {str(e)}")
                    continue
            
            # Store signals in history
            self.signal_history.extend(generated_signals)
            
            # Update active signals (remove old ones, add new ones)
            self._update_active_signals(generated_signals)
            
            logger.info(f"Generated {len(generated_signals)} signals using {strategy_name} strategy")
            return generated_signals
            
        except Exception as e:
            logger.error(f"Error in signal generation: {str(e)}")
            return []
    
    def generate_multi_strategy_signals(self, symbols: Optional[List[str]] = None, 
                                      strategies: Optional[List[str]] = None,
                                      shariah_only: bool = True, 
                                      min_confidence: float = 0.6) -> Dict[str, List[Dict]]:
        """
        Generate signals using multiple strategies
        
        Args:
            symbols: List of stock symbols
            strategies: List of strategy names (defaults to all available)
            shariah_only: Whether to use only Shariah compliant stocks
            min_confidence: Minimum confidence score for signals
            
        Returns:
            Dictionary with strategy names as keys and signal lists as values
        """
        try:
            if strategies is None:
                strategies = list(self.strategies.keys())
            
            all_signals = {}
            
            for strategy_name in strategies:
                if strategy_name in self.strategies:
                    signals = self.generate_signals(
                        symbols=symbols,
                        strategy_name=strategy_name,
                        shariah_only=shariah_only,
                        min_confidence=min_confidence
                    )
                    all_signals[strategy_name] = signals
                else:
                    logger.warning(f"Strategy {strategy_name} not found")
                    all_signals[strategy_name] = []
            
            return all_signals
            
        except Exception as e:
            logger.error(f"Error in multi-strategy signal generation: {str(e)}")
            return {}
    
    def _update_active_signals(self, new_signals: List[Dict]):
        """Update active signals list"""
        try:
            # Remove expired signals (older than validity period)
            current_time = datetime.now()
            active_signals = []
            
            for signal in self.active_signals:
                generated_time = datetime.fromisoformat(signal.get('generated_at', current_time.isoformat()))
                validity_days = signal.get('validity_days', 5)
                
                if (current_time - generated_time).days < validity_days:
                    active_signals.append(signal)
            
            # Add new signals
            active_signals.extend(new_signals)
            
            self.active_signals = active_signals
            
        except Exception as e:
            logger.error(f"Error updating active signals: {str(e)}")
    
    def get_active_signals(self, strategy_name: Optional[str] = None) -> List[Dict]:
        """Get currently active signals"""
        try:
            if strategy_name:
                return [s for s in self.active_signals if s.get('strategy') == strategy_name]
            return self.active_signals
        except Exception as e:
            logger.error(f"Error getting active signals: {str(e)}")
            return []
    
    def backtest_strategy(self, 
                         strategy_name: str = 'momentum',
                         start_date: str = "2012-01-01", 
                         end_date: str = "2018-12-31",
                         symbols: Optional[List[str]] = None) -> Dict:
        """
        Run comprehensive backtest for a strategy
        
        Args:
            strategy_name: Strategy to backtest
            start_date: Backtest start date
            end_date: Backtest end date  
            symbols: List of symbols to test (defaults to Shariah universe)
            
        Returns:
            Backtest results dictionary
        """
        try:
            if symbols is None:
                symbols = self.get_shariah_universe()[:20]  # Limit for demo
            
            if strategy_name not in self.strategies:
                return {'error': f'Strategy {strategy_name} not found'}
            
            strategy = self.strategies[strategy_name]
            
            # Collect historical data for all symbols
            price_data = {}
            historical_signals = []
            
            for symbol in symbols:
                try:
                    # Get historical data
                    hist_data = self.data_fetcher.get_historical_data(symbol, start_date, end_date)
                    
                    if hist_data.empty or len(hist_data) < 50:  # Need enough data
                        continue
                    
                    # Add technical indicators
                    hist_data = self.data_fetcher.calculate_technical_indicators(hist_data)
                    price_data[symbol] = hist_data
                    
                    # Get stock info
                    stock_info = self.data_fetcher.get_stock_info(symbol)
                    
                    # Generate historical signals by walking through data
                    for i in range(50, len(hist_data), 5):  # Check every 5 days, need 50 days history
                        slice_data = hist_data.iloc[:i]
                        signal = strategy.generate_signal(symbol, slice_data, stock_info)
                        
                        if signal:
                            signal['date'] = hist_data.iloc[i]['date'].strftime('%Y-%m-%d')
                            signal['backtest_signal'] = True
                            historical_signals.append(signal)
                
                except Exception as e:
                    logger.error(f"Error processing {symbol} for backtest: {str(e)}")
                    continue
            
            if not historical_signals:
                return {'error': 'No signals generated for backtest'}
            
            # Run backtest
            backtest_results = self.backtest_engine.run_backtest(
                historical_signals, price_data, start_date, end_date
            )
            
            backtest_results['strategy'] = strategy_name
            backtest_results['symbols_tested'] = len(price_data)
            backtest_results['signals_generated'] = len(historical_signals)
            
            logger.info(f"Completed backtest for {strategy_name}: "
                       f"{len(historical_signals)} signals on {len(price_data)} stocks")
            
            return backtest_results
            
        except Exception as e:
            logger.error(f"Error running backtest: {str(e)}")
            return {'error': str(e)}
    
    def forward_test_evaluation(self, 
                               start_date: str = "2019-01-01",
                               end_date: str = "2024-12-31") -> Dict:
        """
        Evaluate strategy performance on forward test period (2019-2024)
        
        Args:
            start_date: Forward test start date
            end_date: Forward test end date
            
        Returns:
            Forward test results
        """
        try:
            # Use the same backtest engine but with forward test dates
            forward_results = self.backtest_strategy(
                strategy_name='momentum',
                start_date=start_date,
                end_date=end_date
            )
            
            forward_results['test_type'] = 'forward_test'
            forward_results['period_description'] = 'Out-of-sample forward test (2019-2024)'
            
            return forward_results
            
        except Exception as e:
            logger.error(f"Error running forward test: {str(e)}")
            return {'error': str(e)}
    
    def get_active_signals(self, strategy: Optional[str] = None) -> List[Dict]:
        """Get currently active trading signals"""
        try:
            if strategy:
                return [s for s in self.active_signals if s.get('strategy', '').lower() == strategy.lower()]
            return self.active_signals
        except Exception as e:
            logger.error(f"Error getting active signals: {str(e)}")
            return []
    
    def get_signal_performance(self, signal_id: str) -> Dict:
        """Get performance data for a specific signal"""
        try:
            # Find the signal
            signal = next((s for s in self.signal_history if s.get('signal_id') == signal_id), None)
            
            if not signal:
                return {'error': 'Signal not found'}
            
            symbol = signal['symbol']
            entry_date = signal.get('generated_at', signal.get('timestamp', ''))[:10]
            
            # Get recent price data to check performance
            recent_data = self.data_fetcher.get_nse_stock_data(symbol, period="3mo")
            
            if recent_data.empty:
                return {'error': 'No price data available'}
            
            # Calculate current performance
            entry_price = signal['entry_price']
            current_price = recent_data.iloc[-1]['close']
            
            performance = {
                'signal_id': signal_id,
                'symbol': symbol,
                'strategy': signal.get('strategy', ''),
                'entry_price': entry_price,
                'current_price': current_price,
                'absolute_return': current_price - entry_price,
                'percentage_return': ((current_price - entry_price) / entry_price) * 100,
                'target_price': signal.get('target_price', 0),
                'stop_loss': signal.get('stop_loss', 0),
                'days_active': (datetime.now() - datetime.fromisoformat(entry_date.replace('Z', '+00:00'))).days,
                'status': self._determine_signal_status(signal, current_price)
            }
            
            return performance
            
        except Exception as e:
            logger.error(f"Error getting signal performance: {str(e)}")
            return {'error': str(e)}
    
    def _determine_signal_status(self, signal: Dict, current_price: float) -> str:
        """Determine current status of a signal"""
        try:
            target = signal.get('target_price', 0)
            stop_loss = signal.get('stop_loss', 0)
            
            if target > 0 and current_price >= target:
                return 'target_hit'
            elif stop_loss > 0 and current_price <= stop_loss:
                return 'stop_loss_hit'
            else:
                return 'active'
        except:
            return 'unknown'
    
    def get_strategy_summary(self, strategy_name: str = 'momentum') -> Dict:
        """Get summary statistics for a strategy"""
        try:
            strategy_signals = [s for s in self.signal_history if s.get('strategy', '').lower() == strategy_name.lower()]
            
            if not strategy_signals:
                return {'error': f'No signals found for strategy {strategy_name}'}
            
            # Calculate summary metrics
            total_signals = len(strategy_signals)
            buy_signals = len([s for s in strategy_signals if s.get('signal_type') == 'BUY'])
            sell_signals = len([s for s in strategy_signals if s.get('signal_type') == 'SELL'])
            
            # Confidence score statistics
            confidence_scores = [s.get('confidence_score', 0) for s in strategy_signals if s.get('confidence_score')]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            # Sector distribution
            sectors = {}
            for signal in strategy_signals:
                sector = signal.get('sector', 'Unknown')
                sectors[sector] = sectors.get(sector, 0) + 1
            
            return {
                'strategy_name': strategy_name,
                'total_signals': total_signals,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'average_confidence': round(avg_confidence, 3),
                'sector_distribution': sectors,
                'recent_signals': strategy_signals[-10:] if strategy_signals else [],
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting strategy summary: {str(e)}")
            return {'error': str(e)}

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize signal engine
    engine = SignalEngine()
    
    # Test signal generation
    print("Testing signal generation...")
    signals = engine.generate_signals(['RELIANCE', 'TCS', 'HDFCBANK'])
    print(f"Generated {len(signals)} signals")
    
    # Test backtest
    print("Testing backtest...")
    backtest_results = engine.backtest_strategy(
        symbols=['RELIANCE', 'TCS'], 
        start_date="2020-01-01", 
        end_date="2021-12-31"
    )
    print(f"Backtest completed with {backtest_results.get('total_trades', 0)} trades")