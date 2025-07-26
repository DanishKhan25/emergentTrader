"""
ML-Enhanced Signal Engine - Integrates ML Interface Engine with Signal Generation
Combines multi-strategy consensus signals with ML-based quality enhancement
"""

import sys
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
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

# Import Improved ML Interface Engine
from ml.improved_ml_inference_engine import ImprovedMLInferenceEngine

logger = logging.getLogger(__name__)

class MLEnhancedSignalEngine:
    """
    Enhanced Signal Engine with ML Integration
    
    Features:
    - Multi-strategy consensus signal generation
    - ML-based signal quality enhancement
    - Real-time signal filtering and scoring
    - Market regime-aware signal processing
    """
    
    def __init__(self, enable_ml: bool = True, ml_model_path: str = None):
        """Initialize ML-enhanced signal engine"""
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
        self.consensus_engine = ConsensusEngine(self)
        self.signal_db = SignalDatabase()
        
        # Initialize ML Interface Engine
        self.enable_ml = enable_ml
        self.ml_engine = None
        
        if self.enable_ml:
            try:
                self.ml_engine = ImprovedMLInferenceEngine(model_path=ml_model_path)
                logger.info("Improved ML Interface Engine initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize improved ML engine: {str(e)}")
                logger.info("Continuing without ML enhancement")
                self.enable_ml = False
        
        # Signal storage
        self.active_signals = []
        self.signal_history = []
        self.consensus_signals = []
        self.ml_enhanced_signals = []
        
        logger.info(f"ML-Enhanced Signal Engine initialized (ML enabled: {self.enable_ml})")
    
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
    
    def get_market_context(self) -> Dict:
        """Get current market context for ML enhancement"""
        try:
            # Get NIFTY data for market regime detection
            nifty_data = self.data_fetcher.get_nse_stock_data("^NSEI", period="6mo")
            
            if nifty_data.empty:
                logger.warning("Could not fetch NIFTY data for market context")
                return self._default_market_context()
            
            # Calculate market indicators
            current_price = nifty_data['Close'].iloc[-1]
            sma_20 = nifty_data['Close'].rolling(20).mean().iloc[-1]
            sma_50 = nifty_data['Close'].rolling(50).mean().iloc[-1]
            sma_200 = nifty_data['Close'].rolling(200).mean().iloc[-1] if len(nifty_data) >= 200 else sma_50
            
            # Market volatility (20-day)
            returns = nifty_data['Close'].pct_change()
            volatility = returns.rolling(20).std().iloc[-1] * (252 ** 0.5)  # Annualized
            
            # Market momentum (20-day return)
            momentum_20d = (current_price / nifty_data['Close'].iloc[-21] - 1) if len(nifty_data) >= 21 else 0
            
            # Determine market regime
            if current_price > sma_50 > sma_200:
                regime = 'BULL'
            elif current_price < sma_50 < sma_200:
                regime = 'BEAR'
            else:
                regime = 'SIDEWAYS'
            
            return {
                'regime': regime,
                'current_price': current_price,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'volatility': volatility,
                'trend_20d': momentum_20d,
                'above_sma_20': current_price > sma_20,
                'above_sma_50': current_price > sma_50,
                'above_sma_200': current_price > sma_200,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market context: {str(e)}")
            return self._default_market_context()
    
    def _default_market_context(self) -> Dict:
        """Default market context when data unavailable"""
        return {
            'regime': 'SIDEWAYS',
            'volatility': 0.20,
            'trend_20d': 0.0,
            'above_sma_20': True,
            'above_sma_50': True,
            'above_sma_200': False,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_ml_enhanced_signals(self, 
                                   symbols: Optional[List[str]] = None,
                                   shariah_only: bool = True,
                                   max_symbols: int = 50,
                                   min_ml_probability: float = 0.6) -> List[Dict]:
        """
        Generate signals with ML enhancement
        
        Args:
            symbols: List of symbols to analyze
            shariah_only: Whether to use only Shariah compliant stocks
            max_symbols: Maximum number of symbols to process
            min_ml_probability: Minimum ML probability threshold for signals
            
        Returns:
            List of ML-enhanced signals
        """
        try:
            logger.info("Generating ML-enhanced signals...")
            
            # Step 1: Generate consensus signals using existing engine
            consensus_signals = self.consensus_engine.generate_consensus_signals(
                symbols=symbols,
                shariah_only=shariah_only,
                max_symbols=max_symbols,
                min_strategy_confidence=0.5
            )
            
            if not consensus_signals:
                logger.warning("No consensus signals generated")
                return []
            
            logger.info(f"Generated {len(consensus_signals)} consensus signals for ML enhancement")
            
            # Step 2: Get market context for ML enhancement
            market_context = self.get_market_context()
            logger.info(f"Market context: {market_context['regime']} regime, {market_context['volatility']:.1%} volatility")
            
            # Step 3: Enhance signals with ML if enabled
            if self.enable_ml and self.ml_engine:
                enhanced_signals = self.ml_engine.enhance_signals_batch(consensus_signals, market_context)
                
                # Filter by ML probability
                high_quality_signals, low_quality_signals = self.ml_engine.filter_signals_by_quality(
                    enhanced_signals, min_ml_probability
                )
                
                logger.info(f"ML filtering: {len(high_quality_signals)} high quality, {len(low_quality_signals)} low quality")
                
                # Use high quality signals
                final_signals = high_quality_signals
                
            else:
                # No ML enhancement - use original signals
                final_signals = consensus_signals
                logger.info("ML enhancement disabled - using original consensus signals")
            
            # Step 4: Add metadata and store signals
            for signal in final_signals:
                signal['id'] = str(uuid.uuid4())
                signal['generated_at'] = datetime.now().isoformat()
                signal['signal_source'] = 'ml_enhanced_consensus' if self.enable_ml else 'consensus_engine'
                signal['market_context'] = market_context
                signal['ml_enhanced'] = self.enable_ml and self.ml_engine is not None
                
                # Add to storage
                self.ml_enhanced_signals.append(signal)
                self.active_signals.append(signal)
                self.signal_history.append(signal)
            
            # Step 5: Save to database
            if final_signals:
                saved_count = save_consensus_signals(final_signals)
                logger.info(f"Saved {saved_count}/{len(final_signals)} ML-enhanced signals to database")
            
            logger.info(f"Generated {len(final_signals)} ML-enhanced signals")
            return final_signals
            
        except Exception as e:
            logger.error(f"Error generating ML-enhanced signals: {str(e)}")
            return []
    
    def generate_signals(self, 
                        symbols: Optional[List[str]] = None, 
                        strategy_name: str = 'ml_consensus', 
                        shariah_only: bool = True, 
                        min_confidence: float = 0.6,
                        enable_ml_filter: bool = True) -> List[Dict]:
        """
        Generate trading signals with optional ML enhancement
        
        Args:
            symbols: List of stock symbols to analyze
            strategy_name: Strategy to use ('ml_consensus', 'consensus', or specific strategy)
            shariah_only: Whether to filter for Shariah compliant stocks only
            min_confidence: Minimum confidence threshold for signals
            enable_ml_filter: Whether to apply ML filtering
            
        Returns:
            List of trading signals
        """
        try:
            # ML-enhanced consensus signals (recommended)
            if strategy_name == 'ml_consensus':
                return self.generate_ml_enhanced_signals(
                    symbols=symbols,
                    shariah_only=shariah_only,
                    max_symbols=50,
                    min_ml_probability=min_confidence
                )
            
            # Regular consensus signals
            elif strategy_name == 'consensus':
                return self.consensus_engine.generate_consensus_signals(
                    symbols=symbols,
                    shariah_only=shariah_only,
                    max_symbols=50,
                    min_strategy_confidence=min_confidence
                )
            
            # Single strategy with optional ML enhancement
            elif strategy_name in self.strategies:
                signals = self._generate_single_strategy_signals(
                    symbols, strategy_name, shariah_only, min_confidence
                )
                
                # Apply ML enhancement if requested and available
                if enable_ml_filter and self.enable_ml and self.ml_engine and signals:
                    market_context = self.get_market_context()
                    enhanced_signals = self.ml_engine.enhance_signals_batch(signals, market_context)
                    
                    # Filter by ML probability
                    high_quality, _ = self.ml_engine.filter_signals_by_quality(
                        enhanced_signals, min_confidence
                    )
                    
                    return high_quality
                
                return signals
            
            else:
                available_strategies = list(self.strategies.keys()) + ['consensus', 'ml_consensus']
                logger.error(f"Strategy {strategy_name} not found. Available: {available_strategies}")
                return []
                
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}")
            return []
    
    def _generate_single_strategy_signals(self, 
                                        symbols: Optional[List[str]] = None, 
                                        strategy_name: str = 'momentum', 
                                        shariah_only: bool = True, 
                                        min_confidence: float = 0.6) -> List[Dict]:
        """Generate signals using a single strategy"""
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
                    
                except Exception as e:
                    logger.error(f"Error generating signal for {symbol}: {str(e)}")
                    continue
            
            # Store signals
            self.signal_history.extend(generated_signals)
            self._update_active_signals(generated_signals)
            
            # Save to database
            if generated_signals:
                saved_count = self.signal_db.save_signals_batch(generated_signals)
                logger.info(f"Saved {saved_count}/{len(generated_signals)} signals to database")
            
            return generated_signals
            
        except Exception as e:
            logger.error(f"Error in single strategy signal generation: {str(e)}")
            return []
    
    def get_shariah_universe(self, force_refresh: bool = False) -> List[str]:
        """Get list of Shariah compliant stocks"""
        try:
            nse_stocks = self.data_fetcher.get_nse_universe()
            shariah_symbols = self.shariah_filter.get_shariah_universe_smart_cached(
                nse_stocks, self.data_fetcher, force_refresh
            )
            logger.info(f"Found {len(shariah_symbols)} Shariah compliant stocks")
            return shariah_symbols
        except Exception as e:
            logger.error(f"Error getting Shariah universe: {str(e)}")
            return []
    
    def get_ml_enhanced_signals(self, days: int = 7) -> List[Dict]:
        """Get recent ML-enhanced signals"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            recent_signals = [
                signal for signal in self.ml_enhanced_signals
                if datetime.fromisoformat(signal['generated_at']) > cutoff_date
            ]
            
            return recent_signals
            
        except Exception as e:
            logger.error(f"Error getting ML-enhanced signals: {str(e)}")
            return []
    
    def get_ml_performance_summary(self) -> Dict:
        """Get ML enhancement performance summary"""
        try:
            if not self.enable_ml or not self.ml_engine:
                return {'ml_enabled': False, 'message': 'ML enhancement not available'}
            
            # Get model info
            model_info = self.ml_engine.get_model_info()
            
            # Count ML-enhanced signals
            ml_signals = [s for s in self.signal_history if s.get('ml_enhanced', False)]
            
            # Calculate ML statistics
            if ml_signals:
                ml_probabilities = [s.get('ml_probability', 0) for s in ml_signals]
                confidence_adjustments = [s.get('confidence_adjustment', 0) for s in ml_signals]
                
                avg_ml_probability = sum(ml_probabilities) / len(ml_probabilities)
                avg_confidence_adjustment = sum(confidence_adjustments) / len(confidence_adjustments)
                
                # Count recommendations
                recommendations = {}
                for signal in ml_signals:
                    rec = signal.get('ml_recommendation', 'UNKNOWN')
                    recommendations[rec] = recommendations.get(rec, 0) + 1
            else:
                avg_ml_probability = 0
                avg_confidence_adjustment = 0
                recommendations = {}
            
            return {
                'ml_enabled': True,
                'model_info': model_info,
                'total_signals_processed': len(self.signal_history),
                'ml_enhanced_signals': len(ml_signals),
                'ml_enhancement_rate': len(ml_signals) / len(self.signal_history) * 100 if self.signal_history else 0,
                'average_ml_probability': avg_ml_probability,
                'average_confidence_adjustment': avg_confidence_adjustment,
                'recommendation_breakdown': recommendations,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting ML performance summary: {str(e)}")
            return {'error': str(e)}
    
    def _update_active_signals(self, new_signals: List[Dict]):
        """Update active signals list"""
        try:
            current_time = datetime.now()
            active_signals = []
            
            for signal in self.active_signals:
                generated_time = datetime.fromisoformat(signal.get('generated_at', current_time.isoformat()))
                validity_days = signal.get('validity_days', 5)
                
                if (current_time - generated_time).days < validity_days:
                    active_signals.append(signal)
            
            active_signals.extend(new_signals)
            self.active_signals = active_signals
            
        except Exception as e:
            logger.error(f"Error updating active signals: {str(e)}")
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status including ML capabilities"""
        try:
            # Get database stats
            db_stats = self.signal_db.get_database_stats()
            
            # Get ML status
            ml_status = {
                'ml_enabled': self.enable_ml,
                'ml_engine_loaded': self.ml_engine is not None,
                'ml_models_available': self.ml_engine.get_model_info() if self.ml_engine else {},
                'ml_enhanced_signals_count': len([s for s in self.signal_history if s.get('ml_enhanced', False)])
            }
            
            return {
                'strategies_available': len(self.strategies),
                'strategy_names': list(self.strategies.keys()),
                'consensus_engine_active': self.consensus_engine is not None,
                'active_signals': len(self.active_signals),
                'ml_enhanced_signals': len(self.ml_enhanced_signals),
                'signal_history_count': len(self.signal_history),
                'database_stats': db_stats,
                'ml_status': ml_status,
                'shariah_filter_type': 'SmartShariahFilter',
                'last_signal_generated': self.signal_history[-1]['generated_at'] if self.signal_history else None,
                'system_ready': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {'error': str(e), 'system_ready': False}
    
    def test_ml_integration(self) -> Dict:
        """Test ML integration with sample data"""
        try:
            if not self.enable_ml or not self.ml_engine:
                return {'status': 'failed', 'reason': 'ML engine not available'}
            
            # Create test signal
            test_signal = {
                'symbol': 'TCS',
                'strategy': 'momentum',
                'confidence': 0.7,
                'current_price': 3500,
                'signal_type': 'BUY',
                'rsi': 45,
                'volume_ratio': 1.2,
                'volatility': 0.18
            }
            
            # Get market context
            market_context = self.get_market_context()
            
            # Test ML prediction
            ml_result = self.ml_engine.predict_signal_quality(test_signal, market_context)
            
            return {
                'status': 'success',
                'test_signal': test_signal,
                'market_context': market_context,
                'ml_result': ml_result,
                'ml_engine_info': self.ml_engine.get_model_info(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error testing ML integration: {str(e)}")
            return {'status': 'failed', 'error': str(e)}

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🤖 Testing ML-Enhanced Signal Engine")
    print("=" * 50)
    
    # Initialize ML-enhanced signal engine
    engine = MLEnhancedSignalEngine(enable_ml=True)
    
    # Test ML integration
    ml_test = engine.test_ml_integration()
    print(f"ML Integration Test: {ml_test['status']}")
    
    if ml_test['status'] == 'success':
        print(f"ML Probability: {ml_test['ml_result']['ml_probability']:.1%}")
        print(f"Recommendation: {ml_test['ml_result']['recommendation']}")
    
    # Generate ML-enhanced signals
    print(f"\n🎯 Generating ML-Enhanced Signals...")
    ml_signals = engine.generate_ml_enhanced_signals(
        shariah_only=True, 
        max_symbols=10,
        min_ml_probability=0.6
    )
    
    print(f"Generated {len(ml_signals)} ML-enhanced signals")
    
    # Show sample signals
    for i, signal in enumerate(ml_signals[:3]):
        print(f"\nSignal {i+1}: {signal['symbol']} ({signal.get('strategy', 'consensus')})")
        print(f"  Original Confidence: {signal.get('confidence', 0):.1%}")
        if signal.get('ml_enhanced'):
            print(f"  ML Probability: {signal.get('ml_probability', 0):.1%}")
            print(f"  ML Recommendation: {signal.get('ml_recommendation', 'N/A')}")
            print(f"  Quality Score: {signal.get('ml_quality_score', 'N/A')}")
    
    # Get system status
    status = engine.get_system_status()
    print(f"\n📊 System Status:")
    print(f"  ML Enabled: {status['ml_status']['ml_enabled']}")
    print(f"  ML Engine Loaded: {status['ml_status']['ml_engine_loaded']}")
    print(f"  Active Signals: {status['active_signals']}")
    print(f"  ML Enhanced Signals: {status['ml_enhanced_signals']}")
    
    print(f"\n✅ ML-Enhanced Signal Engine test complete!")
