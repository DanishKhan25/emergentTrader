"""
Enhanced Signal Engine - Multi-Strategy Consensus Signal Generation
Integrates all 10 trading strategies through consensus engine for high-quality signals
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
from core.enhanced_shariah_filter_smart import SmartShariahFilter
from core.consensus_engine import ConsensusEngine
from core.strategies.momentum_strategy import MomentumStrategy
from core.strategies.mean_reversion_strategy import MeanReversionStrategy
from core.strategies.breakout_strategy import BreakoutStrategy
from core.strategies.value_investing_strategy import ValueInvestingStrategy
from core.strategies.swing_trading_strategy import SwingTradingStrategy
from core.strategies.multibagger_strategy import MultibaggerStrategy
from core.strategies.fundamental_growth_strategy import FundamentalGrowthStrategy
from core.strategies.sector_rotation_strategy import SectorRotationStrategy
from core.strategies.low_volatility_strategy import LowVolatilityStrategy
from core.strategies.pivot_cpr_strategy import PivotCPRStrategy
from core.backtest_engine import BacktestEngine
from core.signal_database import SignalDatabase, save_signals, save_consensus_signals

logger = logging.getLogger(__name__)

class EnhancedSignalEngine:
    def __init__(self):
        """Initialize enhanced signal engine with all strategies and consensus engine"""
        self.data_fetcher = YFinanceFetcher()
        self.shariah_filter = SmartShariahFilter()
        
        # Initialize all 10 trading strategies
        self.strategies = {
            'momentum': MomentumStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'breakout': BreakoutStrategy(),
            'value_investing': ValueInvestingStrategy(),
            'swing_trading': SwingTradingStrategy(),
            'multibagger': MultibaggerStrategy(),
            'fundamental_growth': FundamentalGrowthStrategy(),
            'sector_rotation': SectorRotationStrategy(),
            'low_volatility': LowVolatilityStrategy(),
            'pivot_cpr': PivotCPRStrategy()
        }
        
        self.backtest_engine = BacktestEngine()
        
        # Initialize consensus engine
        self.consensus_engine = ConsensusEngine(self)
        
        # Initialize signal database
        self.signal_db = SignalDatabase()
        
        # Signal storage
        self.active_signals = []
        self.signal_history = []
        self.consensus_signals = []
        
        logger.info("Enhanced Signal Engine initialized with 10 strategies, consensus engine, and database storage")
    
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
    
    def get_shariah_universe(self, force_refresh: bool = False) -> List[str]:
        """Get list of Shariah compliant stocks using smart filter with caching"""
        try:
            # Get NSE universe
            nse_stocks = self.data_fetcher.get_nse_universe()
            
            # Use cached universe method for better performance
            shariah_symbols = self.shariah_filter.get_shariah_universe_smart_cached(
                nse_stocks, self.data_fetcher, force_refresh
            )
            
            logger.info(f"Found {len(shariah_symbols)} Shariah compliant stocks (force_refresh: {force_refresh})")
            return shariah_symbols
            
        except Exception as e:
            logger.error(f"Error getting Shariah universe: {str(e)}")
            return []
    
    def generate_consensus_signals(self, 
                                 symbols: Optional[List[str]] = None,
                                 shariah_only: bool = True,
                                 max_symbols: int = 50) -> List[Dict]:
        """
        Generate high-quality consensus signals using all 10 strategies
        
        Args:
            symbols: List of symbols to analyze (None for auto-selection)
            shariah_only: Whether to use only Shariah compliant stocks
            max_symbols: Maximum number of symbols to process
            
        Returns:
            List of consensus signals with multi-strategy agreement
        """
        try:
            logger.info("Generating consensus signals using all 10 strategies...")
            
            # Generate consensus signals
            consensus_signals = self.consensus_engine.generate_consensus_signals(
                symbols=symbols,
                shariah_only=shariah_only,
                max_symbols=max_symbols,
                min_strategy_confidence=0.5
            )
            
            # Store consensus signals in memory and database
            for signal in consensus_signals:
                signal['id'] = str(uuid.uuid4())
                signal['generated_at'] = datetime.now().isoformat()
                signal['signal_source'] = 'consensus_engine'
                
                self.consensus_signals.append(signal)
                self.active_signals.append(signal)
                self.signal_history.append(signal)
            
            # Save consensus signals to database
            if consensus_signals:
                saved_count = save_consensus_signals(consensus_signals)
                logger.info(f"Saved {saved_count}/{len(consensus_signals)} consensus signals to database")
            
            logger.info(f"Generated {len(consensus_signals)} consensus signals")
            return consensus_signals
            
        except Exception as e:
            logger.error(f"Error generating consensus signals: {str(e)}")
            return []
    
    def generate_signals(self, symbols: Optional[List[str]] = None, 
                        strategy_name: str = 'consensus', 
                        shariah_only: bool = True, 
                        min_confidence: float = 0.6) -> List[Dict]:
        """
        Generate trading signals - defaults to consensus signals for best quality
        
        Args:
            symbols: List of stock symbols to analyze
            strategy_name: Strategy to use ('consensus' for multi-strategy, or specific strategy)
            shariah_only: Whether to filter for Shariah compliant stocks only
            min_confidence: Minimum confidence threshold for signals
            
        Returns:
            List of trading signals
        """
        try:
            # Use consensus engine by default for highest quality signals
            if strategy_name == 'consensus':
                return self.generate_consensus_signals(
                    symbols=symbols,
                    shariah_only=shariah_only,
                    max_symbols=50
                )
            
            # Single strategy signal generation
            elif strategy_name in self.strategies:
                return self._generate_single_strategy_signals(
                    symbols, strategy_name, shariah_only, min_confidence
                )
            
            else:
                logger.error(f"Strategy {strategy_name} not found. Available: {list(self.strategies.keys()) + ['consensus']}")
                return []
                
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}")
            return []
    
    def _generate_single_strategy_signals(self, 
                                        symbols: Optional[List[str]] = None, 
                                        strategy_name: str = 'momentum', 
                                        shariah_only: bool = True, 
                                        min_confidence: float = 0.6) -> List[Dict]:
        """
        Generate signals using a single strategy (fallback method)
        """
        try:
            # Determine stock universe
            if symbols is None:
                if shariah_only:
                    symbols = self.get_shariah_universe()
                else:
                    nse_stocks = self.data_fetcher.get_nse_universe()
                    symbols = [stock['symbol'] for stock in nse_stocks]
            
            # Limit symbols for performance
            symbols = symbols[:30]
            
            if strategy_name not in self.strategies:
                logger.error(f"Strategy {strategy_name} not found")
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
                        shariah_stocks = self.get_shariah_universe()
                        stock_info['shariah_compliant'] = symbol in shariah_stocks
                    
                    # Generate signal
                    signal = strategy.generate_signal(symbol, stock_data, stock_info)
                    
                    if signal:
                        # Add metadata
                        signal['signal_id'] = str(uuid.uuid4())
                        signal['strategy'] = strategy_name
                        signal['generated_at'] = datetime.now().isoformat()
                        signal['shariah_compliant'] = stock_info.get('shariah_compliant', False)
                        signal['status'] = 'ACTIVE'
                        signal['signal_source'] = 'single_strategy'
                        
                        # Filter by confidence score
                        confidence = signal.get('confidence_score', 0)
                        if confidence >= min_confidence:
                            generated_signals.append(signal)
                            logger.info(f"Generated {signal['signal_type']} signal for {symbol}")
                    
                except Exception as e:
                    logger.error(f"Error generating signal for {symbol}: {str(e)}")
                    continue
            
            # Store signals in memory and database
            self.signal_history.extend(generated_signals)
            self._update_active_signals(generated_signals)
            
            # Save signals to database
            if generated_signals:
                save_stats = self.signal_db.save_signals_batch(generated_signals)
                logger.info(f"Signal save stats: {save_stats['saved']} saved, {save_stats['duplicates']} duplicates skipped, {save_stats['errors']} errors")
                
                # Store save statistics for API response
                self._last_save_stats = save_stats
            else:
                self._last_save_stats = {'saved': 0, 'duplicates': 0, 'errors': 0, 'total_processed': 0}
            
            logger.info(f"Generated {len(generated_signals)} {strategy_name} signals")
            return generated_signals
            
        except Exception as e:
            logger.error(f"Error in single strategy signal generation: {str(e)}")
            return []
    
    def generate_multi_strategy_signals(self, 
                                      symbols: Optional[List[str]] = None, 
                                      strategies: Optional[List[str]] = None,
                                      shariah_only: bool = True, 
                                      min_confidence: float = 0.6) -> Dict[str, List[Dict]]:
        """
        Generate signals using multiple strategies (for comparison/analysis)
        
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
                    signals = self._generate_single_strategy_signals(
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
    
    def get_consensus_summary(self) -> Dict:
        """Get summary of consensus signal generation"""
        try:
            if not self.consensus_signals:
                return {'message': 'No consensus signals generated yet'}
            
            return self.consensus_engine.get_consensus_summary(self.consensus_signals)
            
        except Exception as e:
            logger.error(f"Error getting consensus summary: {str(e)}")
            return {'error': str(e)}
    
    def get_active_signals(self, strategy: Optional[str] = None, signal_source: Optional[str] = None) -> List[Dict]:
        """
        Get currently active trading signals
        
        Args:
            strategy: Filter by strategy name ('consensus' for consensus signals)
            signal_source: Filter by signal source ('consensus_engine' or 'single_strategy')
        """
        try:
            signals = self.active_signals
            
            if strategy:
                if strategy == 'consensus':
                    signals = [s for s in signals if s.get('strategy') == 'consensus']
                else:
                    signals = [s for s in signals if s.get('strategy', '').lower() == strategy.lower()]
            
            if signal_source:
                signals = [s for s in signals if s.get('signal_source') == signal_source]
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting active signals: {str(e)}")
            return []
    
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
    
    def get_strategy_performance_comparison(self) -> Dict:
        """
        Compare performance of individual strategies vs consensus
        """
        try:
            # Get signals by source
            consensus_signals = [s for s in self.signal_history if s.get('signal_source') == 'consensus_engine']
            single_strategy_signals = [s for s in self.signal_history if s.get('signal_source') == 'single_strategy']
            
            # Strategy breakdown
            strategy_counts = {}
            for signal in single_strategy_signals:
                strategy = signal.get('strategy', 'unknown')
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            
            return {
                'consensus_signals': len(consensus_signals),
                'single_strategy_signals': len(single_strategy_signals),
                'strategy_breakdown': strategy_counts,
                'total_signals': len(self.signal_history),
                'consensus_percentage': round(len(consensus_signals) / len(self.signal_history) * 100, 1) if self.signal_history else 0,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting strategy performance comparison: {str(e)}")
            return {'error': str(e)}
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        try:
            # Get database stats
            db_stats = self.signal_db.get_database_stats()
            
            return {
                'strategies_available': len(self.strategies),
                'strategy_names': list(self.strategies.keys()),
                'consensus_engine_active': self.consensus_engine is not None,
                'active_signals': len(self.active_signals),
                'consensus_signals': len([s for s in self.active_signals if s.get('strategy') == 'consensus']),
                'signal_history_count': len(self.signal_history),
                'database_stats': db_stats,
                'shariah_filter_type': 'SmartShariahFilter',
                'last_signal_generated': self.signal_history[-1]['generated_at'] if self.signal_history else None,
                'system_ready': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {'error': str(e), 'system_ready': False}
    
    def get_active_signals(self, strategy: Optional[str] = None) -> List[Dict]:
        """Get active signals from database"""
        try:
            return self.signal_db.get_active_signals(strategy=strategy)
        except Exception as e:
            logger.error(f"Error getting active signals: {str(e)}")
            return []
    
    def get_strategy_performance(self, strategy: str, days: int = 30) -> Dict:
        """Get strategy performance from database"""
        try:
            return self.signal_db.get_strategy_performance(strategy, days)
        except Exception as e:
            logger.error(f"Error getting strategy performance: {str(e)}")
            return {'strategy': strategy, 'error': str(e)}
    
    def get_consensus_signals_db(self, days: int = 7) -> List[Dict]:
        """Get recent consensus signals from database"""
        try:
            return self.signal_db.get_consensus_signals(days)
        except Exception as e:
            logger.error(f"Error getting consensus signals: {str(e)}")
            return []
    
    def get_signal_performance(self, signal_id: str) -> Dict:
        """Get performance tracking for a specific signal"""
        try:
            # This would need to be implemented with real-time price tracking
            # For now, return basic info
            return {
                'signal_id': signal_id,
                'status': 'tracking_not_implemented',
                'message': 'Real-time performance tracking will be implemented in next phase'
            }
        except Exception as e:
            logger.error(f"Error getting signal performance: {str(e)}")
            return {'error': str(e)}

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize enhanced signal engine
    engine = EnhancedSignalEngine()
    
    # Test consensus signal generation
    print("Testing consensus signal generation...")
    consensus_signals = engine.generate_consensus_signals(shariah_only=True, max_symbols=10)
    print(f"Generated {len(consensus_signals)} consensus signals")
    
    # Get system status
    status = engine.get_system_status()
    print(f"System status: {status}")
